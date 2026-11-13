"""Guest-safe webshop cart bridge.

The upstream `webshop` app assumes every visitor has a Customer party. A guest
has none, so `get_party()` returns ``None`` and ``_get_cart_quotation`` then
dereferences ``party.name`` -> ``AttributeError`` -> HTTP 500 on `/cart`.

This module patches that function at request time. It also protects the cart
from stale quotation rows whose items no longer have a published Website Item.
Authenticated users keep the exact upstream behaviour for valid rows; guests
receive an unsaved, empty Quotation-shaped document so the standard `/cart`
template renders its "empty cart" state and the Magala payment panel still
loads from `magala_checkout.get_cart`.

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


def _published_website_item(item_code):
    """Return the Website Item name for an item code, or None.

    A missing Website Item is the exact condition that makes upstream
    `decorate_quotation_doc()` call `d.update(None)` and crash `/cart`.
    """

    if not item_code:
        return None
    try:
        return frappe.db.get_value("Website Item", {"item_code": item_code}, "name")
    except Exception:
        return None


def _prune_stale_items(doc):
    """Remove quotation rows that cannot be decorated by the webshop.

    This is an in-memory guard. The one-time repair patch persists the cleanup
    for existing carts; this wrapper keeps future deletions from breaking the
    page even if an old quotation still contains a removed product.
    """

    items = getattr(doc, "items", None) if doc is not None else None
    if not items:
        return doc

    valid_rows = []
    removed = []
    for row in items:
        code = getattr(row, "item_code", None)
        if _published_website_item(code):
            valid_rows.append(row)
        else:
            removed.append(code or "<empty item_code>")

    if not removed:
        return doc

    try:
        doc.set("items", valid_rows)
        doc.calculate_taxes_and_totals()
    except Exception:
        # A totals failure must never make the cart page worse; the row
        # removal is still the important safety step.
        pass

    try:
        frappe.logger("ethiobiz").warning(
            "Pruned stale cart rows from %s: %s",
            getattr(doc, "name", "unsaved quotation"),
            ", ".join(str(code) for code in removed),
        )
    except Exception:
        pass

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

    # A stale Contact/Portal User can point at a Customer or Supplier that no
    # longer exists.  Upstream get_party() then raises DoesNotExistError before
    # the cart guard below ever runs, which Frappe renders as HTTP 403
    # ("Not Permitted") for guests.  Make the lookup guest-safe as well.
    original_get_party = getattr(webshop_cart, "get_party", None)
    if original_get_party and not getattr(original_get_party, "_ethiobiz_guest_safe", False):

        def guest_safe_get_party(user=None):
            try:
                return original_get_party(user)
            except frappe.DoesNotExistError:
                if (user or frappe.session.user) == "Guest":
                    return None
                raise

        guest_safe_get_party._ethiobiz_guest_safe = True
        webshop_cart.get_party = guest_safe_get_party

    original = getattr(webshop_cart, "_get_cart_quotation", None)
    if original and not getattr(original, "_ethiobiz_guest_safe", False):

        def guest_safe_get_cart_quotation(party=None):
            if not party:
                party = webshop_cart.get_party()
            if not party:
                return _blank_quotation()
            return _prune_stale_items(original(party))

        guest_safe_get_cart_quotation._ethiobiz_guest_safe = True
        webshop_cart._get_cart_quotation = guest_safe_get_cart_quotation

    original_decorate = getattr(webshop_cart, "decorate_quotation_doc", None)
    if original_decorate and not getattr(original_decorate, "_ethiobiz_safe_decorate", False):

        def safe_decorate_quotation_doc(doc):
            return original_decorate(_prune_stale_items(doc))

        safe_decorate_quotation_doc._ethiobiz_safe_decorate = True
        webshop_cart.decorate_quotation_doc = safe_decorate_quotation_doc

    _PATCHED = True
