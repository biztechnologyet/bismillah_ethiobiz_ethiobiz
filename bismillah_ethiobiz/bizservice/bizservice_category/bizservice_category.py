# -*- coding: utf-8 -*-
# Bismillah Ar-Rahman Ar-Rahim
# BizService Category — master list of service categories (generic multi-provider)

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class BizServiceCategory(Document):
    def validate(self):
        if not self.category_icon:
            self.category_icon = "🛎"

    def autoname(self):
        if not self.category_name:
            frappe.throw("Category Name is required")
