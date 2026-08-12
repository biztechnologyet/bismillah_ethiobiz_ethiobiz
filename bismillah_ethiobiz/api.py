import frappe
import requests
import json
import re
from frappe.utils.password import get_decrypted_password


def _get_hadeeda_settings():
    return frappe.get_single("HADEEDA Settings")


def _get_user_api_credentials(user):
    if not user or user == "Guest":
        return "", ""
    try:
        api_key = frappe.db.get_value("User", user, "api_key")
        api_secret = get_decrypted_password("User", user, "api_secret", raise_exception=False)

        if not api_key or not api_secret:
            from frappe.core.doctype.user.user import generate_keys
            keys = generate_keys(user)
            api_key = keys.get("api_key") or frappe.db.get_value("User", user, "api_key")
            api_secret = keys.get("api_secret") or get_decrypted_password("User", user, "api_secret", raise_exception=False)

        return api_key or "", api_secret or ""
    except Exception as e:
        frappe.logger("ethiobiz").error("_get_user_api_credentials error for %s: %s" % (user, e))
        return "", ""

def _get_user_department_designation(user):
    """Resolve a user's Department + Designation from the Employee doctype,
    linked via Employee.user_id. A user may map to multiple Employee records;
    deterministic resolution rule:
      1. Prefer an Active employee.
      2. Prefer one with a non-empty department/designation.
      3. Otherwise first match.
    Returns (department, designation); empty strings if no link found."""
    if not user:
        return "", ""
    try:
        rows = frappe.db.sql(
            "SELECT name, status, department, designation FROM `tabEmployee` "
            "WHERE user_id = %s",
            user,
            as_dict=True,
        )
    except Exception as e:
        frappe.logger("ethiobiz").error("_get_user_department_designation error: %s" % e)
        return "", ""

    if not rows:
        return "", ""

    active = [r for r in rows if (r.get("status") or "").lower() == "active"]
    pool = active if active else rows

    def has_both(r):
        return bool(r.get("department") and r.get("designation"))

    for r in pool:
        if has_both(r):
            return r.get("department") or "", r.get("designation") or ""
    for r in pool:
        if r.get("department") or r.get("designation"):
            return r.get("department") or "", r.get("designation") or ""
    return "", ""


def _get_user_language(user):
    """User's language preference, falling back to the site default."""
    try:
        lang = frappe.db.get_value("User", user, "language")
        if lang:
            return lang
    except Exception:
        pass
    try:
        return _get_hadeeda_settings().default_language or "en"
    except Exception:
        return "en"


def _clean_text(value):
    """Strip HTML tags and collapse whitespace for readable AI context."""
    if not value:
        return ""
    try:
        from frappe.utils import strip_html
        text = strip_html(str(value))
    except Exception:
        text = str(value)
    return " ".join(text.split())


def _get_document_context(context):
    """Resolve the inline AI field context (doctype/docname/field) into the
    actual document content so the n8n workflow can act on the right record."""
    if not context:
        return ""
    try:
        ctx = json.loads(context) if isinstance(context, str) else (context or {})
    except (json.JSONDecodeError, TypeError, ValueError):
        return ""
    doctype = ctx.get("doctype") or ""
    docname = ctx.get("docname") or ""
    fieldname = ctx.get("field") or ""
    if not doctype or not docname:
        return ""

    try:
        if fieldname and frappe.db.get_value(doctype, docname, fieldname) is not None:
            value = frappe.db.get_value(doctype, docname, fieldname)
            if value:
                return "[%s %s | %s]\n%s" % (doctype, docname, fieldname, _clean_text(value))

        doc = frappe.get_doc(doctype, docname)
        parts = []
        for f in doc.meta.fields:
            if not f.get("fieldname"):
                continue
            if f.get("fieldtype") not in (
                "Text", "Small Text", "Long Text", "Text Editor", "Markdown Editor",
                "Data", "Select", "Link", "Currency", "Int", "Float", "Percent", "Date",
            ):
                continue
            val = doc.get(f.fieldname)
            if val is None or val == "":
                continue
            if f.fieldtype in ("Currency", "Int", "Float", "Percent") and not val:
                continue
            parts.append("%s: %s" % (f.fieldname, _clean_text(val)))
        if parts:
            return "[%s %s]\n%s" % (doctype, docname, "\n".join(parts))
        return "[%s %s]\n%s" % (doctype, docname, json.dumps(doc.as_dict(), default=str)[:2000])
    except Exception as e:
        frappe.logger("ethiobiz").error("_get_document_context error: %s" % e)
        return ""


