# -*- coding: utf-8 -*-
"""
Bismillah Ar-Rahman Ar-Rahim
EthioBiz Runtime Self-Healing & Permanence Patches
Ensures Helpdesk, LMS, Healthcare, Multi-Company, and Telephony fallbacks persist across reboots, rebuilds, and migrations.
"""

import os
import frappe

# frappe.db is a per-request LocalProxy. The patch must therefore be (re)applied
# on every request, but the wrapper carries a marker so it is never nested.
_SCOPE_MARKER = "__ethio_company_scoped_employee_lookup__"


def ensure_employee_lookup_patch():
    """Apply the employee lookup scope to the current request's db object."""
    try:
        patch_hrms_employee_lookup_company_scope()
    except Exception:
        pass


def patch_hrms_employee_lookup_company_scope():
    """Scope HRMS `user_id -> Employee` lookups to the active company.

    ERPNext/HRMS often resolves the current Employee with only
    ``{"user_id": frappe.session.user}``. Under EthioBiz's one-User/many-Employee
    model that is ambiguous. This wrapper adds the user's active company only
    when the user actually has more than one Employee, so single-company sites
    keep the original behaviour untouched.
    """
    original_db_get_value = getattr(frappe.db, "get_value", None)
    if not original_db_get_value or getattr(original_db_get_value, _SCOPE_MARKER, False):
        return

    def active_company_for(user):
        try:
            company = frappe.defaults.get_user_default("company", user)
        except Exception:
            company = None
        if not company:
            try:
                # Second argument is the DefaultValue parent (the user), not the
                # site-wide __default row.
                company = frappe.db.get_default("company", user)
            except Exception:
                company = None
        return company

    def has_multiple_employees(user):
        flag_key = "ethiobiz_multi_employee_%s" % user.replace("@", "_").replace(".", "_")
        if flag_key not in frappe.flags:
            try:
                frappe.flags[flag_key] = (frappe.db.count("Employee", {"user_id": user}) or 0) > 1
            except Exception:
                frappe.flags[flag_key] = False
        return bool(frappe.flags[flag_key])

    def scoped_filters(filters, user):
        if not isinstance(filters, dict) or filters.get("company"):
            return None
        if filters.get("user_id") != user:
            return None
        if not has_multiple_employees(user):
            return None
        company = active_company_for(user)
        if not company:
            return None
        scoped = dict(filters)
        scoped["company"] = company
        return scoped

    def patched_db_get_value(doctype, *args, **kwargs):
        user = getattr(getattr(frappe, "session", None), "user", None)
        if doctype == "Employee" and user and user not in ("Guest", "Administrator") and args:
            new_filters = scoped_filters(args[0], user)
            if new_filters is not None:
                args = (new_filters,) + args[1:]
        if doctype == "Employee" and user and user not in ("Guest", "Administrator") and "filters" in kwargs:
            new_filters = scoped_filters(kwargs["filters"], user)
            if new_filters is not None:
                kwargs["filters"] = new_filters
        return original_db_get_value(doctype, *args, **kwargs)

    setattr(patched_db_get_value, _SCOPE_MARKER, True)
    frappe.db.get_value = patched_db_get_value

    original_get_value = getattr(frappe, "get_value", None)
    if original_get_value and not getattr(original_get_value, _SCOPE_MARKER, False):
        def patched_get_value(doctype, *args, **kwargs):
            return patched_db_get_value(doctype, *args, **kwargs)
        setattr(patched_get_value, _SCOPE_MARKER, True)
        frappe.get_value = patched_get_value

    original_get_all = getattr(frappe, "get_all", None)
    if original_get_all and not getattr(original_get_all, _SCOPE_MARKER, False):
        def patched_get_all(doctype, *args, **kwargs):
            user = getattr(getattr(frappe, "session", None), "user", None)
            if doctype == "Employee" and user and user not in ("Guest", "Administrator"):
                if args and isinstance(args[0], dict):
                    new_filters = scoped_filters(args[0], user)
                    if new_filters is not None:
                        args = (new_filters,) + args[1:]
                elif "filters" in kwargs:
                    new_filters = scoped_filters(kwargs["filters"], user)
                    if new_filters is not None:
                        kwargs["filters"] = new_filters
            return original_get_all(doctype, *args, **kwargs)
        setattr(patched_get_all, _SCOPE_MARKER, True)
        frappe.get_all = patched_get_all

    frappe.flags.ethiobiz_employee_lookup_patched = True


def apply_runtime_patches():
    """Apply self-healing patches to monkey-patch and secure runtime endpoints."""
    # 0. Multi-company HRMS employee resolution must follow the active company.
    ensure_employee_lookup_patch()

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