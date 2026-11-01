"""Guest-safe webshop cart bridge.

The upstream `webshop` app assumes every visitor has a Customer party. A guest
has none, so `get_party()` returns ``None`` and ``_get_cart_quotation`` then
dereferences ``party.name`` -> ``AttributeError`` -> HTTP 500 on `/cart`.

This module patches that one function at request time. Authenticated users keep
the exact upstream behaviour; guests receive an unsaved, empty Quotation-shaped
document so the standard `/cart` template renders its "empty cart" state and
the Magala payment panel still loads from `magala_checkout.get_cart`.

Registered through `before_request` in hooks.py so it applies to website routes
without forking the third-party app.
"""

import frappe

_PATCHED = False


def _blank_quotation():
    """Return an unsaved, empty Shopping Cart quotation for a guest."""
    currency = "ETB"
    try:
        currency = frappe.db.get_single_value("Webshop Settings", "currency") or currency
    except Exception:
        pass

    doc = frappe.get_doc(
        {
            "doctype": "Quotation",
            "quotation_to": "Customer",
            "party_name": None,
            "order_type": "Shopping Cart",
            "docstatus": 0,
            "status": "Draft",
            "items": [],
            "taxes": [],
            "total_qty": 0,
            "total": 0,
            "net_total": 0,
            "grand_total": 0,
            "currency": currency,
        }
    )
    doc.name = None
    doc.customer_address = None
    doc.shipping_address_name = None
    doc.shipping_rule = None
    doc.coupon_code = None
    doc.terms = None
    doc.flags.ignore_permissions = True
    return doc


def apply():
    """Install the guest-safe cart patch once per worker process."""
    global _PATCHED
    if _PATCHED:
        return

    try:
        from webshop.webshop.shopping_cart import cart as webshop_cart
    except Exception:
        # Webshop is optional; never break a request if it is absent.
        _PATCHED = True
        return

    original = getattr(webshop_cart, "_get_cart_quotation", None)
    if not original or getattr(original, "_ethiobiz_guest_safe", False):
        _PATCHED = True
        return

    def guest_safe_get_cart_quotation(party=None):
        if not party:
            party = webshop_cart.get_party()
        if not party:
            return _blank_quotation()
        return original(party)

    guest_safe_get_cart_quotation._ethiobiz_guest_safe = True
    webshop_cart._get_cart_quotation = guest_safe_get_cart_quotation
    _PATCHED = True