@frappe.whitelist()
def get_chat_config():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Authentication required", frappe.PermissionError)

    settings = _get_hadeeda_settings()
    api_key, api_secret = _get_user_api_credentials(user)
    company = frappe.defaults.get_user_default("company") or ""
    department, designation = _get_user_department_designation(user)

    return {
        "webhook_url": settings.chat_webhook_url,
        "enabled": bool(settings.enabled and settings.chat_enabled),
        "session_id": f"{user}::{company}" if company else user,
        "full_name": frappe.db.get_value("User", user, "full_name") or user,
        "email": frappe.db.get_value("User", user, "email") or "",
        "username": user,
        "company": company,
        "department": department,
        "designation": designation,
        "language": _get_user_language(user),
        "api_key": api_key or "",
        "api_secret": api_secret or "",
        "bot_name": settings.bot_name or "HADEEDA",
        "widget_title": settings.widget_title or "HADEEDA AI Assistant",
        "widget_subtitle": settings.widget_subtitle or "",
        "widget_position": settings.widget_position or "Right",
        "widget_primary_color": settings.widget_primary_color or "#1FB6AE",
        "widget_mode": settings.widget_mode or "window",
        "initial_messages": json.loads(settings.initial_messages or "[]"),
        "allow_file_uploads": bool(settings.allow_file_uploads),
        "allowed_mime_types": settings.allowed_mime_types or "",
        "default_language": settings.default_language or "en",
        "enable_streaming": bool(getattr(settings, "enable_streaming", 1)),
    }



def _parse_ndjson(text):
    """Parse NDJSON (newline-delimited JSON) response from n8n Formatter node.
    Extracts content from type='item' lines and concatenates them into clean text."""
    if not text:
        return None

    full_content = ""
    has_error = False

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                msg_type = parsed.get("type")
                if msg_type == "item":
                    content = parsed.get("content", "")
                    if content:
                        full_content += content
                elif msg_type == "error":
                    has_error = True
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

    if full_content:
        full_content = full_content.replace('\\n', '\n')
        return full_content

    if has_error and not full_content:
        return "As-salamu alaykum! I am currently synchronizing my AI workflow. Please send your message again in a moment, InshaAllah!"

    return None


