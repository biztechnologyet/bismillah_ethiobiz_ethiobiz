# -*- coding: utf-8 -*-
"""
Dikka Shop catalogue + single-item experience.

This module is the single source of truth for:
- the Shop listing (published Website Item records, like /all-products)
- the rich single-item dossier used by /product/<route> and the canonical
  Website Item route (for example /sauce-condiment/ababa-data)
- product reviews, seller responses, helpful votes and rating summaries

It intentionally uses Website Item as the storefront record and Item as the
commerce record (price, stock, seller/company), matching the standard webshop
model while keeping EthioBiz's richer cart, seller and review experience.
"""

from __future__ import annotations

import math
from urllib.parse import quote, unquote

import frappe
from frappe.utils import cint, cstr, flt, format_date, get_url, nowdate, strip_html

try:
    from bismillah_ethiobiz.ethiobiz_identity import require_authed_customer
except ImportError:  # pragma: no cover - fallback for non-package imports
    from ethiobiz_identity import require_authed_customer


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

EXCLUDED_GROUPS = (
    "Services",
    "Jobs & Careers",
    "Properties & Real Estate",
    "Properties",
)

TEST_GROUP_REGEX = r"^(RM|FG|Packing) [0-9]+$"
TEST_NAME_REGEX = (
    r"^(Shop Item|WI Co Roundtrip|Fabric Test|T-Shirt Test|Carton Test|"
    r"Tuition |E2E-|FG-TEE-|FAB-|CTN-)"
)

LISTING_LIMIT_DEFAULT = 24
LISTING_LIMIT_MAX = 60


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _safe_text(value) -> str:
    return cstr(value or "").strip()


def _plain(value, limit: int | None = None) -> str:
    text = " ".join(strip_html(cstr(value or "")).split())
    if limit and len(text) > limit:
        text = text[: max(0, limit - 1)].rstrip() + "…"
    return text


def _truncate(value, limit: int) -> str:
    text = _safe_text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _first_nonempty(*values) -> str:
    for value in values:
        if value is not None and cstr(value).strip():
            return cstr(value)
    return ""


def _img(src, fallback: str = "") -> str:
    """Return a browser-safe asset URL without changing legitimate spaces."""
    src = _safe_text(src)
    if not src:
        src = _safe_text(fallback)
    if not src:
        return ""
    if src.startswith(("http://", "https://", "//", "/")):
        return src
    return "/" + src.lstrip("./")


def _clamp_rating(value) -> float:
    value = flt(value or 0)
    return max(0.0, min(5.0, value))


def _normalise_rating(value) -> float:
    """Accept both webshop's 0–1 ratings and legacy 1–5 ratings."""
    value = flt(value or 0)
    if value <= 0:
        return 0.0
    if value <= 1.0:
        value = value * 5.0
    return _clamp_rating(value)


def _star_count(value) -> int:
    return int(round(_normalise_rating(value)))


def _row_get(row, field, default=None):
    if row is None:
        return default
    try:
        return row.get(field, default)
    except Exception:
        return getattr(row, field, default)


def _as_dict_list(rows) -> list[dict]:
    out = []
    for row in rows or []:
        if isinstance(row, dict):
            out.append(row)
        elif hasattr(row, "as_dict"):
            out.append(row.as_dict())
        else:
            out.append(dict(row))
    return out


def _item_price(item_code: str, company: str | None = None) -> tuple[float, str]:
    row = frappe.db.sql(
        """
        SELECT price_list_rate, currency
        FROM `tabItem Price`
        WHERE item_code = %s
          AND selling = 1
          AND price_list = 'Standard Selling'
        ORDER BY modified DESC
        LIMIT 1
        """,
        (item_code,),
        as_dict=True,
    )
    if row:
        return flt(row[0].get("price_list_rate")), cstr(row[0].get("currency") or "ETB")

    standard_rate = frappe.db.get_value("Item", item_code, "standard_rate")
    currency = "ETB"
    if company:
        currency = frappe.db.get_value("Company", company, "default_currency") or currency
    return flt(standard_rate), currency


def _stock_status(item, website_warehouse: str | None = None, on_backorder=0) -> tuple[str, float]:
    if cint(on_backorder):
        return "Available on backorder", 0.0
    if not item:
        return "In Stock", 0.0
    if not cint(_row_get(item, "is_stock_item", 0)):
        return "In Stock", 0.0

    if website_warehouse:
        qty = frappe.db.sql(
            "SELECT COALESCE(SUM(actual_qty), 0) FROM `tabBin` WHERE item_code=%s AND warehouse=%s",
            (item.name, website_warehouse),
        )[0][0]
    else:
        qty = frappe.db.sql(
            "SELECT COALESCE(SUM(actual_qty), 0) FROM `tabBin` WHERE item_code=%s",
            (item.name,),
        )[0][0]

    qty = flt(qty)
    if website_warehouse and qty <= 0:
        return "Out of Stock", qty
    # Most EthioBiz products are made-to-order or not stock-tracked in a
    # website warehouse. Avoid a false "Out of Stock" when no warehouse is set.
    return "In Stock", qty


def _stock_map(rows: list[dict]) -> tuple[dict, dict]:
    codes = sorted({row.get("item_code") for row in rows if row.get("item_code")})
    if not codes:
        return {}, {}
    bins = frappe.db.sql(
        """
        SELECT item_code, warehouse, COALESCE(SUM(actual_qty), 0) AS qty
        FROM `tabBin`
        WHERE item_code IN %(codes)s
        GROUP BY item_code, warehouse
        """,
        {"codes": tuple(codes)},
        as_dict=True,
    )
    by_warehouse: dict[tuple[str, str], float] = {}
    totals: dict[str, float] = {}
    for row in bins:
        code = row.get("item_code")
        warehouse = row.get("warehouse") or ""
        qty = flt(row.get("qty"))
        by_warehouse[(code, warehouse)] = qty
        totals[code] = totals.get(code, 0.0) + qty
    return by_warehouse, totals


