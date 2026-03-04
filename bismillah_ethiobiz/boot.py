# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Boot Session
Inject theme configuration into frappe.boot
"""

import frappe

def boot_session(bootinfo):
    """Inject EthioBiz theme configuration into boot"""
    
    # Use dictionary access to be safe, as bootinfo might not be an attr_dict
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
    
    # Override default app name
    bootinfo["app_name"] = "EthioBiz"