@frappe.whitelist(allow_guest=True, methods=["POST"])
def chat_webhook_proxy():
    """Server-side proxy for @n8n/chat widget webhook.

    Receives the chat payload from @n8n/chat, forwards it to n8n,
    parses the NDJSON string response, and returns {"output": text}
    as a raw JSON response.
    """
    frappe.flags.ignore_csrf = True
    from werkzeug.wrappers import Response as WerkzeugResponse

    settings = _get_hadeeda_settings()
    if not settings.enabled or not settings.chat_enabled:
        return WerkzeugResponse(
            json.dumps({"output": "Chat is currently disabled."}),
            status=200, content_type="application/json"
        )

    # Read raw request body or form_dict
    try:
        raw_body = frappe.request.get_data(as_text=True)
        if raw_body and raw_body.strip():
            payload = json.loads(raw_body)
        else:
            payload = dict(frappe.form_dict)
    except Exception:
        payload = dict(frappe.form_dict)

    # Inject the user's API credentials server-side so the n8n workflow always
    # receives the unmasked api_key/api_secret (same as chat_inline), regardless
    # of what the @n8n/chat widget forwards in its client-side metadata.
    user = frappe.session.user if (frappe.session.user and frappe.session.user != "Guest") else None
    if not user and isinstance(payload.get("metadata"), dict):
        user = payload["metadata"].get("username") or payload["metadata"].get("user_id")

    if user and user != "Guest" and frappe.db.exists("User", user):
        try:
            api_key, api_secret = _get_user_api_credentials(user)
            company = frappe.defaults.get_user_default("company", user) or ""
            full_name = frappe.db.get_value("User", user, "full_name") or user
            department, designation = _get_user_department_designation(user)

            metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
            metadata["username"] = user
            metadata["user_id"] = user
            metadata["full_name"] = full_name
            metadata["company"] = company
            metadata["department"] = department
            metadata["designation"] = designation
            metadata["language"] = _get_user_language(user)
            metadata["source"] = "widget"
            metadata["api_key"] = api_key or ""
            metadata["api_secret"] = api_secret or ""
            payload["metadata"] = metadata
        except Exception as e:
            frappe.logger("ethiobiz").error("chat_webhook_proxy metadata inject error: %s" % e)

    webhook_url = settings.chat_webhook_url
    if not webhook_url:
        return WerkzeugResponse(
            json.dumps({"output": "Webhook URL not configured."}),
            status=500, content_type="application/json"
        )

    headers = {"Content-Type": "application/json"}
    if settings.webhook_auth_header and settings.get_password("webhook_auth_value"):
        headers[settings.webhook_auth_header] = settings.get_password("webhook_auth_value")

    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=120
        )
        raw_text = resp.text

        # 1. Parse NDJSON streaming format
        clean_text = _parse_ndjson(raw_text)
        if clean_text:
            body = json.dumps({"output": clean_text})
            return WerkzeugResponse(body, status=200, content_type="application/json")

        # 2. Try standard JSON
        try:
            data = json.loads(raw_text)
            if isinstance(data, dict) and "output" in data:
                body = json.dumps({"output": data["output"]})
            elif isinstance(data, list) and len(data) > 0:
                item = data[0]
                out_val = None
                if isinstance(item, dict):
                    out_val = item.get("output") or item.get("json", {}).get("output") or item.get("message")
                if out_val:
                    body = json.dumps({"output": out_val})
                else:
                    body = json.dumps({"output": "As-salamu alaykum! Please send your message again, InshaAllah!"})
            elif isinstance(data, dict) and "message" in data:
                body = json.dumps({"output": data["message"]})
            else:
                body = json.dumps({"output": "As-salamu alaykum! Please send your message again, InshaAllah!"})
            return WerkzeugResponse(body, status=200, content_type="application/json")
        except (json.JSONDecodeError, TypeError):
            if '"type":"error"' in raw_text or '"type": "error"' in raw_text:
                fallback = "As-salamu alaykum! I am currently synchronizing my AI workflow. Please try again in a moment, InshaAllah!"
            else:
                fallback = raw_text if raw_text else "As-salamu alaykum! How can I assist you today?"
            body = json.dumps({"output": fallback})
            return WerkzeugResponse(body, status=200, content_type="application/json")

    except requests.exceptions.Timeout:
        frappe.logger("ethiobiz").error("chat_webhook_proxy timeout")
        body = json.dumps({"output": "⚠️ Request timed out. Please try again."})
        return WerkzeugResponse(body, status=200, content_type="application/json")
    except Exception as e:
        frappe.logger("ethiobiz").error(f"chat_webhook_proxy error: {e}")
        body = json.dumps({"output": "⚠️ An error occurred. Please try again."})
        return WerkzeugResponse(body, status=200, content_type="application/json")


@frappe.whitelist(methods=["POST"])
def get_user_credentials(username=None, telegram_username=None):
    """Return a user's API key + DECRYPTED API secret and profile as raw JSON.

    Replaces the n8n erpNext 'Get user' node which reads the api_secret Password
    field and gets the encrypted blob. This endpoint decrypts server-side via
    get_decrypted_password so CIO can authenticate. Authenticated callers only.
    """
    frappe.flags.ignore_csrf = True
    from werkzeug.wrappers import Response as WerkzeugResponse

    caller = frappe.session.user
    if not caller or caller == "Guest":
        return WerkzeugResponse(
            json.dumps({"error": "Authentication required"}),
            status=401, content_type="application/json"
        )

    target = username or ""
    if not target and telegram_username:
        target = frappe.db.get_value("User", {"telegram_username": telegram_username}, "name") or ""
    if not target:
        return WerkzeugResponse(
            json.dumps({"error": "User not found"}),
            status=404, content_type="application/json"
        )

    api_key, api_secret = _get_user_api_credentials(target)
    company = frappe.defaults.get_user_default("company", target) or ""
    department, designation = _get_user_department_designation(target)

    data = {
        "name": target,
        "full_name": frappe.db.get_value("User", target, "full_name") or target,
        "first_name": frappe.db.get_value("User", target, "first_name") or "",
        "company": company,
        "department": department,
        "designation": designation,
        "enabled": 1 if frappe.db.get_value("User", target, "enabled") else 0,
        "language": frappe.db.get_value("User", target, "language") or "",
        "api_key": api_key or "",
        "api_secret": api_secret or "",
    }
    return WerkzeugResponse(json.dumps(data), status=200, content_type="application/json")