def _listing_conditions() -> list[str]:
    groups = ", ".join("%s" for _ in EXCLUDED_GROUPS)
    # The placeholders are filled by search_products/get_categories. Keeping
    # the strings here makes the Shop and category counts agree exactly.
    return [
        "wi.published = 1",
        "it.disabled = 0",
        "it.has_variants = 0",
        "(it.is_sales_item = 1 OR it.is_stock_item = 1)",
        f"wi.item_group NOT IN ({groups})",
        "wi.item_group NOT REGEXP %(test_group_regex)s",
        "wi.web_item_name NOT REGEXP %(test_name_regex)s",
        "it.item_group NOT REGEXP %(test_group_regex)s",
        "it.item_code NOT LIKE 'E2E-%%'",
    ]


def _listing_values() -> dict:
    return {
        "test_group_regex": TEST_GROUP_REGEX,
        "test_name_regex": TEST_NAME_REGEX,
        "excluded_groups": list(EXCLUDED_GROUPS),
    }


def _listing_from_sql() -> str:
    return """
        FROM `tabWebsite Item` wi
        JOIN `tabItem` it ON it.name = wi.item_code
        LEFT JOIN `tabItem Group` ig ON ig.name = wi.item_group
        LEFT JOIN (
            SELECT item_code,
                   MAX(price_list_rate) AS price_list_rate,
                   MAX(currency) AS currency
            FROM `tabItem Price`
            WHERE selling = 1 AND price_list = 'Standard Selling'
            GROUP BY item_code
        ) ip ON ip.item_code = it.name
        LEFT JOIN `tabCompany` c ON c.name = it.company
    """


def _listing_where(query: str = "", category: str | None = None,
                   company: str | None = None, region: str | None = None,
                   min_price=None, max_price=None, min_rating=None) -> tuple[str, dict]:
    values = _listing_values()
    values.update({
        "test_group_regex": TEST_GROUP_REGEX,
        "test_name_regex": TEST_NAME_REGEX,
    })
    clauses = [
        "wi.published = 1",
        "it.disabled = 0",
        "it.has_variants = 0",
        "(it.is_sales_item = 1 OR it.is_stock_item = 1)",
        "wi.item_group NOT IN %(excluded_groups)s",
        "wi.item_group NOT REGEXP %(test_group_regex)s",
        "wi.web_item_name NOT REGEXP %(test_name_regex)s",
        "it.item_group NOT REGEXP %(test_group_regex)s",
        "it.item_code NOT LIKE 'E2E-%%'",
    ]

    if query:
        q = f"%{query.strip()}%"
        values["q"] = q
        clauses.append(
            "("
            "wi.web_item_name LIKE %(q)s OR wi.item_name LIKE %(q)s OR "
            "wi.item_code LIKE %(q)s OR wi.brand LIKE %(q)s OR "
            "wi.short_description LIKE %(q)s OR wi.web_long_description LIKE %(q)s OR "
            "wi.description LIKE %(q)s OR it.item_name LIKE %(q)s OR "
            "it.item_code LIKE %(q)s OR it.description LIKE %(q)s OR "
            "it.company LIKE %(q)s OR it.item_group LIKE %(q)s"
            ")"
        )

    if category:
        values["category"] = category
        clauses.append(
            "("
            "wi.item_group = %(category)s OR ig.parent_item_group = %(category)s OR "
            "EXISTS (SELECT 1 FROM `tabWebsite Item Group` wig "
            "WHERE wig.parent = wi.name AND wig.item_group = %(category)s)"
            ")"
        )

    if company:
        values["company"] = company
        clauses.append("it.company = %(company)s")

    if region:
        values["region"] = region
        clauses.append(
            "(c.location_address LIKE %(region_like)s OR c.state LIKE %(region_like)s)"
        )
        values["region_like"] = f"%{region}%"

    if min_price not in (None, ""):
        values["min_price"] = flt(min_price)
        clauses.append("COALESCE(ip.price_list_rate, it.standard_rate, 0) >= %(min_price)s")
    if max_price not in (None, ""):
        values["max_price"] = flt(max_price)
        clauses.append("COALESCE(ip.price_list_rate, it.standard_rate, 0) <= %(max_price)s")
    if min_rating not in (None, ""):
        values["min_rating"] = flt(min_rating)
        clauses.append("COALESCE(it.average_product_rating, 0) >= %(min_rating)s")

    return " AND ".join(clauses), values


# ---------------------------------------------------------------------------
# Website Item resolution
# ---------------------------------------------------------------------------


def _resolve_website_item(identifier) -> frappe.model.document.Document | None:
    if not identifier:
        return None
    candidate = unquote(cstr(identifier)).strip().strip("/")
    if not candidate:
        return None

    for field in ("name", "route", "item_code"):
        name = frappe.db.get_value(
            "Website Item",
            {field: candidate, "published": 1},
            "name",
        )
        if name:
            return frappe.get_doc("Website Item", name)

    # Route fields are sometimes stored without the leading slash but with a
    # trailing slash. Try both once more for robustness.
    for field in ("route",):
        name = frappe.db.get_value(
            "Website Item",
            {field: candidate + "/", "published": 1},
            "name",
        )
        if name:
            return frappe.get_doc("Website Item", name)

    return None


def _company_info(company_name: str | None) -> dict:
    if not company_name or not frappe.db.exists("Company", company_name):
        return {}
    company = frappe.get_doc("Company", company_name)
    return {
        "company": company.name,
        "company_name": company.company_name or company.name,
        "company_slug": company.get("company_slug") or "",
        "company_logo": _img(company.get("company_logo")),
        "company_address": company.get("location_address") or "",
        "company_phone": company.get("phone_no") or "",
        "company_email": company.get("email") or "",
        "company_website": company.get("website") or "",
        "company_latitude": company.get("latitude"),
        "company_longitude": company.get("longitude"),
    }


# ---------------------------------------------------------------------------
# Gallery, specs, tabs, offers, highlights
# ---------------------------------------------------------------------------


