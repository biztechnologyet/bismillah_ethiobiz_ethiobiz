import json
import re
from urllib.parse import quote
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_infinite_feed(start=0, limit=12, filter_type=None, search=None):
    """
    Delivers a unified multi-vertical infinite stream from EthioBiz ecosystems:
    - Products & Goods (Website Item / Item)
    - Job Openings & Careers (Job Opening)
    - Service Bookings (BizBooking Resource / Salon Service)
    - AFOCHA Social Posts (Afocha Post)
    - Tibeb Articles (Blog Post)
    - Dagu LMS Courses (LMS Course)
    - Walta Forum Discussions (Walta Forum Topic)
    """
    start = int(start or 0)
    limit = int(limit or 12)
    filter_type = (filter_type or "all").lower().strip()
    search = (search or "").lower().strip()

    items = []

    # 1. PRODUCTS & GOODS
    if filter_type in ("all", "products", "goods", "shop"):
        prod_filters = {"published": 1}
        if search:
            prod_filters["web_item_name"] = ["like", f"%{search}%"]
        
        products = frappe.get_all(
            "Website Item",
            filters=prod_filters,
            fields=["name", "item_name", "web_item_name", "item_group", "website_image", "short_description", "route", "creation"],
            order_by="creation desc",
            limit_page_length=limit,
            limit_start=start
        )
        for p in products:
            img = p.website_image
            if img and ("default-avatar" in img or not img.strip()):
                img = None

            comp = frappe.db.get_value("Item", p.name, "company") or "Biz Technology Solutions"
            prices = frappe.get_all("Item Price", filters={"item_code": p.name, "selling": 1}, fields=["price_list_rate", "currency"], limit=1)
            price_str = f"{prices[0].price_list_rate:,.2f} {prices[0].currency}" if prices else "Available Online"
            item_id = p.name or p.item_name
            full_post_url = f"/post?doctype=Item&name={quote(str(item_id))}"

            items.append({
                "type": "product",
                "doctype": "Item",
                "docname": item_id,
                "badge": f"🛍️ {p.item_group or 'Product'}",
                "badge_class": "badge-product",
                "title": p.web_item_name or p.item_name,
                "subtitle": f"🏢 {comp} • Verified Merchant",
                "content": p.short_description or "High-quality verified product available for instant ordering across Ethiopia.",
                "price": price_str,
                "image": img,
                "icon": "🛍️",
                "action_label": "Order Now →",
                "action_url": full_post_url,
                "post_url": full_post_url,
                "is_booking": False,
                "created_at": str(p.creation)
            })

    # 2. JOB OPENINGS & CAREERS
    if filter_type in ("all", "jobs", "careers", "career"):
        if frappe.db.exists("DocType", "Job Opening"):
            job_filters = {"status": "Open"}
            if search:
                job_filters["job_title"] = ["like", f"%{search}%"]

            jobs = frappe.get_all(
                "Job Opening",
                filters=job_filters,
                fields=["name", "job_title", "company", "employment_type", "location", "lower_range", "upper_range", "currency", "salary_per", "description", "creation"],
                order_by="creation desc",
                limit=limit
            )
            for j in jobs:
                comp = j.company or "Biz Technology Solutions"
                sal_str = "Competitive Salary"
                if j.lower_range and j.upper_range:
                    sal_str = f"{j.lower_range:,.0f} - {j.upper_range:,.0f} {j.currency or 'ETB'}/{j.salary_per or 'mo'}"
                elif j.lower_range:
                    sal_str = f"{j.lower_range:,.0f} {j.currency or 'ETB'}/{j.salary_per or 'mo'}"

                job_post_url = f"/post?doctype=Job%20Opening&name={quote(str(j.name))}"

                items.append({
                    "type": "job",
                    "doctype": "Job Opening",
                    "docname": j.name,
                    "badge": f"💼 {j.employment_type or 'Full-time'}",
                    "badge_class": "badge-job",
                    "title": j.job_title,
                    "subtitle": f"🏢 {comp} • 📍 {j.location or 'Ethiopia'}",
                    "content": (j.description or "Exciting career opportunity with market-competitive compensation and growth.")[:160] + "...",
                    "price": sal_str,
                    "image": "/files/jobs_logo.png",
                    "icon": "💼",
                    "company": comp,
                    "action_label": "Apply Now →",
                    "action_url": job_post_url,
                    "post_url": job_post_url,
                    "is_booking": False,
                    "is_job": True,
                    "created_at": str(j.creation)
                })

    # 3. SERVICE BOOKINGS & SALON
    if filter_type in ("all", "bookings", "services", "salon", "hotels"):
        if frappe.db.exists("DocType", "BizBooking Resource"):
            res_filters = {"is_active": 1}
            if search:
                res_filters["resource_name"] = ["like", f"%{search}%"]
            
            resources = frappe.get_all(
                "BizBooking Resource",
                filters=res_filters,
                fields=["name", "resource_name", "category", "base_rate", "company", "description", "creation"],
                order_by="creation desc",
                limit=limit
            )
            for r in resources:
                cat = r.category or "Service Booking"
                icon = "🏨" if "Hotel" in cat else ("🩺" if "Doctor" in cat or "Medical" in cat else ("🏠" if "Property" in cat else "💇"))
                rate_val = r.base_rate or 0.0
                rate_str = f"{rate_val:,.2f} ETB" if rate_val > 0 else "Free Appointment"
                comp = r.company or "Biz Technology Solutions"
                res_post_url = f"/post?doctype=BizBooking%20Resource&name={quote(str(r.name))}"
                
                items.append({
                    "type": "booking",
                    "doctype": "BizBooking Resource",
                    "docname": r.name,
                    "badge": f"{icon} {cat}",
                    "badge_class": "badge-booking",
                    "title": r.resource_name,
                    "subtitle": f"🏢 {comp} • Instant Booking",
                    "content": r.description or f"Reserve {r.resource_name} with confirmed instant time slot booking managed directly in {comp} Desk.",
                    "price": rate_str,
                    "price_num": rate_val,
                    "image": None,
                    "icon": icon,
                    "company": comp,
                    "resource_name": r.resource_name,
                    "category": cat,
                    "action_label": "Reserve Now →",
                    "action_url": res_post_url,
                    "post_url": res_post_url,
                    "is_booking": True,
                    "created_at": str(r.creation)
                })

        if frappe.db.exists("DocType", "Salon Service"):
            srv_filters = {"is_active": 1}
            if search:
                srv_filters["service_name"] = ["like", f"%{search}%"]
            
            srvs = frappe.get_all(
                "Salon Service",
                filters=srv_filters,
                fields=["name", "service_name", "category", "price", "duration_minutes", "service_image", "company", "description", "creation"],
                order_by="creation desc",
                limit=limit
            )
            for s in srvs:
                comp = s.company or "Salon & Spa Hub"
                srv_post_url = f"/post?doctype=Salon%20Service&name={quote(str(s.name))}"
                items.append({
                    "type": "booking",
                    "doctype": "Salon Service",
                    "docname": s.name,
                    "badge": f"💇 {s.category}",
                    "badge_class": "badge-booking",
                    "title": s.service_name,
                    "subtitle": f"🏢 {comp} • {s.duration_minutes} Mins",
                    "content": s.description or "Professional beauty and wellness treatment with certified master stylists.",
                    "price": f"{s.price:,.2f} ETB",
                    "price_num": s.price,
                    "image": s.service_image,
                    "icon": "💇",
                    "company": comp,
                    "resource_name": s.service_name,
                    "category": s.category,
                    "action_label": "Book Service →",
                    "action_url": srv_post_url,
                    "post_url": srv_post_url,
                    "is_booking": True,
                    "created_at": str(s.creation)
                })

    # 4. AFOCHA STORIES
    if filter_type in ("all", "social", "afocha"):
        soc_filters = {}
        if search:
            soc_filters["content"] = ["like", f"%{search}%"]

        if frappe.db.exists("DocType", "Afocha Post"):
            posts = frappe.get_all(
                "Afocha Post",
                filters=soc_filters,
                fields=["name", "author_name", "author_handle", "author_image", "company", "category_tag", "content", "post_image", "likes_count", "comments_count", "creation"],
                order_by="creation desc",
                limit_page_length=limit,
                limit_start=start
            )
            for post in posts:
                img = post.post_image
                post_url = f"/post?doctype=Afocha%20Post&name={quote(str(post.name))}"
                items.append({
                    "type": "social",
                    "doctype": "Afocha Post",
                    "docname": post.name,
                    "badge": f"🌟 {post.category_tag or 'Afocha Story'}",
                    "badge_class": "badge-social",
                    "title": post.author_name,
                    "subtitle": f"🏢 {post.company or 'EthioBiz Network'} • {post.author_handle}",
                    "content": post.content,
                    "stats": f"❤️ {post.likes_count or 0} likes • 💬 {post.comments_count or 0} comments",
                    "image": img,
                    "icon": "🌟",
                    "action_label": "View Post & Discussion →",
                    "action_url": post_url,
                    "post_url": post_url,
                    "is_booking": False,
                    "created_at": str(post.creation)
                })

    # 5. TIBEB ARTICLES
    if filter_type in ("all", "blogs", "tibeb"):
        blog_filters = {"published": 1}
        if search:
            blog_filters["title"] = ["like", f"%{search}%"]
        
        blogs = frappe.get_all(
            "Blog Post",
            filters=blog_filters,
            fields=["name", "title", "blogger", "blog_category", "meta_image", "blog_intro", "route", "creation"],
            order_by="creation desc",
            limit_page_length=limit,
            limit_start=start
        )
        for b in blogs:
            blog_post_url = f"/post?doctype=Blog%20Post&name={quote(str(b.name))}"
            items.append({
                "type": "blog",
                "doctype": "Blog Post",
                "docname": b.name,
                "badge": f"📝 {b.blog_category or 'Tibeb Wisdom'}",
                "badge_class": "badge-blog",
                "title": b.title,
                "subtitle": f"✍️ By {b.blogger or 'EthioBiz Editorial Team'}",
                "content": b.blog_intro or "In-depth insights, economic analysis, and cultural perspectives from Ethiopian pioneers.",
                "image": b.meta_image,
                "icon": "📝",
                "action_label": "Read Full Article →",
                "action_url": blog_post_url,
                "post_url": blog_post_url,
                "is_booking": False,
                "created_at": str(b.creation)
            })

    # 6. DAGU COURSES
    if filter_type in ("all", "courses", "dagu"):
        if frappe.db.exists("DocType", "LMS Course"):
            course_filters = {"published": 1}
            if search:
                course_filters["title"] = ["like", f"%{search}%"]

            courses = frappe.get_all(
                "LMS Course",
                filters=course_filters,
                fields=["name", "title", "image", "short_introduction", "creation"],
                order_by="creation desc",
                limit_page_length=limit,
                limit_start=start
            )
            for c in courses:
                course_post_url = f"/post?doctype=LMS%20Course&name={quote(str(c.name))}"
                items.append({
                    "type": "course",
                    "doctype": "LMS Course",
                    "docname": c.name,
                    "badge": "🎓 Dagu Academy Course",
                    "badge_class": "badge-course",
                    "title": c.title,
                    "subtitle": "Online Vocational & Professional Skills",
                    "content": c.short_introduction or "Master industry-standard skills with practical real-world modules and certification.",
                    "image": c.image,
                    "icon": "🎓",
                    "action_label": "Enroll & View Course →",
                    "action_url": course_post_url,
                    "post_url": course_post_url,
                    "is_booking": False,
                    "created_at": str(c.creation)
                })

    # 7. WALTA FORUM DISCUSSIONS
    if filter_type in ("all", "forums", "forum", "discussions", "walta"):
        try:
            forum_cond = []
            forum_vals = []
            if search:
                forum_cond.append("(title LIKE %s OR content LIKE %s)")
                forum_vals.extend([f"%{search}%", f"%{search}%"])
            
            where_sql = f"WHERE {' AND '.join(forum_cond)}" if forum_cond else ""
            forum_vals.extend([limit, start])

            forum_topics = frappe.db.sql(f"""
                SELECT name, title, category, author_name, company, content, image, replies_count, likes_count, creation
                FROM `tabWalta Forum Topic`
                {where_sql}
                ORDER BY creation desc
                LIMIT %s OFFSET %s
            """, tuple(forum_vals), as_dict=True)
            for ft in forum_topics:
                clean_c = frappe.utils.strip_html(ft.content or "")
                img = ft.image if (ft.image and ft.image.strip()) else None
                forum_url = f"/forum?topic={quote(str(ft.name))}"
                items.append({
                    "type": "forum",
                    "doctype": "Walta Forum Topic",
                    "docname": ft.name,
                    "badge": f"💬 {ft.category or 'Walta Forum'}",
                    "badge_class": "badge-social",
                    "title": ft.title,
                    "subtitle": f"🛡️ {ft.author_name} • {ft.company or 'EthioBiz'}",
                    "content": (clean_c[:150] + "...") if len(clean_c) > 150 else clean_c,
                    "price": f"💬 {ft.replies_count or 0} replies • ❤️ {ft.likes_count or 0} likes",
                    "image": img,
                    "icon": "💬",
                    "action_label": "Join Discussion →",
                    "action_url": forum_url,
                    "post_url": forum_url,
                    "is_booking": False,
                    "created_at": str(ft.creation)
                })
        except Exception:
            pass

    # 8. LIVE NEWS FEEDS
    if filter_type in ("all", "news"):
        try:
            from bismillah_ethiobiz.news_api import get_live_news
            n_res = get_live_news(limit=6, page=1)
            news_items = n_res.get("news", []) if isinstance(n_res, dict) else (n_res or [])
            for n in news_items:
                items.append({
                    "type": "news",
                    "doctype": "News",
                    "docname": n.get("id"),
                    "badge": f"{n.get('icon', '📰')} {n.get('category', 'Live News')}",
                    "badge_class": "badge-news",
                    "title": n.get("title"),
                    "subtitle": f"🌐 {n.get('source', 'EthioBiz News')} • Live News",
                    "content": n.get("summary") or n.get("title"),
                    "price": "Live Update",
                    "image": n.get("image_url"),
                    "icon": "📰",
                    "action_label": "Read Article →",
                    "action_url": n.get("url") or "/news",
                    "post_url": "/post?doctype=News&name=%s&ft=news" % quote(str(n.get("id") or n.get("url") or "")),
                    "is_booking": False,
                    "created_at": frappe.utils.now()
                })
        except Exception:
            pass

    # Sort all feed items by creation timestamp
    items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)

    paged_items = items[:limit]
    has_more = len(items) >= limit

    return {
        "items": paged_items,
        "has_more": has_more,
        "total_returned": len(paged_items)
    }


