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
    try:
        user = frappe.session.user
        if user in ("Guest", "Administrator"):
            return

        current_default = frappe.defaults.get_user_default("company")
        old_default = frappe.defaults.get_user_default("Company")

        if current_default:
            if old_default:
                frappe.defaults.clear_user_default("Company")
            return

        if old_default:
            frappe.defaults.set_user_default("company", old_default)
            frappe.defaults.clear_user_default("Company")
            return

        user_company, source = _resolve_user_company(user)

        if user_company:
            frappe.defaults.set_user_default("company", user_company)
            frappe.db.set_value("User", user, "company", user_company)
            frappe.logger("ethiobiz").info(
                f"Auto-set company '{user_company}' for user '{user}' "
                f"(source: {source}) on new session"
            )
        else:
            frappe.logger("ethiobiz").warning(
                f"Could not resolve any company for user '{user}' on login."
            )

    except Exception as e:
        frappe.logger("ethiobiz").error(
            f"Auto-company error for {frappe.session.user}: {e}"
        )


def ensure_company_default():
    try:
        user = frappe.session.user
        if user in ("Guest", "Administrator"):
            return None

        current_default = frappe.defaults.get_user_default("company")
        old_default = frappe.defaults.get_user_default("Company")

        if current_default:
            if old_default:
                frappe.defaults.clear_user_default("Company")
            return {"company": current_default, "source": "existing_default"}

        if old_default:
            frappe.defaults.set_user_default("company", old_default)
            frappe.defaults.clear_user_default("Company")
            return {"company": old_default, "source": "migrated_from_uppercase"}

        user_company, source = _resolve_user_company(user)

        if user_company:
            frappe.defaults.set_user_default("company", user_company)
            frappe.db.set_value("User", user, "company", user_company)
            frappe.logger("ethiobiz").info(
                f"Boot fallback: set company '{user_company}' for '{user}' "
                f"(source: {source})"
            )
            return {"company": user_company, "source": source}

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
