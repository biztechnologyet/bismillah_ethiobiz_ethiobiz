# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
class SalonAppointmentService(Document):
    def validate(self):
        if self.salon_service:
            price = frappe.db.get_value("Salon Service", self.salon_service, "price_etb")
            if price:
                self.amount = price