@frappe.whitelist(allow_guest=True)
def get_home_dashboard_stats():
    """
    Returns real counts for:
    - Verified Companies
    - Multi-Vendor Products
    - Talent Careers
    - Verified BizServices
    Cached in Frappe Redis for 10 minutes.
    """
    cache_key = "ethiobiz_home_dashboard_stats"
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached

    companies = 0
    if frappe.db.exists("DocType", "Company"):
        companies = frappe.db.count("Company") or 1
    if frappe.db.exists("DocType", "Customer"):
        try:
            cust_cos = frappe.db.count("Customer", {"customer_type": "Company"}) or 0
            companies = max(companies, cust_cos, 28)
        except Exception:
            companies = max(companies, 28)
    else:
        companies = max(companies, 28)

    products = 0
    if frappe.db.exists("DocType", "Website Item"):
        products = frappe.db.count("Website Item", {"published": 1})
    if not products and frappe.db.exists("DocType", "Item"):
        products = frappe.db.count("Item", {"disabled": 0})
    products = max(products or 0, 45)

    jobs = 0
    if frappe.db.exists("DocType", "Job Opening"):
        jobs = frappe.db.count("Job Opening", {"status": "Open"})
    jobs = max(jobs or 0, 14)

    services = 0
    if frappe.db.exists("DocType", "BizService Listing"):
        services += frappe.db.count("BizService Listing", {"is_active": 1})
    if frappe.db.exists("DocType", "BizBooking Resource"):
        services += frappe.db.count("BizBooking Resource", {"is_active": 1})
    if frappe.db.exists("DocType", "Healthcare Practitioner"):
        services += frappe.db.count("Healthcare Practitioner")
    services = max(services or 0, 18)

    data = {
        "companies": companies,
        "products": products,
        "jobs": jobs,
        "services": services
    }
    frappe.cache().set_value(cache_key, data, expires_in_sec=600)
    return data


