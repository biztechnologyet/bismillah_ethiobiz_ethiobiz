import frappe
import requests
import json
import re
from frappe.utils.password import get_decrypted_password
from frappe.utils import cint


def _get_hadeeda_settings():
    return frappe.get_single("HADEEDA Settings")


def _get_user_api_credentials(user):
    if not user or user == "Guest":
        return "", ""
    try:
        api_key = frappe.db.get_value("User", user, "api_key")
        api_secret = get_decrypted_password("User", user, "api_secret", raise_exception=False)

        if not api_key or not api_secret:
            user_doc = frappe.get_doc("User", user)
            if not user_doc.api_key:
                api_key = frappe.generate_hash(length=15)
                user_doc.api_key = api_key
                user_doc.save(ignore_permissions=True)

            if not api_secret:
                api_secret = frappe.generate_hash(length=15)
                from frappe.utils.password import set_encrypted_password
                set_encrypted_password("User", user, api_secret, "api_secret")

            frappe.db.commit()

        api_key = api_key or frappe.db.get_value("User", user, "api_key") or ""
        api_secret = api_secret or get_decrypted_password("User", user, "api_secret", raise_exception=False) or ""

        return api_key, api_secret
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


@frappe.whitelist(allow_guest=True)
def set_user_language(lang):
    """Persists user language preference for logged-in users and sets session cookie."""
    lang = "am" if lang in ("am", "amharic", "amh") else "en"
    user = frappe.session.user
    if user and user != "Guest":
        try:
            frappe.db.set_value("User", user, "language", lang, update_modified=False)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error updating user language: {e}")
    if hasattr(frappe.local, "cookie_manager") and frappe.local.cookie_manager:
        frappe.local.cookie_manager.set_cookie("preferred_language", lang)
    return {"status": "success", "language": lang, "user": user}




def _get_user_industry_religion(user):
    """Read the custom industry and religion fields from the User record."""
    if not user:
        return "", ""
    try:
        industry = frappe.db.get_value("User", user, "industry") or ""
        religion = frappe.db.get_value("User", user, "religion") or ""
        return industry, religion
    except Exception:
        return "", ""


def _get_user_behaviour_and_company_industry(user, company=None):
    """Retrieve user_behaviour from User and industry from Company."""
    if not user:
        return "", ""
    try:
        user_behaviour = frappe.db.get_value("User", user, "user_behaviour") or ""
        target_company = company or frappe.defaults.get_user_default("company", user) or ""
        company_industry = frappe.db.get_value("Company", target_company, "industry") if target_company else ""
        return user_behaviour or "", company_industry or ""
    except Exception:
        return "", ""



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


