# -*- coding: utf-8 -*-
"""
EthioBiz Auto-Company Session Setter
Bismillah Ar-Rahman Ar-Rahim

Automatically sets the user's default company from their User profile
when they log in on a new device/browser, preventing the
"Company is mandatory" error.

Fallback chain:
  1. User.company field (DocType: User)
  2. Employee.company (linked active Employee)
  3. First Company in system
  4. No company (log warning + show user notification)

© 2026 EthioBiz | Powered by Biz Technology Solutions
"""

import frappe


def on_session_creation(login_manager):
    """
    LAYER 1 (PRIMARY): Called by Frappe immediately after a new session
    is created (user login). Reads the company from DocType User > company
    field and sets it as the session default.
    
    Hook: on_session_creation in hooks.py
    """
    try:
        user = frappe.session.user
        
        # Skip for Guest and Administrator
        if user in ("Guest", "Administrator"):
            return
        
        # Check if user already has a company default set
        current_default = frappe.defaults.get_user_default("Company")
        if current_default:
            # Already has a company set (e.g., returning on same device)
            return
        
        # Resolve company using the fallback chain
        user_company, source = _resolve_user_company(user)
        
        if user_company:
            # Set the resolved company as the user's session default
            frappe.defaults.set_user_default("Company", user_company)
            frappe.logger("ethiobiz").info(
                f"Auto-set company '{user_company}' for user '{user}' "
                f"(source: {source}) on new session"
            )
        else:
            # NO company could be resolved - log warning
            frappe.logger("ethiobiz").warning(
                f"Could not resolve any company for user '{user}' on login. "
                f"User.company field is empty, no active Employee found, "
                f"and no Company exists in the system."
            )
        
    except Exception as e:
        # NEVER break the login flow - log and continue silently
        frappe.logger("ethiobiz").error(
            f"Auto-company error for {frappe.session.user}: {e}"
        )


def ensure_company_default():
    """
    LAYER 2 (FALLBACK): Called during boot_session to verify the user
    has a company default. Acts as a safety net for cases where
    on_session_creation didn't fire or the default was lost.
    
    Returns dict with company info and status.
    """
    try:
        user = frappe.session.user
        
        if user in ("Guest", "Administrator"):
            return None
        
        # Check if user already has a company default
        current_default = frappe.defaults.get_user_default("Company")
        if current_default:
            return {"company": current_default, "source": "existing_default"}
        
        # No default set — resolve using the fallback chain
        user_company, source = _resolve_user_company(user)
        
        if user_company:
            frappe.defaults.set_user_default("Company", user_company)
            frappe.logger("ethiobiz").info(
                f"Boot fallback: set company '{user_company}' for '{user}' "
                f"(source: {source})"
            )
            return {"company": user_company, "source": source}
        
        # No company could be resolved
        return {"company": None, "source": "none", "needs_setup": True}
        
    except Exception:
        return None


def _resolve_user_company(user):
    """
    Internal helper: Resolves a company for the given user using
    a 3-step fallback chain.
    
    Returns:
        tuple: (company_name, source_description) or (None, None)
    """
    # STEP 1: Read company from User doctype (DocType: User > company field)
    try:
        user_company = frappe.db.get_value("User", user, "company")
        if user_company and frappe.db.exists("Company", user_company):
            return (user_company, "User.company")
    except Exception:
        pass
    
    # STEP 2: Fallback — check linked active Employee record
    try:
        employee_company = frappe.db.get_value(
            "Employee",
            {"user_id": user, "status": "Active"},
            "company"
        )
        if employee_company and frappe.db.exists("Company", employee_company):
            return (employee_company, "Employee.company")
    except Exception:
        pass
    
    # STEP 3: Final fallback — use the first Company in the system
    try:
        first_company = frappe.db.sql(
            "SELECT name FROM `tabCompany` ORDER BY creation LIMIT 1",
            as_dict=True
        )
        if first_company:
            return (first_company[0].name, "first_company_fallback")
    except Exception:
        pass
    
    # All fallbacks exhausted
    return (None, None)