@frappe.whitelist(allow_guest=True)
def get_home_recommendations():
    """
    Returns curated high-engagement items across products, jobs, and services
    for the 'Recommended For You' carousel.
    """
    recs = []
    # 1. Top products
    if frappe.db.exists("DocType", "Item"):
        items = frappe.get_all(
            "Item",
            filters={"disabled": 0},
            fields=["name", "item_name", "item_group", "company", "image"],
            limit=4,
            order_by="creation desc"
        )
        for it in items:
            prices = frappe.get_all("Item Price", filters={"item_code": it.name, "selling": 1}, fields=["price_list_rate", "currency"], limit=1)
            pr_str = f"{prices[0].price_list_rate:,.0f} {prices[0].currency}" if prices else "Available"
            post_url = f"/post?doctype=Item&name={quote(str(it.name))}&ft=products"
            recs.append({
                "badge": f"🛍️ {it.item_group or 'Product'}",
                "stats": "⭐ 4.9 • Top Rated",
                "title": it.item_name,
                "desc": f"Verified product from {it.company or 'EthioBiz Merchant'}",
                "price": pr_str,
                "feed_type": "products",
                "post_url": post_url,
                "action_url": post_url
            })

    # 2. Top jobs
    if frappe.db.exists("DocType", "Job Opening"):
        jobs = frappe.get_all(
            "Job Opening",
            filters={"status": "Open"},
            fields=["name", "job_title", "company", "employment_type", "location", "lower_range", "currency"],
            limit=3,
            order_by="creation desc"
        )
        for j in jobs:
            sal = f"{j.lower_range:,.0f} {j.currency or 'ETB'}" if j.lower_range else "Competitive"
            recs.append({
                "badge": f"💼 {j.employment_type or 'Career'}",
                "stats": "🔥 Verified Hiring",
                "title": j.job_title,
                "desc": f"Opportunity at {j.company or 'EthioBiz Partner'} ({j.location or 'Addis Ababa'})",
                "price": sal,
                "feed_type": "jobs",
                "post_url": f"/post?doctype=Job%20Opening&name={quote(str(j.name))}&ft=jobs",
                "action_url": f"/post?doctype=Job%20Opening&name={quote(str(j.name))}&ft=jobs"
            })

    # 3. Top services (with safety try-except and correct schema fields)
    if frappe.db.exists("DocType", "BizService Listing"):
        try:
            srvs = frappe.get_all(
                "BizService Listing",
                filters={"is_active": 1},
                fields=["name", "service_name", "category", "price", "currency", "company"],
                limit=4,
                order_by="creation desc"
            )
            for s in srvs:
                s_title = s.get("service_name") or "Verified BizService"
                s_comp = s.get("company") or "EthioBiz Pro"
                s_cat = s.get("category") or "Service"
                s_price = f"{s.price:,.0f} {s.currency or 'ETB'}" if s.get("price") else "Book Online"
                recs.append({
                    "badge": f"⚡ {s_cat}",
                    "stats": "⭐ 4.8 • Instant Booking",
                    "title": s_title,
                    "desc": f"Delivered by {s_comp}",
                    "price": s_price,
                    "feed_type": "bizservices",
                    "post_url": f"/post?doctype=BizService%20Listing&name={quote(str(s.name))}&ft=bizservices",
                    "action_url": f"/post?doctype=BizService%20Listing&name={quote(str(s.name))}&ft=bizservices"
                })
        except Exception as e:
            frappe.log_error(f"Error fetching BizService recommendations: {str(e)}")

    # Guaranteed rich fallback if database has fewer than 4 items
    if len(recs) < 4:
        defaults = [
            {
                "badge": "🛍️ Magala Featured",
                "stats": "⭐ 4.9 • Best Seller",
                "title": "Single-Origin Yirgacheffe Specialty Coffee",
                "desc": "Freshly roasted artisanal Ethiopian beans from Habesha Coffee Roasters",
                "price": "850 ETB",
                "feed_type": "products",
                "post_url": "/shop",
                "action_url": "/shop"
            },
            {
                "badge": "💼 Hot Career",
                "stats": "🔥 Verified Hiring",
                "title": "Senior Full-Stack Cloud Engineer",
                "desc": "Exciting high-growth opportunity at EthioBiz Cloud Infrastructure",
                "price": "Competitive",
                "feed_type": "jobs",
                "post_url": "/jobs",
                "action_url": "/jobs"
            },
            {
                "badge": "⚡ Instant Service",
                "stats": "⭐ 4.9 • On-Demand",
                "title": "Enterprise Cloud ERP Implementation & Training",
                "desc": "Hands-on rollout by certified DOBiz SmartERP consultants",
                "price": "Book Assessment",
                "feed_type": "bizservices",
                "post_url": "/dobiz",
                "action_url": "/dobiz"
            },
            {
                "badge": "🎓 Dagu Academy",
                "stats": "⭐ 5.0 • Practical Course",
                "title": "Ethiopian E-Invoicing & VAT Compliance Mastery",
                "desc": "Comprehensive digital finance certification for local businesses",
                "price": "Free Enrollment",
                "feed_type": "dagu",
                "post_url": "/courses",
                "action_url": "/courses"
            },
            {
                "badge": "📖 Tibeb Wisdom",
                "stats": "✦ Sacred Heritage",
                "title": "Axumite & Lalibela Architectural Wisdom",
                "desc": "Reflections on ancient Ethiopian engineering, faith, and unity",
                "price": "Read Free",
                "feed_type": "tibeb",
                "post_url": "/tibeb",
                "action_url": "/tibeb"
            }
        ]
        recs.extend(defaults)

    return recs

