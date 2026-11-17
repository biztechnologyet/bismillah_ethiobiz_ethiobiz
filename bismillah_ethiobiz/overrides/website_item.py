# -*- coding: utf-8 -*-
"""Canonical Website Item page override.

The standard webshop item page is intentionally minimal. EthioBiz needs the
same rich Dikka Shop experience on the canonical published Website Item route
(for example ``/sauce-condiment/ababa-data``) that we provide on
``/product/<route>``. Subclassing the webshop controller lets us keep all
standard Website Item behaviour (Desk, cart, variants, routing) while swapping
only the website template and context.
"""

import frappe
from webshop.webshop.doctype.website_item.website_item import WebsiteItem

from bismillah_ethiobiz.magala_shop_api import build_product_context


class EthioBizWebsiteItem(WebsiteItem):
    website = frappe._dict(
        page_title_field="web_item_name",
        condition_field="published",
        template="templates/generators/item/dikka_item.html",
        no_cache=1,
    )

    def get_context(self, context):
        # Preserve every standard webshop context key first (cart settings,
        # wishlist, variants, breadcrumbs, metatags, etc.). If the standard
        # context fails for an edge-case item, our own dossier can still render
        # a safe page instead of a 500.
        try:
            super().get_context(context)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "EthioBiz Website Item context")
            context.show_search = True
            context.body_class = "product-page"

        return build_product_context(context, self.name)
