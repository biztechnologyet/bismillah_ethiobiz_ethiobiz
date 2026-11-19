# -*- coding: utf-8 -*-
"""
Overrides for ERPNext/HRMS Employee to support one User linked to Employees
in different companies (multi-company master identity).

Standard ERPNext enforces a 1:1 User↔Employee mapping in
`validate_duplicate_user_id`. In EthioBiz multi-company, the same master User
may hold memberships in multiple companies and needs a company-scoped Employee
record per company where required.

This override allows the same user_id only when the existing Employee belongs
to a different company. Same-company duplicates remain blocked.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cstr

from erpnext.setup.doctype.employee.employee import Employee as ERPNextEmployee


class EthioBizEmployee(ERPNextEmployee):
    def validate_duplicate_user_id(self):
        """Allow same user_id across different companies; block same-company duplicates."""
        employee = self.get_duplicate_user_id()
        if not employee:
            return

        # Normalize companies for comparison
        this_company = cstr(self.company).strip()
        other_company = cstr(employee.get("company")).strip()

        # Allow multi-company: same user may be linked to employees in different companies.
        # If either company is blank, fall back to standard strict behavior to avoid ambiguity.
        if this_company and other_company and this_company != other_company:
            return

        frappe.throw(
            _("User {0} is already assigned to Employee {1}").format(
                self.user_id, employee.get("name")
            ),
            frappe.DuplicateEntryError,
        )

    def get_duplicate_user_id(self):
        """Return an existing Employee using the same user_id (any company)."""
        if not self.user_id:
            return None

        fields = ["name", "company"]
        filters = {"user_id": self.user_id}
        if not self.is_new():
            filters["name"] = ("!=", self.name)

        # Prefer same-company match if present (so error message is clear)
        if cstr(self.company).strip():
            same_company = frappe.db.get_value(
                "Employee",
                {**filters, "company": self.company},
                fields,
                as_dict=True,
            )
            if same_company:
                return same_company

        return frappe.db.get_value("Employee", filters, fields, as_dict=True)
