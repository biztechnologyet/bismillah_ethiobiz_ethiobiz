# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Frappe Hooks
Bismillah Ar-Rahman Ar-Rahim

Static theme deployment for EthioBiz ERPNext ecosystem.
© 2025 EthioBiz | Powered by Biz Technology Solutions
"""

from __future__ import unicode_literals

# ============================================
# EVENT NOTIFICATION PATCH
# ============================================
# Scope event email reminders to only event owners and participants,
# rather than sending them to all users with reminders enabled.

import frappe.desk.doctype.event.event as _event_module
from bismillah_ethiobiz.event_notification import send_event_digest as _patched_send_event_digest

_event_module.send_event_digest = _patched_send_event_digest

# ============================================
# RUNTIME SELF-HEALING PATCHES
# ============================================
import bismillah_ethiobiz.runtime_patch  # noqa: F401

# ============================================

app_name = "bismillah_ethiobiz"
app_title = "EthioBiz Theme"
app_publisher = "Biz Technology Solutions"
app_description = "Beautiful, static branding theme for EthioBiz ERPNext with glassmorphism design"
app_icon = "octicon octicon-globe"
app_color = "#1FB6AE"
app_email = "biz.technology@outlook.com"
app_version = "2.1.0"
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
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js",
    "/assets/bismillah_ethiobiz/js/pwa_register.js?v=1.0.4",
    "/assets/bismillah_ethiobiz/js/ethiobiz_desk_filters.js",
    "/assets/bismillah_ethiobiz/js/delivery_find_bizride.js"
]

# CSS for website (frontend/portal)
web_include_css = [
    "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css",
    "/assets/bismillah_ethiobiz/css/walta.css",
    "/assets/bismillah_ethiobiz/css/dagu.css",
    "/assets/bismillah_ethiobiz/css/magala_checkout.css",
    "/assets/bismillah_ethiobiz/css/magala_shop.css",
    "/assets/bismillah_ethiobiz/css/ethiobiz_map.css",
]

# JS for website (frontend/portal)
web_include_js = [
    "/assets/bismillah_ethiobiz/js/ethiobiz_fetch.js?v=1.0.0",
    "/assets/bismillah_ethiobiz/js/embedding_block.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js",
    "/assets/bismillah_ethiobiz/js/walta.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js",
    "/assets/bismillah_ethiobiz/js/pwa_register.js?v=1.0.4",
    "/assets/bismillah_ethiobiz/js/ethiobiz_particles.js?v=1.0.0",
    "/assets/bismillah_ethiobiz/js/all_products_custom.js?v=1.1.0",
    "/assets/bismillah_ethiobiz/js/magala_checkout.js?v=1.3.1",
]

# ============================================
# WEBSITE SETTINGS
# ============================================

# Custom page renderers (PWA: /sw.js + /manifest.webmanifest)
page_renderer = [
    "bismillah_ethiobiz.pwa_renderer.PWAStaticFile"
]

# Website route rules
website_route_rules = [
    {"from_route": "/theme-viewer", "to_route": "theme-viewer"},
    {"from_route": "/theme-viewer/<path:app>", "to_route": "theme-viewer"},
    {"from_route": "/walta", "to_route": "helpdesk"},
    {"from_route": "/walta/<path:app>", "to_route": "helpdesk"},
    {"from_route": "/helpdesk", "to_route": "helpdesk"},
    {"from_route": "/helpdesk/<path:app_path>", "to_route": "helpdesk"},
    {"from_route": "/lms", "to_route": "lms"},
    {"from_route": "/lms/<path:app_path>", "to_route": "lms"},
    {"from_route": "/map", "to_route": "map"},
    {"from_route": "/companies", "to_route": "map"},
    {"from_route": "/shop", "to_route": "shop"},
    {"from_route": "/bizhealth", "to_route": "bizhealth"},
    {"from_route": "/bizfix", "to_route": "bizfix"},
    {"from_route": "/bizride", "to_route": "bizride"},
    {"from_route": "/booking", "to_route": "booking"},
    {"from_route": "/bizhome", "to_route": "bizhome"},
]

# ============================================
# BOOT SESSION
# ============================================

# Inject data into frappe.boot at session start
boot_session = "bismillah_ethiobiz.boot.boot_session"

# ============================================
# SESSION CREATION (AUTO-COMPANY)
# ============================================

# Automatically set user's company default on login (new device fix)
# Reads from DocType: User > company field with fallback chain
on_session_creation = [
	"bismillah_ethiobiz.auto_company.on_session_creation",
	"bismillah_ethiobiz.api.ensure_csrf_token",
]

# Force Context Update
update_website_context = "bismillah_ethiobiz.api.update_website_context"

# ============================================
# DOC EVENTS
# ============================================

doc_events = {
    "Workspace": {
        "before_insert": "bismillah_ethiobiz.overrides.validate_workspace_permissions",
        "before_save": "bismillah_ethiobiz.overrides.validate_workspace_permissions"
    },
    "Company": {
        "before_insert": "bismillah_ethiobiz.overrides.validate_company_permissions"
    },
    "EthioBiz Theme": {
        "on_update": "bismillah_ethiobiz.api.on_theme_update"
    }
}

# ============================================
# OVERRIDE METHODS
# ============================================

# Override whitelisted methods
override_whitelisted_methods = {
    "frappe.desk.search.get_names_for_mentions": "bismillah_ethiobiz.mentions.get_names_for_mentions"
}

# ============================================
# FIXTURES
# ============================================

# Default fixtures (Translations + HADEEDA Settings)
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

# ============================================
# JINJA METHODS
# ============================================

# Add custom Jinja methods
jinja = {
    "methods": [
        "bismillah_ethiobiz.utils.get_theme_config"
    ]
}

# ============================================
# INSTALLATION
# ============================================

# After install hook
after_install = "bismillah_ethiobiz.install.after_install"

# Before uninstall hook
before_uninstall = "bismillah_ethiobiz.install.before_uninstall"

# ============================================
# MULTI-COMPANY ISOLATION
# ============================================

# Apply multi-company custom fields and property setters after every migrate
after_migrate = "bismillah_ethiobiz.setup_multi_company.after_migrate"
