# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
class BizBooking(Document):
    def validate(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            frappe.throw("End Time must be after Start Time")
        self.validate_overlap()
    def validate_overlap(self):
        if not (self.service and self.booking_date and self.start_time and self.end_time):
            return
        existing = frappe.db.sql("""
            SELECT name FROM `tabBizBooking`
            WHERE service = %s AND booking_date = %s
            AND status NOT IN ('Cancelled', 'No Show')
            AND name != %s
            AND start_time < %s AND end_time > %s
        """, (self.service, self.booking_date, self.name or "~~~",
              self.end_time, self.start_time), as_dict=True)
        if existing:
            frappe.throw("Time conflict with booking {0}".format(existing[0].name))
    def before_save(self):
        if not self.provider_doctype and self.service:
            svc = frappe.get_doc("BizBookable Service", self.service)
            self.provider_doctype = svc.provider_doctype or ""
            self.provider_name = svc.provider_field or ""
