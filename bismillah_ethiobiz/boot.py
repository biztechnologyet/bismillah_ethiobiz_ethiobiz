import frappe
from bismillah_ethiobiz.auto_company import ensure_company_default
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

    sanitize_boot_workspaces(bootinfo)

    # Inject Hadeeda Settings into boot payload for chat widget & inline AI
    try:
        settings = _get_hadeeda_settings()
        if settings and getattr(settings, "enabled", 0):
            bootinfo["hadeeda_settings"] = settings.as_dict()
    except Exception as e:
        frappe.logger("ethiobiz").error(f"Hadeeda boot injection error: {e}")

    primary_color = "#1FB6AE" 
    
    bootinfo.ethiobiz_theme_css = f"""
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
