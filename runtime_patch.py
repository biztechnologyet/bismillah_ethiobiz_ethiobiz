# -*- coding: utf-8 -*-
"""
Bismillah Ar-Rahman Ar-Rahim
EthioBiz Runtime Self-Healing & Permanence Patches
Ensures Helpdesk, LMS, Healthcare, Multi-Company, and Telephony fallbacks persist across reboots, rebuilds, and migrations.
"""

import os
import frappe

def apply_runtime_patches():
    """Apply self-healing patches to monkey-patch and secure runtime endpoints."""
    # 1. Telephony fallback
    try:
        import telephony.api
    except Exception:
        import sys, types
        telephony_mod = types.ModuleType("telephony")
        telephony_api_mod = types.ModuleType("telephony.api")
        
        @frappe.whitelist(allow_guest=True)
        def is_call_integration_enabled():
            return False
            
        telephony_api_mod.is_call_integration_enabled = is_call_integration_enabled
        telephony_mod.api = telephony_api_mod
        sys.modules["telephony"] = telephony_mod
        sys.modules["telephony.api"] = telephony_api_mod

    # 2. Patch Helpdesk auth.get_user for guest & logged-in user safety
    try:
        import helpdesk.api.auth as _hd_auth
        _orig_get_user = getattr(_hd_auth, "get_user", None)
        
        @frappe.whitelist(allow_guest=True)
        def _patched_get_user():
            current_user = getattr(getattr(frappe, "session", None), "user", "Guest")
            if not current_user or current_user == "Guest":
                return {
                    "has_desk_access": False,
                    "is_admin": False,
                    "is_agent": False,
                    "user_id": "Guest",
                    "is_manager": False,
                    "user_image": None,
                    "user_first_name": "Guest",
                    "user_name": "Guest",
                    "username": "guest",
                    "time_zone": "Africa/Addis_Ababa",
                    "language": "en",
                    "user_teams": [],
                }
            if _orig_get_user:
                return _orig_get_user()
            return {"has_desk_access": False, "user_id": current_user}
            
        _hd_auth.get_user = _patched_get_user
    except Exception:
        pass

    # 3. Patch Helpdesk get_boot for safe CSRF token & multi-company
    try:
        import helpdesk.www.helpdesk as _hd_www
        
        def _patched_hd_boot():
            csrf = None
            try:
                csrf = frappe.sessions.get_csrf_token()
            except Exception:
                csrf = getattr(getattr(frappe.local, "session", None), "data", {}).get("csrf_token") if hasattr(frappe.local, "session") else None
            return frappe._dict({
                "default_route": "/helpdesk",
                "site_name": getattr(frappe.local, "site", "ethiobiz.et"),
                "read_only_mode": getattr(frappe.flags, "read_only", False),
                "csrf_token": csrf or "",
                "setup_complete": 1,
                "is_fc_site": False,
                "session_user": getattr(getattr(frappe, "session", None), "user", "Guest"),
                "date_format": "yyyy-mm-dd",
                "time_format": "HH:mm:ss",
            })
            
        _hd_www.get_boot = _patched_hd_boot
    except Exception:
        pass

    # 4. Patch LMS get_boot for safe CSRF token
    try:
        import lms.www.lms as _lms_www
        
        def _patched_lms_boot():
            csrf = None
            try:
                csrf = frappe.sessions.get_csrf_token()
            except Exception:
                csrf = getattr(getattr(frappe.local, "session", None), "data", {}).get("csrf_token") if hasattr(frappe.local, "session") else None
            return frappe._dict({
                "frappe_version": frappe.__version__,
                "read_only_mode": getattr(frappe.flags, "read_only", False),
                "csrf_token": csrf or "",
                "site_name": getattr(frappe.local, "site", "ethiobiz.et"),
            })
            
        _lms_www.get_boot = _patched_lms_boot
    except Exception:
        pass

    # 5. Multi-Company Custom Fields Guarantee
    try:
        if frappe.db and hasattr(frappe.db, "exists") and frappe.db.exists("DocType", "HD Ticket"):
            if not frappe.db.exists("Custom Field", "HD Ticket-company"):
                from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
                create_custom_fields({
                    "HD Ticket": [{"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "insert_after": "subject", "in_list_view": 1, "in_standard_filter": 1, "in_global_search": 1}],
                    "HD Team": [{"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "insert_after": "team_name", "in_list_view": 1, "in_standard_filter": 1}],
                    "HD Service Level Agreement": [{"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "insert_after": "service_level", "in_list_view": 1, "in_standard_filter": 1}]
                }, update=True)
                frappe.db.commit()
    except Exception:
        pass

# Run patches on module import
apply_runtime_patches()