# -*- coding: utf-8 -*-
"""
DOBiz PWA Settings - DocType Controller
Bismillah Ar-Rahman Ar-Rahim
"""

import frappe
from frappe.model.document import Document


class DOBizPWASettings(Document):
    def on_update(self):
        self.last_updated_on = frappe.utils.now_datetime()
        frappe.db.set_value("DOBiz PWA Settings", "DOBiz PWA Settings", "last_updated_on", self.last_updated_on)
        frappe.clear_document_cache("DOBiz PWA Settings", "DOBiz PWA Settings")