def _get_hadeeda_company_context(user, active_company=None):
    """Return company context for Hadeeda/agent integrations.

    Includes all companies the user has privilege to (EthioBiz memberships and
    Company User Permissions), with the default company clearly marked.
    """
    try:
        from bismillah_ethiobiz import company_access
        ctx = company_access.get_company_context(user) or {}
    except Exception:
        ctx = {}

    companies = list(ctx.get("companies") or [])
    active = ctx.get("active_company") or active_company or ""
    default = ctx.get("default_company") or active

    # Union Company User Permissions so all privileged companies are exposed.
    try:
        ups = frappe.get_all(
            "User Permission",
            filters={"user": user, "allow": "Company"},
            fields=["for_value", "is_default"],
        )
    except Exception:
        ups = []

    seen = {
        (c.get("name") if isinstance(c, dict) else c)
        for c in companies
        if (c.get("name") if isinstance(c, dict) else c)
    }
    for up in ups:
        name = up.get("for_value")
        if not name or name in seen:
            # If UP marks default, reflect it on existing entry.
            if name and up.get("is_default"):
                for c in companies:
                    cname = c.get("name") if isinstance(c, dict) else c
                    if cname == name and isinstance(c, dict):
                        c["is_default"] = True
            continue
        companies.append(
            {
                "name": name,
                "is_default": bool(up.get("is_default")),
                "role_profile": None,
                "roles": None,
                "source": "User Permission",
            }
        )
        seen.add(name)

    if not companies and active_company:
        companies = [{"name": active_company, "is_default": True, "role_profile": None, "roles": None}]
        seen.add(active_company)

    # Resolve default/active with privilege awareness.
    default = default or next((c.get("name") for c in companies if isinstance(c, dict) and c.get("is_default")), "")
    if not default and companies:
        first = companies[0]
        default = first.get("name") if isinstance(first, dict) else first
    if active and active not in seen:
        active = default
    if not active:
        active = default

    enriched = []
    for c in companies:
        name = c.get("name") if isinstance(c, dict) else c
        if not name:
            continue
        try:
            industry = frappe.db.get_value("Company", name, "custom_industry") or frappe.db.get_value("Company", name, "industry") or ""
        except Exception:
            industry = ""
        is_default = bool(c.get("is_default")) if isinstance(c, dict) else (name == default)
        if name == default:
            is_default = True
        enriched.append({
            "name": name,
            "is_default": is_default,
            "role_profile": c.get("role_profile") if isinstance(c, dict) else None,
            "roles": c.get("roles") if isinstance(c, dict) else None,
            "industry": industry,
        })

    # Keep default company first for consumer convenience, then others stable.
    enriched.sort(key=lambda x: (0 if x.get("is_default") else 1, x.get("name") or ""))

    return {
        "user": user,
        "companies": enriched,
        "allowed_companies": enriched,
        "active_company": active,
        "default_company": default,
    }


def _is_valid_hadeeda_service_token(settings=None):
    """Best-effort service-token auth for machine callers (HADEEDA agent/n8n)."""
    try:
        settings = settings or _get_hadeeda_settings()
        if not cint(getattr(settings, "enable_service_token_auth", 0)):
            return False
        token = ""
        try:
            token = settings.get_password("service_auth_token") or ""
        except Exception:
            token = getattr(settings, "service_auth_token", "") or ""
        if not token:
            return False
        req = getattr(frappe, "request", None)
        if not req:
            return False
        hdr = req.headers if getattr(req, "headers", None) else {}
        provided = (
            hdr.get("X-Hadeeda-Token")
            or hdr.get("X-HADEEDA-TOKEN")
            or ""
        )
        if not provided:
            auth = hdr.get("Authorization") or ""
            if auth.lower().startswith("bearer "):
                provided = auth.split(" ", 1)[1].strip()
        if not provided:
            return False
        try:
            from frappe.utils.password import passlibctx  # noqa: F401
        except Exception:
            pass
        return str(provided) == str(token)
    except Exception:
        return False


