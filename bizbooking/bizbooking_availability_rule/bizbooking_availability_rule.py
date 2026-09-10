# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
class BizBookingAvailabilityRule(Document):
    def validate(self):
        if self.window_start and self.window_end and self.window_start >= self.window_end:
            frappe.throw("Window End must be after Window Start")