@frappe.whitelist()
def chat_inline(prompt, context=None):
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Authentication required", frappe.PermissionError)

    settings = _get_hadeeda_settings()
    if not settings.enabled or not settings.inline_ai_enabled:
        frappe.throw("Inline AI is disabled", frappe.PermissionError)

    api_key, api_secret = _get_user_api_credentials(user)
    company = frappe.defaults.get_user_default("company") or ""
    full_name = frappe.db.get_value("User", user, "full_name") or user
    department, designation = _get_user_department_designation(user)
    document_content = _get_document_context(context)

    # Embed the actual document content directly into the message so the
    # n8n AI agent can act on the specific record the user is viewing,
    # even if it does not read the metadata object.
    chat_input = prompt
    if document_content:
        chat_input = "%s\n\n[DOCUMENT CONTEXT]\n%s" % (prompt, document_content)

    payload = {
        "action": "sendMessage",
        "sessionId": f"{user}::{company}" if company else user,
        "chatInput": chat_input,
        "metadata": {
            "source": "widget",
            "username": user,
            "user_id": user,
            "full_name": full_name,
            "company": company,
            "department": department,
            "designation": designation,
            "language": _get_user_language(user),
            "api_key": api_key or "",
            "api_secret": api_secret or "",
            "field_context": context or "",
            "document_content": document_content,
        }
    }

    headers = {"Content-Type": "application/json"}
    if settings.webhook_auth_header and settings.get_password("webhook_auth_value"):
        headers[settings.webhook_auth_header] = settings.get_password("webhook_auth_value")

    try:
        resp = requests.post(
            settings.inline_webhook_url,
            json=payload,
            headers=headers,
            timeout=60
        )
        raw_text = resp.text

        # 1. Try NDJSON parsing first (n8n Formatter node output)
        clean_text = _parse_ndjson(raw_text)
        if clean_text:
            return {"reply": clean_text}

        # 2. Try standard JSON
        try:
            data = json.loads(raw_text)
            if isinstance(data, list) and len(data) > 0:
                item = data[0]
                if isinstance(item, dict):
                    reply = item.get("output") or item.get("json", {}).get("message", "") or item.get("message", "") or str(item)
                else:
                    reply = str(item)
            elif isinstance(data, dict):
                reply = data.get("output") or data.get("message", "") or str(data)
            else:
                reply = str(data)
            return {"reply": reply}
        except (json.JSONDecodeError, TypeError):
            return {"reply": raw_text if raw_text else "No response received."}

    except Exception as e:
        frappe.logger("ethiobiz").error(f"chat_inline error: {e}")
        return {"reply": "⚠️ Sorry, I encountered an error processing your request. Please try again."}


def update_website_context(context):
    if not context.get("web_include_css"):
        context.web_include_css = []

    css_files = [
        "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css",
        "/assets/bismillah_ethiobiz/css/walta.css"
    ]
    for css in css_files:
        if css not in context.web_include_css:
            context.web_include_css.append(css)

    if not context.get("web_include_js"):
        context.web_include_js = []

    js_files = [
        "/assets/bismillah_ethiobiz/js/embedding_block.js",
        "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js",
        "/assets/bismillah_ethiobiz/js/walta.js",
        "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.5.5",
        "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.6.0"
    ]
    for js in js_files:
        if js not in context.web_include_js:
            context.web_include_js.append(js)
