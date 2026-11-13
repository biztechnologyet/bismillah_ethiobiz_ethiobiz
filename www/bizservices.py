# -*- coding: utf-8 -*-
# Bismillah Ar-Rahman Ar-Rahim
# Legacy /bizservices (plural) -> /bizservice (canonical singular). 302 redirect.
import frappe


def get_context(context):
    frappe.local.flags.redirect_location = "/bizservice"
    raise frappe.Redirect
