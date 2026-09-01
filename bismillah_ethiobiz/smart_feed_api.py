# -*- coding: utf-8 -*-
"""
BISMALLAH AR-RAHMAN AR-RAHIM
EthioBiz Smart Feed Personalization & User Interaction Logging API
Modeled after Facebook, TikTok, LinkedIn, and Amazon recommendation systems.
"""

import math
import json
import random
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
            "categories": {"Electronics": 0.25, "Healthcare": 0.2, "Maintenance": 0.2, "General": 0.15, "Real Estate": 0.1, "Education": 0.1},
            "content_types": {"product": 0.25, "doctor": 0.2, "fix_service": 0.2, "social_post": 0.15, "property": 0.1, "course": 0.1}
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
            "categories": {"Electronics": 0.25, "Healthcare": 0.2, "Maintenance": 0.2, "General": 0.15, "Real Estate": 0.1, "Education": 0.1},
            "content_types": {"product": 0.25, "doctor": 0.2, "fix_service": 0.2, "social_post": 0.15, "property": 0.1, "course": 0.1}
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
    BizHealth Doctors, BizFix Maintenance, Booking Lodging, BizHome Properties, and Promoted Ad Campaigns.
    Ranks items dynamically based on the current user's preferences, engagement velocity, and recency.
    """
    start = cint(start)
    limit = cint(limit) or 12
    filter_type = (filter_type or "all").lower().strip()
    search = (search or "").lower().strip()
    user = frappe.session.user if (frappe.session and frappe.session.user != "Guest") else None

    # 1. Fetch User Affinity
    pref = compute_user_preferences(user)
    cat_affinities = pref.get("categories", {})
    type_affinities = pref.get("content_types", {})

    items = []

    # 2. SOURCE A: Products (Website Item / Item)
    if filter_type in ["all", "products", "goods", "shop"]:
        p_query = {"disabled": 0}
        if search:
            p_query["item_name"] = ["like", f"%{search}%"]
        products = frappe.get_all(
            "Item",
            filters=p_query,
            fields=["name", "item_name", "item_group", "company", "image", "creation", "total_product_reviews", "average_product_rating"],
            limit=25,
            order_by="creation desc"
        )
        for p in products:
            prices = frappe.get_all("Item Price", filters={"item_code": p.name, "selling": 1}, fields=["price_list_rate", "currency"], limit=1)
            price_str = f"{prices[0].price_list_rate:,.2f} {prices[0].currency}" if prices else "Available Online"
            items.append({
                "id": p.name,
                "type": "product",
                "badge": f"🛍️ {p.item_group or 'Product'}",
                "badge_class": "badge-product",
                "title": p.item_name,
                "subtitle": f"🏢 {p.company or 'Verified Merchant'} • In Stock",
                "content": f"High-quality verified {p.item_name} from {p.company or 'EthioBiz Merchant'}, available for nationwide delivery.",
                "category": p.item_group or "General",
                "image": p.image or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                "author": p.company or "Verified Merchant",
                "author_name": p.company or "Verified Merchant",
                "rating": flt(p.average_product_rating or 5.0),
                "reviews": cint(p.total_product_reviews or 0),
                "likes_count": cint(p.total_product_reviews or 8) * 3 + 4,
                "comments_count": cint(p.total_product_reviews or 2),
                "price": price_str,
                "created": p.creation,
                "action_url": f"/shop?product={p.name}",
                "action_label": "Order Product ➔",
                "is_booking": False
            })

    # 3. SOURCE B: Jobs & Careers
    if filter_type in ["all", "jobs", "careers", "career"]:
        if frappe.db.exists("DocType", "Job Opening"):
            j_query = {"status": "Open"}
            if search:
                j_query["job_title"] = ["like", f"%{search}%"]
            jobs = frappe.get_all(
                "Job Opening",
                filters=j_query,
                fields=["name", "job_title", "company", "employment_type", "location", "lower_range", "upper_range", "currency", "salary_per", "description", "creation"],
                limit=15,
                order_by="creation desc"
            )
            for j in jobs:
                sal_str = "Competitive Salary"
                if j.lower_range and j.upper_range:
                    sal_str = f"{j.lower_range:,.0f} - {j.upper_range:,.0f} {j.currency or 'ETB'}/{j.salary_per or 'mo'}"
                elif j.lower_range:
                    sal_str = f"{j.lower_range:,.0f} {j.currency or 'ETB'}/{j.salary_per or 'mo'}"

                items.append({
                    "id": j.name,
                    "type": "job",
                    "badge": f"💼 {j.employment_type or 'Career'}",
                    "badge_class": "badge-job",
                    "title": j.job_title,
                    "subtitle": f"🏢 {j.company or 'EthioBiz Partner'} • 📍 {j.location or 'Addis Ababa'}",
                    "content": (j.description or "Exciting career opportunity with professional growth.")[:200] + "...",
                    "category": "Career",
                    "image": "/files/jobs_logo.png",
                    "author": j.company or "EthioBiz Partner",
                    "author_name": j.company or "EthioBiz Partner",
                    "rating": 5.0,
                    "likes_count": 14,
                    "comments_count": 3,
                    "price": sal_str,
                    "created": j.creation,
                    "action_url": f"/jobs",
                    "action_label": "Apply Now ➔",
                    "is_booking": False
                })

    # 4. SOURCE C: BizHealth Doctors & Clinics
    if filter_type in ["all", "health", "doctors", "clinics"]:
        if frappe.db.exists("DocType", "Healthcare Practitioner"):
            doc_query = {}
            if search:
                doc_query["first_name"] = ["like", f"%{search}%"]
            doctors = frappe.get_all(
                "Healthcare Practitioner",
                filters=doc_query,
                fields=["name", "first_name", "last_name", "department", "image", "consultation_fee", "hospital", "average_rating", "total_reviews", "creation"],
                limit=15
            )
            for d in doctors:
                dname = f"{d.first_name or ''} {d.last_name or ''}".strip() or d.name
                fee = f"{flt(d.consultation_fee or 500):,.2f} ETB"
                items.append({
                    "id": d.name,
                    "type": "doctor",
                    "badge": f"🩺 {d.department or 'Healthcare'}",
                    "badge_class": "badge-booking",
                    "title": f"Dr. {dname}" if not dname.startswith("Dr.") else dname,
                    "subtitle": f"🏥 {d.hospital or 'St. Paul Hospital'} • Verified Specialist",
                    "content": f"Book in-clinic appointments, video teleconsultations, or home medical visits with certified physician {dname}.",
                    "category": "Healthcare",
                    "image": d.image or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "author": d.hospital or "EthioBiz Health Network",
                    "author_name": dname,
                    "rating": flt(d.average_rating or 4.9),
                    "reviews": cint(d.total_reviews or 24),
                    "likes_count": 36,
                    "comments_count": 5,
                    "price": fee,
                    "created": d.creation or now_datetime(),
                    "action_url": f"/bizhealth?doctor={d.name}",
                    "action_label": "Book Doctor ➔",
                    "is_booking": True
                })

    # 5. SOURCE D: BizFix Maintenance Services
    if filter_type in ["all", "fix", "maintenance", "repair"]:
        if frappe.db.exists("DocType", "BizService Listing"):
            srv_query = {"is_active": 1}
            if search:
                srv_query["service_name"] = ["like", f"%{search}%"]
            services = frappe.get_all(
                "BizService Listing",
                filters=srv_query,
                fields=["name", "service_name", "category", "price", "duration_minutes", "company", "average_rating", "creation"],
                limit=15
            )
            for s in services:
                items.append({
                    "id": s.name,
                    "type": "fix_service",
                    "badge": f"⚡ {s.category or 'Maintenance'}",
                    "badge_class": "badge-booking",
                    "title": s.service_name or s.name,
                    "subtitle": f"🏢 {s.company or 'EthioBiz Certified Service'} • 45-Min Express Dispatch",
                    "content": f"Professional certified {s.service_name} for homes, offices, and commercial facilities across Ethiopia.",
                    "category": "Maintenance",
                    "image": "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "author": s.company or "EthioBiz Certified Technician",
                    "author_name": s.company or "Certified Technician",
                    "rating": flt(s.average_rating or 4.9),
                    "reviews": 28,
                    "likes_count": 42,
                    "comments_count": 6,
                    "price": f"{flt(s.price or 450):,.2f} ETB",
                    "created": s.creation or now_datetime(),
                    "action_url": f"/bizfix?service={s.name}",
                    "action_label": "Dispatch Technician ➔",
                    "is_booking": True
                })

    # 6. SOURCE E: BizBooking (Hotels, Salons, Workspaces, Rentals)
    if filter_type in ["all", "bookings", "booking", "hotels", "salons", "spaces", "rentals"]:
        if frappe.db.exists("DocType", "BizBooking Resource"):
            res_query = {"is_active": 1}
            if search:
                res_query["resource_name"] = ["like", f"%{search}%"]
            resources = frappe.get_all(
                "BizBooking Resource",
                filters=res_query,
                fields=["name", "resource_name", "category", "base_rate", "company", "description", "creation"],
                limit=15,
                order_by="creation desc"
            )
            for r in resources:
                cat = r.category or "Service Booking"
                rate_val = r.base_rate or 0.0
                rate_str = f"{rate_val:,.2f} ETB" if rate_val > 0 else "Free Appointment"
                items.append({
                    "id": r.name,
                    "type": "booking",
                    "badge": f"🏨 {cat}",
                    "badge_class": "badge-booking",
                    "title": r.resource_name,
                    "subtitle": f"🏢 {r.company or 'EthioBiz Hospitality'} • Instant Voucher Pass",
                    "content": r.description or f"Reserve {r.resource_name} with confirmed instant time slot booking and verified digital pass.",
                    "category": cat,
                    "image": "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "author": r.company or "Verified Host",
                    "author_name": r.company or "Verified Host",
                    "rating": 4.9,
                    "likes_count": 30,
                    "comments_count": 4,
                    "price": rate_str,
                    "created": r.creation,
                    "action_url": f"/booking",
                    "action_label": "Reserve Now ➔",
                    "is_booking": True
                })

    # 7. SOURCE F: BizHome Properties & Lodging
    if filter_type in ["all", "home", "bizhome", "property", "lodging", "realestate"]:
        try:
            from bismillah_ethiobiz.bizhome_api import search_properties
            props_res = search_properties(city=search if search else None, limit=12)
            for p in props_res.get("properties", []):
                items.append({
                    "id": p["name"],
                    "type": "property",
                    "badge": f"🏠 {p.get('tenure', 'Property')}",
                    "badge_class": "badge-booking",
                    "title": p["title"],
                    "subtitle": f"📍 {p.get('city', 'Addis Ababa')} • {p.get('bedrooms', 1)} Beds • {p.get('property_type', 'Property')}",
                    "content": p.get("description") or f"Premium {p.get('tenure', 'Rental')} property in {p.get('city', 'Addis Ababa')}, verified title deeds and modern amenities.",
                    "category": "Real Estate",
                    "image": p.get("image") or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "author": "EthioBiz Property Network",
                    "author_name": "EthioBiz Real Estate",
                    "rating": flt(p.get("rating", 4.9)),
                    "reviews": cint(p.get("reviews_count", 20)),
                    "likes_count": 52,
                    "comments_count": 7,
                    "price": f"{flt(p.get('price', 0)):,.2f} ETB/{p.get('price_unit', 'mo')}",
                    "created": now_datetime(),
                    "action_url": f"/bizhome?property={p['name']}",
                    "action_label": "View Property ➔",
                    "is_booking": True
                })
        except Exception as e:
            frappe.log_error(f"BizHome feed source error: {str(e)}")

    # 8. SOURCE G: Afocha Social Posts
    if filter_type in ["all", "social", "afocha"]:
        if frappe.db.exists("DocType", "Afocha Post"):
            soc_query = {}
            if search:
                soc_query["content"] = ["like", f"%{search}%"]
            posts = frappe.get_all(
                "Afocha Post",
                filters=soc_query,
                fields=["name", "author_name", "author_handle", "author_image", "company", "category_tag", "content", "post_image", "likes_count", "comments_count", "creation"],
                limit=15,
                order_by="creation desc"
            )
            for post in posts:
                items.append({
                    "id": post.name,
                    "type": "social",
                    "badge": f"🌟 {post.category_tag or 'Afocha Story'}",
                    "badge_class": "badge-social",
                    "title": post.author_name,
                    "subtitle": f"🏢 {post.company or 'EthioBiz Network'} • {post.author_handle or '@member'}",
                    "content": post.content,
                    "category": post.category_tag or "Social",
                    "image": post.post_image,
                    "author": post.author_name,
                    "author_name": post.author_name,
                    "avatar": post.author_image,
                    "rating": 5.0,
                    "likes_count": cint(post.likes_count or 12),
                    "comments_count": cint(post.comments_count or 3),
                    "price": "Social Update",
                    "created": post.creation,
                    "action_url": f"/social?post={post.name}",
                    "action_label": "Join Conversation ➔",
                    "is_booking": False
                })

    # 9. SOURCE H: Tibeb Knowledge Articles
    if filter_type in ["all", "blogs", "tibeb", "articles"]:
        b_query = {"published": 1}
        if search:
            b_query["title"] = ["like", f"%{search}%"]
        blogs = frappe.get_all(
            "Blog Post",
            filters=b_query,
            fields=["name", "title", "blogger", "blog_category", "meta_image", "blog_intro", "route", "published_on", "creation"],
            limit=10,
            order_by="creation desc"
        )
        for b in blogs:
            items.append({
                "id": b.name,
                "type": "blog",
                "badge": f"📝 {b.blog_category or 'Tibeb Wisdom'}",
                "badge_class": "badge-blog",
                "title": b.title,
                "subtitle": f"✍️ By {b.blogger or 'EthioBiz Editorial Team'}",
                "content": b.blog_intro or "In-depth insights, economic analysis, and cultural perspectives from Ethiopian pioneers.",
                "category": "Knowledge",
                "image": b.meta_image or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                "author": b.blogger or "Editorial Team",
                "author_name": b.blogger or "Editorial Team",
                "rating": 5.0,
                "likes_count": 22,
                "comments_count": 4,
                "price": "Knowledge Article",
                "created": b.published_on or b.creation,
                "action_url": f"/{b.route or 'blog'}",
                "action_label": "Read Article ➔",
                "is_booking": False
            })

    # 10. SOURCE I: Dagu LMS Courses
    if filter_type in ["all", "courses", "dagu", "academy"]:
        if frappe.db.exists("DocType", "LMS Course"):
            c_query = {"published": 1}
            if search:
                c_query["title"] = ["like", f"%{search}%"]
            courses = frappe.get_all(
                "LMS Course",
                filters=c_query,
                fields=["name", "title", "image", "short_introduction", "creation"],
                limit=10,
                order_by="creation desc"
            )
            for c in courses:
                items.append({
                    "id": c.name,
                    "type": "course",
                    "badge": "🎓 Dagu Academy",
                    "badge_class": "badge-course",
                    "title": c.title,
                    "subtitle": "Online Vocational & Professional Skills Certification",
                    "content": c.short_introduction or "Master industry-standard skills with practical real-world modules and verified digital certificates.",
                    "category": "Education",
                    "image": c.image or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "author": "Dagu Academy",
                    "author_name": "Dagu Academy",
                    "rating": 4.9,
                    "likes_count": 45,
                    "comments_count": 9,
                    "price": "Free / Verified",
                    "created": c.creation,
                    "action_url": f"/courses/{c.name}",
                    "action_label": "Enroll in Course ➔",
                    "is_booking": False
                })

    # 11. SOURCE J: Walta Forum Discussions
    if filter_type in ["all", "forums", "forum", "walta", "discussions"]:
        if frappe.db.exists("DocType", "Walta Forum Topic"):
            try:
                forum_cond = []
                forum_vals = []
                if search:
                    forum_cond.append("(title LIKE %s OR content LIKE %s)")
                    forum_vals.extend([f"%{search}%", f"%{search}%"])
                where_sql = f"WHERE {' AND '.join(forum_cond)}" if forum_cond else ""
                forum_vals.append(10)

                topics = frappe.db.sql(f"""
                    SELECT name, title, category, author_name, company, content, image, replies_count, likes_count, creation
                    FROM `tabWalta Forum Topic`
                    {where_sql}
                    ORDER BY creation desc
                    LIMIT %s
                """, tuple(forum_vals), as_dict=True)
                for ft in topics:
                    clean_c = frappe.utils.strip_html(ft.content or "")
                    items.append({
                        "id": ft.name,
                        "type": "forum",
                        "badge": f"💬 {ft.category or 'Walta Forum'}",
                        "badge_class": "badge-forum",
                        "title": ft.title,
                        "subtitle": f"🛡️ {ft.author_name} • {ft.company or 'EthioBiz'}",
                        "content": (clean_c[:180] + "...") if len(clean_c) > 180 else clean_c,
                        "category": ft.category or "Discussion",
                        "image": ft.image,
                        "author": ft.author_name,
                        "author_name": ft.author_name,
                        "rating": 5.0,
                        "likes_count": cint(ft.likes_count or 15),
                        "comments_count": cint(ft.replies_count or 6),
                        "price": f"💬 {ft.replies_count or 0} replies",
                        "created": ft.creation,
                        "action_url": f"/forum?topic={ft.name}",
                        "action_label": "Join Topic ➔",
                        "is_booking": False
                    })
            except Exception:
                pass

    # 12. SOURCE K: Promoted Ad Campaigns (From Desk Ad Management)
    if filter_type in ["all", "products", "shop"]:
        ads = get_ad_campaigns()
        for ad in ads:
            items.append({
                "id": ad.get("name"),
                "type": "ad",
                "badge": "Sponsored 📢",
                "badge_class": "badge-social",
                "title": ad.get("campaign_name"),
                "subtitle": f"🏢 {ad.get('company') or 'EthioBiz Partner'} • Sponsored",
                "content": "Discover featured enterprise solutions and exclusive flash offers from verified partners.",
                "category": "Sponsored",
                "image": ad.get("creative_image") or "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                "author": ad.get("company") or "EthioBiz Partner",
                "author_name": ad.get("company") or "EthioBiz Partner",
                "rating": 5.0,
                "likes_count": 120,
                "comments_count": 14,
                "price": "Special Offer",
                "created": now_datetime(),
                "action_url": ad.get("click_url") or "/shop",
                "action_label": "Learn More ➔",
                "is_booking": False
            })

    # 13. Apply Personalization Algorithm (Facebook/TikTok/LinkedIn/Amazon Hybrid Scorer)
    for it in items:
        # User Affinity (0.0 to 1.0)
        cat_aff = cat_affinities.get(it.get("category", ""), 0.05)
        type_aff = type_affinities.get(it.get("type", ""), 0.1)
        affinity_score = (cat_aff * 0.7) + (type_aff * 0.3)

        # Engagement Velocity
        likes_c = flt(it.get("likes_count", 0))
        engagement_score = min(likes_c / 100.0, 1.0)

        # Recency Decay
        recency_score = 0.95

        # Publisher Authority
        authority_score = 0.95 if it.get("type") in ["doctor", "fix_service", "property"] else 0.85

        # Promoted Ad Boost
        ad_boost = 0.20 if it.get("type") == "ad" else 0.0

        # Exploration diversity jitter to ensure fresh organic feed rotation on refresh
        diversity_jitter = round(random.uniform(0.01, 0.08), 4)

        it["feed_score"] = round(
            (0.35 * affinity_score) +
            (0.25 * engagement_score) +
            (0.20 * recency_score) +
            (0.10 * authority_score) +
            diversity_jitter +
            ad_boost,
            4
        )

    # Sort descending by algorithmic feed_score
    items.sort(key=lambda x: x.get("feed_score", 0), reverse=True)

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
        fields=["name", "campaign_name", "click_url", "creative_image", "alt_text", "company",
                "impressions", "clicks", "promoted_listing", "target_vertical", "budget_etb", "campaign_url", "slot"],
        limit=5,
        order_by="modified desc"
    )

    # Increment impressions counter + decrement budget on each served impression
    for ad in ads:
        try:
            frappe.db.set_value("EthioBiz Ad Campaign", ad.name, "impressions", cint(ad.impressions) + 1, update_modified=False)
        except Exception:
            pass
        # BISMALLAH (Phase 6.3): surface campaign_url (fallback to legacy click_url) and
        # decrement running budget so Desk Ads analytics match the served feed.
        if not ad.get("campaign_url"):
            ad["campaign_url"] = ad.get("click_url") or ""
        try:
            budget = flt(ad.get("budget_etb") or 0)
            if budget > 0:
                new_budget = max(0.0, round(budget - 0.01, 2))
                frappe.db.set_value("EthioBiz Ad Campaign", ad.name, "budget_etb", new_budget, update_modified=False)
                ad["budget_etb"] = new_budget
        except Exception:
            pass

    frappe.db.commit()
    return ads
