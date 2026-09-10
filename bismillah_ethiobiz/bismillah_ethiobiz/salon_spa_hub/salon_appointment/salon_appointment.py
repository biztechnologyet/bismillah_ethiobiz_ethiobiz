# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
class SalonAppointment(Document):
    def validate(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            frappe.throw("End Time must be after Start Time")
        self.validate_overlap()
    def validate_overlap(self):
        if not (self.stylist and self.appointment_date and self.start_time and self.end_time):
            return
        existing = frappe.db.sql("""
            SELECT name FROM `tabSalon Appointment`
            WHERE stylist = %s AND appointment_date = %s
            AND status NOT IN ('Cancelled', 'No Show')
            AND name != %s
            AND start_time < %s AND end_time > %s
        """, (self.stylist, self.appointment_date, self.name or "~~~",
              self.end_time, self.start_time), as_dict=True)
        if existing:
            frappe.throw("Time conflict with appointment {0}".format(existing[0].name))
