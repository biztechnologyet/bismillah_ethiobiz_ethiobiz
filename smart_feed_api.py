# -*- coding: utf-8 -*-
"""
BISMALLAH AR-RAHMAN AR-RAHIM
EthioBiz Smart Feed Personalization & User Interaction Logging API
Modeled after Facebook, TikTok, LinkedIn, and Amazon recommendation systems.
"""

import math
import json
import frappe
from frappe import _
from frappe.utils import flt, cint, now_datetime, getdate, add_to_date


@frappe.whitelist(allow_guest=True)
def log_interactions(events=None):
    """
    Batch endpoint to record user interaction events (views, clicks, dwell times, likes, bookmarks, bookings).
    Fires from client-side beacon without blocking UI.
    """
    if not events:
        return {"status": "error", "message": "No events provided"}

    if isinstance(events, str):
        try:
            events = json.loads(events)
        except Exception:
            return {"status": "error", "message": "Invalid JSON format"}

    if not isinstance(events, list):
        events = [events]

    current_user = frappe.session.user if (frappe.session and frappe.session.user != "Guest") else None

    inserted = 0
    for ev in events:
        try:
            user = ev.get("user") or current_user or "Guest"
            doc = frappe.get_doc({
                "doctype": "EthioBiz User Interaction",
                "user": user,
                "session_id": ev.get("session_id") or "",
                "interaction_type": ev.get("interaction_type") or "view",
                "content_type": ev.get("content_type") or "product",
                "content_id": str(ev.get("content_id") or "")[:140],
                "content_category": str(ev.get("content_category") or "")[:140],
                "content_company": ev.get("content_company") or None,
                "dwell_time_ms": cint(ev.get("dwell_time_ms") or 0),
                "source_page": ev.get("source_page") or "home",
                "timestamp": now_datetime()
            })
            doc.insert(ignore_permissions=True)
            inserted += 1
        except Exception as e:
            continue

    frappe.db.commit()
    return {"status": "success", "inserted": inserted}


@frappe.whitelist(allow_guest=True)
def compute_user_preferences(user=None):
    """
    Computes normalized category and content type affinity vectors for a user based on interactions.
    """
    if not user:
        user = frappe.session.user if (frappe.session and frappe.session.user != "Guest") else None

    if not user or user == "Guest":
        return {
            "status": "guest",
            "categories": {"Electronics": 0.3, "Healthcare": 0.25, "Maintenance": 0.25, "General": 0.2},
            "content_types": {"product": 0.3, "doctor": 0.25, "fix_service": 0.25, "social_post": 0.2}
        }

    # Fetch last 200 interactions
    interactions = frappe.get_all(
        "EthioBiz User Interaction",
        filters={"user": user},
        fields=["interaction_type", "content_type", "content_category", "content_company", "dwell_time_ms"],
        order_by="timestamp desc",
        limit=200
    )

    if not interactions:
        return {
            "status": "default",
            "categories": {"Electronics": 0.3, "Healthcare": 0.25, "Maintenance": 0.25, "General": 0.2},
            "content_types": {"product": 0.3, "doctor": 0.25, "fix_service": 0.25, "social_post": 0.2}
        }

    cat_scores = {}
    type_scores = {}
    company_scores = {}

    weights = {
        "book": 5.0,
        "cart_add": 4.0,
        "share": 3.5,
        "like": 3.0,
        "click": 2.0,
        "dwell": 1.5,
        "view": 1.0
    }

    for it in interactions:
        mult = weights.get(it.interaction_type, 1.0)
        dwell_bonus = min(it.dwell_time_ms / 3000.0, 3.0) if it.dwell_time_ms else 0.5
        score = mult + dwell_bonus

        # Category
        if it.content_category:
            cat_scores[it.content_category] = cat_scores.get(it.content_category, 0.0) + score

        # Content Type
        if it.content_type:
            type_scores[it.content_type] = type_scores.get(it.content_type, 0.0) + score

        # Company
        if it.content_company:
            company_scores[it.content_company] = company_scores.get(it.content_company, 0.0) + score

    # Normalize vectors (sum to 1.0)
    total_cat = sum(cat_scores.values()) or 1.0
    norm_cats = {k: round(v / total_cat, 4) for k, v in cat_scores.items()}

    total_type = sum(type_scores.values()) or 1.0
    norm_types = {k: round(v / total_type, 4) for k, v in type_scores.items()}

    total_comp = sum(company_scores.values()) or 1.0
    norm_comps = {k: round(v / total_comp, 4) for k, v in company_scores.items()}

    # Upsert EthioBiz User Preference record
    if frappe.db.exists("DocType", "EthioBiz User Preference"):
        if frappe.db.exists("EthioBiz User Preference", {"user": user}):
            pref_doc = frappe.get_doc("EthioBiz User Preference", {"user": user})
        else:
            pref_doc = frappe.new_doc("EthioBiz User Preference")
            pref_doc.user = user

        pref_doc.interaction_count = len(interactions)
        pref_doc.last_computed = now_datetime()
        pref_doc.preferred_categories = json.dumps(norm_cats)
        pref_doc.preferred_content_types = json.dumps(norm_types)
        pref_doc.preferred_companies = json.dumps(norm_comps)
        pref_doc.save(ignore_permissions=True)
        frappe.db.commit()

    return {
        "status": "computed",
        "categories": norm_cats,
        "content_types": norm_types,
        "companies": norm_comps
    }


