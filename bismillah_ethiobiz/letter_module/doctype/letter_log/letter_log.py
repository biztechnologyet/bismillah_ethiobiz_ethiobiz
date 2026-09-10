import frappe
from frappe.model.document import Document

class LetterLog(Document):
    def validate(self):
        if not self.reference_number:
            frappe.throw("Reference Number is required")