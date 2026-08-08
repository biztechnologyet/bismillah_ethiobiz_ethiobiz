# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Boot Session
Inject theme configuration into frappe.boot
"""

import frappe
import json

from bismillah_ethiobiz.auto_company import ensure_company_default

def boot_session(bootinfo):
    """Inject EthioBiz theme + HADEEDA configuration into boot"""

    # LAYER 2: Ensure user has a company default (safety net for new device/cache clear)
    company_info = ensure_company_default()
    if company_info:
        bootinfo["ethiobiz_active_company"] = company_info.get("company")
        if company_info.get("needs_setup"):
            bootinfo["ethiobiz_company_needs_setup"] = True

    bootinfo["ethiobiz_theme"] = {
        "app_name": "EthioBiz",
        "app_tagline": "Uniting Humanity Through Shared Progress",
        "app_logo": "/assets/bismillah_ethiobiz/images/ethiobiz_logo.png",
        "primary_color": "#1FB6AE",
        "pillars": [
            {"id": "tibeb", "name": "Tibeb", "color": "#C9A24D", "domain": "Soul & Belief"},
            {"id": "dagu", "name": "Dagu", "color": "#2E3A8C", "domain": "Mind & Knowledge"},
            {"id": "magala", "name": "Magala", "color": "#2F6B4F", "domain": "Work & Economy"},
            {"id": "walta", "name": "Walta", "color": "#0F3557", "domain": "Security & Self"},
            {"id": "afocha", "name": "Afocha", "color": "#B83A3A", "domain": "Community"}
        ]
    }

    bootinfo["app_name"] = "EthioBiz"

    # ============================================
    # HADEEDA AI SETTINGS BOOT INJECTION
    # ============================================
    try:
        settings = frappe.get_single("HADEEDA Settings")
        bootinfo["hadeeda_settings"] = {
            "enabled": bool(settings.enabled),
            "chat_enabled": bool(settings.chat_enabled),
            "inline_ai_enabled": bool(settings.inline_ai_enabled),
            "bot_name": settings.bot_name or "HADEEDA",
            "widget_title": settings.widget_title or "HADEEDA AI Assistant",
            "widget_subtitle": settings.widget_subtitle or "",
            "widget_position": settings.widget_position or "Right",
            "widget_primary_color": settings.widget_primary_color or "#1FB6AE",
            "widget_mode": settings.widget_mode or "window",
            "trigger_character": settings.trigger_character or "/",
            "show_trigger_hint": bool(settings.show_trigger_hint),
            "excluded_doctypes": settings.excluded_doctypes or "",
            "excluded_fields": settings.excluded_fields or "",
            "default_language": settings.default_language or "en",
            "user_language": frappe.db.get_value("User", frappe.session.user, "language") or "",
            "allow_file_uploads": bool(settings.allow_file_uploads),
            "allowed_mime_types": settings.allowed_mime_types or "",
        }
    except Exception:
        bootinfo["hadeeda_settings"] = {
            "enabled": True,
            "chat_enabled": True,
            "inline_ai_enabled": True,
            "bot_name": "HADEEDA",
            "widget_title": "HADEEDA AI Assistant",
            "widget_subtitle": "",
            "widget_position": "Right",
            "widget_primary_color": "#1FB6AE",
            "widget_mode": "window",
            "trigger_character": "/",
            "show_trigger_hint": True,
            "excluded_doctypes": "",
            "excluded_fields": "",
            "default_language": "en",
            "user_language": "",
            "allow_file_uploads": False,
            "allowed_mime_types": "",
        }
