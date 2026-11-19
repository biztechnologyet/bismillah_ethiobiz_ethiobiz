import frappe
from bismillah_ethiobiz.auto_company import ensure_company_default
from bismillah_ethiobiz.company_access import get_company_context
from bismillah_ethiobiz.workspace_cleaner import sanitize_boot_workspaces
from bismillah_ethiobiz.api import _get_hadeeda_settings

def boot_session(bootinfo):
    """
    Inject Dynamic Theme branding & Hadeeda Settings directly into boot session.
    """
    company_info = ensure_company_default()
    if company_info:
        bootinfo["ethiobiz_active_company"] = company_info.get("company")
        if company_info.get("needs_setup"):
            bootinfo["ethiobiz_company_needs_setup"] = True

    # Seed the navbar company selector from boot so multi-company users see their
    # current tenant immediately, without an extra round trip. The selector
    # refreshes from get_my_companies in the background.
    try:
        user = frappe.session.user
        if user and user != "Guest":
            context = get_company_context(user)
            companies = context.get("companies") or []
            if companies:
                bootinfo["ethiobiz_companies"] = companies
                bootinfo["ethiobiz_active_company"] = (
                    context.get("active_company")
                    or context.get("default_company")
                    or companies[0].get("name")
                )
                bootinfo["ethiobiz_default_company"] = context.get("default_company")
    except Exception as e:
        frappe.logger("ethiobiz").warning(f"Company boot context injection failed: {e}")

    sanitize_boot_workspaces(bootinfo)

    # Inject a sanitized Hadeeda settings snapshot into the boot payload.
    # Webhook URLs, auth headers/secrets, API credentials, and custom CSS are
    # intentionally excluded so they never reach the browser.
    try:
        settings = _get_hadeeda_settings()
        if settings and getattr(settings, "enabled", 0):
            bootinfo["hadeeda_settings"] = {
                "enabled": bool(settings.enabled),
                "bot_name": settings.bot_name or "HADEEDA",
                "default_language": settings.default_language or "en",
                "chat_enabled": bool(settings.chat_enabled),
                "enable_streaming": bool(getattr(settings, "enable_streaming", 1)),
                "widget_title": settings.widget_title or "",
                "widget_subtitle": settings.widget_subtitle or "",
                "widget_position": settings.widget_position or "Right",
                "widget_primary_color": settings.widget_primary_color or "#1FB6AE",
                "widget_mode": settings.widget_mode or "window",
                "allow_file_uploads": bool(settings.allow_file_uploads),
                "allowed_mime_types": settings.allowed_mime_types or "",
                "inline_ai_enabled": bool(settings.inline_ai_enabled),
                "trigger_character": settings.trigger_character or "/",
                "show_trigger_hint": bool(settings.show_trigger_hint),
                "excluded_doctypes": settings.excluded_doctypes or "",
                "excluded_fields": settings.excluded_fields or "",
                "bot_avatar": settings.bot_avatar or "",
            }
    except Exception as e:
        frappe.logger("ethiobiz").error(f"Hadeeda boot injection error: {e}")

    primary_color = "#1FB6AE" 
    
    bootinfo["ethiobiz_theme_css"] = f"""

    <style id="ethiobiz-boot-css">
        :root {{
            --primary-color: {primary_color} !important;
            --primary: {primary_color} !important;
            --blue-500: {primary_color} !important;
            --text-color: #0E1A1A !important;
            --btn-primary-bg: {primary_color} !important;
            --btn-primary-color: #ffffff !important;
        }}
        .btn-primary, 
        .primary-action, 
        button[data-label="Save"], 
        button[data-label="Create"],
        button[data-label="Submit"],
        button[data-label="Update"],
        button.btn-primary {{
            background-color: {primary_color} !important;
            border-color: {primary_color} !important;
            color: #ffffff !important;
            fill: #ffffff !important;
            background-image: none !important;
        }}
        .btn-primary:hover,
        button[data-label="Save"]:hover {{
            filter: brightness(0.9);
        }}
    </style>
    """
