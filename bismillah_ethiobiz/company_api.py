# -*- coding: utf-8 -*-
"""Whitelisted multi-company APIs (TASK-2026-00972)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

from bismillah_ethiobiz.company_access import (
    _is_admin,
    ensure_membership,
    get_active_memberships,
    get_company_context,
    get_enabled_industry_modules,
    log_company_audit,
    switch_company as _switch_company,
)


def _require_login():
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Please log in to continue."), frappe.PermissionError)
    return user


def _normalise_company_name(value):
    return " ".join(str(value or "").strip().split())


def _next_abbr(company_name):
    base = "".join(w[0] for w in company_name.split() if w).upper()[:5] or "DOB"
    abbr = base
    counter = 0
    while frappe.db.exists("Company", {"abbr": abbr}):
        counter += 1
        suffix = str(counter)
        abbr = base[: max(1, 5 - len(suffix))] + suffix
    return abbr


@frappe.whitelist()
def get_my_companies():
    """Return the master identity's active companies and current context."""
    user = _require_login()
    return get_company_context(user)


@frappe.whitelist()
def get_company_memberships(user=None):
    """Admin view of memberships for a user (System Manager only)."""
    if not _is_admin():
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    target = user or frappe.session.user
    return get_active_memberships(target)


@frappe.whitelist(methods=["POST"])
def switch_company(company=None):
    """Switch the active company after re-validating active membership."""
    user = _require_login()
    company = _normalise_company_name(company)
    if not company:
        frappe.throw(_("Company is required."), frappe.ValidationError)
    result = _switch_company(user, company)
    result["context"] = get_company_context(user)
    return result


@frappe.whitelist(methods=["POST"])
def add_company(company_name=None, industry=None, role_profile=None, notes=None,
                make_default=0):
    """Create a new tenant company under the logged-in master identity.

    This is the post-signup "Add another company" path.  It never creates a new
    User or password; the same master login gains an Active membership.  The
    operation is idempotent: retrying with the same name returns the existing
    membership instead of creating duplicates.
    """
    user = _require_login()
    company_name = _normalise_company_name(company_name)
    industry = str(industry or "").strip()
    if not company_name:
        frappe.throw(_("Company name is required."), frappe.ValidationError)
    if len(company_name) < 2:
        frappe.throw(_("Company name is too short."), frappe.ValidationError)
    if not industry:
        frappe.throw(_("Industry is required."), frappe.ValidationError)

    # The switcher submits the canonical provisioning label, while older callers
    # may still submit the Theme display label.  Accept both and store the
    # canonical label on the Company row.
    modules = get_enabled_industry_modules()
    canonical_by_label = {}
    for module in modules:
        display_label = str(module.get("label") or "").strip()
        canonical_label = str(module.get("canonical_label") or display_label).strip()
        if display_label:
            canonical_by_label[display_label] = canonical_label
        if canonical_label:
            canonical_by_label[canonical_label] = canonical_label
    canonical_industry = canonical_by_label.get(industry)
    if not canonical_industry:
        log_company_audit(user, company_name, "Add Company", "Failed",
                          "Industry not enabled: {0}".format(industry))
        frappe.throw(
            _("This industry is currently unavailable. Please choose another industry."),
            frappe.ValidationError,
        )
    industry = canonical_industry

    existing_membership = frappe.db.get_value(
        "EthioBiz Company Membership",
        {"user": user, "company": company_name},
        "name",
    )
    if existing_membership:
        return {
            "success": True,
            "created": False,
            "company": company_name,
            "membership": existing_membership,
            "message": _("You already have access to this company."),
        }

    if frappe.db.exists("Company", company_name):
        log_company_audit(user, company_name, "Add Company", "Failed",
                          "Company exists without a membership for this user")
        frappe.throw(
            _("A company with this name already exists. Ask an administrator to invite you."),
            frappe.ValidationError,
        )

    abbr = _next_abbr(company_name)
    created = False
    try:
        from bizmarketing.api.dobiz_trial import _create_company_fast
        created = bool(_create_company_fast(company_name, abbr, industry))
    except Exception as exc:
        frappe.logger("company_access").warning(
            "Fast company create failed for %s: %s", company_name, exc
        )
    if not frappe.db.exists("Company", company_name):
        # Last-resort bare row; keeps the master identity usable even if a
        # third-party Company hook is temporarily broken.
        frappe.db.sql(
            """
            INSERT IGNORE INTO `tabCompany`
            (name, company_name, abbr, default_currency, country, creation, modified, modified_by, owner)
            VALUES (%s, %s, %s, 'ETB', 'Ethiopia', NOW(), NOW(), %s, %s)
            """,
            (company_name, company_name, abbr, user, user),
        )
        created = True

    if not frappe.db.exists("Company", company_name):
        log_company_audit(user, company_name, "Add Company", "Failed", "Company insert failed")
        frappe.throw(_("The company could not be created. Please try again."))

    first_company = not get_active_memberships(user)
    membership = ensure_membership(
        user,
        company_name,
        role_profile=role_profile,
        is_default=bool(cint(make_default) or first_company),
        notes=notes or "Created from the DOBiz add-company flow",
    )
    log_company_audit(user, company_name, "Add Company", "Success",
                      "Membership {0}".format(getattr(membership, "name", "")))
    return {
        "success": True,
        "created": True,
        "company": company_name,
        "abbr": abbr,
        "membership": getattr(membership, "name", None),
        "is_default": bool(cint(getattr(membership, "is_default", 0))),
        "message": _("Company added to your master account."),
    }


@frappe.whitelist(methods=["POST"])
def revoke_company_membership(user=None, company=None):
    """System Manager: immediately revoke a master user's company access."""
    if not _is_admin():
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    target = user or frappe.session.user
    company = _normalise_company_name(company)
    if not target or not company:
        frappe.throw(_("User and company are required."), frappe.ValidationError)
    name = frappe.db.get_value(
        "EthioBiz Company Membership", {"user": target, "company": company}, "name"
    )
    if not name:
        frappe.throw(_("Membership not found."), frappe.ValidationError)
    doc = frappe.get_doc("EthioBiz Company Membership", name)
    doc.status = "Revoked"
    doc.is_default = 0
    doc.save(ignore_permissions=True)
    log_company_audit(target, company, "Membership Revoked", "Success",
                      "Revoked by {0}".format(frappe.session.user))
    return {"success": True, "membership": name, "status": "Revoked"}
