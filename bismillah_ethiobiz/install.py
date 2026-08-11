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
    
    # Create HADEEDA Settings doctype if not exists (custom=1, not auto-created by migrate)
    if not frappe.db.exists("DocType", "HADEEDA Settings"):
        json_path = os.path.join(os.path.dirname(__file__), "doctype", "hadeeda_settings", "hadeeda_settings.json")
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

    # Create DOBiz PWA Settings doctype if not exists (custom=1, not auto-created by migrate)
    if not frappe.db.exists("DocType", "DOBiz PWA Settings"):
        json_path = os.path.join(os.path.dirname(__file__), "doctype", "dobiz_pwa_settings", "dobiz_pwa_settings.json")
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
            # Seed the single record with defaults
            frappe.get_doc({
                "doctype": "DOBiz PWA Settings",
                "name": "DOBiz PWA Settings",
                "enabled": 1,
                "app_name": "DOBiz Smart ERP - EthioBiz",
                "short_name": "DOBiz",
                "description": "Rooted in Ethiopia. Built for Humanity.",
                "theme_color": "#1FB6AE",
                "background_color": "#0E1A1A",
                "start_url": "/app/dobiz",
                "display": "standalone",
                "offline_title": "You are offline",
                "offline_message": "Reconnect to continue using DOBiz",
                "install_prompt_enabled": 1,
                "cache_version": "1",
            }).insert(ignore_permissions=True)
            frappe.db.commit()

    frappe.db.commit()
    print("EthioBiz Theme installed successfully!")

def before_uninstall():
    """Run before app uninstallation"""
    
    # Clean up translations (optional)
    # frappe.db.delete("Translation", {"source_text": ["in", ["Frappe Light", "Timeless Night"]]})
    
    print("🗑️ EthioBiz Theme uninstalled.")