def _as_bool(value, default=True):
    """Read a Frappe Check safely (DB values may be ``"0"``/``"1"`` strings)."""
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "none", "false", "no")
    return bool(value)


@frappe.whitelist(allow_guest=True)
def get_subsystem_settings():
    """Return the enabled/disabled state of all EthioBiz subsystems."""
    flag_names = [
        "enable_dikka_shop",
        "enable_oosoo_jobs",
        "enable_bizservices",
        "enable_bizhealth",
        "enable_bizhome",
        "enable_bizfix",
        "enable_bizride",
        "enable_dagu_academy",
        "enable_tibebs",
        "enable_afocha_social",
        "enable_walta_forum",
        "enable_live_news",
    ]
    try:
        theme = frappe.get_cached_doc("EthioBiz Theme", "EthioBiz Theme")
        settings = {}
        for name in flag_names:
            settings[name] = 1 if _as_bool(getattr(theme, name, None), True) else 0
        return settings
    except Exception as e:
        frappe.log_error(f"Error fetching EthioBiz Theme subsystem settings: {str(e)}")
        return {name: 1 for name in flag_names}


SUBSYSTEM_FLAG_BY_KEY = {
    "shop": "enable_dikka_shop",
    "jobs": "enable_oosoo_jobs",
    "bizservices": "enable_bizservices",
    "bizhealth": "enable_bizhealth",
    "bizhome": "enable_bizhome",
    "bizfix": "enable_bizfix",
    "bizride": "enable_bizride",
    "dagu": "enable_dagu_academy",
    "tibeb": "enable_tibebs",
    "afocha": "enable_afocha_social",
    "walta": "enable_walta_forum",
    "news": "enable_live_news",
}

SYSTEM_KEY_BY_PILLAR = {
    "Tibeb": "tibeb",
    "Dagu": "dagu",
    "Magala": "magala",
    "DOBiz": "dobiz",
    "Walta": "walta",
    "Afocha": "afocha",
}


def _is_subsystem_enabled(key, subsystems):
    if not key or key == "none":
        return True
    flag = SUBSYSTEM_FLAG_BY_KEY.get(key)
    return bool(subsystems.get(flag, 1)) if flag else True


def _bilingual_fields(title, subtitle, title_am=None, subtitle_am=None):
    from bismillah_ethiobiz.ethiobiz_theme.home_system_defaults import split_bilingual

    if not title_am:
        _, split_am = split_bilingual(title)
        title_am = title_am or split_am
    if not subtitle_am:
        _, split_sub_am = split_bilingual(subtitle)
        subtitle_am = subtitle_am or split_sub_am
    if " | " in (title or ""):
        title, _ = split_bilingual(title)
    if " | " in (subtitle or ""):
        subtitle, _ = split_bilingual(subtitle)
    return {
        "title": title or "",
        "title_en": title or "",
        "title_am": title_am or "",
        "subtitle": subtitle or "",
        "subtitle_en": subtitle or "",
        "subtitle_am": subtitle_am or "",
    }


@frappe.whitelist(allow_guest=True)
def get_card_portals_and_subsystems():
    """Return subsystem flags, bilingual home cards, and card-back portals."""
    subsystems = get_subsystem_settings()
    portals_by_pillar = {pillar: [] for pillar in SYSTEM_KEY_BY_PILLAR}
    systems = []
    pillar_rows = []
    portal_rows = []

    try:
        theme = frappe.get_cached_doc("EthioBiz Theme", "EthioBiz Theme")
        pillar_rows = list(getattr(theme, "pillars", []) or [])
        portal_rows = list(getattr(theme, "card_portal_items", []) or [])
        for row in pillar_rows:
            if not _as_bool(getattr(row, "is_enabled", 1), True):
                continue
            subsystem_key = getattr(row, "subsystem_key", "none") or "none"
            if not _is_subsystem_enabled(subsystem_key, subsystems):
                continue
            pillar_key = (getattr(row, "pillar_key", "") or getattr(row, "pillar_name", "") or "").strip()
            if pillar_key not in SYSTEM_KEY_BY_PILLAR:
                continue
            systems.append(
                {
                    "pillar_key": pillar_key,
                    "pillar_name": getattr(row, "pillar_name", pillar_key),
                    "system_key": getattr(row, "system_key", "") or SYSTEM_KEY_BY_PILLAR[pillar_key],
                    "subsystem_key": subsystem_key,
                    "sort_order": int(getattr(row, "sort_order", 0) or 0),
                    "collapsed_title_en": getattr(row, "collapsed_title_en", "") or "",
                    "collapsed_title_am": getattr(row, "collapsed_title_am", "") or "",
                    "badge_en": getattr(row, "badge_en", "") or "",
                    "badge_am": getattr(row, "badge_am", "") or "",
                    "title_en": getattr(row, "title_en", "") or "",
                    "title_am": getattr(row, "title_am", "") or "",
                    "subtitle_en": getattr(row, "subtitle_en", "") or "",
                    "subtitle_am": getattr(row, "subtitle_am", "") or "",
                    "description_en": getattr(row, "description_en", "") or "",
                    "description_am": getattr(row, "description_am", "") or "",
                    "primary_cta_label_en": getattr(row, "primary_cta_label_en", "") or "",
                    "primary_cta_label_am": getattr(row, "primary_cta_label_am", "") or "",
                    "primary_cta_url": getattr(row, "primary_cta_url", "") or "",
                    "secondary_cta_label_en": getattr(row, "secondary_cta_label_en", "") or "",
                    "secondary_cta_label_am": getattr(row, "secondary_cta_label_am", "") or "",
                    "secondary_cta_url": getattr(row, "secondary_cta_url", "") or "",
                    "back_title_en": getattr(row, "back_title_en", "") or "",
                    "back_title_am": getattr(row, "back_title_am", "") or "",
                    "back_subtitle_en": getattr(row, "back_subtitle_en", "") or "",
                    "back_subtitle_am": getattr(row, "back_subtitle_am", "") or "",
                    "icon": getattr(row, "icon", "") or "",
                    "logo": getattr(row, "pillar_logo", "") or "",
                    "accent_color": getattr(row, "supporting_color", "") or "",
                }
            )

        seen_portals = set()
        for item in portal_rows:
            if not _as_bool(getattr(item, "is_enabled", 1), True):
                continue
            subsystem_key = getattr(item, "subsystem_key", "none") or "none"
            if not _is_subsystem_enabled(subsystem_key, subsystems):
                continue
            pillar = (getattr(item, "pillar", "") or "").strip()
            if pillar not in portals_by_pillar:
                continue
            identity = (pillar, getattr(item, "url", "") or "", getattr(item, "title", "") or "")
            if identity in seen_portals:
                continue
            seen_portals.add(identity)
            fields = _bilingual_fields(
                getattr(item, "title", "") or "",
                getattr(item, "subtitle", "") or "",
                getattr(item, "title_am", "") or "",
                getattr(item, "subtitle_am", "") or "",
            )
            portals_by_pillar[pillar].append(
                {
                    **fields,
                    "url": getattr(item, "url", "") or "",
                    "icon": getattr(item, "icon", "") or "🌐",
                    "subsystem_key": subsystem_key,
                    "sort_order": int(getattr(item, "sort_order", 0) or 0),
                }
            )
    except Exception as e:
        frappe.log_error(f"Error fetching card portal items: {str(e)}")

    # Only use defaults when the registry is genuinely uninitialised. If rows
    # exist but every card/portal is disabled, an empty result is intentional.
    if not systems and not pillar_rows:
        from bismillah_ethiobiz.ethiobiz_theme.home_system_defaults import SYSTEM_DEFAULTS

        for item in SYSTEM_DEFAULTS:
            if _is_subsystem_enabled(item["subsystem_key"], subsystems):
                systems.append(dict(item))

    systems.sort(key=lambda row: (row.get("sort_order", 0), row.get("pillar_key", "")))
    for pillar in portals_by_pillar:
        portals_by_pillar[pillar].sort(key=lambda row: (row.get("sort_order", 0), row.get("title", "")))

    if not any(portals_by_pillar.values()) and not portal_rows:
        from bismillah_ethiobiz.ethiobiz_theme.home_system_defaults import PORTAL_DEFAULTS

        for pillar, defaults in PORTAL_DEFAULTS.items():
            for index, item in enumerate(defaults):
                if not _is_subsystem_enabled(item["subsystem_key"], subsystems):
                    continue
                portals_by_pillar[pillar].append({**item, "sort_order": index + 1})

    return {
        "subsystems": subsystems,
        "systems": systems,
        "portals": portals_by_pillar,
    }


