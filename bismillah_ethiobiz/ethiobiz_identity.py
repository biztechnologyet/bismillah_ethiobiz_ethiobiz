# -*- coding: utf-8 -*-
"""Shared customer + company identity for all EthioBiz vertical bookings.

BISMALLAH — every mutating portal endpoint (BizFix, BizHealth, BizRide, BizHome,
Shop, Jobs, BizService) must stamp a real Customer linked to the logged-in User
and write the listing's owning Company. Silent string fallbacks are forbidden.
"""

from __future__ import unicode_literals

import frappe
from frappe import _


def require_login(message=None):
    """Reject Guest. Returns the session user."""
    user = (frappe.session.user or "").strip() or "Guest"
    if user == "Guest":
        frappe.throw(
            message or _("Please log in to continue."),
            frappe.PermissionError,
        )
    return user


def require_authed_customer(message=None):
    """Login required + resolved Customer name. Throws on Guest."""
    user = require_login(message)
    return get_or_create_customer_for_user(user)


def get_or_create_customer_for_user(user=None):
    """Return (and create if needed) the Customer linked to a Frappe User."""
    user = user or require_login()
    if user == "Guest":
        frappe.throw(_("A logged-in user is required to create a Customer."), frappe.PermissionError)

    email = frappe.db.get_value("User", user, "email") or user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    phone = (
        frappe.db.get_value("User", user, "mobile_no")
        or frappe.db.get_value("User", user, "phone")
        or ""
    )

    existing = None
    if frappe.db.exists("DocType", "Customer"):
        if email:
            existing = frappe.db.get_value("Customer", {"email_id": email}, "name")
        if not existing:
            existing = frappe.db.get_value("Customer", {"customer_name": full_name}, "name")
        if not existing and frappe.db.exists("Customer", user):
            existing = user
    if existing:
        return existing

    group = frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual"
    territory = frappe.db.get_single_value("Selling Settings", "territory") or "Ethiopia"
    doc = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": full_name,
            "customer_type": "Individual",
            "customer_group": group,
            "territory": territory,
            "email_id": email,
            "mobile_no": phone,
        }
    )
    doc.flags.ignore_permissions = True
    try:
        doc.insert(ignore_permissions=True)
    except Exception:
        existing = frappe.db.get_value("Customer", {"email_id": email}, "name")
        if existing:
            return existing
        existing = frappe.db.get_value("Customer", {"customer_name": full_name}, "name")
        if existing:
            return existing
        raise
    return doc.name


def resolve_booking_company(owning_company, label="listing"):
    """Return a real Company name. Throws if missing or not in Desk."""
    company = (owning_company or "").strip() if owning_company else ""
    if not company:
        frappe.throw(
            _("This {0} has no owning Company. Assign a Company in Desk before taking bookings.").format(
                label
            )
        )
    if not frappe.db.exists("Company", company):
        frappe.throw(
            _("Owning Company '{0}' on this {1} is not a valid Company.").format(company, label)
        )
    return company


def session_contact_defaults():
    """Get contact defaults from current user session."""
    user = frappe.session.user or ""
    if user == "Guest":
        return {}
    
    return {
        "full_name": frappe.db.get_value("User", user, "full_name") or "",
        "email": frappe.db.get_value("User", user, "email") or "",
        "phone": frappe.db.get_value("User", user, "mobile_no") or frappe.db.get_value("User", user, "phone") or ""
    }

def resolve_booking_company(owning_company, label="listing"):
    """Return a real Company name. Throws if missing or not in Desk."""
    company = (owning_company or "").strip() if owning_company else ""
    if not company:
        frappe.throw(
            _("This {0} has no owning Company. Assign a Company in Desk before taking bookings.").format(
                label
            )
        )
    if not frappe.db.exists("Company", company):
        frappe.throw(
            _("Owning Company '{0}' on this {1} is not a valid Company.").format(company, label)
        )
    return company
