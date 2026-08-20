# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Frappe Hooks
Bismillah Ar-Rahman Ar-Rahim

Static theme deployment for EthioBiz ERPNext ecosystem.
© 2025-2026 EthioBiz | Powered by Biz Technology Solutions
"""

from __future__ import unicode_literals

# ============================================
# EVENT NOTIFICATION PATCH
# ============================================
import frappe.desk.doctype.event.event as _event_module
from bismillah_ethiobiz.event_notification import send_event_digest as _patched_send_event_digest

_event_module.send_event_digest = _patched_send_event_digest

# ============================================
# APP METADATA
# ============================================

app_name = "bismillah_ethiobiz"
app_title = "EthioBiz Theme"
app_publisher = "Biz Technology Solutions"
app_description = "Unified Cloud Super-Ecosystem and Branding Theme for EthioBiz ERPNext"
app_icon = "octicon octicon-globe"
app_color = "#1FB6AE"
app_email = "biz.technology@outlook.com"
app_version = "2.2.0"
app_license = "MIT"

# ============================================
# ASSET INCLUSION
# ============================================

# CSS included in desk (backend)
app_include_css = [
    "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css",
    "/assets/bismillah_ethiobiz/css/walta.css",
    "/assets/bismillah_ethiobiz/css/dagu.css"
]

# JS included in desk (backend)
app_include_js = [
    "/assets/bismillah_ethiobiz/js/embedding_block.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js",
    "/assets/bismillah_ethiobiz/js/workspace_dropdown_fix.js",
    "/assets/bismillah_ethiobiz/js/force_layout.js",
    "/assets/bismillah_ethiobiz/js/walta.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.5.5",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.6.0",
    "/assets/bismillah_ethiobiz/js/company_custom.js?v=2.0.0",
    "/assets/bismillah_ethiobiz/js/pwa_register.js?v=1.0.4"
]

# CSS for website (frontend/portal)
web_include_css = [
    "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css",
    "/assets/bismillah_ethiobiz/css/walta.css",
    "/assets/bismillah_ethiobiz/css/dagu.css"
]

# JS for website (frontend/portal)
web_include_js = [
    "/assets/bismillah_ethiobiz/js/embedding_block.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js",
    "/assets/bismillah_ethiobiz/js/walta.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.5.5",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.6.0",
    "/assets/bismillah_ethiobiz/js/all_products_custom.js?v=2.0.0",
    "/assets/bismillah_ethiobiz/js/pwa_register.js?v=1.0.4"
]

# Form JS mappings
doctype_js = {
    "Company": "public/js/company_custom.js"
}

# ============================================
# WEBSITE SETTINGS & ROUTING
# ============================================

page_renderer = [
    "bismillah_ethiobiz.pwa_renderer.PWAStaticFile"
]

website_route_rules = [
    {"from_route": "/theme-viewer", "to_route": "theme-viewer"},
    {"from_route": "/theme-viewer/<path:app>", "to_route": "theme-viewer"},
    {"from_route": "/walta", "to_route": "helpdesk"},
    {"from_route": "/walta/<path:app>", "to_route": "helpdesk"},
    {"from_route": "/helpdesk", "to_route": "helpdesk"},
    {"from_route": "/helpdesk/<path:app_path>", "to_route": "helpdesk"},
    {"from_route": "/lms", "to_route": "lms"},
    {"from_route": "/lms/<path:app_path>", "to_route": "lms"},
]

# ============================================
# BOOT SESSION & CONTEXT
# ============================================

boot_session = "bismillah_ethiobiz.boot.boot_session"
on_session_creation = "bismillah_ethiobiz.auto_company.on_session_creation"
update_website_context = "bismillah_ethiobiz.api.update_website_context"

# ============================================
# DOC EVENTS (UNIFIED & COMPLETE)
# ============================================

doc_events = {
    "Workspace": {
        "before_insert": "bismillah_ethiobiz.overrides.validate_workspace_permissions",
        "before_save": "bismillah_ethiobiz.overrides.validate_workspace_permissions"
    },
    "Company": {
        "before_insert": "bismillah_ethiobiz.overrides.validate_company_permissions",
        "before_save": "bismillah_ethiobiz.company_hooks.before_save_company",
        "validate": "bismillah_ethiobiz.company_hooks.before_save_company"
    }
}

# ============================================
# OVERRIDE METHODS & FIXTURES
# ============================================

override_whitelisted_methods = {
    "frappe.desk.search.get_names_for_mentions": "bismillah_ethiobiz.mentions.get_names_for_mentions"
}

fixtures = [
    {
        "dt": "Translation",
        "filters": [
            ["source_text", "in", ["Frappe Light", "Timeless Night", "ERPNext", "Frappe"]]
        ]
    },
    {
        "dt": "HADEEDA Settings",
        "filters": [
            ["name", "=", "HADEEDA Settings"]
        ]
    }
]

jinja = {
    "methods": [
        "bismillah_ethiobiz.utils.get_theme_config"
    ]
}

after_install = "bismillah_ethiobiz.install.after_install"
before_uninstall = "bismillah_ethiobiz.install.before_uninstall"
after_migrate = "bismillah_ethiobiz.setup_multi_company.after_migrate"