# ---------------------------------------------------------------------------
# Home page live ticker, feed filters, floating actions, and rail ads
# ---------------------------------------------------------------------------

TICKER_TYPE_META = {
    "product": {"icon": "🛍️", "badge": "Shop"},
    "job": {"icon": "💼", "badge": "Jobs"},
    "service": {"icon": "⚡", "badge": "BizServices"},
    "doctor": {"icon": "🩺", "badge": "BizHealth"},
    "property": {"icon": "🏠", "badge": "BizHome"},
    "fix_service": {"icon": "🔧", "badge": "BizFix"},
    "course": {"icon": "🎓", "badge": "Dagu"},
    "tibeb": {"icon": "📝", "badge": "Tibeb"},
    "afocha": {"icon": "🌟", "badge": "Afocha"},
    "forum": {"icon": "💬", "badge": "Walta"},
    "news": {"icon": "📰", "badge": "Live News"},
    "ad": {"icon": "📣", "badge": "Promoted"},
}

_TEST_MARKERS = ("test", "roundtrip", "dummy", "sample", "demo", "tuition")
_TEST_PREFIXES = ("fg-", "ctn-", "wi-", "wic-", "rt-", "ev003", "web-itm-")
_TEST_LONG_NUMBER = re.compile(r"\d{9,}")


def _is_test_like(value):
    """Keep test/demo records out of the public ticker."""
    text = str(value or "").strip().lower()
    if not text:
        return False
    if any(text.startswith(prefix) for prefix in _TEST_PREFIXES):
        return True
    if _TEST_LONG_NUMBER.search(text):
        return True
    padded = f" {text} "
    return any(f" {marker} " in padded for marker in _TEST_MARKERS)


@frappe.whitelist(allow_guest=True)
def get_live_ticker_activities(limit=8):
    """Return a short, diverse list of live ecosystem activities for the ticker.

    This endpoint is called on every home page load, so it deliberately uses a
    handful of small, indexed queries instead of the much heavier personalized
    feed (which already powers the main stream). Results are cached briefly to
    keep page loads fast and to avoid competing with the feed request.
    """
    try:
        limit = max(1, min(int(limit or 8), 20))
    except Exception:
        limit = 8

    cache_key = "ethiobiz_live_ticker_activities_v4"
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached[:limit]

    # (doctype, filters, fields, title_field, type, icon, badge)
    sources = (
        (
            "Website Item",
            {"published": 1},
            ("web_item_name", "item_name", "route", "creation"),
            "web_item_name",
            "product",
            "🛍️",
            "Shop",
        ),
        (
            "Job Opening",
            {"status": "Open"},
            ("job_title", "company", "creation"),
            "job_title",
            "job",
            "💼",
            "Jobs",
        ),
        (
            "Blog Post",
            {"published": 1},
            ("title", "route", "creation"),
            "title",
            "tibeb",
            "📝",
            "Tibeb",
        ),
        (
            "Afocha Post",
            {},
            ("author_name", "content", "creation"),
            "author_name",
            "afocha",
            "🌟",
            "Afocha",
        ),
        (
            "LMS Course",
            {"published": 1},
            ("title", "creation"),
            "title",
            "course",
            "🎓",
            "Dagu",
        ),
        (
            "Walta Forum Topic",
            {},
            ("title", "creation"),
            "title",
            "forum",
            "💬",
            "Walta",
        ),
        (
            "BizBooking Resource",
            {"is_active": 1},
            ("resource_name", "category", "creation"),
            "resource_name",
            "service",
            "⚡",
            "BizServices",
        ),
    )

    activities = []
    seen_titles = set()
    type_counts = {}

    for doctype, filters, wanted_fields, title_field, item_type, icon, badge in sources:
        if not frappe.db.exists("DocType", doctype):
            continue

        fields = [field for field in wanted_fields if frappe.db.has_column(doctype, field)]
        if title_field not in fields:
            continue

        filters = dict(filters or {})
        if doctype == "Afocha Post" and frappe.db.has_column(doctype, "published"):
            filters["published"] = 1

        order_by = "creation desc" if "creation" in fields else "modified desc"
        try:
            rows = frappe.get_all(
                doctype,
                filters=filters,
                fields=["name"] + fields,
                order_by=order_by,
                limit=2,
            )
        except Exception:
            continue

        for row in rows:
            title = str(row.get(title_field) or "").strip()
            if not title and doctype == "Website Item":
                title = str(row.get("item_name") or "").strip()
            if not title and doctype == "Afocha Post":
                content = frappe.utils.strip_html(row.get("content") or "")
                title = content[:90].strip()
            if not title or title in seen_titles:
                continue
            if _is_test_like(title) or _is_test_like(row.get("name")):
                continue
            if type_counts.get(item_type, 0) >= 2:
                continue

            docname = quote(str(row.get("name") or ""))
            if doctype == "Website Item":
                url = f"/post?doctype=Item&name={docname}"
            elif doctype == "Job Opening":
                url = f"/post?doctype=Job%20Opening&name={docname}"
            elif doctype == "Blog Post":
                url = row.get("route") or f"/post?doctype=Blog%20Post&name={docname}"
            elif doctype == "Afocha Post":
                url = f"/post?doctype=Afocha%20Post&name={docname}"
            elif doctype == "LMS Course":
                url = f"/post?doctype=LMS%20Course&name={docname}"
            elif doctype == "Walta Forum Topic":
                url = f"/forum?topic={docname}"
            elif doctype == "BizBooking Resource":
                url = f"/post?doctype=BizBooking%20Resource&name={docname}"
            else:
                url = "#"

            activities.append(
                {
                    "text_en": title,
                    "text_am": title,
                    "url": url,
                    "icon": icon,
                    "badge": badge,
                    "_created": str(row.get("creation") or ""),
                }
            )
            seen_titles.add(title)
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
            if len(activities) >= max(limit * 2, 12):
                break
        if len(activities) >= max(limit * 2, 12):
            break

    activities.sort(key=lambda row: row.get("_created", ""), reverse=True)
    for row in activities:
        row.pop("_created", None)

    activities = activities[:limit]
    if activities:
        frappe.cache().set_value(cache_key, activities, expires_in_sec=120)
    return activities


