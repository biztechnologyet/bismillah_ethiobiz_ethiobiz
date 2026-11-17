# Copyright (c) 2026, Biz Technology Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class EthioBizCompanyMembership(Document):
    def validate(self):
        self._validate_unique()
        self._validate_status()
        if not self.joined_on and self.status == "Active":
            self.joined_on = now_datetime()
        if self.is_default and self.status != "Active":
            frappe.throw(_("Only an Active membership can be the default company."))

    def _validate_unique(self):
        filters = {"user": self.user, "company": self.company}
        if not self.is_new():
            filters["name"] = ("!=", self.name)
        if frappe.db.exists("EthioBiz Company Membership", filters):
            frappe.throw(
                _("A membership for {0} in {1} already exists.").format(
                    frappe.bold(self.user), frappe.bold(self.company)
                ),
                title=_("Duplicate Membership"),
            )

    def _validate_status(self):
        allowed = {"Active", "Invited", "Suspended", "Revoked"}
        if (self.status or "") not in allowed:
            frappe.throw(_("Invalid membership status: {0}").format(self.status))

    def after_insert(self):
        from bismillah_ethiobiz.company_access import sync_membership_access

        sync_membership_access(self, previous_status=None)

    def on_update(self):
        from bismillah_ethiobiz.company_access import sync_membership_access

        previous_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
        sync_membership_access(self, previous_status=previous_status)

    def on_trash(self):
        from bismillah_ethiobiz.company_access import remove_user_permission, log_company_audit

        remove_user_permission(self.user, self.company)
        log_company_audit(
            self.user,
            self.company,
            "Membership Deleted",
            "Success",
            "Membership {0} deleted".format(self.name),
        )
