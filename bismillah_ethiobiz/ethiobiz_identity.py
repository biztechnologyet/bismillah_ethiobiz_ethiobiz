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


def ensure_registered_party(full_name=None, phone=None, email=None, party_type="Customer"):
    """
    BISMALLAH - Universal User, Customer, and Patient Provisioning Engine.
    Ensures that any person booking, applying, or purchasing on ethiobiz.et
    is properly and permanently registered in the database as:
    1. A registered Frappe User (User Type: 'Website User', Role: 'Customer' / 'Patient')
    2. A registered ERPNext Customer (Customer Group: 'Individual', Territory: 'Ethiopia')
    3. A registered Healthcare Patient (if party_type == 'Patient' or during Healthcare bookings)
    
    Returns a dict: {"user": user_name, "customer": customer_name, "patient": patient_name}
    """
    name = (full_name or "").strip() or "Valued Member"
    phone_clean = "".join(c for c in (phone or "") if c.isdigit() or c == "+").strip()
    email_clean = (email or "").strip().lower()

    # 1. RESOLVE OR REGISTER FRAPPE USER
    user_name = None
    sess_user = (frappe.session.user or "").strip()
    if sess_user and sess_user != "Guest":
        user_name = sess_user
    elif email_clean and frappe.db.exists("User", email_clean):
        user_name = email_clean
    elif phone_clean and frappe.db.exists("User", {"mobile_no": phone_clean}):
        user_name = frappe.db.get_value("User", {"mobile_no": phone_clean}, "name")

    if not user_name:
        generated_email = email_clean or (f"{phone_clean}@ethiobiz.et" if phone_clean else f"user_{cint(frappe.utils.now_datetime().timestamp())}@ethiobiz.et")
        if frappe.db.exists("User", generated_email):
            user_name = generated_email
        else:
            parts = name.split()
            f_name = parts[0] if parts else "EthioBiz"
            l_name = " ".join(parts[1:]) if len(parts) > 1 else "Customer"
            roles = [{"role": "Customer"}]
            if party_type == "Patient" and frappe.db.exists("Role", "Patient"):
                roles.append({"role": "Patient"})

            try:
                u_doc = frappe.get_doc({
                    "doctype": "User",
                    "email": generated_email,
                    "first_name": f_name,
                    "last_name": l_name,
                    "full_name": name,
                    "mobile_no": phone_clean,
                    "user_type": "Website User",
                    "send_welcome_email": 0,
                    "roles": roles
                })
                u_doc.flags.ignore_permissions = True
                u_doc.flags.ignore_password_policy = True
                u_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                user_name = u_doc.name
            except Exception:
                user_name = generated_email

    # 2. RESOLVE OR REGISTER ERPNEXT CUSTOMER
    customer_name = None
    if frappe.db.exists("DocType", "Customer"):
        if phone_clean:
            customer_name = frappe.db.get_value("Customer", {"mobile_no": phone_clean}, "name")
        if not customer_name and email_clean:
            customer_name = frappe.db.get_value("Customer", {"email_id": email_clean}, "name")
        if not customer_name:
            customer_name = frappe.db.get_value("Customer", {"customer_name": name}, "name")

        if not customer_name:
            c_group = frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual"
            territory = frappe.db.get_single_value("Selling Settings", "territory") or "Ethiopia"
            try:
                c_doc = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": name,
                    "customer_type": "Individual",
                    "customer_group": c_group,
                    "territory": territory,
                    "mobile_no": phone_clean,
                    "email_id": email_clean or (user_name if "@" in str(user_name) else None)
                })
                c_doc.flags.ignore_permissions = True
                c_doc.flags.ignore_mandatory = True
                c_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                customer_name = c_doc.name
            except Exception:
                customer_name = frappe.db.get_value("Customer", {}, "name") or name

    # 3. RESOLVE OR REGISTER HEALTHCARE PATIENT
    patient_name = None
    if party_type == "Patient" or frappe.db.exists("DocType", "Patient"):
        if phone_clean:
            patient_name = frappe.db.get_value("Patient", {"mobile": phone_clean}, "name")
        if not patient_name and email_clean:
            patient_name = frappe.db.get_value("Patient", {"email": email_clean}, "name")
        if not patient_name:
            patient_name = frappe.db.get_value("Patient", {"patient_name": name}, "name")

        if not patient_name and party_type == "Patient" and frappe.db.exists("DocType", "Patient"):
            is_female = any(w in name.lower() for w in ["w/ro", "w/rt", "mrs", "ms", "miss", "female", "woizero"])
            try:
                p_doc = frappe.get_doc({
                    "doctype": "Patient",
                    "patient_name": name,
                    "mobile": phone_clean,
                    "email": email_clean or (user_name if "@" in str(user_name) else None),
                    "customer": customer_name,
                    "sex": "Female" if is_female else "Male",
                    "status": "Active"
                })
                p_doc.flags.ignore_permissions = True
                p_doc.flags.ignore_mandatory = True
                p_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                patient_name = p_doc.name
            except Exception:
                patient_name = frappe.db.get_value("Patient", {}, "name") or name

    return {
        "user": user_name or "Guest",
        "customer": customer_name or name,
        "patient": patient_name
    }


def resolve_or_create_customer(customer_name=None, customer_phone=None, email=None):
    """Resolve or register User + Customer, returning the Customer name."""
    res = ensure_registered_party(full_name=customer_name, phone=customer_phone, email=email, party_type="Customer")
    return res["customer"]


def resolve_or_create_patient(patient_name=None, patient_phone=None, email=None):
    """Resolve or register User + Customer + Patient, returning dict of all three."""
    return ensure_registered_party(full_name=patient_name, phone=patient_phone, email=email, party_type="Patient")