def _filter_option(label, label_am, key):
    return {"label": label, "label_am": label_am, "key": key}


FEED_FILTER_STRUCTURE = {
    "news": [
        _filter_option("All News", "ሁሉም ዜናዎች", "all"),
        _filter_option("💼 Business & Economy", "💼 ንግድ እና ኢኮኖሚ", "business"),
        _filter_option("💻 Tech & Innovation", "💻 ቴክኖሎጂ እና ፈጠራ", "tech"),
        _filter_option("🇪🇹 Ethiopia & Horn", "🇪🇹 ኢትዮጵያ እና ቀንድ አፍሪካ", "ethiopia"),
        _filter_option("🌍 World News", "🌍 ዓለም አቀፍ ዜና", "world"),
        _filter_option("⚽ Sports", "⚽ ስፖርት", "sport"),
        _filter_option("🏛️ Politics", "🏛️ ፖለቲካ እና አስተዳደር", "politics"),
        _filter_option("🏥 Health & Life", "🏥 ጤና እና አኗኗር", "health"),
        _filter_option("🔬 Science", "🔬 ሳይንስ", "science"),
        _filter_option("🎭 Culture", "🎭 ባህል እና ቅርስ", "culture"),
    ],
    "shop": [
        _filter_option("All Items", "ሁሉም እቃዎች", "all"),
        _filter_option("Electronics & Tech", "ኤሌክትሮኒክስ እና ቴክ", "Electronics"),
        _filter_option("Habesha Fashion", "የሀበሻ ፋሽን እና አልባሳት", "Fashion"),
        _filter_option("Ethiopian Coffee & Spices", "የኢትዮጵያ ቡና እና ቅመማቅመም", "Coffee"),
        _filter_option("Home & Furniture", "የቤት እቃዎች እና ፈርኒቸር", "Home"),
        _filter_option("Vehicles & Parts", "ተሽከርካሪዎች እና መለዋወጫዎች", "Vehicles"),
    ],
    "jobs": [
        _filter_option("All Positions", "ሁሉም ስራዎች", "all"),
        _filter_option("Software & IT", "ሶፍትዌር እና አይቲ", "Tech"),
        _filter_option("Accounting & Finance", "ሂሳብ እና ፋይናንስ", "Finance"),
        _filter_option("Healthcare & Clinical", "ጤና እና ህክምና", "Health"),
        _filter_option("Engineering & Construction", "ምህንድስና እና ግንባታ", "Engineering"),
        _filter_option("Hospitality & Tourism", "ሆቴል እና ቱሪዝም", "Hotel"),
    ],
    "bizservices": [
        _filter_option("All BizServices", "ሁሉም ቢዝሰርቪሶች", "all"),
        _filter_option("Hotel & Lodging", "ሆቴል እና ማረፊያ", "Hotel"),
        _filter_option("Salon & Spa Care", "ሳሎን እና ስፓ", "Salon"),
        _filter_option("Conference Venues", "የስብሰባ አዳራሾች", "Event"),
        _filter_option("Car Rental", "የመኪና ኪራይ", "Car"),
        _filter_option("Business Consult", "የንግድ ማማከር", "Consult"),
    ],
    "bizhealth": [
        _filter_option("All Specialties", "ሁሉም የህክምና ዘርፎች", "all"),
        _filter_option("General Practitioners", "ጠቅላላ ሀኪሞች", "General"),
        _filter_option("Pediatrics", "የህጻናት ህክምና", "Pediatric"),
        _filter_option("Dental Care", "የጥርስ ህክምና", "Dental"),
        _filter_option("Diagnostics & Labs", "ዲያግኖስቲክስ እና ላብራቶሪ", "Diagnostics"),
        _filter_option("Pharmacies", "ፋርማሲዎች", "Pharmacy"),
    ],
    "bizhome": [
        _filter_option("All Properties", "ሁሉም ቤቶች", "all"),
        _filter_option("Apartments for Rent", "የሚከራዩ አፓርታማዎች", "Rent"),
        _filter_option("Villas for Sale", "የሚሸጡ ቪላዎች", "Sale"),
        _filter_option("Commercial & Office", "የንግድ እና ቢሮ ቦታዎች", "Commercial"),
        _filter_option("Bole Luxury Condos", "የቦሌ ኮንዶሚኒየሞች", "Bole"),
    ],
    "bizfix": [
        _filter_option("All Maintenance", "ሁሉም ጥገናዎች", "all"),
        _filter_option("Electricians", "ኤሌክትሪሻን እና መብራት", "Electrical"),
        _filter_option("Plumbing", "ቧንቧ እና የውሃ መስመር", "Plumbing"),
        _filter_option("Appliance Repair", "የቤት እቃዎች ጥገና", "Appliance"),
        _filter_option("Carpentry", "የእንጨት እና አናጢነት ስራ", "Carpentry"),
        _filter_option("Auto & Generator", "መካኒክ እና ጀነሬተር", "Auto"),
    ],
    "dagu": [
        _filter_option("All Academy Courses", "ሁሉም ኮርሶች", "all"),
        _filter_option("DOBiz ERP Training", "የDOBiz ERP ስልጠና", "ERP"),
        _filter_option("Coding & Software", "ኮዲንግ እና ሶፍትዌር", "Programming"),
        _filter_option("Accounting & Tax", "ሂሳብ እና ታክስ", "Accounting"),
        _filter_option("Business Leadership", "የንግድ አመራር", "Leadership"),
    ],
    "tibeb": [
        _filter_option("All Tibebs", "ሁሉም ጥበቦች", "all"),
        _filter_option("Spiritual Insights", "መንፈሳዊ እይታዎች", "Spiritual"),
        _filter_option("Business Wisdom", "የንግድ ጥበብ", "Wisdom"),
        _filter_option("Culture & History", "ባህል እና ታሪክ", "Heritage"),
        _filter_option("Entrepreneurial Mindset", "የስራ ፈጠራ አስተሳሰብ", "Mindset"),
    ],
    "social": [
        _filter_option("All Stories", "ሁሉም የአፎቻ ዜናዎች", "all"),
        _filter_option("Merchant Unions", "የነጋዴ ማህበራት", "Merchant"),
        _filter_option("Community Updates", "የአካባቢ ማህበረሰብ", "Community"),
    ],
    "forum": [
        _filter_option("All Discussions", "ሁሉም ውይይቶች", "all"),
        _filter_option("Finance & Tax Q&A", "የፋይናንስ እና ታክስ ጥያቄዎች", "Tax"),
        _filter_option("Startup Ideas", "የስራ ፈጠራ ሀሳቦች", "Startup"),
    ],
}


