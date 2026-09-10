# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document

class EthioBizAdCampaign(Document):
    def validate(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw("Start Date cannot be after End Date")
    def on_submit(self):
        if self.status == "Draft":
            self.status = "Pending Approval"
            self.db_set("status", "Pending Approval")
