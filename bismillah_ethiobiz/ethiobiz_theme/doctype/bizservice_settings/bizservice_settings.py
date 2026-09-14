# -*- coding: utf-8 -*-
# Bismillah Ar-Rahman Ar-Rahim
# BizService Settings — Single configuration for the BizServices module

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class BizServiceSettings(Document):
    def get_settings_dict(self):
        return {
            "company": self.get("company"),
            "booking_window_days": self.get("booking_window_days") or 30,
            "auto_dispatch_bizride": bool(self.get("auto_dispatch_bizride")),
            "default_payment_method": self.get("default_payment_method") or "Cash on Delivery",
            "commission_percent": self.get("commission_percent") or 0,
            "review_gating": bool(self.get("review_gating")),
        }