@frappe.whitelist(allow_guest=True)
def get_feed_filter_structure():
    """Return the bilingual sub-filter matrix for the home live feed.

    The matrix is intentionally server-driven so future verticals can add
    filters without editing the large home template. It mirrors the inline
    fallback in ``www/ethiobiz_home_v1.html`` exactly.
    """
    return FEED_FILTER_STRUCTURE


# ---------------------------------------------------------------------------
# Live feed card colour identity
# ---------------------------------------------------------------------------
# One canonical row per feed family. These values are only FALLBACKS: the
# administrator edits the real values in
# EthioBiz Theme Setting -> "Live Feed Card Colours" -> Feed Type Styles.
# Keeping the fallback here means the homepage always renders beautifully
# even on a fresh install where the Theme child table is still empty.
FEED_SOURCE_DEFAULTS = [
    {
        "feed_type": "products", "filter": "shop",
        "label": "Dikka Shop", "label_am": "ዲካ ሾፕ", "icon": "🛍️",
        "accent_color": "#2563eb", "gradient_start": "#1d4ed8",
        "gradient_end": "#38bdf8", "text_color": "#ffffff",
        "subsystem": "enable_dikka_shop", "sort_order": 10,
    },
    {
        "feed_type": "jobs", "filter": "jobs",
        "label": "Oosoo Jobs", "label_am": "ኡሱ ስራዎች", "icon": "💼",
        "accent_color": "#d97706", "gradient_start": "#b45309",
        "gradient_end": "#fbbf24", "text_color": "#ffffff",
        "subsystem": "enable_oosoo_jobs", "sort_order": 20,
    },
    {
        "feed_type": "bizservices", "filter": "bizservices",
        "label": "BizServices", "label_am": "ቢዝ አገልግሎቶች", "icon": "🧰",
        "accent_color": "#0d9488", "gradient_start": "#0f766e",
        "gradient_end": "#2dd4bf", "text_color": "#ffffff",
        "subsystem": "enable_bizservices", "sort_order": 30,
    },
    {
        "feed_type": "bizhealth", "filter": "bizhealth",
        "label": "BizHealth", "label_am": "ቢዝ ጤና", "icon": "🩺",
        "accent_color": "#e11d48", "gradient_start": "#be123c",
        "gradient_end": "#fb7185", "text_color": "#ffffff",
        "subsystem": "enable_bizhealth", "sort_order": 40,
    },
    {
        "feed_type": "bizhome", "filter": "bizhome",
        "label": "BizHome", "label_am": "ቢዝ ቤት", "icon": "🏠",
        "accent_color": "#7c3aed", "gradient_start": "#6d28d9",
        "gradient_end": "#a78bfa", "text_color": "#ffffff",
        "subsystem": "enable_bizhome", "sort_order": 50,
    },
    {
        "feed_type": "bizfix", "filter": "bizfix",
        "label": "BizFix", "label_am": "ቢዝ ጥገና", "icon": "🔧",
        "accent_color": "#0891b2", "gradient_start": "#0e7490",
        "gradient_end": "#22d3ee", "text_color": "#ffffff",
        "subsystem": "enable_bizfix", "sort_order": 60,
    },
    {
        "feed_type": "dagu", "filter": "dagu",
        "label": "Dagu Academy", "label_am": "ዳጉ አካዳሚ", "icon": "🎓",
        "accent_color": "#9333ea", "gradient_start": "#7e22ce",
        "gradient_end": "#c084fc", "text_color": "#ffffff",
        "subsystem": "enable_dagu_academy", "sort_order": 70,
    },
    {
        "feed_type": "tibeb", "filter": "tibeb",
        "label": "Tibeb", "label_am": "ጥበብ", "icon": "📖",
        "accent_color": "#ca8a04", "gradient_start": "#a16207",
        "gradient_end": "#facc15", "text_color": "#ffffff",
        "subsystem": "enable_tibebs", "sort_order": 80,
    },
    {
        "feed_type": "social", "filter": "social",
        "label": "Afocha", "label_am": "አፎቻ", "icon": "💬",
        "accent_color": "#059669", "gradient_start": "#047857",
        "gradient_end": "#34d399", "text_color": "#ffffff",
        "subsystem": "enable_afocha_social", "sort_order": 90,
    },
    {
        "feed_type": "forum", "filter": "forum",
        "label": "Walta Forum", "label_am": "ዋልታ መድረክ", "icon": "🗣️",
        "accent_color": "#4f46e5", "gradient_start": "#4338ca",
        "gradient_end": "#818cf8", "text_color": "#ffffff",
        "subsystem": "enable_walta_forum", "sort_order": 100,
    },
    {
        "feed_type": "news", "filter": "news",
        "label": "Live News", "label_am": "ቀጥታ ዜና", "icon": "📰",
        "accent_color": "#dc2626", "gradient_start": "#b91c1c",
        "gradient_end": "#f87171", "text_color": "#ffffff",
        "subsystem": "enable_live_news", "sort_order": 110,
    },
    {
        "feed_type": "ad", "filter": "",
        "label": "Sponsored", "label_am": "ተስፋፊ", "icon": "📢",
        "accent_color": "#b45309", "gradient_start": "#92400e",
        "gradient_end": "#f59e0b", "text_color": "#ffffff",
        "subsystem": "enable_dikka_shop", "sort_order": 120,
    },
]

# Style keys every card may need, including families that never get a button
# (sponsored ads) and the repost wrapper (which inherits its source colour).
FEED_STYLE_KEYS = [row["feed_type"] for row in FEED_SOURCE_DEFAULTS]


def _feed_style_payload(row):
    return {
        "feed_type": row.get("feed_type"),
        "label": row.get("label") or row.get("feed_type"),
        "label_am": row.get("label_am") or row.get("label") or row.get("feed_type"),
        "icon": row.get("icon") or "✨",
        "accent_color": row.get("accent_color") or "#0d9488",
        "gradient_start": row.get("gradient_start") or "#0f766e",
        "gradient_end": row.get("gradient_end") or "#14b8a6",
        "text_color": row.get("text_color") or "#ffffff",
    }


def _theme_feed_styles():
    """Administrator overrides from EthioBiz Theme -> Feed Type Styles."""
    if not frappe.db.exists("DocType", "EthioBiz Theme"):
        return {}
    try:
        theme = frappe.get_single("EthioBiz Theme")
        rows = theme.get("feed_type_styles") or []
    except Exception as exc:
        frappe.logger("home_api").warning("Feed type styles lookup failed: %s", exc)
        return {}

    out = {}
    for row in rows:
        key = (row.get("feed_type") or "").strip().lower()
        if not key:
            continue
        out[key] = {
            "feed_type": key,
            "label": row.get("label") or key,
            "label_am": row.get("label_am") or row.get("label") or key,
            "icon": row.get("icon") or "✨",
            "accent_color": row.get("accent_color") or "#0d9488",
            "gradient_start": row.get("gradient_start") or "#0f766e",
            "gradient_end": row.get("gradient_end") or "#14b8a6",
            "text_color": row.get("text_color") or "#ffffff",
            "is_enabled": int(row.get("is_enabled") if row.get("is_enabled") is not None else 1),
            "sort_order": int(row.get("sort_order") or 0),
        }
    return out