def _build_gallery(wi, item) -> list[dict]:
    gallery: list[dict] = []
    seen: set[str] = set()

    def add(src, caption="", is_primary=0, url=""):
        src = _img(src)
        if not src or src in seen:
            return
        seen.add(src)
        gallery.append({
            "image": src,
            "caption": _safe_text(caption),
            "is_primary": 1 if is_primary or not gallery else 0,
            "url": _safe_text(url),
        })

    if wi:
        add(wi.get("website_image"), wi.get("website_image_alt") or wi.get("web_item_name") or "", 1)
        slideshow = wi.get("slideshow")
        if slideshow and frappe.db.exists("Website Slideshow", slideshow):
            try:
                slideshow_doc = frappe.get_doc("Website Slideshow", slideshow)
                for row in slideshow_doc.get("slideshow_items") or []:
                    add(
                        row.get("image"),
                        row.get("heading") or row.get("description") or "",
                        0,
                        row.get("url") or "",
                    )
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Dikka product slideshow")

    if item:
        add(item.get("image"), item.get("item_name") or "", 0)
        for row in item.get("product_images") or []:
            add(row.get("image"), row.get("caption") or "", row.get("is_primary"))

    return gallery


def _build_specs(wi, item, company_info: dict, stock_status: str,
                 price: float, currency: str) -> list[dict]:
    specs: list[dict] = []
    seen: set[str] = set()

    def add(label, description):
        label = _safe_text(label)
        description = cstr(description or "").strip()
        if not label or not description or label.lower() in seen:
            return
        seen.add(label.lower())
        specs.append({"label": label, "description": description})

    if wi:
        for row in wi.get("website_specifications") or []:
            add(row.get("label"), row.get("description"))

    add("Brand", (wi.get("brand") if wi else "") or (item.get("brand") if item else ""))
    add("Category", (wi.get("item_group") if wi else "") or (item.get("item_group") if item else ""))
    add("Unit of Measure", (wi.get("stock_uom") if wi else "") or (item.get("stock_uom") if item else ""))
    add("Item Code", item.get("name") if item else (wi.get("item_code") if wi else ""))
    add("Seller", company_info.get("company_name") or (item.get("company") if item else ""))
    add("Availability", stock_status)
    add("Price", f"{price:,.2f} {currency}" if price > 0 else "Price on request")

    if item:
        add("Country of Origin", item.get("country_of_origin"))
        add("Warranty", item.get("warranty_period"))
        shelf_life = item.get("shelf_life_in_days")
        if shelf_life:
            add("Shelf Life", f"{shelf_life} days")
        add("Description", item.get("description") and _plain(item.get("description"), 220))

    return specs


def _build_tabs(wi, description_html: str, website_content: str) -> list[dict]:
    tabs: list[dict] = []
    if wi:
        for row in wi.get("tabs") or []:
            label = _safe_text(row.get("label"))
            content = cstr(row.get("content") or "").strip()
            if label and content:
                tabs.append({"label": label, "content": content})

    existing = {tab["label"].lower() for tab in tabs}
    if website_content and "more details" not in existing:
        tabs.append({"label": "More details", "content": website_content})

    return tabs


def _build_offers(wi) -> list[dict]:
    offers: list[dict] = []
    if not wi:
        return offers
    for row in wi.get("offers") or []:
        title = _safe_text(row.get("offer_title"))
        subtitle = _safe_text(row.get("offer_subtitle"))
        details = cstr(row.get("offer_details") or "").strip()
        if title or subtitle or details:
            offers.append({
                "offer_title": title or "Special offer",
                "offer_subtitle": subtitle,
                "offer_details": details,
            })
    return offers


def _build_highlights(item, wi, company_info: dict, item_group: str, uom: str) -> list[dict]:
    highlights: list[dict] = []
    if item:
        for row in item.get("product_highlights") or []:
            text = _safe_text(row.get("highlight_text") or row.get("highlight"))
            if text:
                highlights.append({
                    "text": text,
                    "icon": _safe_text(row.get("highlight_icon")) or "✓",
                })

    if len(highlights) < 2:
        short = _plain((wi.get("short_description") if wi else "") or (item.get("description") if item else ""))
        chunks = []
        for separator in ("•", "|", "\n", ";", ". "):
            if separator in short:
                chunks = [chunk.strip(" .•|-") for chunk in short.split(separator)]
                break
        if not chunks:
            chunks = [short]
        for chunk in chunks:
            if 3 <= len(chunk) <= 140 and len(highlights) < 4:
                highlights.append({"text": chunk, "icon": "✓"})

    fallback = [
        (company_info.get("company_name") and f"Curated by {company_info['company_name']}", "◆"),
        (item_group and f"Category: {item_group}", "▣"),
        (uom and f"Sold per {uom}", "◈"),
        ("Published on Dikka Shop", "✦"),
    ]
    for text, icon in fallback:
        if len(highlights) >= 4:
            break
        if text and all(_safe_text(h["text"]).lower() != _safe_text(text).lower() for h in highlights):
            highlights.append({"text": text, "icon": icon})

    return highlights[:5]


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------


def _review_where(website_item: str | None, item_code: str | None) -> tuple[str, dict]:
    values: dict = {}
    clauses = []
    if website_item and item_code:
        values["website_item"] = website_item
        values["item_code"] = item_code
        clauses.append("(ir.website_item = %(website_item)s OR ir.item = %(item_code)s)")
    elif website_item:
        values["website_item"] = website_item
        clauses.append("ir.website_item = %(website_item)s")
    elif item_code:
        values["item_code"] = item_code
        clauses.append("ir.item = %(item_code)s")
    else:
        clauses.append("1=0")
    return " AND ".join(clauses), values


def _review_summary(where: str, values: dict) -> dict:
    counts: dict[int, int] = {star: 0 for star in range(1, 6)}
    if not frappe.db.exists("DocType", "Item Review"):
        return {"average": 0.0, "total": 0, "rows": []}

    rows = frappe.db.sql(
        f"""
        SELECT ir.rating, COUNT(*) AS total
        FROM `tabItem Review` ir
        WHERE {where}
        GROUP BY ir.rating
        """,
        values,
        as_dict=True,
    )
    for row in rows:
        stars = _star_count(row.get("rating"))
        if 1 <= stars <= 5:
            counts[stars] += cint(row.get("total"))

    total = sum(counts.values())
    average = (sum(star * count for star, count in counts.items()) / total) if total else 0.0
    summary_rows = []
    for star in range(5, 0, -1):
        count = counts[star]
        summary_rows.append({
            "star": star,
            "count": count,
            "percent": round((count / total) * 100, 1) if total else 0.0,
        })
    return {"average": round(average, 2), "total": total, "rows": summary_rows}