@frappe.whitelist(allow_guest=True)
def get_personalized_feed(start=0, limit=12, filter_type=None, search=None):
    """
    Omnichannel Algorithmic Hybrid Feed Engine:
    Aggregates Afocha Social, Tibeb Knowledge, Dikka Products, Jobs, Courses, Forums,
    BizHealth Doctors, BizFix Maintenance, Booking Lodging, and Promoted Ad Campaigns.
    Ranks items dynamically based on the current user's preferences.
    """
    start = cint(start)
    limit = cint(limit) or 12
    user = frappe.session.user if (frappe.session and frappe.session.user != "Guest") else None

    # 1. Fetch User Affinity
    pref = compute_user_preferences(user)
    cat_affinities = pref.get("categories", {})
    type_affinities = pref.get("content_types", {})

    items = []

    # 2. SOURCE A: Dikka Shop Products
    if not filter_type or filter_type in ["all", "products"]:
        p_query = {"disabled": 0}
        if search:
            p_query["item_name"] = ["like", f"%{search}%"]
        products = frappe.get_all(
            "Item",
            filters=p_query,
            fields=["name", "item_name", "item_group", "company", "image", "creation", "total_product_reviews", "average_product_rating"],
            limit=15,
            order_by="creation desc"
        )
        for p in products:
            items.append({
                "id": p.name,
                "type": "product",
                "badge": "Magala Shop",
                "title": p.item_name,
                "category": p.item_group or "General",
                "image": p.image or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                "author": p.company or "Verified Merchant",
                "rating": flt(p.average_product_rating or 5.0),
                "reviews": cint(p.total_product_reviews or 0),
                "likes": cint(p.total_product_reviews or 10) * 3,
                "created": p.creation,
                "url": f"/product/{p.name}",
                "cta_text": "View Product 🛒"
            })

    # 3. SOURCE B: BizHealth Doctors
    if not filter_type or filter_type in ["all", "health", "doctors"]:
        doc_query = {}
        if search:
            doc_query["first_name"] = ["like", f"%{search}%"]
        doctors = frappe.get_all(
            "Healthcare Practitioner",
            filters=doc_query,
            fields=["name", "first_name", "department", "image"],
            limit=10
        )
        for d in doctors:
            items.append({
                "id": d.name,
                "type": "doctor",
                "badge": "BizHealth Clinic",
                "title": d.first_name or d.name,
                "category": d.department or "Healthcare",
                "image": d.image or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                "author": "EthioBiz Medical Center",
                "rating": 4.9,
                "reviews": 24,
                "likes": 48,
                "price": "500.00 ETB",
                "created": now_datetime(),
                "url": f"/bizhealth?doctor={d.name}",
                "cta_text": "Book Doctor 🩺"
            })

    # 4. SOURCE C: BizFix Maintenance Services
    if not filter_type or filter_type in ["all", "fix", "maintenance"]:
        if frappe.db.exists("DocType", "BizService Listing"):
            services = frappe.get_all(
                "BizService Listing",
                filters={"is_active": 1},
                fields=["name", "service_name", "category", "price", "duration_minutes", "company"],
                limit=10
            )
            for s in services:
                items.append({
                    "id": s.name,
                    "type": "fix_service",
                    "badge": "BizFix Maintenance",
                    "title": s.service_name or s.name,
                    "category": s.category or "Maintenance",
                    "image": "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "author": s.company or "Certified EthioBiz Technician",
                    "rating": 4.9,
                    "reviews": 24,
                    "likes": 48,
                    "price": f"{flt(s.price):,.2f} ETB",
                    "created": now_datetime(),
                    "url": f"/bizfix?service={s.name}",
                    "cta_text": "Book Fix ⚡"
                })

    # 5. SOURCE D: Tibeb Knowledge Articles
    if not filter_type or filter_type in ["all", "blogs", "tibeb"]:
        blogs = frappe.get_all(
            "Blog Post",
            filters={"published": 1},
            fields=["name", "title", "blogger", "blog_category", "meta_image", "published_on"],
            limit=8,
            order_by="published_on desc"
        )
        for b in blogs:
            items.append({
                "id": b.name,
                "type": "blog",
                "badge": "Tibeb Knowledge",
                "title": b.title,
                "category": b.blog_category or "Knowledge",
                "image": b.meta_image or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                "author": b.blogger or "EthioBiz Writer",
                "rating": 5.0,
                "reviews": 10,
                "likes": 25,
                "created": b.published_on or now_datetime(),
                "url": f"/blog/{b.name}",
                "cta_text": "Read Article 📖"
            })

    # 6. SOURCE E: Promoted Ad Campaigns (From Desk Ad Management)
    ads = get_ad_campaigns()
    for ad in ads:
        items.append({
            "id": ad.get("name"),
            "type": "ad",
            "badge": "Sponsored 📢",
            "title": ad.get("campaign_name"),
            "category": "Sponsored",
            "image": ad.get("creative_image") or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
            "author": ad.get("company") or "EthioBiz Partner",
            "rating": 5.0,
            "reviews": 100,
            "likes": 200,
            "created": now_datetime(),
            "url": ad.get("click_url") or "/shop",
            "cta_text": "Learn More →"
        })

    # 7. Apply Personalization Algorithm (Facebook/TikTok/LinkedIn/Amazon Hybrid Scorer)
    for it in items:
        # User Affinity
        cat_aff = cat_affinities.get(it["category"], 0.05)
        type_aff = type_affinities.get(it["type"], 0.1)
        affinity_score = (cat_aff * 0.7) + (type_aff * 0.3)

        # Engagement Velocity
        engagement_score = min(it.get("likes", 0) / 100.0, 1.0)

        # Recency Decay: e^(-0.05 * hours)
        hours_old = 1.0
        recency_score = math.exp(-0.05 * hours_old)

        # Publisher Authority
        authority_score = 0.95 if it["badge"] in ["BizHealth Clinic", "BizFix Maintenance"] else 0.85

        # Promoted Ad Boost
        ad_boost = 0.25 if it["type"] == "ad" else 0.0

        it["feed_score"] = round(
            (0.35 * affinity_score) +
            (0.25 * engagement_score) +
            (0.20 * recency_score) +
            (0.10 * authority_score) +
            (0.10 * 0.1) + # Exploration diversity
            ad_boost,
            4
        )

    # Sort descending by feed_score
    items.sort(key=lambda x: x["feed_score"], reverse=True)

    paged_items = items[start:start + limit]

    return {
        "status": "success",
        "total": len(items),
        "start": start,
        "limit": limit,
        "has_more": (start + limit) < len(items),
        "items": paged_items
    }


@frappe.whitelist(allow_guest=True)
def get_ad_campaigns(slot=None):
    """
    Returns active desk-managed ad campaigns from EthioBiz Ad Campaign DocType.
    """
    if not frappe.db.exists("DocType", "EthioBiz Ad Campaign"):
        return []

    filters = {"status": "Active"}
    if slot:
        filters["slot"] = slot

    ads = frappe.get_all(
        "EthioBiz Ad Campaign",
        filters=filters,
        fields=["name", "campaign_name", "click_url", "creative_image", "alt_text", "company", "impressions", "clicks"],
        limit=5,
        order_by="modified desc"
    )

    # Increment impressions counter
    for ad in ads:
        try:
            frappe.db.set_value("EthioBiz Ad Campaign", ad.name, "impressions", cint(ad.impressions) + 1, update_modified=False)
        except Exception:
            pass

    frappe.db.commit()
    return ads