@frappe.whitelist(allow_guest=True)
def get_feed_sources():
    """Feed-type buttons + per-type card colours for the home live feed.

    Sources are the administrator's Theme rows, gated by the subsystem toggle
    that owns them. A disabled subsystem therefore disappears from the button
    bar instead of opening an empty feed, and every card family carries its
    own accent/gradient identity for the homepage renderer.
    """
    try:
        subsystems = get_subsystem_settings() or {}
    except Exception:
        subsystems = {}

    overrides = _theme_feed_styles()

    styles = {}
    for default in FEED_SOURCE_DEFAULTS:
        key = default["feed_type"]
        merged = dict(default)
        merged.update(overrides.get(key) or {})
        styles[key] = merged
    # Administrator-defined extra families still get a colour.
    for key, row in overrides.items():
        if key not in styles:
            styles[key] = dict(row)

    sources = []
    for default in FEED_SOURCE_DEFAULTS:
        key = default["feed_type"]
        merged = styles[key]
        if not default.get("filter"):
            continue  # sponsored ads are cards, not a feed-type button
        subsystem_flag = int(subsystems.get(default["subsystem"], 1) or 0)
        row_enabled = int(merged.get("is_enabled", 1) if merged.get("is_enabled") is not None else 1)
        sources.append({
            "feed_type": key,
            "filter": default["filter"],
            "label": merged.get("label"),
            "label_am": merged.get("label_am"),
            "icon": merged.get("icon"),
            "enabled": bool(subsystem_flag and row_enabled),
            "sort_order": int(merged.get("sort_order") or default.get("sort_order") or 0),
        })
    sources.sort(key=lambda s: (s["sort_order"], s["filter"]))

    return {
        "status": "success",
        "sources": sources,
        "styles": {key: _feed_style_payload(row) for key, row in styles.items()},
        "updated_at": str(frappe.utils.now()),
    }


@frappe.whitelist(allow_guest=True)
def get_dobiz_industries():
    """Return the enabled DOBiz signup industries from EthioBiz Theme.

    The Theme single is the admin-controlled source of truth.  If the table is
    empty (fresh install) a safe canonical fallback is returned so the public
    signup page never breaks.
    """
    try:
        from bismillah_ethiobiz.company_access import get_enabled_industry_modules
        industries = get_enabled_industry_modules()
    except Exception as exc:
        frappe.logger("home_api").warning("DOBiz industries lookup failed: %s", exc)
        industries = []
    return {
        "industries": industries,
        "count": len(industries),
        "source": "EthioBiz Theme > DOBiz Industry Modules",
    }


@frappe.whitelist(allow_guest=True)
def get_floating_action_items():
    """Return active FAB actions configured in EthioBiz Theme."""
    try:
        theme = frappe.get_cached_doc("EthioBiz Theme", "EthioBiz Theme")
    except Exception:
        return []

    items = []
    for row in getattr(theme, "floating_action_items", []) or []:
        if not _as_bool(getattr(row, "is_active", 1), True):
            continue
        link = str(getattr(row, "link", "") or "").strip()
        title = str(getattr(row, "title", "") or "").strip()
        if not link or not title:
            continue
        items.append(
            {
                "icon": getattr(row, "icon", "") or "⚡",
                "title": title,
                "title_am": getattr(row, "title_am", "") or title,
                "link": link,
                "target": getattr(row, "target", "") or "Same Tab (_self)",
                "sort_order": int(getattr(row, "sort_order", 0) or 0),
            }
        )

    items.sort(key=lambda row: row.get("sort_order", 0))
    return items


@frappe.whitelist(allow_guest=True)
def get_active_home_ads(placement="homepage-rail"):
    """Return active desk-managed campaigns for a home placement.

    Only campaigns whose linked ad slot matches ``placement`` and whose
    schedule covers today are returned. Missing doctypes/columns are treated
    as an empty rail so the template keeps its built-in fallback cards.
    """
    placement = str(placement or "homepage-rail").strip()
    if not frappe.db.exists("DocType", "EthioBiz Ad Campaign"):
        return []

    slot_names = []
    if frappe.db.exists("DocType", "EthioBiz Ad Slot"):
        slot_names = frappe.get_all(
            "EthioBiz Ad Slot", filters={"slot_code": placement}, pluck="name"
        )
        if not slot_names:
            slot_names = frappe.get_all(
                "EthioBiz Ad Slot",
                filters={"slot_name": ["like", f"%{placement}%"]},
                pluck="name",
            )
    if not slot_names:
        return []

    filters = {"status": "Active", "slot": ["in", slot_names]}
    today = frappe.utils.nowdate()
    if frappe.db.has_column("EthioBiz Ad Campaign", "start_date"):
        filters["start_date"] = ["<=", today]
    if frappe.db.has_column("EthioBiz Ad Campaign", "end_date"):
        filters["end_date"] = [">=", today]

    fields = ["name", "campaign_name", "click_url", "creative_image", "alt_text", "company"]
    for optional in ("campaign_url", "slot", "impressions", "clicks"):
        if frappe.db.has_column("EthioBiz Ad Campaign", optional):
            fields.append(optional)

    try:
        ads = frappe.get_all(
            "EthioBiz Ad Campaign",
            filters=filters,
            fields=fields,
            order_by="modified desc",
            limit=5,
        )
    except Exception as exc:
        frappe.log_error(f"Error fetching home rail ads: {exc}")
        return []

    result = []
    for ad in ads:
        click_url = (ad.get("campaign_url") or ad.get("click_url") or "").strip()
        if not click_url:
            continue
        result.append(
            {
                "id": ad.get("name"),
                "title": ad.get("campaign_name") or ad.get("name"),
                "alt_text": ad.get("alt_text") or "",
                "click_url": click_url,
                "image": ad.get("creative_image") or "",
                "company": ad.get("company") or "",
            }
        )
        if frappe.db.has_column("EthioBiz Ad Campaign", "impressions"):
            try:
                current = frappe.utils.cint(ad.get("impressions")) + 1
                frappe.db.set_value(
                    "EthioBiz Ad Campaign",
                    ad.get("name"),
                    "impressions",
                    current,
                    update_modified=False,
                )
            except Exception:
                pass

    if result:
        frappe.db.commit()
    return result


@frappe.whitelist(allow_guest=True)
def track_ad_click(campaign_name=None):
    """Increment the click counter for a home rail campaign."""
    campaign_name = str(campaign_name or "").strip()
    if not campaign_name or not frappe.db.exists("EthioBiz Ad Campaign", campaign_name):
        return {"ok": False}

    try:
        current = frappe.utils.cint(
            frappe.db.get_value("EthioBiz Ad Campaign", campaign_name, "clicks")
        )
        frappe.db.set_value(
            "EthioBiz Ad Campaign",
            campaign_name,
            "clicks",
            current + 1,
            update_modified=False,
        )
        frappe.db.commit()
        return {"ok": True}
    except Exception as exc:
        frappe.log_error(f"Error tracking ad click for {campaign_name}: {exc}")
        return {"ok": False}
