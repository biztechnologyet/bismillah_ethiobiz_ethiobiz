# -*- coding: utf-8 -*-
"""Multi-company master identity helpers (TASK-2026-00972).

One Frappe ``User`` is the master identity.  Access to a tenant is represented
by an ``EthioBiz Company Membership`` row.  ERPNext ``User Permission`` rows for
``Company`` are kept in sync so existing permission/query hooks keep working,
while this module adds explicit server-side checks for switching and Company
reads.

The module is deliberately defensive: it is imported from ``hooks.py`` during
migrate/install, before every new DocType may exist, so every database touch is
guarded.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, now_datetime

MEMBERSHIP_DOCTYPE = "EthioBiz Company Membership"
AUDIT_DOCTYPE = "EthioBiz Company Audit"

# Canonical rows seeded into EthioBiz Theme > DOBiz Industry Modules.  Existing
# installations keep their enabled/disabled choices; only missing rows are added.
CANONICAL_INDUSTRY_BY_KEY = {
    "healthcare": "Healthcare & Clinics",
    "restaurant": "Restaurants & Food Service",
    "manufacturing": "Manufacturing & Assembly",
    "education": "Education & Schools",
    "retail": "Retail & Wholesale",
    "non_profit": "Non-Profit & NGOs",
    "agriculture": "Agriculture & Agribusiness",
    "government": "Government & Public-Interest",
    "other": "Other",
    "hotel": "Hotels & Hospitality",
    "property": "Real Estate & Property",
    "professional_services": "Professional Services",
    "transportation": "Transportation & Fleet",
    "construction": "Construction & Engineering",
    "logistics": "Logistics & Warehouse",
    "maintenance": "Maintenance & Repair",
}

DEFAULT_INDUSTRY_MODULES = [
    {"industry_key": "healthcare", "label": "Healthcare & Clinic", "icon": "🏥",
     "description": "Clinical records, pharmacy, lab and billing.", "sort_order": 10},
    {"industry_key": "restaurant", "label": "Restaurant & POS", "icon": "🍽️",
     "description": "Tables, kitchen display, delivery and cash.", "sort_order": 20},
    {"industry_key": "manufacturing", "label": "Manufacturing & Assembly", "icon": "🏭",
     "description": "BOM, work orders, costing and warehouses.", "sort_order": 30},
    {"industry_key": "education", "label": "Education & Schools", "icon": "🎓",
     "description": "Courses, students, results and career placement.", "sort_order": 40},
    {"industry_key": "retail", "label": "Retail & Wholesale", "icon": "🛍️",
     "description": "Storefront, stock, orders and settlements.", "sort_order": 50},
    {"industry_key": "non_profit", "label": "Non-Profit & NGOs", "icon": "🤝",
     "description": "Programs, donors, beneficiaries and reporting.", "sort_order": 60},
    {"industry_key": "agriculture", "label": "Agriculture & Agribusiness", "icon": "🌾",
     "description": "Produce, cooperatives, inputs and buyer orders.", "sort_order": 70},
    {"industry_key": "government", "label": "Government & Public-Interest", "icon": "🏛️",
     "description": "Programs, records, service queues and reporting.", "sort_order": 80},
    {"industry_key": "other", "label": "Other", "icon": "✨",
     "description": "Explore the full EthioBiz ecosystem.", "sort_order": 90},
    # Existing verticals kept visible by default so the signup page does not lose
    # options that were available before Theme-driven visibility was introduced.
    {"industry_key": "hotel", "label": "Hotel & Hospitality", "icon": "🏨",
     "description": "Reservations, rooms, folios and housekeeping.", "sort_order": 15},
    {"industry_key": "property", "label": "Property & Real Estate", "icon": "🏢",
     "description": "Units, leases, rent roll and maintenance.", "sort_order": 25},
    {"industry_key": "professional_services", "label": "Professional Services", "icon": "💼",
     "description": "Projects, timesheets, retainers and invoicing.", "sort_order": 45},
    {"industry_key": "transportation", "label": "Transportation & Fleet", "icon": "🚕",
     "description": "Trips, drivers, fleet cash and live dispatch.", "sort_order": 55},
    {"industry_key": "construction", "label": "Construction & Engineering", "icon": "🏗️",
     "description": "Projects, BOQ, site materials and subcontractors.", "sort_order": 65},
    {"industry_key": "logistics", "label": "Logistics & Warehouse", "icon": "🚚",
     "description": "Dispatch, warehouses, proof of delivery and cash.", "sort_order": 75},
    {"industry_key": "maintenance", "label": "Maintenance & Repair", "icon": "🛠️",
     "description": "Tickets, technicians, spare parts and SLAs.", "sort_order": 85},
]


def _has_doctype(doctype: str) -> bool:
    try:
        return bool(frappe.db.exists("DocType", doctype))
    except Exception:
        return False


def _is_admin(user: str | None = None) -> bool:
    user = user or frappe.session.user
    if not user or user == "Guest":
        return False
    if user == "Administrator":
        return True
    try:
        return "System Manager" in frappe.get_roles(user)
    except Exception:
        return False


def log_company_audit(user, company, action, status="Success", details=None):
    """Best-effort audit trail; never break the caller."""
    if not _has_doctype(AUDIT_DOCTYPE):
        return
    try:
        ip = ""
        try:
            ip = frappe.local.request_ip or ""
        except Exception:
            pass
        frappe.get_doc({
            "doctype": AUDIT_DOCTYPE,
            "user": user,
            "company": company,
            "action": action,
            "status": status,
            "details": (details or "")[:1000],
            "ip_address": ip,
            "timestamp": now_datetime(),
        }).insert(ignore_permissions=True)
    except Exception:
        try:
            frappe.logger("company_access").warning(
                "Audit write failed for %s/%s/%s", user, company, action, exc_info=True
            )
        except Exception:
            pass


def get_active_memberships(user):
    if not user or user == "Guest" or not _has_doctype(MEMBERSHIP_DOCTYPE):
        return []
    try:
        return frappe.get_all(
            MEMBERSHIP_DOCTYPE,
            filters={"user": user, "status": "Active"},
            fields=["name", "user", "company", "status", "is_default", "role_profile",
                    "roles", "invited_by", "joined_on", "notes"],
            order_by="is_default desc, company asc",
        )
    except Exception:
        return []


def get_active_companies(user):
    return [m["company"] for m in get_active_memberships(user)]


def get_default_company(user):
    for membership in get_active_memberships(user):
        if cint(membership.get("is_default")):
            return membership["company"]
    companies = get_active_companies(user)
    if companies:
        return companies[0]
    try:
        return frappe.defaults.get_user_default("company", user)
    except Exception:
        return None


def get_company_context(user=None):
    user = user or frappe.session.user
    memberships = get_active_memberships(user)
    active = None
    try:
        active = frappe.defaults.get_user_default("company", user)
    except Exception:
        active = None
    if active not in [m["company"] for m in memberships]:
        active = get_default_company(user)
    return {
        "user": user,
        "companies": [
            {
                "name": m["company"],
                "abbr": frappe.db.get_value("Company", m["company"], "abbr"),
                "currency": _company_currency(m["company"]),
                "is_default": bool(cint(m.get("is_default"))),
                "role_profile": m.get("role_profile"),
                "roles": m.get("roles"),
            }
            for m in memberships
        ],
        "active_company": active,
        "default_company": get_default_company(user),
    }


def _company_currency(company):
    try:
        return frappe.db.get_value("Company", company, "default_currency")
    except Exception:
        return None


def _set_user_company_fields(user, company):
    try:
        meta = frappe.get_meta("User")
        values = {}
        for fieldname in ("company", "custom_company"):
            if meta.has_field(fieldname):
                values[fieldname] = company
        if values:
            frappe.db.set_value("User", user, values, update_modified=False)
    except Exception:
        pass


def ensure_user_permission(user, company):
    """Ensure a Company User Permission exists for the user.

    Uses apply_to_all_doctypes so Frappe's native permission engine restricts
    all doctypes with a Company field to the user's permitted companies (and
    allows access across all companies the user is a member of).
    """
    if not user or not company:
        return
    try:
        name = frappe.db.get_value(
            "User Permission",
            {"user": user, "allow": "Company", "for_value": company},
            "name",
        )
        if name:
            # Normalize existing permission: multi-company access should apply to
            # all doctypes; default-company flag is managed by set_default_company.
            try:
                doc = frappe.get_doc("User Permission", name)
                changed = False
                if not cint(getattr(doc, "apply_to_all_doctypes", 0)):
                    doc.apply_to_all_doctypes = 1
                    doc.applicable_for = None
                    changed = True
                if changed:
                    doc.flags.ignore_permissions = True
                    doc.save(ignore_permissions=True)
            except Exception:
                pass
            return

        frappe.get_doc({
            "doctype": "User Permission",
            "user": user,
            "allow": "Company",
            "for_value": company,
            "apply_to_all_doctypes": 1,
            "is_default": 0,
        }).insert(ignore_permissions=True)
    except Exception as exc:
        frappe.logger("company_access").warning(
            "Could not sync User Permission for %s/%s: %s", user, company, exc
        )


def remove_user_permission(user, company):
    if not user or not company:
        return
    try:
        frappe.db.delete(
            "User Permission",
            {"user": user, "allow": "Company", "for_value": company},
        )
    except Exception:
        pass


def set_default_company(user, company):
    if not user or not company:
        return
    try:
        ensure_user_permission(user, company)
    except Exception:
        pass
    try:
        frappe.db.set_value(
            MEMBERSHIP_DOCTYPE,
            {"user": user, "is_default": 1, "name": ("!=", _membership_name(user, company))},
            "is_default",
            0,
            update_modified=False,
        )
    except Exception:
        pass
    try:
        name = _membership_name(user, company)
        if name:
            frappe.db.set_value(MEMBERSHIP_DOCTYPE, name, "is_default", 1, update_modified=False)
    except Exception:
        pass
    try:
        frappe.defaults.set_user_default("company", company, user)
        # DefaultValue reads are cached in Redis; invalidate immediately so every
        # interface (Desk boot, Hadeeda, HRMS) sees the newly active company.
        frappe.defaults.clear_defaults_cache()
        frappe.clear_cache(user=user)
    except Exception:
        pass
    try:
        # Keep the ERPNext Company User Permission default in sync with the
        # master-identity default.  Exactly one Company permission is default.
        frappe.db.sql(
            "UPDATE `tabUser Permission` SET is_default=0 WHERE user=%s AND allow='Company'",
            (user,),
        )
        frappe.db.sql(
            "UPDATE `tabUser Permission` SET is_default=1 "
            "WHERE user=%s AND allow='Company' AND for_value=%s",
            (user, company),
        )
    except Exception:
        pass
    _set_user_company_fields(user, company)


def _membership_name(user, company):
    try:
        return frappe.db.get_value(
            MEMBERSHIP_DOCTYPE, {"user": user, "company": company}, "name"
        )
    except Exception:
        return None


def sync_membership_access(membership, previous_status=None):
    """Keep User Permission + default company in sync with a membership row."""
    user = membership.user
    company = membership.company
    status = membership.status or "Active"
    if status == "Active":
        ensure_user_permission(user, company)
        if cint(membership.is_default):
            set_default_company(user, company)
        elif not get_default_company(user):
            set_default_company(user, company)
    else:
        remove_user_permission(user, company)
        if cint(membership.is_default):
            try:
                frappe.db.set_value(MEMBERSHIP_DOCTYPE, membership.name, "is_default", 0,
                                    update_modified=False)
            except Exception:
                pass
            remaining = [m for m in get_active_memberships(user) if m["company"] != company]
            if remaining:
                set_default_company(user, remaining[0]["company"])
    if previous_status != status:
        log_company_audit(
            user, company,
            "Membership {0}".format(status),
            "Success",
            "Status {0} -> {1}".format(previous_status or "New", status),
        )


def ensure_membership(user, company, role_profile=None, is_default=False,
                      invited_by=None, notes=None, status="Active"):
    """Idempotently create/update one membership row."""
    if not _has_doctype(MEMBERSHIP_DOCTYPE):
        return None
    name = _membership_name(user, company)
    if name:
        doc = frappe.get_doc(MEMBERSHIP_DOCTYPE, name)
        previous_status = doc.status
        changed = False
        if status and doc.status != status:
            doc.status = status
            changed = True
        if role_profile and doc.role_profile != role_profile:
            doc.role_profile = role_profile
            changed = True
        if is_default and not cint(doc.is_default):
            doc.is_default = 1
            changed = True
        if notes and doc.notes != notes:
            doc.notes = notes
            changed = True
        if changed:
            doc.flags.ignore_company_sync = 0
            doc.save(ignore_permissions=True)
            # The controller normally does this, but explicit sync keeps the
            # API path correct even if the DocType controller was not reloaded.
            sync_membership_access(doc, previous_status=previous_status)
        return doc
    doc = frappe.get_doc({
        "doctype": MEMBERSHIP_DOCTYPE,
        "user": user,
        "company": company,
        "status": status,
        "is_default": 1 if is_default else 0,
        "role_profile": role_profile,
        "invited_by": invited_by,
        "joined_on": now_datetime(),
        "notes": notes,
    })
    doc.insert(ignore_permissions=True)
    sync_membership_access(doc, previous_status=None)
    return doc


def switch_company(user, company):
    """Validate membership and switch the active company for ``user``."""
    if not user or user == "Guest":
        log_company_audit(user or "Guest", company, "Switch Company", "Failed",
                          "Not logged in")
        frappe.throw(_("Please log in to switch companies."), frappe.PermissionError)
    membership = None
    for row in get_active_memberships(user):
        if row["company"] == company:
            membership = row
            break
    if not membership:
        log_company_audit(user, company, "Switch Company", "Failed",
                          "No active membership")
        frappe.throw(_("You do not have active access to this company."),
                     frappe.PermissionError)
    set_default_company(user, company)
    try:
        frappe.local.session.data["company"] = company
    except Exception:
        pass
    log_company_audit(user, company, "Switch Company", "Success",
                      "Active company changed")
    return {
        "company": company,
        "currency": _company_currency(company),
        "role_profile": membership.get("role_profile"),
        "roles": membership.get("roles"),
        "redirect_url": "/app",
    }


def company_has_permission(doc, ptype=None, user=None, debug=False):
    """Company-level guard: normal users only see their active memberships."""
    user = user or frappe.session.user
    if _is_admin(user):
        return True
    if not user or user == "Guest":
        return False
    company = getattr(doc, "name", None) or (doc if isinstance(doc, str) else None)
    if not company:
        return False
    return company in get_active_companies(user)


def company_query_conditions(user=None):
    user = user or frappe.session.user
    if _is_admin(user):
        return ""
    companies = get_active_companies(user)
    if not companies:
        return "1=0"
    escaped = ", ".join(frappe.db.escape(c) for c in companies)
    return "`tabCompany`.`name` in ({0})".format(escaped)


def ensure_company_membership_schema():
    """Add the (user, company) unique index once the table exists."""
    if not _has_doctype(MEMBERSHIP_DOCTYPE):
        return
    try:
        frappe.db.add_unique(
            MEMBERSHIP_DOCTYPE,
            ["user", "company"],
            constraint_name="unique_ethiobiz_company_membership_user_company",
        )
    except Exception:
        # Already present, or legacy duplicate rows exist.  The controller still
        # validates duplicates; the index is a defence-in-depth optimisation.
        pass


def seed_dobiz_industry_modules():
    """Seed missing Theme rows without overwriting admin enable/disable choices."""
    if not _has_doctype("EthioBiz Theme"):
        return
    try:
        theme = frappe.get_single("EthioBiz Theme")
    except Exception:
        return
    if not theme.meta.has_field("dobiz_industry_modules"):
        return
    existing = {((row.industry_key or "").strip().lower()) for row in (theme.dobiz_industry_modules or [])}
    changed = False
    for row in DEFAULT_INDUSTRY_MODULES:
        key = row["industry_key"]
        if key in existing:
            continue
        theme.append("dobiz_industry_modules", {
            "industry_key": key,
            "label": row["label"],
            "icon": row["icon"],
            "description": row["description"],
            "enabled": 1,
            "sort_order": row["sort_order"],
        })
        changed = True
    if changed:
        theme.flags.ignore_permissions = True
        theme.save(ignore_permissions=True)


def get_enabled_industry_modules():
    """Return Theme-driven industry rows, or a safe fallback when unset."""
    rows = []
    try:
        theme = frappe.get_single("EthioBiz Theme")
        if theme.meta.has_field("dobiz_industry_modules"):
            rows = [
                {
                    "industry_key": (r.industry_key or "").strip().lower(),
                    "label": (r.label or "").strip(),
                    "icon": r.icon or "",
                    "description": r.description or "",
                    "enabled": bool(cint(r.enabled)),
                    "sort_order": cint(r.sort_order),
                }
                for r in (theme.dobiz_industry_modules or [])
            ]
    except Exception:
        rows = []
    rows = [r for r in rows if r["label"]]
    if not rows:
        rows = [
            {
                "industry_key": r["industry_key"],
                "label": r["label"],
                "icon": r["icon"],
                "description": r["description"],
                "enabled": True,
                "sort_order": r["sort_order"],
            }
            for r in DEFAULT_INDUSTRY_MODULES
        ]
    rows.sort(key=lambda r: (r["sort_order"], r["label"].lower()))
    for row in rows:
        row["canonical_label"] = CANONICAL_INDUSTRY_BY_KEY.get(
            row.get("industry_key", ""), row.get("label", "")
        )
    return [r for r in rows if r["enabled"]]


def get_enabled_industry_labels():
    return [r["label"] for r in get_enabled_industry_modules()]


def get_enabled_industry_canonical_labels():
    """Canonical labels accepted by the provisioning API."""
    return [r["canonical_label"] for r in get_enabled_industry_modules()]


def backfill_memberships():
    """Create memberships for existing Company User Permissions (idempotent)."""
    if not _has_doctype(MEMBERSHIP_DOCTYPE):
        return
    try:
        permissions = frappe.get_all(
            "User Permission",
            filters={"allow": "Company"},
            fields=["user", "for_value"],
        )
    except Exception:
        return
    seen = set()
    for row in permissions:
        user = row.get("user")
        company = row.get("for_value")
        if not user or not company or user in ("Administrator", "Guest"):
            continue
        key = (user, company)
        if key in seen:
            continue
        seen.add(key)
        if frappe.db.exists(MEMBERSHIP_DOCTYPE, {"user": user, "company": company}):
            continue
        default_company = None
        try:
            default_company = frappe.defaults.get_user_default("company", user)
        except Exception:
            pass
        try:
            ensure_membership(
                user, company,
                is_default=(default_company == company),
                notes="Backfilled from existing Company User Permission",
            )
        except Exception:
            frappe.logger("company_access").warning(
                "Membership backfill failed for %s/%s", user, company, exc_info=True
            )