def _review_rows(website_item: str | None, item_code: str | None,
                 limit: int = 50, offset: int = 0, sort_by: str = "newest") -> list[dict]:
    if not frappe.db.exists("DocType", "Item Review"):
        return []
    where, values = _review_where(website_item, item_code)
    values["limit"] = max(1, min(cint(limit) or 50, 100))
    values["offset"] = max(0, cint(offset) or 0)

    order = {
        "highest": "ir.rating DESC, ir.creation DESC",
        "lowest": "ir.rating ASC, ir.creation DESC",
        "helpful": "ir.helpful_count DESC, ir.creation DESC",
        "newest": "ir.creation DESC",
    }.get(cstr(sort_by or "newest"), "ir.creation DESC")

    rows = frappe.db.sql(
        f"""
        SELECT
            ir.name, ir.user, ir.customer, ir.item, ir.website_item,
            ir.rating, ir.review_title, ir.comment, ir.verified_purchase,
            ir.seller_response, ir.helpful_count, ir.reviewer_region,
            ir.published_on, ir.creation
        FROM `tabItem Review` ir
        WHERE {where}
        ORDER BY {order}
        LIMIT %(limit)s OFFSET %(offset)s
        """,
        values,
        as_dict=True,
    )
    if not rows:
        return []

    user_ids = sorted({row.get("user") for row in rows if row.get("user")})
    user_map: dict[str, dict] = {}
    if user_ids:
        for user in frappe.get_all(
            "User",
            filters={"name": ["in", user_ids]},
            fields=["name", "full_name", "user_image"],
            limit_page_length=0,
        ):
            user_map[user["name"]] = user

    out = []
    for row in rows:
        user = user_map.get(row.get("user")) or {}
        rating = _normalise_rating(row.get("rating"))
        out.append({
            "name": row.get("name"),
            "user": row.get("user") or "",
            "user_name": user.get("full_name") or row.get("user") or "Verified customer",
            "user_image": _img(user.get("user_image")),
            "customer": row.get("customer") or "",
            "item": row.get("item") or "",
            "website_item": row.get("website_item") or "",
            "rating": round(rating, 2),
            "rating_stars": int(round(rating)),
            "review_title": _safe_text(row.get("review_title")),
            "comment": cstr(row.get("comment") or ""),
            "verified_purchase": cint(row.get("verified_purchase")),
            "seller_response": cstr(row.get("seller_response") or ""),
            "helpful_count": cint(row.get("helpful_count")),
            "reviewer_region": _safe_text(row.get("reviewer_region")),
            "published_on": cstr(row.get("published_on") or ""),
            "creation": cstr(row.get("creation") or ""),
            "creation_iso": cstr(row.get("creation") or ""),
            "date_label": format_date(row.get("published_on") or row.get("creation")) or "",
        })
    return out


def _recalculate_item_rating(item_code: str) -> tuple[float, int]:
    if not item_code or not frappe.db.exists("DocType", "Item Review"):
        return 0.0, 0
    row = frappe.db.sql(
        """
        SELECT AVG(rating) AS average, COUNT(*) AS total
        FROM `tabItem Review`
        WHERE item = %s
        """,
        (item_code,),
        as_dict=True,
    )
    average = 0.0
    total = 0
    if row:
        total = cint(row[0].get("total"))
        average = _normalise_rating(row[0].get("average")) if total else 0.0
    if frappe.db.exists("Item", item_code):
        frappe.db.set_value(
            "Item",
            item_code,
            {
                "average_product_rating": round(average, 2),
                "total_product_reviews": total,
            },
            update_modified=False,
        )
    return round(average, 2), total


def _insert_review(item_code: str, website_item: str | None, rating: float,
                   review_title: str, review_text: str) -> dict:
    customer = require_authed_customer()
    user = frappe.session.user

    wi = None
    if website_item:
        wi = _resolve_website_item(website_item)
        if not wi:
            wi = frappe.get_doc("Website Item", website_item)
    if wi:
        item_code = item_code or wi.get("item_code")
    if not item_code or not frappe.db.exists("Item", item_code):
        frappe.throw("Product not found", frappe.DoesNotExistError)

    item = frappe.get_doc("Item", item_code)

    if wi:
        duplicate = frappe.db.exists(
            "Item Review",
            {"user": user, "website_item": wi.name},
        )
        if not duplicate:
            duplicate = frappe.db.exists(
                "Item Review",
                {"user": user, "item": item_code},
            )
    else:
        duplicate = frappe.db.exists(
            "Item Review",
            {"user": user, "item": item_code},
        )
    if duplicate:
        frappe.throw("You have already reviewed this product. Thank you!")

    rating = flt(rating)
    if rating < 1 or rating > 5:
        frappe.throw("Please choose a rating between 1 and 5 stars.")
    review_text = cstr(review_text or "").strip()
    if len(review_text) < 3:
        frappe.throw("Please write a short review before publishing.")
    review_title = _truncate(review_title, 140) or "Customer Review"

    doc = frappe.get_doc({
        "doctype": "Item Review",
        "website_item": wi.name if wi else None,
        "item": item_code,
        "user": user,
        "customer": customer,
        "company": item.get("company") or (wi.get("company") if wi else None),
        "rating": round(rating / 5.0, 4),
        "review_title": review_title,
        "comment": review_text,
        "verified_purchase": 1,
        "published_on": nowdate(),
        "helpful_count": 0,
    })
    doc.insert(ignore_permissions=True)

    average, total = _recalculate_item_rating(item_code)
    try:
        frappe.cache().delete_value("item_reviews")
    except Exception:
        pass
    frappe.db.commit()

    review = _review_rows(
        wi.name if wi else None,
        item_code,
        limit=1,
        offset=0,
        sort_by="newest",
    )
    return {
        "status": "success",
        "message": "Your review has been published.",
        "review": review[0] if review else None,
        "average_rating": average,
        "total": total,
    }


