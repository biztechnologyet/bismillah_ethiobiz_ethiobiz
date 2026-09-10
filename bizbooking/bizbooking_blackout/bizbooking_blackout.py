# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
class BizBookingBlackout(Document):
    def validate(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw("To Date must be on or after From Date")
