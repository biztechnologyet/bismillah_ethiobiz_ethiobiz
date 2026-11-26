# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Frappe Hooks
Bismillah Ar-Rahman Ar-Rahim

Static theme deployment for EthioBiz ERPNext ecosystem.
Ã‚Â© 2025 EthioBiz | Powered by Biz Technology Solutions
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
    "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css?v=2.3.1",
    "/assets/bismillah_ethiobiz/css/walta.css",
    "/assets/bismillah_ethiobiz/css/dagu.css",
    "/assets/bismillah_ethiobiz/css/hadeeda_inline_thread.css?v=1.2.2",
    "/assets/bismillah_ethiobiz/css/hadeeda_chat_enhance.css?v=1.2.1"
]

# JS included in desk (backend)
app_include_js = [
    "/assets/bismillah_ethiobiz/js/embedding_block.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js?v=2.5.7",
    "/assets/bismillah_ethiobiz/js/workspace_dropdown_fix.js",
    "/assets/bismillah_ethiobiz/js/force_layout.js",
    "/assets/bismillah_ethiobiz/js/walta.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.6.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.7.1",
    "/assets/bismillah_ethiobiz/js/hadeeda_inline_thread.js?v=1.2.2",
    "/assets/bismillah_ethiobiz/js/hadeeda_chat_enhance.js?v=1.2.1",
    "/assets/bismillah_ethiobiz/js/pwa_register.js?v=1.0.4",
    "/assets/bismillah_ethiobiz/js/ethiobiz_desk_filters.js",
    "/assets/bismillah_ethiobiz/js/delivery_find_bizride.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_company_switcher.js?v=2.1.0"
]

# CSS for website (frontend/portal)
web_include_css = [
    "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css?v=2.3.1",
    "/assets/bismillah_ethiobiz/css/walta.css",
    "/assets/bismillah_ethiobiz/css/dagu.css",
    "/assets/bismillah_ethiobiz/css/magala_checkout.css",
    "/assets/bismillah_ethiobiz/css/magala_shop.css?v=3.2.0",
    "/assets/bismillah_ethiobiz/css/ethiobiz_map.css",
    "/assets/bismillah_ethiobiz/css/product_pages_atmosphere.css?v=1.1.1",
    "/assets/bismillah_ethiobiz/css/ethiobiz_pages_atmosphere.css?v=1.0.1",
    "/assets/bismillah_ethiobiz/css/ethiobiz_all_pages_polish.css?v=1.0.0",
    "/assets/bismillah_ethiobiz/css/hadeeda_inline_thread.css?v=1.2.2",
    "/assets/bismillah_ethiobiz/css/hadeeda_chat_enhance.css?v=1.2.1",
]

# JS for website (frontend/portal)
web_include_js = [
    "/assets/bismillah_ethiobiz/js/ethiobiz_fetch.js?v=1.0.0",
    "/assets/bismillah_ethiobiz/js/embedding_block.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js?v=2.5.7",
    "/assets/bismillah_ethiobiz/js/walta.js",
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.6.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.7.1",
    "/assets/bismillah_ethiobiz/js/hadeeda_inline_thread.js?v=1.2.2",
    "/assets/bismillah_ethiobiz/js/hadeeda_chat_enhance.js?v=1.2.1",
    "/assets/bismillah_ethiobiz/js/pwa_register.js?v=1.0.4",
    "/assets/bismillah_ethiobiz/js/ethiobiz_particles.js?v=1.0.0",
    "/assets/bismillah_ethiobiz/js/all_products_custom.js?v=1.1.0",
    "/assets/bismillah_ethiobiz/js/magala_checkout.js?v=1.4.0",
    "/assets/bismillah_ethiobiz/js/ethiobiz_i18n.js?v=2.2.4",
    "/assets/bismillah_ethiobiz/js/ethiobiz_company_switcher.js?v=2.1.0",
    "/assets/bismillah_ethiobiz/js/product_pages_atmosphere.js?v=1.1.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_pages_atmosphere.js?v=1.0.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_all_pages_polish.js?v=1.0.0",
    "/assets/bismillah_ethiobiz/js/hadeeda_inline_thread.js?v=1.2.2",
    "/assets/bismillah_ethiobiz/js/hadeeda_chat_enhance.js?v=1.2.1",
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
    {"from_route": "/magala", "to_route": "shop"},
    {"from_route": "/magala/<path:item_code>", "to_route": "product"},
    {"from_route": "/product/<path:item_code>", "to_route": "product"},
    {"from_route": "/products/<path:item_code>", "to_route": "product"},
    # Published Website Items under general Item Group routes (for example
    # /food-dining/<slug>) use the same rich Dikko single-item experience.
    {"from_route": "/food-dining/<path:item_code>", "to_route": "product"},
    {"from_route": "/bizhealth", "to_route": "bizhealth"},
    {"from_route": "/doctor/<path:slug>", "to_route": "doctor_detail"},
    {"from_route": "/bizfix", "to_route": "bizfix"},
    {"from_route": "/bizride", "to_route": "bizride"},
    {"from_route": "/booking", "to_route": "booking"},
]

# Render the canonical published Website Item route with the same rich Dikko
# Shop single-item experience used by /product/<route>. The subclass keeps all
# standard webshop Website Item behaviour and only swaps the website template.
# EthioBiz multi-company: allow the same master User to be linked to Employees
# in different companies (company-scoped Employee records).
override_doctype_class = {
    "Website Item": "bismillah_ethiobiz.overrides.website_item.EthioBizWebsiteItem",
    "Employee": "bismillah_ethiobiz.overrides.employee.EthioBizEmployee",
}

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

# Guest-safe webshop cart (prevents HTTP 500 on /cart for visitors without a
# Customer party). See bismillah_ethiobiz/webshop_guest_cart.py.
before_request = [
    "bismillah_ethiobiz.webshop_guest_cart.apply",
    # Ensure HRMS user_id -> Employee lookups follow the active company on
    # every request (hooks.py itself may not be imported for API-only calls).
    "bismillah_ethiobiz.runtime_patch.ensure_employee_lookup_patch",
]

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
# MULTI-COMPANY MASTER IDENTITY (TASK-2026-00972)
# ============================================

# Company-level guard + query filter.  Administrator/System Manager bypass.
has_permission = {
    "Company": "bismillah_ethiobiz.company_access.company_has_permission",
}

permission_query_conditions = {
    "Company": "bismillah_ethiobiz.company_access.company_query_conditions",
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

