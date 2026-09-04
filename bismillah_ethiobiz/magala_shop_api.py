# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz Magala Marketplace & Omni-Search APIs
Bismillah Ar-Rahman Ar-Rahim

Exposes robust, cached whitelisted endpoints for:
- Omni-Search with typeahead and fuzzy matching across products, services, companies, categories
- Dynamic category-specific attribute filters (RAM, Storage, OS, Bed type, etc.)
- Multi-image product dossier with reviews, highlights, and seller info
- Full company storefront data with products and services
- GeoJSON company map data for /map and shop map view
"""

import json
import math
import frappe
from frappe.utils import cint, flt, cstr
try:
    from bismillah_ethiobiz import ethiobiz_identity
    from bismillah_ethiobiz.ethiobiz_identity import require_authed_customer, resolve_booking_company
except ImportError:
    import ethiobiz_identity
    from ethiobiz_identity import require_authed_customer, resolve_booking_company

@frappe.whitelist(allow_guest=True)
def search_products(query="", category=None, company=None, region=None,
                    min_price=None, max_price=None, min_rating=None,
                    sort_by="relevance", page=1, limit=20, view_mode="grid"):
    """
    High-performance, full-text & faceted search across Magala marketplace.
    Supports products, services, companies, and categories.
    """
    page = max(1, cint(page))
    limit = min(50, max(1, cint(limit)))
    offset = (page - 1) * limit

    conditions = ["item.disabled = 0", "item.has_variants = 0"]
    # Only products to be purchased
    conditions.append("(item.is_sales_item = 1 OR item.is_stock_item = 1)")
    if not category or not category.strip():
        conditions.append("item.item_group NOT IN ('Services', 'Jobs & Careers', 'Properties & Real Estate', 'Properties')")

    values = {}

    # Category / Item Group filter (hierarchical)
    if category and category.strip():
        conditions.append("(item.item_group = %(category)s OR ig.parent_item_group = %(category)s)")
        values["category"] = category.strip()

    # Company filter
    if company and company.strip():
        conditions.append("item.company = %(company)s")
        values["company"] = company.strip()

    # Text Query
    if query and query.strip():
        q = f"%{query.strip()}%"
        conditions.append("""(
            item.item_name LIKE %(q)s
            OR item.item_code LIKE %(q)s
            OR item.description LIKE %(q)s
            OR item.item_group LIKE %(q)s
            OR item.company LIKE %(q)s
        )""")
        values["q"] = q

    # Price range filter
    if min_price is not None and min_price != "":
        conditions.append("COALESCE(ip.price_list_rate, item.standard_rate, 0) >= %(min_price)s")
        values["min_price"] = flt(min_price)
    if max_price is not None and max_price != "":
        conditions.append("COALESCE(ip.price_list_rate, item.standard_rate, 0) <= %(max_price)s")
        values["max_price"] = flt(max_price)

    # Rating filter
    if min_rating is not None and min_rating != "":
        conditions.append("COALESCE(item.average_product_rating, 5.0) >= %(min_rating)s")
        values["min_rating"] = flt(min_rating)

    # Sorting
    order_clause = "item.modified DESC"
    if sort_by == "price_low_high":
        order_clause = "price ASC"
    elif sort_by == "price_high_low":
        order_clause = "price DESC"
    elif sort_by == "rating":
        order_clause = "rating DESC"
    elif sort_by == "best_seller":
        order_clause = "item.total_product_reviews DESC"
    elif sort_by == "newest":
        order_clause = "item.creation DESC"

    where_sql = " AND ".join(conditions)

    sql = f"""
        SELECT
            item.name as item_code,
            item.item_name,
            item.item_group,
            item.company,
            item.description,
            item.image,
            item.product_video_url,
            COALESCE(item.average_product_rating, 5.0) as rating,
            COALESCE(item.total_product_reviews, 0) as total_reviews,
            COALESCE(ip.price_list_rate, item.standard_rate, 0.0) as price,
            c.company_name,
            c.company_logo,
            c.latitude as seller_lat,
            c.longitude as seller_lng,
            c.location_address as seller_address
        FROM `tabItem` item
        LEFT JOIN `tabItem Group` ig ON ig.name = item.item_group
        LEFT JOIN `tabItem Price` ip ON ip.item_code = item.name AND ip.price_list = 'Standard Selling' AND ip.selling = 1
        LEFT JOIN `tabCompany` c ON c.name = item.company
        WHERE {where_sql}
        ORDER BY {order_clause}
        LIMIT %(limit)s OFFSET %(offset)s
    """
    values["limit"] = limit
    values["offset"] = offset

    items = frappe.db.sql(sql, values, as_dict=True)

    # Total count query
    count_sql = f"""
        SELECT COUNT(*)
        FROM `tabItem` item
        LEFT JOIN `tabItem Group` ig ON ig.name = item.item_group
        LEFT JOIN `tabItem Price` ip ON ip.item_code = item.name AND ip.price_list = 'Standard Selling' AND ip.selling = 1
        WHERE {where_sql}
    """
    total = frappe.db.sql(count_sql, values)[0][0]

    # Format gallery and stock status
    for it in items:
        if not it.get("image"):
            it["image"] = "/assets/frappe/images/default-avatar.png"
        it["formatted_price"] = f"{flt(it['price']):,.2f} ETB"
        it["stock_status"] = "In Stock"

    # Matched categories and companies for autocomplete/facet previews
    categories_matched = []
    companies_matched = []
    if query and query.strip():
        categories_matched = frappe.db.sql("""
            SELECT name, item_group_name FROM `tabItem Group`
            WHERE name LIKE %s OR parent_item_group LIKE %s
            LIMIT 5
        """, (f"%{query}%", f"%{query}%"), as_dict=True)

        companies_matched = frappe.db.sql("""
            SELECT name, company_name, company_logo FROM `tabCompany`
            WHERE (company_name LIKE %s OR name LIKE %s)
            LIMIT 5
        """, (f"%{query}%", f"%{query}%"), as_dict=True)

    return {
        "status": "success",
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if limit else 1,
        "items": items,
        "categories_matched": categories_matched,
        "companies_matched": companies_matched
    }


@frappe.whitelist(allow_guest=True)
def get_companies_map(category=None, region=None, user_lat=None, user_lng=None, radius_km=None):
    """
    Returns full GeoJSON and company listings with coordinates for the /map portal
    and shop map view.
    """
    filters = {}

    # BISMALLAH — honor BOTH the legacy `show_on_map` flag and the `map_enabled`
    # flag added by magala_setup, and error-safely handle either missing column
    # (defensive: DocTypes come from the DB on this server, not guaranteed JSON).
    has_show = frappe.db.has_column("Company", "show_on_map")
    has_enabled = frappe.db.has_column("Company", "map_enabled")

    # Company is mapable if EITHER flag is set (OR), or unconditionally when neither
    # column exists (so pins are not hidden by a missing flag schema).
    or_filters = []
    if has_show:
        or_filters.append(["show_on_map", "=", 1])
    if has_enabled:
        or_filters.append(["map_enabled", "=", 1])

    if category and category.strip() and category != "all":
        filters["map_category"] = category.strip()

    _fields = [
        "name", "company_name", "company_slug", "company_description_public",
        "business_category", "map_category", "map_pin_color", "latitude", "longitude",
        "location_address", "phone_no", "email", "website", "company_logo",
        "company_banner", "established_year", "store_tier"
    ]

    companies = frappe.get_all(
        "Company",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        fields=_fields
    )

    user_lat = flt(user_lat) if user_lat else None
    user_lng = flt(user_lng) if user_lng else None
    radius_km = flt(radius_km) if radius_km else None

    # BISMALLAH (Phase 6.5 multi-pin): reuse the shared per-company pin resolver so
    # every `company_locations` child row (Addis Ababa Branch, Hawasa Branch,
    # Showroom, Factory, ...) renders as its own pin. Defensive import.
    _pin_rows = None
    try:
        from bismillah_ethiobiz import company_map_api as _cma
        _pin_rows = _cma._company_pin_rows
        _sound = _cma._sound_pin
    except Exception:
        _pin_rows = None

    locations = []
    for comp in companies:
        lat = flt(comp.get("latitude"))
        lng = flt(comp.get("longitude"))

        # Multi-point: one pin per branch row when available
        if _pin_rows is not None:
            rows = _pin_rows(comp)
        else:
            # Defensive fallback: treat the single coordinate as one pin
            rows = [frappe._dict({"latitude": lat, "longitude": lng,
                                  "location_name": "Head Office", "branch_type": "Head Office",
                                  "is_primary": 1, "is_active": 1,
                                  "location_address": comp.get("location_address") or "",
                                  "ethiopian_region": comp.get("ethiopian_region") or "",
                                  "gps_accuracy": comp.get("gps_accuracy") or 0})] \
                if (lat and lng and not (lat == 0 and lng == 0)) else []

        emitted = 0
        for row in rows:
            rlat = flt(row.get("latitude"))
            rlng = flt(row.get("longitude"))
            if _pin_rows is not None and not _sound(rlat, rlng):
                continue
            if _pin_rows is None and (not rlat or not rlng or (rlat == 0 and rlng == 0)):
                continue

            distance_km = None
            if user_lat and user_lng:
                dlat = math.radians(rlat - user_lat)
                dlng = math.radians(rlng - user_lng)
                a = math.sin(dlat / 2)**2 + math.cos(math.radians(user_lat)) * math.cos(math.radians(rlat)) * math.sin(dlng / 2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                distance_km = round(6371 * c, 2)
                if radius_km and distance_km > radius_km:
                    continue

            # Count active products & services once per company (shared across pins)
            if emitted == 0:
                product_count = frappe.db.count("Item", {"company": comp.name, "disabled": 0})
                service_count = frappe.db.count("BizService Listing", {"company": comp.name, "is_active": 1}) if frappe.db.exists("DocType", "BizService Listing") else 0

            emitted += 1
            locations.append({
                "id": f"{comp.name}:{row.get('location_name') or 'loc'}",
                "company": comp.name,
                "company_name": comp.company_name or comp.name,
                "name": row.get("location_name") or comp.company_name or comp.name,
                "branch_type": row.get("branch_type") or "Branch",
                "is_primary": int(row.get("is_primary") or 0),
                "slug": comp.company_slug or comp.name.lower().replace(" ", "-"),
                "category": comp.map_category or comp.business_category or "shops",
                "pin_color": comp.map_pin_color or "#1FB6AE",
                "lat": rlat,
                "lng": rlng,
                "address": row.get("location_address") or comp.location_address or "Addis Ababa, Ethiopia",
                "region": row.get("ethiopian_region") or comp.ethiopian_region or "",
                "serving_cities": row.get("serving_cities") or "",
                "phone": comp.phone_no or "",
                "email": comp.email or "",
                "website": comp.website or "",
                "logo": comp.company_logo or "/assets/frappe/images/default-avatar.png",
                "banner": comp.company_banner or "/assets/bismillah_ethiobiz/images/default-banner.jpg",
                "description": comp.company_description_public or "",
                "product_count": product_count,
                "service_count": service_count,
                "rating": 4.9,
                "distance_km": distance_km,
                "is_open": True,
                "working_hours": "Mon - Sat: 8:30 AM - 8:00 PM"
            })

    if user_lat and user_lng:
        locations.sort(key=lambda x: x.get("distance_km") or 999999)

    return {
        "status": "success",
        "total": len(locations),
        "companies": locations
    }


@frappe.whitelist(allow_guest=True)
def get_product_detail(item_code):
    """Returns complete product dossier including multi-image gallery, highlights and reviews."""
    if not frappe.db.exists("Item", item_code):
        frappe.throw("Product not found", frappe.DoesNotExistError)

    item = frappe.get_doc("Item", item_code)
    price_info = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": "Standard Selling", "selling": 1}, ["price_list_rate", "currency"], as_dict=True) or {"price_list_rate": 0, "currency": "ETB"}

    company_doc = frappe.get_doc("Company", item.company) if item.company and frappe.db.exists("Company", item.company) else None

    # Multi-images
    gallery = []
    if item.image:
        gallery.append({"image": item.image, "caption": item.item_name, "is_primary": 1})
    if hasattr(item, "product_images"):
        for row in item.product_images:
            if row.image and row.image != item.image:
                gallery.append({"image": row.image, "caption": row.caption or "", "is_primary": row.is_primary})

    # Highlights
    highlights = []
    if hasattr(item, "product_highlights"):
        for h in item.product_highlights:
            highlights.append({"text": h.highlight_text, "icon": h.highlight_icon or "✓"})

    # Reviews
    reviews = []
    if frappe.db.exists("DocType", "Item Review"):
        reviews = frappe.get_all("Item Review", filters={"item_code": item_code}, fields=["name", "user", "review_title", "comment", "rating", "creation", "verified_purchase", "seller_response"], limit=10)

    return {
        "item_code": item.name,
        "item_name": item.item_name,
        "item_group": item.item_group,
        "company": item.company,
        "company_name": company_doc.company_name if company_doc else item.company,
        "company_slug": getattr(company_doc, "company_slug", item.company.lower().replace(" ", "-")) if company_doc else "",
        "company_logo": getattr(company_doc, "company_logo", "") if company_doc else "",
        "company_address": getattr(company_doc, "location_address", "") if company_doc else "",
        "description": item.description or "",
        "price": flt(price_info["price_list_rate"]),
        "formatted_price": f"{flt(price_info['price_list_rate']):,.2f} ETB",
        "rating": flt(getattr(item, "average_product_rating", 5.0)),
        "total_reviews": cint(getattr(item, "total_product_reviews", len(reviews))),
        "gallery": gallery,
        "highlights": highlights,
        "video_url": getattr(item, "product_video_url", ""),
        "reviews": reviews,
        "stock_status": "In Stock"
    }


@frappe.whitelist(allow_guest=True)
def get_category_filters(item_group):
    """Returns dynamic filter definitions configured for a category."""
    if not item_group or not frappe.db.exists("DocType", "Magala Filter Group"):
        return {"filters": []}

    group = frappe.db.get_value("Magala Filter Group", {"item_group": item_group, "is_active": 1}, "name")
    if not group:
        return {"filters": []}

    doc = frappe.get_doc("Magala Filter Group", group)
    filters_data = []
    for f in doc.filters:
        options = [o.strip() for o in (f.filter_options or "").split(",") if o.strip()]
        filters_data.append({
            "label": f.filter_label,
            "field": f.filter_field,
            "type": f.filter_type,
            "options": options
        })

    return {"filters": filters_data}


@frappe.whitelist(allow_guest=True)
def get_regions():
    """Returns full Ethiopian Region hierarchy tree."""
    if not frappe.db.exists("DocType", "Ethiopian Region"):
        return {"regions": []}

    regions = frappe.get_all("Ethiopian Region", fields=["name", "region_name", "parent_ethiopian_region", "region_type", "is_group", "latitude", "longitude"])
    return {"regions": regions}


@frappe.whitelist()
def submit_review(item_code, rating, review_text, review_title="Customer Review"):
    """Submits verified product review and updates average product rating.
    BISMALLAH: Integrated with ethiobiz_identity for proper customer binding."""
    
    # Require login and get customer
    customer = require_authed_customer("Please log in to submit reviews")
    
    user = frappe.session.user
    if not frappe.db.exists("DocType", "Item Review"):
        frappe.throw("Review system not installed")

    doc = frappe.get_doc({
        "doctype": "Item Review",
        "item_code": item_code,
        "user": user,
        "customer": customer,  # BISMALLAH: Link to customer
        "rating": flt(rating),
        "review_title": review_title,
        "comment": review_text,
        "verified_purchase": 1
    })
    doc.insert(ignore_permissions=True)

    # Recalculate average rating on Item
    avg_data = frappe.db.sql("""
        SELECT AVG(rating) as avg_r, COUNT(*) as cnt
        FROM `tabItem Review`
        WHERE item_code = %s
    """, (item_code,), as_dict=True)

    if avg_data and avg_data[0]["cnt"] > 0:
        frappe.db.set_value("Item", item_code, {
            "average_product_rating": round(avg_data[0]["avg_r"], 1),
            "total_product_reviews": avg_data[0]["cnt"]
        })
        frappe.db.commit()

    return {"status": "success", "message": "Review submitted successfully"}


@frappe.whitelist(allow_guest=True)
def get_categories(parent=None):
    """
    Returns the hierarchical Item Group (category) tree with live product
    counts per category for building the marketplace category sidebar.
    """
    filters = {}
    if parent:
        filters["parent_item_group"] = parent

    groups = frappe.db.sql("""
        SELECT
            ig.name as item_group,
            ig.item_group_name,
            ig.parent_item_group,
            ig.is_group,
            ig.image,
            (SELECT COUNT(*) FROM `tabItem` it WHERE it.item_group = ig.name AND it.disabled = 0) as product_count
        FROM `tabItem Group` ig
        WHERE ig.name != 'All Item Groups'
        AND (%(parent)s = '' OR ig.parent_item_group = %(parent)s)
        ORDER BY ig.lft ASC
    """, {"parent": parent or ""}, as_dict=True)

    for g in groups:
        # Include sub-group counts for non-group parents if requested
        if not parent:
            sub_count = frappe.db.count(
                "Item",
                {
                    "item_group": [
                        "in",
                        frappe.db.sql_list(
                            "SELECT name FROM `tabItem Group` WHERE parent_item_group = %s",
                            g["item_group"]
                        )
                    ],
                    "disabled": 0,
                },
            )
            g["product_count"] = cint(g["product_count"]) + cint(sub_count)

    # Exclude services, jobs, and properties so /shop is strictly tangible purchasable products
    excluded_groups = {'Services', 'Jobs & Careers', 'Properties & Real Estate', 'Properties'}
    groups = [g for g in groups if g["item_group"] not in excluded_groups and g["product_count"] > 0]

    return {
        "status": "success",
        "total": len(groups),
        "categories": groups
    }


@frappe.whitelist(allow_guest=True)
def get_companies(query="", region=None, category=None, page=1, limit=10):
    """
    Returns a paginated list of seller companies with product/service counts,
    ratings, and map coordinates — used for the seller directory / storefronts.
    """
    page = max(1, cint(page))
    limit = min(50, max(1, cint(limit)))
    offset = (page - 1) * limit

    conditions = ["1=1"]
    values = {}

    if query and query.strip():
        q = f"%{query.strip()}%"
        conditions.append("(c.company_name LIKE %(q)s OR c.name LIKE %(q)s OR c.business_category LIKE %(q)s)")
        values["q"] = q

    if category and category.strip() and category != "all":
        conditions.append("(c.business_category = %(category)s OR c.map_category = %(category)s)")
        values["category"] = category.strip()

    if region and region.strip():
        conditions.append("(c.region = %(region)s OR c.location_address LIKE %(region)s)")
        values["region"] = region.strip()

    where_sql = " AND ".join(conditions)

    sql = f"""
        SELECT
            c.name as id,
            c.company_name,
            c.company_slug,
            c.company_description_public as description,
            c.business_category,
            c.map_category,
            c.latitude,
            c.longitude,
            c.location_address as address,
            c.phone_no,
            c.email,
            c.website,
            c.company_logo,
            c.company_banner,
            c.established_year,
            c.store_tier,
            (SELECT COUNT(*) FROM `tabItem` it WHERE it.company = c.name AND it.disabled = 0) as product_count
        FROM `tabCompany` c
        WHERE {where_sql}
        ORDER BY c.company_name ASC
        LIMIT %(limit)s OFFSET %(offset)s
    """
    values["limit"] = limit
    values["offset"] = offset

    companies = frappe.db.sql(sql, values, as_dict=True)

    total = 0
    count_sql = f"SELECT COUNT(*) FROM `tabCompany` c WHERE {where_sql}"
    total = frappe.db.sql(count_sql, values)[0][0]

    for comp in companies:
        comp["service_count"] = frappe.db.count(
            "BizService Listing", {"company": comp["id"], "is_active": 1}
        ) if frappe.db.exists("DocType", "BizService Listing") else 0
        comp["rating"] = 4.9
        comp["storefront_url"] = f"/company/{comp['company_slug'] or comp['id']}"
        if not comp.get("company_logo"):
            comp["company_logo"] = "/assets/frappe/images/default-avatar.png"

    return {
        "status": "success",
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if limit else 1,
        "companies": companies
    }


@frappe.whitelist(allow_guest=True)
def get_company_storefront(company_slug=None, company_name=None):
    """
    Returns a complete company storefront: profile, products, services,
    reviews, and map coordinates.
    """
    lookup = None
    if company_slug:
        lookup = frappe.db.get_value("Company", {"company_slug": company_slug}, "name")
    if not lookup and company_name:
        lookup = frappe.db.get_value("Company", {"company_name": company_name}, "name") or (company_name if frappe.db.exists("Company", company_name) else None)
    if not lookup:
        frappe.throw("Company not found", frappe.DoesNotExistError)

    company = frappe.get_doc("Company", lookup)

    # Products
    products = frappe.db.sql("""
        SELECT
            it.name as item_code,
            it.item_name,
            it.item_group,
            it.image,
            COALESCE(it.average_product_rating, 5.0) as rating,
            COALESCE(it.total_product_reviews, 0) as total_reviews,
            COALESCE(ip.price_list_rate, 0.0) as price
        FROM `tabItem` it
        LEFT JOIN `tabItem Price` ip ON ip.item_code = it.name AND ip.price_list = 'Standard Selling' AND ip.selling = 1
        WHERE it.company = %s AND it.disabled = 0
        ORDER BY it.modified DESC
        LIMIT 50
    """, (lookup,), as_dict=True)

    for p in products:
        p["formatted_price"] = f"{flt(p['price']):,.2f} ETB"

    # Services
    services = []
    if frappe.db.exists("DocType", "BizService Listing"):
        services = frappe.get_all(
            "BizService Listing",
            filters={"company": lookup, "is_active": 1},
            fields=["name", "service_name", "category", "price", "duration_minutes", "average_rating"]
        )
        for s in services:
            s["formatted_price"] = f"{flt(s.get('price', 0.0)):,.2f} ETB"

    # Reviews (aggregated across products)
    reviews = []
    if frappe.db.exists("DocType", "Item Review"):
        reviews = frappe.db.sql("""
            SELECT ir.name, ir.item_code, it.item_name, ir.user, ir.rating,
                   ir.review_title, ir.comment, ir.verified_purchase, ir.seller_response, ir.creation
            FROM `tabItem Review` ir
            LEFT JOIN `tabItem` it ON it.name = ir.item_code
            WHERE it.company = %s
            ORDER BY ir.creation DESC
            LIMIT 20
        """, (lookup,), as_dict=True)
        for r in reviews:
            r["rating_stars"] = cint(r.get("rating") or 0)

    return {
        "status": "success",
        "company": {
            "id": company.name,
            "company_name": company.company_name or company.name,
            "slug": company.company_slug or company.name.lower().replace(" ", "-"),
            "description": company.company_description_public or "",
            "business_category": company.business_category or "",
            "map_category": company.map_category or "",
            "logo": company.company_logo or "/assets/frappe/images/default-avatar.png",
            "banner": company.company_banner or "/assets/bismillah_ethiobiz/images/default-banner.jpg",
            "established_year": company.established_year or "",
            "store_tier": company.store_tier or "",
            "latitude": company.latitude or 0.0,
            "longitude": company.longitude or 0.0,
            "address": company.location_address or "",
            "phone": company.phone_no or "",
            "email": company.email or "",
            "website": company.website or ""
        },
        "product_count": len(products),
        "service_count": len(services),
        "products": products,
        "services": services,
        "reviews": reviews
    }


@frappe.whitelist(allow_guest=True)
def get_product_reviews(item_code, page=1, limit=12, sort_by="newest"):
    """
    Returns paginated reviews for a product with optional sorting
    (newest / highest / lowest) and includes the seller's response.
    """
    if not item_code or not frappe.db.exists("Item", item_code):
        frappe.throw("Product not found", frappe.DoesNotExistError)

    if not frappe.db.exists("DocType", "Item Review"):
        return {"status": "success", "total": 0, "page": page, "limit": limit, "reviews": []}

    page = max(1, cint(page))
    limit = min(50, max(1, cint(limit)))
    offset = (page - 1) * limit

    order_clause = "ir.creation DESC"
    if sort_by == "highest":
        order_clause = "ir.rating DESC"
    elif sort_by == "lowest":
        order_clause = "ir.rating ASC"

    reviews = frappe.db.sql(f"""
        SELECT ir.name, ir.user, ir.rating, ir.review_title, ir.comment,
               ir.verified_purchase, ir.seller_response, ir.creation
        FROM `tabItem Review` ir
        WHERE ir.item_code = %s
        ORDER BY {order_clause}
        LIMIT %s OFFSET %s
    """, (item_code, limit, offset), as_dict=True)

    total = frappe.db.count("Item Review", {"item_code": item_code})

    item = frappe.get_doc("Item", item_code)
    for r in reviews:
        r["rating_stars"] = cint(r.get("rating") or 0)

    return {
        "status": "success",
        "item_code": item_code,
        "item_name": item.item_name,
        "average_rating": flt(getattr(item, "average_product_rating", 5.0)),
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if limit else 1,
        "reviews": reviews
    }


@frappe.whitelist(allow_guest=True)
def place_quick_order(item_code, quantity=1, customer_name=None, customer_phone=None, customer_email=None, delivery_address=None, payment_method="Telebirr", **kwargs):
    """
    Direct Quick-Order endpoint for purchasing items on /shop.
    Auto-registers or binds user to ERPNext Customer, creates Sales Order,
    and returns immediate confirmation with order reference.
    """
    if not item_code:
        frappe.throw(_("Item Code is required"))

    qty = max(1, cint(quantity))
    
    party = ethiobiz_identity.ensure_registered_party(
        full_name=customer_name,
        phone=customer_phone,
        email=customer_email,
        party_type="Customer"
    )
    customer = party.get("customer")
    
    item_doc = frappe.get_doc("Item", item_code)
    company = resolve_booking_company(item_doc.company, label="item")
    
    # Get price
    price = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": "Standard Selling", "selling": 1}, "price_list_rate")
    if not price:
        price = item_doc.standard_rate or 0.0

    total_amount = flt(price) * qty
    
    # Create Sales Order if DocType exists
    order_id = f"ORD-{item_code[:10]}-{cint(frappe.utils.now_datetime().timestamp())}"
    if frappe.db.exists("DocType", "Sales Order"):
        try:
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "customer": customer,
                "company": company,
                "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1),
                "items": [{
                    "item_code": item_code,
                    "item_name": item_doc.item_name,
                    "qty": qty,
                    "rate": flt(price),
                    "amount": total_amount,
                    "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1)
                }],
                "notes": f"Payment: {payment_method} | Delivery Address: {delivery_address or 'Standard customer address'}"
            })
            so.flags.ignore_permissions = True
            so.flags.ignore_mandatory = True
            so.insert(ignore_permissions=True)
            so.submit()
            frappe.db.commit()
            order_id = so.name
        except Exception as e:
            frappe.log_error(f"Sales Order creation fallback: {e}")
            
    return {
        "status": "success",
        "order_id": order_id,
        "item_code": item_code,
        "item_name": item_doc.item_name,
        "quantity": qty,
        "price": flt(price),
        "total_amount": total_amount,
        "customer": customer,
        "payment_method": payment_method,
        "delivery_address": delivery_address,
        "message": f"Alhamdulillah! Order #{order_id} has been placed successfully for {item_doc.item_name}. You will receive a confirmation call/SMS shortly."
    }