# ---------------------------------------------------------------------------
# Recommended items
# ---------------------------------------------------------------------------


def _recommended_card(row: dict) -> dict:
    price = flt(row.get("price"))
    currency = row.get("currency") or "ETB"
    route = _safe_text(row.get("website_route") or row.get("route"))
    item_code = _safe_text(row.get("item_code"))
    detail_url = ("/" + route.lstrip("/")) if route else f"/product/{quote(item_code, safe='')}"
    return {
        "website_item": row.get("website_item") or row.get("name") or "",
        "item_code": item_code,
        "item_name": row.get("web_item_name") or row.get("item_name") or item_code,
        "web_item_name": row.get("web_item_name") or "",
        "item_group": row.get("item_group") or "",
        "company_name": row.get("company_name") or row.get("company") or "",
        "company": row.get("company") or "",
        "image": _img(row.get("image") or row.get("website_image") or row.get("company_logo")),
        "website_image": _img(row.get("website_image") or row.get("image")),
        "price": price,
        "currency": currency,
        "formatted_price": f"{price:,.2f} {currency}" if price > 0 else "Price on request",
        "rating": _clamp_rating(row.get("rating")),
        "total_reviews": cint(row.get("total_reviews")),
        "stock_status": "In Stock",
        "detail_url": detail_url,
        "website_route": route,
    }


def _fetch_recommended(wi, item, limit: int = 8) -> list[dict]:
    cards: list[dict] = []
    seen: set[str] = set()

    names: list[str] = []
    codes: list[str] = []
    if wi:
        for row in wi.get("recommended_items") or []:
            name = _safe_text(row.get("website_item"))
            code = _safe_text(row.get("item_code"))
            if name:
                names.append(name)
            if code:
                codes.append(code)
            if not name and not code:
                # A row may only contain a route; resolve it below.
                route = _safe_text(row.get("route"))
                if route:
                    found = frappe.db.get_value(
                        "Website Item",
                        {"route": route.lstrip("/"), "published": 1},
                        "name",
                    )
                    if found:
                        names.append(found)

    if names or codes:
        values: dict = {}
        clauses = []
        if names:
            values["names"] = tuple(sorted(set(names)))
            clauses.append("wi.name IN %(names)s")
        if codes:
            values["codes"] = tuple(sorted(set(codes)))
            clauses.append("wi.item_code IN %(codes)s")
        rows = frappe.db.sql(
            f"""
            SELECT
                wi.name AS website_item, wi.route AS website_route, wi.web_item_name,
                wi.item_code, wi.item_group, wi.website_image,
                it.item_name, it.company, it.image, it.average_product_rating AS rating,
                it.total_product_reviews, it.standard_rate,
                COALESCE(ip.price_list_rate, it.standard_rate, 0) AS price,
                ip.currency, c.company_name, c.company_logo
            FROM `tabWebsite Item` wi
            JOIN `tabItem` it ON it.name = wi.item_code
            LEFT JOIN (
                SELECT item_code, MAX(price_list_rate) AS price_list_rate,
                       MAX(currency) AS currency
                FROM `tabItem Price`
                WHERE selling = 1 AND price_list = 'Standard Selling'
                GROUP BY item_code
            ) ip ON ip.item_code = it.name
            LEFT JOIN `tabCompany` c ON c.name = it.company
            WHERE wi.published = 1 AND ({" OR ".join(clauses)})
            ORDER BY wi.ranking DESC, wi.modified DESC
            LIMIT %(limit)s
            """,
            {**values, "limit": max(limit * 2, 12)},
            as_dict=True,
        )
        for row in rows:
            card = _recommended_card(row)
            if card["item_code"] and card["item_code"] != (item.get("name") if item else ""):
                key = card["website_item"] or card["item_code"]
                if key not in seen:
                    seen.add(key)
                    cards.append(card)
            if len(cards) >= limit:
                break

    if len(cards) < limit and item:
        category = (wi.get("item_group") if wi else "") or item.get("item_group") or ""
        fallback = search_products(category=category, limit=limit * 2, page=1)
        for card in fallback.get("items") or []:
            if card.get("item_code") == item.get("name"):
                continue
            key = card.get("website_item") or card.get("item_code")
            if key and key not in seen:
                seen.add(key)
                cards.append(card)
            if len(cards) >= limit:
                break

    return cards[:limit]


# ---------------------------------------------------------------------------
# Single item dossier
# ---------------------------------------------------------------------------


