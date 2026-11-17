# Bismillah Ar-Rahman Ar-Rahim
# EthioBiz home page moved from Web Page doctype `ethiobiz`
# (route `ethiobiz_home_v1`) to a standalone www template.
import frappe
from frappe.website.doctype.website_settings.website_settings import get_website_settings


def get_context(context):
    context.no_cache = 1
    context.title = "EthioBiz"
    # Mint the CSRF token before the template renders. The standalone
    # home page does not extend templates/base.html, so it must receive
    # the token through context (same pattern as www/social.py).
    context.csrf_token = frappe.sessions.get_csrf_token()
    # The standalone template renders its own modern navbar, so it needs the
    # Website Settings menu/brand/CTA values that templates/base.html normally
    # supplies through init_context()/post_process_context().
    context.update(get_website_settings(context))
    return context
