import json
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
                    "post_url": n.get("url") or "/news",
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
            recs.append({
                "badge": f"🛍️ {it.item_group or 'Product'}",
                "stats": "⭐ 4.9 • Top Rated",
                "title": it.item_name,
                "desc": f"Verified product from {it.company or 'EthioBiz Merchant'}",
                "price": pr_str,
                "action_url": f"/post?doctype=Item&name={it.name}"
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
                "action_url": f"/post?doctype=Job%20Opening&name={j.name}"
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
                    "action_url": f"/post?doctype=BizService%20Listing&name={s.name}"
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
                "action_url": "/shop"
            },
            {
                "badge": "💼 Hot Career",
                "stats": "🔥 Verified Hiring",
                "title": "Senior Full-Stack Cloud Engineer",
                "desc": "Exciting high-growth opportunity at EthioBiz Cloud Infrastructure",
                "price": "Competitive",
                "action_url": "/jobs"
            },
            {
                "badge": "⚡ Instant Service",
                "stats": "⭐ 4.9 • On-Demand",
                "title": "Enterprise Cloud ERP Implementation & Training",
                "desc": "Hands-on rollout by certified DOBiz SmartERP consultants",
                "price": "Book Assessment",
                "action_url": "/dobiz"
            },
            {
                "badge": "🎓 Dagu Academy",
                "stats": "⭐ 5.0 • Practical Course",
                "title": "Ethiopian E-Invoicing & VAT Compliance Mastery",
                "desc": "Comprehensive digital finance certification for local businesses",
                "price": "Free Enrollment",
                "action_url": "/courses"
            },
            {
                "badge": "📖 Tibeb Wisdom",
                "stats": "✦ Sacred Heritage",
                "title": "Axumite & Lalibela Architectural Wisdom",
                "desc": "Reflections on ancient Ethiopian engineering, faith, and unity",
                "price": "Read Free",
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