@frappe.whitelist(allow_guest=True)
def get_chat_config():
    user = frappe.session.user
    settings = _get_hadeeda_settings()

    is_guest = user == "Guest"

    if is_guest:
        # 2026-11-14 contract: guests must never receive the logged-in webhook.
        guest_webhook = getattr(settings, "chat_webhook_url_guest", None) or ""
        return {
            "webhook_url": guest_webhook,
            "is_guest": True,
            "enabled": bool(settings.enabled and settings.chat_enabled and guest_webhook),
            "session_id": f"guest::{frappe.utils.nowdate()}",
            "full_name": "Guest",
            "email": "",
            "username": "Guest",
            "company": "",
            "active_company": "",
            "default_company": "",
            "companies": [],
            "department": "",
            "designation": "",
            "industry": "",
            "religion": "",
            "user_behaviour": "",
            "company_industry": "",
            "language": settings.default_language or "en",
            "api_key": "",
            "api_secret": "",
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
            "bot_avatar": getattr(settings, "bot_avatar", "") or "",
            "chat_floating_button_label": getattr(settings, "chat_floating_button_label", "") or "Chat with us",
            "chat_floating_button_icon": getattr(settings, "chat_floating_button_icon", "") or "",
            "inline_widget_title": getattr(settings, "inline_widget_title", "") or "HADEEDA BizAi",
            "inline_widget_icon": getattr(settings, "inline_widget_icon", "") or "",
            "inline_badge_text": getattr(settings, "inline_badge_text", "") or "H",
        }

    api_key, api_secret = _get_user_api_credentials(user)
    company = frappe.defaults.get_user_default("company") or ""
    department, designation = _get_user_department_designation(user)
    company_ctx = _get_hadeeda_company_context(user, company)
    active_company = company_ctx.get("active_company") or company

    return {
        "webhook_url": settings.chat_webhook_url,
        "is_guest": False,
        "enabled": bool(settings.enabled and settings.chat_enabled),

        "session_id": f"{user}::{active_company}" if active_company else user,
        "full_name": frappe.db.get_value("User", user, "full_name") or user,
        "email": frappe.db.get_value("User", user, "email") or "",
        "username": user,
        "company": active_company,
        "active_company": active_company,
        "default_company": company_ctx.get("default_company") or active_company,
        "companies": company_ctx.get("companies") or [],
        "department": department,
        "designation": designation,
        "industry": _get_user_industry_religion(user)[0],
        "religion": _get_user_industry_religion(user)[1],
        "user_behaviour": _get_user_behaviour_and_company_industry(user, active_company)[0],
        "company_industry": _get_user_behaviour_and_company_industry(user, active_company)[1],
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
        "bot_avatar": getattr(settings, "bot_avatar", "") or "",
        "chat_floating_button_label": getattr(settings, "chat_floating_button_label", "") or "Chat with us",
        "chat_floating_button_icon": getattr(settings, "chat_floating_button_icon", "") or "",
        "inline_widget_title": getattr(settings, "inline_widget_title", "") or "HADEEDA BizAi",
        "inline_widget_icon": getattr(settings, "inline_widget_icon", "") or "",
        "inline_badge_text": getattr(settings, "inline_badge_text", "") or "H",
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

    # Inject user/company/API context server-side. Never trust client metadata for
    # credentials or tenant context; only authenticated sessions or a valid
    # HADEEDA service token may select a target user.
    session_user = frappe.session.user if (frappe.session.user and frappe.session.user != "Guest") else None
    target_user = session_user
    metadata_in = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    if not target_user and _is_valid_hadeeda_service_token(settings):
        candidate = metadata_in.get("username") or metadata_in.get("user_id") or ""
        if candidate and candidate != "Guest":
            target_user = candidate

    if target_user and target_user != "Guest" and frappe.db.exists("User", target_user):
        try:
            api_key, api_secret = _get_user_api_credentials(target_user)
            company = frappe.defaults.get_user_default("company", target_user) or ""
            full_name = frappe.db.get_value("User", target_user, "full_name") or target_user
            department, designation = _get_user_department_designation(target_user)
            company_ctx = _get_hadeeda_company_context(target_user, company)
            active_company = company_ctx.get("active_company") or company

            metadata = metadata_in.copy() if isinstance(metadata_in, dict) else {}
            metadata["username"] = target_user
            metadata["user_id"] = target_user
            metadata["full_name"] = full_name
            metadata["company"] = active_company
            metadata["active_company"] = active_company
            metadata["default_company"] = company_ctx.get("default_company") or active_company
            metadata["companies"] = company_ctx.get("companies") or []
            metadata["department"] = department
            metadata["designation"] = designation
            metadata["language"] = _get_user_language(target_user)
            industry, religion = _get_user_industry_religion(target_user)
            metadata["industry"] = industry
            metadata["religion"] = religion
            ub, ci = _get_user_behaviour_and_company_industry(target_user, active_company)
            metadata["user_behaviour"] = ub
            metadata["company_industry"] = ci
            metadata["source"] = metadata.get("source") or "widget"
            metadata["api_key"] = api_key or ""
            metadata["api_secret"] = api_secret or ""
            payload["metadata"] = metadata
        except Exception as e:
            frappe.logger("ethiobiz").error("chat_webhook_proxy metadata inject error: %s" % e)
    else:
        target_user = None
        # Never forward client-supplied identity/credentials for guests.
        guest_metadata = metadata_in.copy() if isinstance(metadata_in, dict) else {}
        guest_metadata["username"] = "Guest"
        guest_metadata["user_id"] = "Guest"
        guest_metadata["full_name"] = "Guest"
        guest_metadata["company"] = ""
        guest_metadata["active_company"] = ""
        guest_metadata["default_company"] = ""
        guest_metadata["companies"] = []
        guest_metadata["api_key"] = ""
        guest_metadata["api_secret"] = ""
        payload["metadata"] = guest_metadata


    # 2026-11-14 contract: guests use ONLY the dedicated guest webhook.
    # Never fall back to the authenticated/logged-in webhook URL.
    if not target_user:
        webhook_url = getattr(settings, "chat_webhook_url_guest", None) or ""
        missing_message = "Guest webhook URL is not configured."
        missing_status = 503
    else:
        webhook_url = settings.chat_webhook_url
        missing_message = "Webhook URL not configured."
        missing_status = 500

    if not webhook_url:
        return WerkzeugResponse(
            json.dumps({"output": missing_message}),
            status=missing_status, content_type="application/json"
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

    Includes master-identity multi-company context so agents can operate across
    all companies the user can access (e.g. Araya in Kistet + Sai Cakes).
    Security: caller must be the target user, System Manager/Administrator, or
    present a valid HADEEDA service token when service-token auth is enabled.
    """
    frappe.flags.ignore_csrf = True
    from werkzeug.wrappers import Response as WerkzeugResponse

    settings = _get_hadeeda_settings()
    caller = frappe.session.user
    service_call = _is_valid_hadeeda_service_token(settings)
    if (not caller or caller == "Guest") and not service_call:
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

    is_admin = caller in ("Administrator",) or ("System Manager" in (frappe.get_roles(caller) if caller and caller != "Guest" else []))
    if not service_call and caller != target and not is_admin:
        return WerkzeugResponse(
            json.dumps({"error": "Not permitted"}),
            status=403, content_type="application/json"
        )

    if not frappe.db.exists("User", target):
        return WerkzeugResponse(
            json.dumps({"error": "User not found"}),
            status=404, content_type="application/json"
        )

    api_key, api_secret = _get_user_api_credentials(target)
    default_company = frappe.defaults.get_user_default("company", target) or ""
    company_ctx = _get_hadeeda_company_context(target, default_company)
    active_company = company_ctx.get("active_company") or default_company
    department, designation = _get_user_department_designation(target)
    industry, religion = _get_user_industry_religion(target)
    ub, ci = _get_user_behaviour_and_company_industry(target, active_company)

    companies = company_ctx.get("companies") or []
    default_company = company_ctx.get("default_company") or active_company
    data = {
        "name": target,
        "full_name": frappe.db.get_value("User", target, "full_name") or target,
        "first_name": frappe.db.get_value("User", target, "first_name") or "",
        "company": active_company,
        "active_company": active_company,
        "default_company": default_company,
        "companies": companies,
        "allowed_companies": companies,
        "department": department,
        "designation": designation,
        "enabled": 1 if frappe.db.get_value("User", target, "enabled") else 0,
        "language": frappe.db.get_value("User", target, "language") or "",
        "api_key": api_key or "",
        "api_secret": api_secret or "",
        "industry": industry,
        "religion": religion,
        "user_behaviour": ub,
        "company_industry": ci,
    }
    return WerkzeugResponse(json.dumps(data), status=200, content_type="application/json")


@frappe.whitelist(allow_guest=True, methods=["POST"])
def chat_inline(prompt, context=None):
    """Inline AI endpoint.

    Routing contract (2026-11-26):
    - Guest users: Website Guest Hadeeda Webhook URL (`chat_webhook_url_guest`) only.
    - Logged-in users: Inline AI Webhook URL (`inline_webhook_url`) only.
    Guests never receive logged-in credentials, API keys, or private company context.
    """
    user = frappe.session.user
    settings = _get_hadeeda_settings()
    if not settings.enabled or not settings.inline_ai_enabled:
        frappe.throw("Inline AI is disabled", frappe.PermissionError)

    is_guest = not user or user == "Guest"
    if is_guest:
        frappe.flags.ignore_csrf = True
        inline_url = getattr(settings, "chat_webhook_url_guest", None) or ""
        api_key, api_secret = "", ""
        company = ""
        full_name = "Guest"
        department, designation = "", ""
        company_ctx = {"active_company": "", "default_company": "", "companies": []}
        active_company = ""
        session_id = f"guest::{frappe.utils.nowdate()}"
        document_content = ""
    else:
        inline_url = settings.inline_webhook_url
        api_key, api_secret = _get_user_api_credentials(user)
        company = frappe.defaults.get_user_default("company") or ""
        full_name = frappe.db.get_value("User", user, "full_name") or user
        department, designation = _get_user_department_designation(user)
        company_ctx = _get_hadeeda_company_context(user, company)
        active_company = company_ctx.get("active_company") or company
        company = active_company
        session_id = f"{user}::{active_company}" if active_company else user
        document_content = _get_document_context(context)

    chat_input = prompt
    if document_content:
        chat_input = "%s\n\n[DOCUMENT CONTEXT]\n%s" % (prompt, document_content)

    payload = {
        "action": "sendMessage",
        "sessionId": session_id,
        "chatInput": chat_input,
        "metadata": {
            "source": "inline",
            "username": "Guest" if is_guest else user,
            "user_id": "Guest" if is_guest else user,
            "full_name": full_name,
            "company": company,
            "active_company": company_ctx.get("active_company") or company,
            "default_company": company_ctx.get("default_company") or company,
            "companies": company_ctx.get("companies") or [],
            "department": department,
            "designation": designation,
            "industry": "" if is_guest else _get_user_industry_religion(user)[0],
            "religion": "" if is_guest else _get_user_industry_religion(user)[1],
            "user_behaviour": "" if is_guest else _get_user_behaviour_and_company_industry(user, company)[0],
            "company_industry": "" if is_guest else _get_user_behaviour_and_company_industry(user, company)[1],
            "language": (settings.default_language or "en") if is_guest else _get_user_language(user),
            "api_key": api_key or "",
            "api_secret": api_secret or "",
            "field_context": "" if is_guest else (context or ""),
            "document_content": document_content,
        }
    }

    if not inline_url:
        if is_guest:
            frappe.throw("Guest webhook URL is not configured for inline AI", frappe.DoesNotExistError)
        frappe.throw("Inline AI webhook URL is not configured", frappe.DoesNotExistError)

    headers = {"Content-Type": "application/json"}
    if settings.webhook_auth_header and settings.get_password("webhook_auth_value"):
        headers[settings.webhook_auth_header] = settings.get_password("webhook_auth_value")

    try:
        resp = requests.post(
            inline_url,
            json=payload,
            headers=headers,
            timeout=60
        )

        raw_text = resp.text

        clean_text = _parse_ndjson(raw_text)
        if clean_text:
            return {"reply": clean_text}

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
        return {"reply": "âš ï¸ Sorry, I encountered an error processing your request. Please try again."}

def ensure_csrf_token():
    """Mint a CSRF token for every non-guest session so website pages render
    a real frappe.csrf_token (base_template_page reads session data directly)
    and Frappe's CSRF validation is actually enforceable."""
    try:
        import traceback

        import frappe.sessions

        # Never mint mid-login: the fresh token would trip
        # validate_csrf_token() later within the same login request.
        req_path = ""
        try:
            req_path = frappe.local.request.path or ""
        except Exception:
            pass
        if (
            req_path.rstrip("/") in ("/login", "/api/method/login")
            or frappe.form_dict.get("cmd") == "login"
            or (frappe.form_dict.get("usr") and frappe.form_dict.get("pwd"))
        ):
            return

        if getattr(frappe.session, "user", "Guest") in (None, "Guest"):
            return
        if not frappe.local.session.data.get("csrf_token"):
            frappe.sessions.generate_csrf_token()
            try:
                frappe.local.cookie_manager.set_cookie(
                    "csrf_token", frappe.local.session.data.csrf_token)
            except Exception:
                pass
    except Exception:
        try:
            with open("/tmp/uwc_debug.log", "a") as _f:
                _f.write("CSRF_HOOK_ERR %s\n" % traceback.format_exc()[-250:])
        except Exception:
            pass


def update_website_context(context):
    import json as _json

    # Mint CSRF token at render time so base_template_page's
    # <!-- csrf_token --> replacement emits a REAL value and Frappe's
    # validation is enforceable (session-creation hook proved unreliable
    # under stale app_hooks caches).
    ensure_csrf_token()

    if not context.get("web_include_css"):
        context.web_include_css = []

    css_files = [
        "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css?v=2.3.1",
        "/assets/bismillah_ethiobiz/css/walta.css",
        "/assets/bismillah_ethiobiz/css/magala_checkout.css",
        "/assets/bismillah_ethiobiz/css/product_pages_atmosphere.css?v=1.1.1",
        "/assets/bismillah_ethiobiz/css/ethiobiz_pages_atmosphere.css?v=1.0.1",
        "/assets/bismillah_ethiobiz/css/ethiobiz_all_pages_polish.css?v=1.0.0",
        "/assets/bismillah_ethiobiz/css/hadeeda_inline_thread.css?v=1.0.0",
        "/assets/bismillah_ethiobiz/css/hadeeda_chat_enhance.css?v=1.0.0",
    ]
    for css in css_files:
        if css not in context.web_include_css:
            context.web_include_css.append(css)

    if not context.get("web_include_js"):
        context.web_include_js = []

    try:
        with open("/tmp/uwc_debug.log", "a") as _f:
            _f.write("IN len=%d %s\n" % (
                len(context.web_include_js), _json.dumps(list(context.web_include_js))))
    except Exception:
        pass

    js_files = [
        "/assets/bismillah_ethiobiz/js/ethiobiz_fetch.js?v=1.0.0",
        "/assets/bismillah_ethiobiz/js/embedding_block.js",
        "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js?v=2.5.7",
        "/assets/bismillah_ethiobiz/js/walta.js",
        "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.5.6",
        "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.6.1",
        "/assets/bismillah_ethiobiz/js/pwa_register.js?v=1.0.4",
        "/assets/bismillah_ethiobiz/js/ethiobiz_particles.js?v=1.0.0",
        "/assets/bismillah_ethiobiz/js/all_products_custom.js?v=1.1.0",
        "/assets/bismillah_ethiobiz/js/magala_checkout.js?v=1.4.0",
        "/assets/bismillah_ethiobiz/js/ethiobiz_i18n.js?v=2.2.4",
        "/assets/bismillah_ethiobiz/js/product_pages_atmosphere.js?v=1.1.1",
        "/assets/bismillah_ethiobiz/js/ethiobiz_pages_atmosphere.js?v=1.0.1",
        "/assets/bismillah_ethiobiz/js/ethiobiz_all_pages_polish.js?v=1.0.0",
        "/assets/bismillah_ethiobiz/js/hadeeda_inline_thread.js?v=1.0.0",
        "/assets/bismillah_ethiobiz/js/hadeeda_chat_enhance.js?v=1.0.0",
    ]
    for js in js_files:
        base = js.split("?")[0]
        if not any((x.split("?")[0] == base) for x in context.web_include_js):
            context.web_include_js.append(js)


@frappe.whitelist(allow_guest=True)
def get_theme_settings():
    """Return active EthioBiz theme settings including background and gradient configuration."""
    try:
        theme = frappe.get_single("EthioBiz Theme")
        has_bg = bool(getattr(theme, "enable_background_images", 0))
        return {
            "app_name": getattr(theme, "app_name", "EthioBiz") or "EthioBiz",
            "app_logo": getattr(theme, "app_logo", "") or "/assets/bismillah_ethiobiz/images/ethiobiz-glass-logo.png",
            "primary_color": getattr(theme, "primary_color", "#1FB6AE") or "#1FB6AE",
            "enable_background_images": has_bg,
            "enable_desk_bg_image": has_bg and bool(getattr(theme, "enable_desk_bg_image", 0)),
            "custom_desk_bg_image": getattr(theme, "custom_desk_bg_image", "") or "",
            "enable_website_bg_image": has_bg and bool(getattr(theme, "enable_website_bg_image", 0)),
            "custom_website_bg_image": getattr(theme, "custom_website_bg_image", "") or "",
            "dark_gradient_style": getattr(theme, "dark_gradient_style", "Obsidian Teal & Emerald Aura (Default)"),
            "bright_gradient_style": getattr(theme, "bright_gradient_style", "Sacred Ivory & Pearl Mist (Default)"),
            "website_gradient_style": getattr(theme, "website_gradient_style", "Deep Cosmos & Emerald Glass (Default)"),
            "glass_blur_intensity": getattr(theme, "glass_blur_intensity", "Balanced (16px)"),
        }
    except Exception as e:
        frappe.logger("ethiobiz").error(f"get_theme_settings error: {e}")
        return {
            "app_name": "EthioBiz",
            "primary_color": "#1FB6AE",
            "enable_background_images": False,
            "enable_desk_bg_image": False,
            "enable_website_bg_image": False,
        }


def on_theme_update(doc, method=None):
    """Triggered on save of EthioBiz Theme single doctype."""
    try:
        from bismillah_ethiobiz.ethiobiz_theme.doctype.ethiobiz_theme.ethiobiz_theme import EthioBizTheme
        EthioBizTheme.generate_theme_css(doc)
        frappe.clear_cache()
        frappe.publish_realtime("ethiobiz_theme_updated", message={"status": "Theme Updated"})
    except Exception as e:
        frappe.logger("ethiobiz").error(f"on_theme_update error: {e}")


@frappe.whitelist()
def set_user_particle_pref(enabled):
    """Set per-user particle preference (0 or 1)."""
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Login required")
    try:
        val = 1 if int(enabled) else 0
        frappe.db.set_value("User", frappe.session.user, "ethiobiz_enable_particles", val)
        frappe.db.commit()
        return {"status": "ok", "enabled": val}
    except Exception as e:
        frappe.logger("ethiobiz").error(f"set_user_particle_pref error: {e}")
        frappe.throw("Failed to save preference")


@frappe.whitelist(allow_guest=True)
def get_user_particle_pref():
    """Get particle preference: user pref > global Theme setting > default ON."""
    try:
        user_pref = None
        if frappe.session.user and frappe.session.user != "Guest":
            user_pref = frappe.db.get_value("User", frappe.session.user, "ethiobiz_enable_particles")
        if user_pref is not None:
            return {"enabled": bool(int(user_pref))}
        theme = frappe.get_single("EthioBiz Theme")
        global_val = getattr(theme, "enable_desk_animation", 1)
        return {"enabled": bool(int(global_val or 1))}
    except Exception:
        return {"enabled": True}




