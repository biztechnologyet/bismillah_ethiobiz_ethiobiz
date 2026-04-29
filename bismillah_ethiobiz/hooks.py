# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Frappe Hooks
Bismillah Ar-Rahman Ar-Rahim

Static theme deployment for EthioBiz ERPNext ecosystem.
© 2025 EthioBiz | Powered by Biz Technology Solutions
"""

from __future__ import unicode_literals

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
    "/assets/bismillah_ethiobiz/js/walta.js"
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
    "/assets/bismillah_ethiobiz/js/walta.js"
]

# ============================================
# WEBSITE SETTINGS
# ============================================

# Website route rules
website_route_rules = [
    {"from_route": "/theme-viewer", "to_route": "theme-viewer"},
    {"from_route": "/theme-viewer/<path:app>", "to_route": "theme-viewer"},
    {"from_route": "/walta", "to_route": "helpdesk"},
    {"from_route": "/walta/<path:app>", "to_route": "helpdesk"},
]

# Home page (optional override)
# home_page = "ethiobiz-home"

# ============================================
# BOOT SESSION
# ============================================

# Inject data into frappe.boot at session start
boot_session = "bismillah_ethiobiz.boot.boot_session"

# Force Context Update
update_website_context = "bismillah_ethiobiz.api.update_website_context"

# ============================================
# DOC EVENTS

# ============================================
# DOC EVENTS
# ============================================

# Hook into document events (if needed for theme updates)
# doc_events = {
#     "EthioBiz Theme": {
#         "on_update": "bismillah_ethiobiz.ethiobiz_theme.doctype.ethiobiz_theme.ethiobiz_theme.on_update"
#     }
# }

# ============================================
# OVERRIDE METHODS
# ============================================

# Override whitelisted methods
# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "bismillah_ethiobiz.event.get_events"
# }

# ============================================
# SCHEDULED TASKS
# ============================================

# Scheduler events (if needed)
# scheduler_events = {
#     "daily": [
#         "bismillah_ethiobiz.tasks.daily"
#     ]
# }

# ============================================
# TRANSLATIONS
# ============================================

# Default translations for theme labels
fixtures = [
    {
        "dt": "Translation",
        "filters": [
            ["source_text", "in", ["Frappe Light", "Timeless Night", "ERPNext", "Frappe"]]
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
