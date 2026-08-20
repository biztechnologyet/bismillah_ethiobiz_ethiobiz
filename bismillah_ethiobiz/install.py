# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Installation Hooks
"""

import frappe, json, os

def after_install():
    """Run after app installation"""
    
    # Create default translations
    translations = [
        {"source_text": "Frappe Light", "translated_text": "EthioBiz Light", "language": "en"},
        {"source_text": "Timeless Night", "translated_text": "EthioBiz Dark", "language": "en"},
        {"source_text": "ERPNext", "translated_text": "EthioBiz", "language": "en"},
        {"source_text": "Welcome to Frappe Learning", "translated_text": "Welcome to Dagu Learning", "language": "en"},
    ]
    
    for t in translations:
        if not frappe.db.exists("Translation", {"source_text": t["source_text"], "language": t["language"]}):
            doc = frappe.get_doc({
                "doctype": "Translation",
                "source_text": t["source_text"],
                "translated_text": t["translated_text"],
                "language": t["language"]
            })
            doc.insert(ignore_permissions=True)
    
    # Create HADEEDA Settings doctype if not exists
    if not frappe.db.exists("DocType", "HADEEDA Settings"):
        json_path = os.path.join(os.path.dirname(__file__), "ethiobiz_theme", "doctype", "hadeeda_settings", "hadeeda_settings.json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                dt_def = json.load(f)
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": dt_def["name"],
                "module": "EthioBiz Theme",
                "custom": 1,
                "issingle": 1,
                "fields": dt_def["fields"],
                "permissions": dt_def.get("permissions", [{"role": "System Manager", "read": 1, "write": 1}]),
            })
            doc.insert(ignore_permissions=True)

    # Seed HADEEDA Settings defaults
    ensure_hadeeda_settings_installed()


def ensure_hadeeda_settings_installed():
    """Seed HADEEDA Settings with defaults if not already configured."""
    try:
        existing = frappe.db.get_value("HADEEDA Settings", "HADEEDA Settings", "name")
        if existing:
            return
        frappe.get_doc({
            "doctype": "HADEEDA Settings",
            "name": "HADEEDA Settings",
            "enabled": 1,
            "chat_enabled": 1,
            "webhook_url": "https://bizflow.ethiobiz.et/webhook/b15677a6-6611-42c8-88e2-43e0eb66f1b6/chat",
            "widget_title": "Hadeeda BizAi",
            "widget_primary_color": "#1FB6AE",
            "widget_mode": "window",
            "initial_messages": '["Selam!", "I am HADEEDA, your AI Executive Assistant. How can I help you today?"]',
            "allow_file_uploads": 1,
            "default_language": "en",
            "bot_name": "HADEEDA",
        }).insert(ignore_permissions=True)
    except Exception as e:
        print(f"EthioBiz: Error seeding HADEEDA Settings: {e}")

    # Create DOBiz PWA Settings doctype if not exists (custom=1, not auto-created by migrate)
    from bismillah_ethiobiz.pwa_settings import create_doctype as _create_pwa_doctype
    _create_pwa_doctype()

    frappe.db.commit()
    print("EthioBiz Theme installed successfully!")

def before_uninstall():
    """Run before app uninstallation"""
    
    # Clean up translations (optional)
    # frappe.db.delete("Translation", {"source_text": ["in", ["Frappe Light", "Timeless Night"]]})
    
    print("🗑️ EthioBiz Theme uninstalled.")
