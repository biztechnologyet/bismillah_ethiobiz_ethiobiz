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
    }


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
