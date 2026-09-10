import frappe
from frappe import _

def validate_workspace_permissions(doc, method):
    if frappe.session.user == "Administrator":
        return
        
    roles = frappe.get_roles()
    if "System Manager" in roles:
        return
        
    frappe.throw(_("You are not authorized to create or edit Workspaces. Please contact the Administrator."))

def validate_company_permissions(doc, method):
    if frappe.session.user == "Administrator":
        return

    roles = frappe.get_roles()
    if "System Manager" in roles:
        return

    frappe.throw(_("You are not authorized to create Companies. Please contact the Administrator."))
