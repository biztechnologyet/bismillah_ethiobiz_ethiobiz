
import frappe

@frappe.whitelist(allow_guest=True)
def get_custom_theme():
    """Returns the EthioBiz Theme settings as a dictionary for the JS engine."""
    try:
        theme = frappe.get_single("EthioBiz Theme")
        return theme.as_dict()
    except Exception:
        return {}
