# -*- coding: utf-8 -*-
"""
EthioBiz Theme - Utility Functions
"""

import frappe

def get_theme_config():
    """Return theme configuration for Jinja templates"""
    return {
        "app_name": "EthioBiz",
        "app_tagline": "Uniting Humanity Through Shared Progress",
        "app_logo": "/assets/bismillah_ethiobiz/images/ethiobiz_logo.png",
        "primary_color": "#1FB6AE",
        "obsidian": "#0E1A1A",
        "ivory": "#F8F6F2",
        "gold": "#C9A24D",
        "pillars": [
            {"id": "tibeb", "name": "Tibeb", "color": "#C9A24D", "tagline": "One Source. Many Rivers."},
            {"id": "dagu", "name": "Dagu", "color": "#2E3A8C", "tagline": "Learning That Illuminates Life."},
            {"id": "magala", "name": "Magala", "color": "#2F6B4F", "tagline": "From Seed to Success."},
            {"id": "walta", "name": "Walta", "color": "#0F3557", "tagline": "Securing the Self."},
            {"id": "afocha", "name": "Afocha", "color": "#B83A3A", "tagline": "One Human Family."}
        ]
    }
