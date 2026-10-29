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
        "cta_icon": "🏠",
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
        "cta_icon": "📖",
        "portal_route": "/blog"
    },
    "Walta Forum Topic": {
        "title_field": "title",
        "desc_field": "content",
        "category_field": "category",
        "cta_label": "Join Topic on Walta",
        "cta_icon": "💬",
        "portal_route": "/forum"
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

    is_forum = (doctype == "Walta Forum Topic")

    if not is_forum and (not doctype or not name or not frappe.db.exists("DocType", doctype)):
        context.post_found = False
        context.title = "Explore Stories & Opportunities | EthioBiz"
        _load_featured_fallback(context)
        return context

    if is_forum:
        topic_exists = frappe.db.sql("SELECT name FROM `tabWalta Forum Topic` WHERE name = %s", (name,))
        if not topic_exists:
            context.post_found = False
            context.title = "Discussion Not Found | EthioBiz"
            _load_featured_fallback(context)
            return context
    elif not frappe.db.exists(doctype, name):
        context.post_found = False
        context.title = "Story Not Found | EthioBiz"
        _load_featured_fallback(context)
        return context

    try:
        if is_forum:
            f_row = frappe.db.sql("""
                SELECT name, title, category, author_name, company, content, image, replies_count, likes_count, creation
                FROM `tabWalta Forum Topic` WHERE name = %s
            """, (name,), as_dict=True)
            if not f_row:
                context.post_found = False
                _load_featured_fallback(context)
                return context
            row = f_row[0]
            doc = frappe._dict(row)
            doc.doctype = "Walta Forum Topic"
        else:
            doc = frappe.get_doc(doctype, name)

        cfg = SUPPORTED_DOCTYPES.get(doctype, {
            "title_field": "title",
            "desc_field": "description",
            "category_field": "category",
            "cta_label": "View Details",
            "cta_icon": "➔",
            "portal_route": "/feed"
        })

        title = doc.get(cfg["title_field"]) or doc.get("name")
        description = doc.get(cfg["desc_field"]) or doc.get("content") or ""
        category = doc.get(cfg["category_field"]) or "Community"

        # Resolve image
        image = None
        for img_field in ["image", "item_image", "company_logo", "banner_image"]:
            if doc.get(img_field):
                image = doc.get(img_field)
                break

        # Resolve author and company
        author_name = doc.get("author_name") or doc.get("owner") or "EthioBiz Member"
        author_company = doc.get("company") or "EthioBiz Cloud Ecosystem"
        author_avatar = "/assets/frappe/images/default-avatar.png"

        # Date formatting
        creation_dt = doc.get("creation")
        time_ago = pretty_date(creation_dt) if creation_dt else "Recently"

        # Counts
        likes_count = cint(doc.get("likes_count") or 0)
        comments_count = cint(doc.get("comments_count") or doc.get("replies_count") or 0)

        # Comments fetching
        comments = []
        if is_forum:
            replies = frappe.db.sql("""
                SELECT name, reply_text as content, author_name as author, creation, company
                FROM `tabWalta Forum Reply` WHERE topic = %s ORDER BY creation asc
            """, (name,), as_dict=True) if frappe.db.table_exists("Walta Forum Reply") else []
            for r in replies:
                comments.append({
                    "author": r.author or "Community Member",
                    "content": r.content or "",
                    "time": pretty_date(r.creation) if r.creation else "Recently",
                    "avatar": "/assets/frappe/images/default-avatar.png"
                })
        else:
            frappe_comments = frappe.get_all(
                "Comment",
                filters={"reference_doctype": doctype, "reference_name": name, "comment_type": "Comment"},
                fields=["content", "comment_by", "creation"],
                order_by="creation asc",
                limit=30
            )
            for c in frappe_comments:
                comments.append({
                    "author": c.comment_by or "Verified User",
                    "content": strip_html_tags(c.content or ""),
                    "time": pretty_date(c.creation) if c.creation else "Recently",
                    "avatar": "/assets/frappe/images/default-avatar.png"
                })

        context.post_found = True
        context.doctype = doctype
        context.name = name
        context.title = f"{title} | EthioBiz"
        context.post = {
            "title": title,
            "description": description,
            "category": category,
            "image": image,
            "author_name": author_name,
            "author_company": author_company,
            "author_avatar": author_avatar,
            "time_ago": time_ago,
            "likes_count": likes_count,
            "comments_count": len(comments) if comments else comments_count,
            "comments": comments,
            "cta_label": cfg["cta_label"],
            "cta_icon": cfg["cta_icon"],
            "portal_route": cfg["portal_route"]
        }

    except Exception as e:
        frappe.log_error(f"Error loading post {doctype}:{name}: {str(e)}", "EthioBiz Post View")
        context.post_found = False
        context.title = "Post Unavailable | EthioBiz"
        _load_featured_fallback(context)

    return context


def _load_featured_fallback(context):
    context.fallback_posts = [
        {
            "title": "Empowering Ethiopian Enterprise with DOBiz Cloud ERP",
            "category": "Technology",
            "url": "/dobiz",
            "icon": "📊"
        },
        {
            "title": "Explore Local Vendors & Supermarket Finds on Magala",
            "category": "Commerce",
            "url": "/shop",
            "icon": "🛍️"
        },
        {
            "title": "Connect with Certified Health Practitioners on BizHealth",
            "category": "Healthcare",
            "url": "/bizhealth",
            "icon": "🩺"
        }
    ]