def get_website_item_detail(identifier):
    """Return a rich product dossier for a Website Item, route or Item code."""
    wi = _resolve_website_item(identifier)
    item = None

    if wi:
        if wi.get("item_code") and frappe.db.exists("Item", wi.get("item_code")):
            item = frappe.get_doc("Item", wi.get("item_code"))
    else:
        if not frappe.db.exists("Item", identifier):
            return None
        item = frappe.get_doc("Item", identifier)
        wi_name = frappe.db.get_value("Website Item", {"item_code": item.name}, "name")
        if wi_name:
            wi = frappe.get_doc("Website Item", wi_name)

    if not wi and not item:
        return None

    item_code = (item.get("name") if item else "") or (wi.get("item_code") if wi else "")
    item_name = (
        (wi.get("web_item_name") if wi else "")
        or (wi.get("item_name") if wi else "")
        or (item.get("item_name") if item else "")
        or item_code
    )
    company_name = (item.get("company") if item else "") or (wi.get("company") if wi else "")
    company_info = _company_info(company_name)
    price, currency = _item_price(item_code, company_name)
    stock_status, stock_qty = _stock_status(
        item,
        wi.get("website_warehouse") if wi else None,
        wi.get("on_backorder") if wi else 0,
    )

    description_html = _first_nonempty(
        wi.get("web_long_description") if wi else "",
        wi.get("description") if wi else "",
        item.get("description") if item else "",
    )
    description_text = _plain(description_html)
    short_description = _first_nonempty(
        wi.get("short_description") if wi else "",
        _truncate(description_text, 220),
    )
    website_content = cstr(wi.get("website_content") or "") if wi else ""

    item_group = (
        (wi.get("item_group") if wi else "")
        or (item.get("item_group") if item else "")
        or "Products"
    )
    uom = (wi.get("stock_uom") if wi else "") or (item.get("stock_uom") if item else "")
    brand = (wi.get("brand") if wi else "") or (item.get("brand") if item else "")
    route = _safe_text(wi.get("route") if wi else "")
    detail_url = ("/" + route.lstrip("/")) if route else f"/product/{quote(item_code, safe='')}"

    gallery = _build_gallery(wi, item)
    specs = _build_specs(wi, item, company_info, stock_status, price, currency)
    tabs = _build_tabs(wi, description_html, website_content)
    offers = _build_offers(wi)
    highlights = _build_highlights(item, wi, company_info, item_group, uom)
    reviews = _review_rows(wi.name if wi else None, item_code, limit=50, sort_by="newest")
    review_summary = _review_summary(*_review_where(wi.name if wi else None, item_code))
    recommended = _fetch_recommended(wi, item)

    rating = review_summary.get("average") or 0.0
    total_reviews = review_summary.get("total") or 0

    breadcrumbs = [
        {"name": "Home", "route": "/"},
        {"name": "Dikka Shop", "route": "/shop"},
    ]
    if item_group:
        breadcrumbs.append({
            "name": item_group,
            "route": "/shop?category=" + quote(item_group, safe=""),
        })
    breadcrumbs.append({"name": item_name, "route": detail_url})

    meta_title = f"{item_name} — Dikka Shop | EthioBiz.ET"
    meta_description = _truncate(
        _plain(short_description or description_text) or
        f"Shop {item_name} from {company_info.get('company_name') or company_name or 'a verified seller'} "
        f"on Dikka Shop, Ethiopia's connected marketplace.",
        160,
    )

    return {
        "website_item": wi.get("name") if wi else "",
        "website_route": route,
        "is_published": 1 if wi and cint(wi.get("published")) else 0,
        "source": "website_item" if wi else "item",
        "item_code": item_code,
        "item_name": item_name,
        "web_item_name": (wi.get("web_item_name") if wi else "") or "",
        "item_group": item_group,
        "brand": brand or "",
        "uom": uom or "",
        "description": description_html,
        "description_text": description_text,
        "short_description": short_description,
        "website_content": website_content,
        "gallery": gallery,
        "specs": specs,
        "tabs": tabs,
        "offers": offers,
        "highlights": highlights,
        "recommended": recommended,
        "reviews": reviews,
        "review_summary": review_summary,
        "rating": round(flt(rating), 2),
        "total_reviews": total_reviews,
        "price": price,
        "currency": currency,
        "formatted_price": f"{price:,.2f} {currency}" if price > 0 else "Price on request",
        "stock_status": stock_status,
        "stock_qty": stock_qty,
        "in_stock": 1 if stock_status in ("In Stock", "Available on backorder") else 0,
        "on_backorder": cint(wi.get("on_backorder")) if wi else 0,
        "website_warehouse": (wi.get("website_warehouse") if wi else "") or "",
        "video_url": (item.get("product_video_url") if item else "") or "",
        "detail_url": detail_url,
        "canonical_url": get_url() + detail_url,
        "breadcrumbs": breadcrumbs,
        "meta_title": meta_title,
        "meta_description": meta_description,
        **company_info,
        "company": company_info.get("company") or company_name,
        "company_name": company_info.get("company_name") or company_name,
        "storefront_url": "/shop?company=" + quote(company_info.get("company_name") or company_name or "", safe=""),
        "share_title": f"{item_name} — Dikka Shop",
    }


# ---------------------------------------------------------------------------
# Shop listing
# ---------------------------------------------------------------------------


