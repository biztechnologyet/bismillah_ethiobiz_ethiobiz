import frappe

def get_context(context):
    context.no_cache = 1
    context.title = "AFOCHA Social & Business Pulse | EthioBiz"
    # Mint the CSRF token before the template renders. Frappe's Jinja sandbox
    # does not expose frappe.local/frappe.sessions, and frappe.session.csrf_token
    # is empty on the outer session dict, so the template must use this value.
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context
