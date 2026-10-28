# -*- coding: utf-8 -*-
"""
BISMALLAH AR-RAHMAN AR-RAHIM
EthioBiz Full Page Post View (/post)
Provides dedicated permalink, rich content view, author dossier,
interactive Frappe comments/likes, and vertical-specific CTAs.
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, strip_html_tags, get_datetime, pretty_date

SUPPORTED_DOCTYPES = {
    "Job Opening": {
        "title_field": "job_title",
        "desc_field": "description",
        "category_field": "designation",
        "cta_label": "Apply for Job",
        "cta_icon": "💼",
        "portal_route": "/jobs"
    },
    "Item": {
        "title_field": "item_name",
        "desc_field": "web_long_description",
        "category_field": "item_group",
        "cta_label": "Buy Now / Order",
        "cta_icon": "🛒",
        "portal_route": "/shop"
    },
    "Healthcare Practitioner": {
        "title_field": "practitioner_name",
        "desc_field": "description",
        "category_field": "practitioner_type",
        "cta_label": "Book Consultation",
        "cta_icon": "🩺",
        "portal_route": "/bizhealth"
    },
    "Property": {
        "title_field": "title",
        "desc_field": "description",
        "category_field": "property_type",
        "cta_label": "Schedule Property Tour",
        "cta_icon": "🏡",
        "portal_route": "/bizhome"
    },
    "BizService Listing": {
        "title_field": "service_name",
        "desc_field": "description",
        "category_field": "category",
        "cta_label": "Book Service",
        "cta_icon": "⚡",
        "portal_route": "/bizservices"
    },
    "Afocha Post": {
        "title_field": "content",
        "desc_field": "content",
        "category_field": "category",
        "cta_label": "Discuss on Afocha",
        "cta_icon": "💬",
        "portal_route": "/social"
    },
    "Blog Post": {
        "title_field": "title",
        "desc_field": "content",
        "category_field": "blog_category",
        "cta_label": "Explore More Articles",
        "cta_icon": "📰",
        "portal_route": "/blog"
    },
    "LMS Course": {
        "title_field": "title",
        "desc_field": "description",
        "category_field": "category",
        "cta_label": "Enroll in Course",
        "cta_icon": "🎓",
        "portal_route": "/courses"
    }
}


def get_context(context):
    context.no_cache = 1
    doctype = frappe.form_dict.get("doctype") or ""
    name = frappe.form_dict.get("name") or frappe.form_dict.get("id") or ""

    # Parse combined id if formatted as "DocType:DocName"
    if not doctype and ":" in name:
        doctype, name = name.split(":", 1)

    if not doctype or not name or not frappe.db.exists("DocType", doctype):
        context.post_found = False
        context.title = "Explore Stories & Opportunities | EthioBiz"
        _load_featured_fallback(context)
        return context

    if not frappe.db.exists(doctype, name):
        context.post_found = False
        context.title = "Story Not Found | EthioBiz"
        _load_featured_fallback(context)
        return context

    try:
        doc = frappe.get_doc(doctype, name)
    except Exception:
        context.post_found = False
        _load_featured_fallback(context)
        return context

    meta_info = SUPPORTED_DOCTYPES.get(doctype, {
        "title_field": "title",
        "desc_field": "description",
        "category_field": "category",
        "cta_label": "View Details",
        "cta_icon": "✨",
        "portal_route": "/"
    })

    # Title resolution
    raw_title = getattr(doc, meta_info["title_field"], None) or getattr(doc, "name", "Story")
    if doctype == "Afocha Post":
        raw_title = strip_html_tags(raw_title or "")[:70] + ("..." if len(strip_html_tags(raw_title or "")) > 70 else "")
    title = str(raw_title).strip()

    # Content / Body resolution
    body = getattr(doc, meta_info["desc_field"], None) or getattr(doc, "description", None) or getattr(doc, "content", "")

    # Image resolution
    image = (
        getattr(doc, "image", None)
        or getattr(doc, "website_image", None)
        or getattr(doc, "hero_image", None)
        or getattr(doc, "banner", None)
        or getattr(doc, "thumbnail", None)
    )

    # Category / Kicker
    category = getattr(doc, meta_info["category_field"], None) or doctype

    # Author / Entity
    author_name = "EthioBiz Community"
    author_avatar = "/assets/bismillah_ethiobiz/img/walta_real_logo.png"
    company_name = getattr(doc, "company", None)

    if company_name and frappe.db.exists("Company", company_name):
        comp = frappe.get_cached_value("Company", company_name, ["company_name", "company_logo"], as_dict=True)
        if comp:
            author_name = comp.company_name or company_name
            if comp.company_logo:
                author_avatar = comp.company_logo
    elif getattr(doc, "owner", None):
        user = getattr(doc, "owner")
        if user and user != "Guest":
            u_doc = frappe.get_cached_value("User", user, ["full_name", "user_image"], as_dict=True)
            if u_doc:
                author_name = u_doc.full_name or user
                if u_doc.user_image:
                    author_avatar = u_doc.user_image

    # Date
    created_dt = getattr(doc, "creation", None)
    date_str = pretty_date(created_dt) if created_dt else "Recent"

    # Engagement counts from Frappe Comment table
    likes_count = 0
    comments_count = 0
    reposts_count = 0
    user_liked = False

    try:
        counts = frappe.db.sql(
            """
            SELECT comment_type, count(name) as cnt
            FROM `tabComment`
            WHERE reference_doctype = %s AND reference_name = %s
            GROUP BY comment_type
            """,
            (doctype, name),
            as_dict=True
        )
        for r in counts:
            if r.comment_type == "Like":
                likes_count = r.cnt
            elif r.comment_type == "Comment":
                comments_count = r.cnt
            elif r.comment_type == "Shared":
                reposts_count = r.cnt

        current_user = frappe.session.user if (frappe.session and frappe.session.user != "Guest") else None
        if current_user:
            user_liked = bool(frappe.db.exists("Comment", {
                "reference_doctype": doctype,
                "reference_name": name,
                "comment_type": "Like",
                "owner": current_user
            }))
    except Exception:
        pass

    # Fetch initial comments (top 20)
    comments = []
    try:
        raw_comments = frappe.get_all(
            "Comment",
            filters={
                "reference_doctype": doctype,
                "reference_name": name,
                "comment_type": "Comment"
            },
            fields=["name", "comment_by", "content", "creation", "owner"],
            order_by="creation desc",
            limit=20
        )
        for c in raw_comments:
            c_owner = c.owner
            avatar = "/assets/bismillah_ethiobiz/img/walta_real_logo.png"
            full_name = c.comment_by or c_owner
            if c_owner and c_owner != "Guest" and frappe.db.exists("User", c_owner):
                u = frappe.get_cached_value("User", c_owner, ["full_name", "user_image"], as_dict=True)
                if u:
                    full_name = u.full_name or full_name
                    if u.user_image:
                        avatar = u.user_image
            comments.append({
                "id": c.name,
                "author": full_name,
                "avatar": avatar,
                "content": c.content,
                "time": pretty_date(c.creation)
            })
    except Exception:
        comments = []

    # Post-specific extras
    extras = {}
    if doctype == "Job Opening":
        salary = "Competitive Compensation"
        if getattr(doc, "lower_range", None) and getattr(doc, "upper_range", None):
            salary = f"{doc.lower_range:,.0f} - {doc.upper_range:,.0f} {doc.currency or 'ETB'} / {doc.salary_per or 'mo'}"
        elif getattr(doc, "lower_range", None):
            salary = f"{doc.lower_range:,.0f} {doc.currency or 'ETB'} / {doc.salary_per or 'mo'}"
        extras["Salary"] = salary
        extras["Location"] = getattr(doc, "location", "Hawassa / Addis Ababa")
        extras["Employment Type"] = getattr(doc, "employment_type", "Full Time")
    elif doctype == "Item":
        rate = getattr(doc, "standard_rate", 0)
        extras["Price"] = f"{flt(rate):,.2f} ETB" if rate else "Inquire for Price"
        extras["Item Code"] = getattr(doc, "item_code", name)
    elif doctype == "Property":
        extras["Price"] = f"{flt(getattr(doc, 'price', 0)):,.0f} ETB" if getattr(doc, "price", 0) else "Contact Agent"
        extras["Location"] = getattr(doc, "location", "Ethiopia")
        extras["Bedrooms"] = getattr(doc, "bedrooms", "N/A")

    context.post_found = True
    context.title = f"{title} | EthioBiz"
    context.post = {
        "doctype": doctype,
        "name": name,
        "title": title,
        "category": category,
        "body": body,
        "image": image,
        "author_name": author_name,
        "author_avatar": author_avatar,
        "company_name": company_name,
        "date_str": date_str,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "reposts_count": reposts_count,
        "user_liked": user_liked,
        "cta_label": meta_info["cta_label"],
        "cta_icon": meta_info["cta_icon"],
        "portal_route": meta_info["portal_route"],
        "extras": extras,
        "comments": comments
    }

    return context


def _load_featured_fallback(context):
    """Fallback feed items if specific post not found."""
    try:
        from bismillah_ethiobiz import smart_feed_api
        res = smart_feed_api.get_personalized_feed(limit=6)
        context.fallback_items = res.get("feed") or []
    except Exception:
        context.fallback_items = []