def search_products(query="", category=None, company=None, region=None,
                    min_price=None, max_price=None, min_rating=None,
                    sort_by="relevance", page=1, limit=LISTING_LIMIT_DEFAULT,
                    view_mode="grid", **kwargs):
    """Search published Website Items, mirroring /all-products."""
    page = max(1, cint(page) or 1)
    limit = max(1, min(cint(limit) or LISTING_LIMIT_DEFAULT, LISTING_LIMIT_MAX))
    offset = (page - 1) * limit

    where, values = _listing_where(
        query=query or "",
        category=category,
        company=company,
        region=region,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
    )

    order = {
        "price_low_high": "price ASC, wi.ranking DESC, wi.modified DESC",
        "price_high_low": "price DESC, wi.ranking DESC, wi.modified DESC",
        "rating": "rating DESC, it.total_product_reviews DESC, wi.modified DESC",
        "newest": "wi.creation DESC",
        "best_seller": "it.total_product_reviews DESC, wi.ranking DESC, wi.modified DESC",
        "featured": "wi.ranking DESC, wi.modified DESC",
        "relevance": "wi.ranking DESC, wi.modified DESC",
    }.get(cstr(sort_by or "relevance"), "wi.ranking DESC, wi.modified DESC")

    from_sql = _listing_from_sql()
    total = cint(frappe.db.sql(
        f"SELECT COUNT(DISTINCT wi.name) {from_sql} WHERE {where}",
        values,
    )[0][0])

    rows = frappe.db.sql(
        f"""
        SELECT
            wi.name AS website_item,
            wi.route AS website_route,
            wi.web_item_name,
            wi.item_code,
            wi.item_name AS website_item_name,
            COALESCE(NULLIF(wi.web_item_name, ''), NULLIF(wi.item_name, ''), it.item_name) AS item_name,
            wi.item_group,
            it.item_group AS item_group_raw,
            it.company,
            COALESCE(NULLIF(wi.short_description, ''), it.description) AS short_description,
            COALESCE(NULLIF(wi.web_long_description, ''), NULLIF(wi.description, ''), it.description) AS description,
            COALESCE(NULLIF(wi.website_image, ''), it.image) AS image,
            wi.website_image,
            COALESCE(NULLIF(wi.brand, ''), it.brand) AS brand,
            it.product_video_url,
            COALESCE(it.average_product_rating, 0.0) AS rating,
            COALESCE(it.total_product_reviews, 0) AS total_reviews,
            COALESCE(ip.price_list_rate, it.standard_rate, 0.0) AS price,
            ip.currency AS currency,
            c.company_name,
            c.company_logo,
            c.company_slug,
            c.latitude AS seller_lat,
            c.longitude AS seller_lng,
            c.location_address AS seller_address,
            wi.ranking,
            wi.on_backorder,
            wi.website_warehouse,
            wi.stock_uom,
            it.is_stock_item,
            it.stock_uom AS item_stock_uom
        {from_sql}
        WHERE {where}
        ORDER BY {order}
        LIMIT %(limit)s OFFSET %(offset)s
        """,
        {**values, "limit": limit, "offset": offset},
        as_dict=True,
    )

    by_warehouse, totals = _stock_map(rows)
    items = []
    for row in rows:
        code = row.get("item_code") or ""
        website_warehouse = row.get("website_warehouse") or ""
        is_stock_item = cint(row.get("is_stock_item"))
        if cint(row.get("on_backorder")):
            stock_status = "Available on backorder"
            stock_qty = 0.0
        elif not is_stock_item:
            stock_status = "In Stock"
            stock_qty = 0.0
        elif website_warehouse:
            stock_qty = by_warehouse.get((code, website_warehouse), 0.0)
            stock_status = "In Stock" if stock_qty > 0 else "Out of Stock"
        else:
            stock_qty = totals.get(code, 0.0)
            stock_status = "In Stock"

        price = flt(row.get("price"))
        currency = row.get("currency") or "ETB"
        route = _safe_text(row.get("website_route"))
        detail_url = ("/" + route.lstrip("/")) if route else f"/product/{quote(code, safe='')}"
        description = _plain(row.get("description"))
        short_description = _plain(row.get("short_description")) or _truncate(description, 180)

        items.append({
            "website_item": row.get("website_item") or "",
            "website_route": route,
            "item_code": code,
            "item_name": row.get("item_name") or row.get("web_item_name") or code,
            "web_item_name": row.get("web_item_name") or "",
            "item_name_raw": row.get("website_item_name") or "",
            "item_group": row.get("item_group") or row.get("item_group_raw") or "Products",
            "company": row.get("company") or "",
            "company_name": row.get("company_name") or row.get("company") or "",
            "company_logo": _img(row.get("company_logo")),
            "company_slug": row.get("company_slug") or "",
            "seller_lat": row.get("seller_lat"),
            "seller_lng": row.get("seller_lng"),
            "seller_address": row.get("seller_address") or "",
            "image": _img(row.get("image") or row.get("company_logo")),
            "website_image": _img(row.get("website_image") or row.get("image")),
            "brand": row.get("brand") or "",
            "description": description,
            "short_description": short_description,
            "price": price,
            "currency": currency,
            "formatted_price": f"{price:,.2f} {currency}" if price > 0 else "Price on request",
            "rating": _clamp_rating(row.get("rating")),
            "total_reviews": cint(row.get("total_reviews")),
            "stock_status": stock_status,
            "stock_qty": stock_qty,
            "in_stock": 1 if stock_status in ("In Stock", "Available on backorder") else 0,
            "uom": row.get("stock_uom") or row.get("item_stock_uom") or "",
            "detail_url": detail_url,
            "product_url": detail_url,
            "is_published": 1,
            "source": "website_item",
            "ranking": cint(row.get("ranking")),
            "on_backorder": cint(row.get("on_backorder")),
            "website_warehouse": website_warehouse,
        })

    categories_matched = []
    if query:
        categories_matched = frappe.db.sql(
            """
            SELECT name, name AS item_group, item_group_name
            FROM `tabItem Group`
            WHERE name LIKE %(q)s OR item_group_name LIKE %(q)s
            ORDER BY lft ASC
            LIMIT 6
            """,
            {"q": f"%{query.strip()}%"},
            as_dict=True,
        )

    companies_matched = []
    if query:
        companies_matched = frappe.db.sql(
            """
            SELECT name, name AS company, company_name, company_logo
            FROM `tabCompany`
            WHERE company_name LIKE %(q)s OR name LIKE %(q)s
            ORDER BY company_name ASC
            LIMIT 4
            """,
            {"q": f"%{query.strip()}%"},
            as_dict=True,
        )
        for row in companies_matched:
            row["company_logo"] = _img(row.get("company_logo"))

    return {
        "status": "success",
        "items": items,
        "categories_matched": categories_matched,
        "companies_matched": companies_matched,
        "query": query or "",
        "sort_by": sort_by,
        "view_mode": view_mode,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": math.ceil(total / limit) if limit else 1,
        "has_more": offset + len(items) < total,
    }


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


def get_categories(parent=None):
    values = _listing_values()
    values["parent"] = parent or ""
    values["excluded_groups"] = list(EXCLUDED_GROUPS)

    rows = frappe.db.sql(
        """
        SELECT *
        FROM (
            SELECT
                ig.name AS item_group,
                ig.item_group_name,
                ig.parent_item_group,
                ig.is_group,
                ig.image,
                (
                    SELECT COUNT(DISTINCT wi.name)
                    FROM `tabWebsite Item` wi
                    JOIN `tabItem` it ON it.name = wi.item_code
                    WHERE wi.published = 1
                      AND it.disabled = 0
                      AND it.has_variants = 0
                      AND (it.is_sales_item = 1 OR it.is_stock_item = 1)
                      AND (
                          wi.item_group = ig.name
                          OR wi.item_group IN (
                              SELECT child.name FROM `tabItem Group` child
                              WHERE child.parent_item_group = ig.name
                          )
                      )
                      AND wi.item_group NOT IN %(excluded_groups)s
                      AND wi.item_group NOT REGEXP %(test_group_regex)s
                      AND wi.web_item_name NOT REGEXP %(test_name_regex)s
                      AND it.item_group NOT REGEXP %(test_group_regex)s
                      AND it.item_code NOT LIKE 'E2E-%%'
                ) AS product_count
            FROM `tabItem Group` ig
            WHERE ig.name != 'All Item Groups'
              AND (%(parent)s = '' OR ig.parent_item_group = %(parent)s)
        ) AS categories
        WHERE categories.product_count > 0
        ORDER BY categories.product_count DESC, categories.item_group_name ASC
        """,
        values,
        as_dict=True,
    )

    out = []
    for row in rows:
        group = row.get("item_group") or ""
        if not group:
            continue
        if group in EXCLUDED_GROUPS:
            continue
        if any(token in group.lower() for token in ("test", "demo", "sample")):
            continue
        out.append({
            "item_group": group,
            "item_group_name": row.get("item_group_name") or group,
            "parent_item_group": row.get("parent_item_group") or "",
            "is_group": cint(row.get("is_group")),
            "image": _img(row.get("image")),
            "product_count": cint(row.get("product_count")),
        })
    return {
        "status": "success",
        "total": len(out),
        "categories": out,
    }


