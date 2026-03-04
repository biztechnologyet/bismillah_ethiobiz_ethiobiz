# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Installation Hooks
"""

import frappe

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
    
    frappe.db.commit()
    print("✅ EthioBiz Theme installed successfully!")

def before_uninstall():
    """Run before app uninstallation"""
    
    # Clean up translations (optional)
    # frappe.db.delete("Translation", {"source_text": ["in", ["Frappe Light", "Timeless Night"]]})
    
    print("🗑️ EthioBiz Theme uninstalled.")
