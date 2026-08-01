import frappe
import requests
import json


def _get_hadeeda_settings():
    return frappe.get_single("HADEEDA Settings")


def _get_user_api_credentials(user):
    api_key = frappe.db.get_value("User", user, "api_key")
    api_secret = frappe.db.get_value("User", user, "api_secret")
    return api_key, api_secret


@frappe.whitelist()
def get_chat_config():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Authentication required", frappe.PermissionError)

    settings = _get_hadeeda_settings()
    api_key, api_secret = _get_user_api_credentials(user)
    company = frappe.defaults.get_user_default("company") or ""

    return {
        "webhook_url": settings.chat_webhook_url,
        "enabled": bool(settings.enabled and settings.chat_enabled),
        "session_id": f"{user}::{company}" if company else user,
        "full_name": frappe.db.get_value("User", user, "full_name") or user,
        "email": frappe.db.get_value("User", user, "email") or "",
        "username": user,
        "company": company,
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
    if '"type"' not in text:
        return None

    full_content = ""
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
            if isinstance(parsed, dict) and parsed.get("type") == "item":
                content = parsed.get("content", "")
                if content:
                    full_content += content
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

    return full_content if full_content else None


@frappe.whitelist(allow_guest=True, methods=["POST"])
def chat_webhook_proxy():
    """Server-side proxy for @n8n/chat widget webhook.

    Receives the chat payload from @n8n/chat, forwards it to n8n,
    parses the NDJSON string response into clean text, and returns
    [{"output": "clean text"}] as a raw JSON response.
    """
    from werkzeug.wrappers import Response as WerkzeugResponse

    settings = _get_hadeeda_settings()
    if not settings.enabled or not settings.chat_enabled:
        return WerkzeugResponse(
            json.dumps([{"output": "Chat is currently disabled."}]),
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

    webhook_url = settings.chat_webhook_url
    if not webhook_url:
        return WerkzeugResponse(
            json.dumps([{"output": "Webhook URL not configured."}]),
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
            body = json.dumps([{"output": clean_text}])
            return WerkzeugResponse(body, status=200, content_type="application/json")

        # 2. Try standard JSON
        try:
            data = json.loads(raw_text)
            if isinstance(data, list) and len(data) > 0 and "output" in data[0]:
                body = json.dumps(data)
            elif isinstance(data, dict) and "output" in data:
                body = json.dumps([data])
            elif isinstance(data, dict) and "message" in data:
                body = json.dumps([{"output": data["message"]}])
            else:
                body = json.dumps([{"output": raw_text}])
            return WerkzeugResponse(body, status=200, content_type="application/json")
        except (json.JSONDecodeError, TypeError):
            body = json.dumps([{"output": raw_text}])
            return WerkzeugResponse(body, status=200, content_type="application/json")

    except requests.exceptions.Timeout:
        frappe.logger("ethiobiz").error("chat_webhook_proxy timeout")
        body = json.dumps([{"output": "⚠️ Request timed out. Please try again."}])
        return WerkzeugResponse(body, status=200, content_type="application/json")
    except Exception as e:
        frappe.logger("ethiobiz").error(f"chat_webhook_proxy error: {e}")
        body = json.dumps([{"output": "⚠️ An error occurred. Please try again."}])
        return WerkzeugResponse(body, status=200, content_type="application/json")


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

    payload = {
        "action": "sendMessage",
        "sessionId": f"{user}::{company}" if company else user,
        "chatInput": prompt,
        "metadata": {
            "source": "inline",
            "username": user,
            "full_name": full_name,
            "company": company,
            "api_key": api_key or "",
            "api_secret": api_secret or "",
            "field_context": context or "",
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
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            reply = data[0].get("json", {}).get("message", "") or data[0].get("message", "")
        elif isinstance(data, dict):
            reply = data.get("message", "") or data.get("output", "")
        else:
            reply = str(data)
        return {"reply": reply}
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
        "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js",
        "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js"
    ]
    for js in js_files:
        if js not in context.web_include_js:
            context.web_include_js.append(js)
