# -*- coding: utf-8 -*-
"""Dikka Shop — single product full page.

Serves ``/product/<route-or-item-code>`` as a complete, server-rendered
product page. The route is registered in ``hooks.py`` (website_route_rules).

The same builder powers the canonical published Website Item route (for
example ``/sauce-condiment/ababa-data``) through the Website Item controller
override, so every entry point shares one beautiful, review-aware experience.
"""

import frappe

# Keep these names importable for the existing test contract and for any
# external integration that imported them from this module.
from bismillah_ethiobiz.magala_shop_api import (  # noqa: F401
    build_product_context,
    get_product_detail,
    get_website_item_detail,
    search_products,
)


def get_context(context):
    identifier = (
        frappe.form_dict.get("item_code")
        or frappe.form_dict.get("route")
        or frappe.form_dict.get("name")
        or ""
    ).strip()

    if not identifier:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    return build_product_context(context, identifier)
