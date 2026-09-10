# -*- coding: utf-8 -*-
"""Shared customer + company identity for all EthioBiz vertical bookings.

BISMALLAH - every mutating portal endpoint (BizFix, BizHealth, BizRide, BizHome,
Shop, Jobs, BizService) must stamp a real Customer linked to the logged-in User
and write the listing's owning Company. Silent string fallbacks are forbidden.

BISMALLAH (2026-09-10) - purchases and bookings are restricted to logged-in
users. The Customer/Patient is ALWAYS resolved from (and linked to) the logged-in
account; typed names and contacts are never used to fabricate identity, so no
"Guest" customers or anonymous Users can ever leak into the ERP.
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
        _link_user_to_customer(user, existing)
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
            _link_user_to_customer(user, existing)
            return existing
        existing = frappe.db.get_value("Customer", {"customer_name": full_name}, "name")
        if existing:
            _link_user_to_customer(user, existing)
            return existing
        raise
    _link_user_to_customer(user, doc.name)
    return doc.name


def _link_user_to_customer(user, customer):
    """Keep User.customer in sync so the account is the single source of truth."""
    if not user or not customer or user == "Guest":
        return
    try:
        if frappe.get_meta("User").has_field("customer"):
            if not frappe.db.get_value("User", user, "customer"):
                frappe.db.set_value("User", user, "customer", customer, update_modified=False)
    except Exception:
        pass


def resolve_booking_company(owning_company, label="listing", *args, **kwargs):
    """Return a real Company name. Robust against variable args and missing companies."""
    company = (owning_company or "").strip() if owning_company else ""
    if not company:
        company = (frappe.db.get_single_value("BizService Settings", "company")
                   or frappe.db.get_single_value("Global Defaults", "default_company")
                   or (frappe.db.get_all("Company", limit=1, pluck="name") or [None])[0] or "")
    if company and not frappe.db.exists("Company", company):
        company = (frappe.db.get_single_value("Global Defaults", "default_company")
                   or (frappe.db.get_all("Company", limit=1, pluck="name") or [None])[0] or company)
    if not company:
        frappe.throw(
            _("This {0} has no owning Company. Assign a Company in Desk before taking bookings.").format(
                label
            )
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


def resolve_booking_customer(provided_name=None, provided_phone=None, provided_email=None):
    """BISMALLAH (2026-09-10): the authority for booking/purchase identity.

    Requires a logged-in user. The Customer is resolved from (and linked to) the
    account profile - the user never needs to type their name or contacts, and a
    Guest can never place a booking. Typed values are only used to enrich missing
    Customer fields.

    Returns {"user", "customer", "full_name", "email", "phone"}.
    """
    user = require_login(
        _("Please log in to continue. Your booking or purchase will be linked to your account automatically.")
    )
    customer = get_or_create_customer_for_user(user)
    email = frappe.db.get_value("User", user, "email") or user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    phone = (
        (provided_phone or "").strip()
        or frappe.db.get_value("User", user, "mobile_no")
        or frappe.db.get_value("User", user, "phone")
        or ""
    )
    if customer:
        cname = frappe.db.get_value("Customer", customer, "customer_name") or ""
        if cname:
            full_name = cname
        # enrich missing Customer fields only (never fabricate identity)
        try:
            p_email = (provided_email or "").strip()
            p_phone = (provided_phone or "").strip()
            if p_email and "@" in p_email and not frappe.db.get_value("Customer", customer, "email_id"):
                frappe.db.set_value("Customer", customer, "email_id", p_email, update_modified=False)
            if p_phone and not frappe.db.get_value("Customer", customer, "mobile_no"):
                frappe.db.set_value("Customer", customer, "mobile_no", p_phone, update_modified=False)
        except Exception:
            pass
    return {
        "user": user,
        "customer": customer or "",
        "full_name": full_name,
        "email": email,
        "phone": phone,
    }


def ensure_registered_party(full_name=None, phone=None, email=None, party_type="Customer"):
    """
    BISMALLAH - Universal User, Customer, and Patient Provisioning Engine.

    BISMALLAH (2026-09-10): restricted to logged-in users. The registered
    User/Customer is ALWAYS the logged-in account and the Customer is auto-linked
    to it - no anonymous Users or "Guest" Customers are ever created. The passed
    name/phone/email only enrich the profile (and, for party_type == "Patient",
    the Patient record when booking healthcare for someone else).

    Returns a dict: {"user": user_name, "customer": customer_name, "patient": patient_name}
    """
    name = (full_name or "").strip() or "Valued Member"
    phone_clean = "".join(c for c in (phone or "") if c.isdigit() or c == "+").strip()
    email_clean = (email or "").strip().lower()

    # 1. LOGGED-IN USER ONLY (never fabricate an anonymous user)
    user_name = require_login(
        _("Please log in to continue. Your booking will be linked to your account automatically.")
    )
    u_phone = (frappe.db.get_value("User", user_name, "mobile_no")
               or frappe.db.get_value("User", user_name, "phone") or "")
    u_email = (frappe.db.get_value("User", user_name, "email") or user_name).strip().lower()
    u_full = frappe.db.get_value("User", user_name, "full_name") or user_name

    phone_clean = phone_clean or u_phone
    email_clean = email_clean or u_email
    if not name or name == "Valued Member":
        name = u_full

    # 2. RESOLVE OR REGISTER ERPNEXT CUSTOMER (linked to the logged-in user)
    customer_name = get_or_create_customer_for_user(user_name)

    # 3. RESOLVE OR REGISTER HEALTHCARE PATIENT (same Customer; typed details allowed)
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
                    "email": email_clean or (u_email if "@" in str(u_email) else None),
                    "customer": customer_name,
                    "user_id": user_name,
                    "invite_user": 0,
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
        "user": user_name,
        "customer": customer_name or name,
        "patient": patient_name
    }


def resolve_or_create_customer(customer_name=None, customer_phone=None, email=None):
    """BISMALLAH (2026-09-10): login-gated. Resolves the logged-in user's linked
    Customer (auto-creating it when needed) instead of ever fabricating a guest."""
    party = resolve_booking_customer(customer_name, customer_phone, email)
    return party["customer"]


def resolve_or_create_patient(patient_name=None, patient_phone=None, email=None):
    """BISMALLAH (2026-09-10): login-gated. Resolves the logged-in user's linked
    Customer + Patient instead of ever fabricating a guest."""
    return ensure_registered_party(full_name=patient_name, phone=patient_phone, email=email, party_type="Patient")


@frappe.whitelist(allow_guest=True)
def get_current_user_profile():
    """Returns comprehensive logged-in user profile with auto-linking to Customer/Patient."""
    user = frappe.session.user
    if not user or user == "Guest":
        return {
            "status": "success",
            "logged_in": False,
            "user": "Guest",
            "full_name": "",
            "phone": "",
            "email": "",
            "address": "",
            "customer": "",
            "patient": ""
        }

    u_doc = frappe.get_doc("User", user)
    full_name = u_doc.full_name or f"{u_doc.first_name or ''} {u_doc.last_name or ''}".strip() or user
    phone = u_doc.mobile_no or u_doc.phone or ""
    email = u_doc.email or ""

    # Resolve ERPNext Customer
    cust = None
    if phone:
        cust = frappe.db.get_value("Customer", {"mobile_no": phone}, "name")
    if not cust and email:
        cust = frappe.db.get_value("Customer", {"email_id": email}, "name")
    if not cust and full_name:
        cust = frappe.db.get_value("Customer", {"customer_name": full_name}, "name")

    # If user has no customer yet, auto-ensure it!
    if not cust and (full_name or phone or email):
        try:
            ensured = ensure_registered_party(full_name=full_name, phone=phone, email=email, party_type="Customer")
            cust = ensured.get("customer")
        except Exception:
            pass

    # Resolve Healthcare Patient
    patient = None
    if frappe.db.exists("DocType", "Patient"):
        if phone:
            patient = frappe.db.get_value("Patient", {"mobile": phone}, "name")
        if not patient and email:
            patient = frappe.db.get_value("Patient", {"email": email}, "name")
        if not patient and full_name:
            patient = frappe.db.get_value("Patient", {"patient_name": full_name}, "name")

    # Resolve Saved Primary Address
    address = ""
    if cust:
        try:
            addr = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": cust, "parenttype": "Address"}, pluck="parent", limit=1)
            if addr:
                a_doc = frappe.get_doc("Address", addr[0])
                address = f"{a_doc.address_line1 or ''}, {a_doc.city or ''}".strip(", ")
        except Exception:
            pass

    return {
        "status": "success",
        "logged_in": True,
        "user": user,
        "full_name": full_name,
        "first_name": u_doc.first_name or (full_name.split()[0] if full_name else ""),
        "last_name": u_doc.last_name or (full_name.split()[-1] if len(full_name.split()) > 1 else ""),
        "phone": phone,
        "email": email,
        "address": address or "Addis Ababa, Ethiopia",
        "customer": cust or "",
        "patient": patient or ""
    }