# ---------------------------------------------------------------------------
# Review APIs
# ---------------------------------------------------------------------------


def get_product_reviews(item_code=None, website_item=None, page=1, limit=12,
                        sort_by="newest", **kwargs):
    page = max(1, cint(page) or 1)
    limit = max(1, min(cint(limit) or 12, 50))

    wi = _resolve_website_item(website_item) if website_item else None
    if wi:
        item_code = item_code or wi.get("item_code")
        website_item_name = wi.get("name")
    else:
        website_item_name = frappe.db.get_value(
            "Website Item",
            {"item_code": item_code, "published": 1},
            "name",
        ) if item_code else None

    if not item_code or not frappe.db.exists("Item", item_code):
        frappe.throw("Product not found", frappe.DoesNotExistError)

    where, values = _review_where(website_item_name, item_code)
    total = cint(frappe.db.sql(
        f"SELECT COUNT(*) FROM `tabItem Review` ir WHERE {where}",
        values,
    )[0][0]) if frappe.db.exists("DocType", "Item Review") else 0
    summary = _review_summary(where, values)
    reviews = _review_rows(
        website_item_name,
        item_code,
        limit=limit,
        offset=(page - 1) * limit,
        sort_by=sort_by,
    )
    item_name = frappe.db.get_value("Item", item_code, "item_name") or item_code

    return {
        "status": "success",
        "item_code": item_code,
        "website_item": website_item_name or "",
        "item_name": item_name,
        "reviews": reviews,
        "average_rating": summary.get("average", 0.0),
        "total": total,
        "review_summary": summary,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if limit else 1,
        "has_more": (page * limit) < total,
    }


def submit_review(item_code=None, rating=0, review_text="", review_title="Customer Review",
                  website_item=None, **kwargs):
    return _insert_review(
        item_code=item_code,
        website_item=website_item,
        rating=rating,
        review_title=review_title,
        review_text=review_text,
    )


def mark_review_helpful(review_name):
    if frappe.session.user in (None, "", "Guest"):
        frappe.throw("Please log in to mark a review as helpful.", frappe.PermissionError)
    if not review_name or not frappe.db.exists("Item Review", review_name):
        frappe.throw("Review not found", frappe.DoesNotExistError)

    cache_key = f"dikka_review_helpful:{frappe.session.user}:{review_name}"
    cache = frappe.cache()
    try:
        if cache.get_value(cache_key):
            current = cint(frappe.db.get_value("Item Review", review_name, "helpful_count"))
            return {"status": "success", "helpful_count": current, "already_marked": True}
    except Exception:
        pass

    frappe.db.sql(
        "UPDATE `tabItem Review` SET helpful_count = COALESCE(helpful_count, 0) + 1 WHERE name=%s",
        (review_name,),
    )
    frappe.db.commit()
    try:
        cache.set_value(cache_key, 1, expires_in_sec=60 * 60 * 24 * 365)
    except Exception:
        pass
    current = cint(frappe.db.get_value("Item Review", review_name, "helpful_count"))
    return {"status": "success", "helpful_count": current, "already_marked": False}


# ---------------------------------------------------------------------------
# Context builder shared by /product and the canonical Website Item page
# ---------------------------------------------------------------------------


def build_product_context(context, identifier):
    product = get_website_item_detail(identifier)
    if not product:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    gallery = product.get("gallery") or []
    primary_image = gallery[0]["image"] if gallery else ""
    product["primary_image"] = primary_image
    product["has_gallery"] = len(gallery) > 1
    product["price_value"] = flt(product.get("price"))
    product["price_label"] = product.get("formatted_price") if flt(product.get("price")) > 0 else "Price on request"
    product["rating_stars"] = int(round(flt(product.get("rating"))))
    product["review_count_label"] = (
        "1 review" if cint(product.get("total_reviews")) == 1
        else f"{cint(product.get('total_reviews'))} reviews"
    )
    product["published_label"] = (
        "Published on Dikka Shop" if cint(product.get("is_published"))
        else "Dikka Shop listing"
    )
    product["canonical_url"] = get_url() + product.get("detail_url", "")
    product["og_image"] = primary_image

    context.product = product
    context.related = product.get("recommended") or []
    context.review_summary = product.get("review_summary") or {"average": 0.0, "total": 0, "rows": []}
    context.can_review = frappe.session.user not in (None, "", "Guest")

    request = getattr(frappe.local, "request", None)
    current_path = (
        getattr(request, "full_path", None)
        or getattr(request, "path", None)
        or product.get("detail_url")
        or "/shop"
    )
    context.login_url = "/login?redirect-to=" + quote(current_path, safe="/?=&")
    try:
        context.csrf_token = frappe.sessions.get_csrf_token()
    except Exception:
        context.csrf_token = ""

    context.title = product.get("meta_title") or f"{product.get('item_name')} — Dikka Shop | EthioBiz.ET"
    context.metatags = {
        "title": context.title,
        "description": product.get("meta_description") or "",
        "image": primary_image,
        "url": product.get("canonical_url") or "",
        "og_type": "product",
        "og_site_name": "EthioBiz.ET",
        "twitter_card": "summary_large_image",
    }
    context.parents = product.get("breadcrumbs") or []
    context.no_cache = 1
    context.show_sidebar = False
    context.body_class = ((context.get("body_class") or "") + " dikka-product-page").strip()
    context.item_code = product.get("item_code")
    context.website_item = product.get("website_item")
    context.item_group = product.get("item_group")
    return context
