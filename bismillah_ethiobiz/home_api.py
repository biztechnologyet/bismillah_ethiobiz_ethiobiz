import json
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
            
            items.append({
                "type": "product",
                "badge": f"🛍️ {p.item_group or 'Product'}",
                "badge_class": "badge-product",
                "title": p.web_item_name or p.item_name,
                "subtitle": f"🏢 {comp} • Verified Merchant",
                "content": p.short_description or "High-quality verified product available for instant ordering across Ethiopia.",
                "price": price_str,
                "image": img,
                "icon": "🛍️",
                "action_label": "Order Now →",
                "action_url": f"/{p.route or 'shop'}",
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

                items.append({
                    "type": "job",
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
                    "action_url": f"/jobs",
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
                
                items.append({
                    "type": "booking",
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
                    "action_url": "#",
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
                items.append({
                    "type": "booking",
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
                    "action_url": "#",
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
                items.append({
                    "type": "social",
                    "badge": f"🌟 {post.category_tag or 'Afocha Story'}",
                    "badge_class": "badge-social",
                    "title": post.author_name,
                    "subtitle": f"🏢 {post.company or 'EthioBiz Network'} • {post.author_handle}",
                    "content": post.content,
                    "stats": f"❤️ {post.likes_count or 0} likes • 💬 {post.comments_count or 0} comments",
                    "image": img,
                    "icon": "🌟",
                    "action_label": "Join Discussion →",
                    "action_url": f"/social?post={post.name}",
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
            items.append({
                "type": "blog",
                "badge": f"📝 {b.blog_category or 'Tibeb Wisdom'}",
                "badge_class": "badge-blog",
                "title": b.title,
                "subtitle": f"✍️ By {b.blogger or 'EthioBiz Editorial Team'}",
                "content": b.blog_intro or "In-depth insights, economic analysis, and cultural perspectives from Ethiopian pioneers.",
                "image": b.meta_image,
                "icon": "📝",
                "action_label": "Read Article →",
                "action_url": f"/{b.route or 'blog'}",
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
                items.append({
                    "type": "course",
                    "badge": "🎓 Dagu Academy Course",
                    "badge_class": "badge-course",
                    "title": c.title,
                    "subtitle": "Online Vocational & Professional Skills",
                    "content": c.short_introduction or "Master industry-standard skills with practical real-world modules and certification.",
                    "image": c.image,
                    "icon": "🎓",
                    "action_label": "Enroll Now →",
                    "action_url": f"/courses/{c.name}",
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
                items.append({
                    "type": "forum",
                    "badge": f"💬 {ft.category or 'Walta Forum'}",
                    "badge_class": "badge-social",
                    "title": ft.title,
                    "subtitle": f"🛡️ {ft.author_name} • {ft.company or 'EthioBiz'}",
                    "content": (clean_c[:150] + "...") if len(clean_c) > 150 else clean_c,
                    "price": f"💬 {ft.replies_count or 0} replies • ❤️ {ft.likes_count or 0} likes",
                    "image": img,
                    "icon": "💬",
                    "action_label": "Join Discussion →",
                    "action_url": f"/forum?topic={ft.name}",
                    "is_booking": False,
                    "created_at": str(ft.creation)
                })
        except Exception:
            pass

    # Sort all feed items by creation timestamp
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    paged_items = items[:limit]
    has_more = len(items) >= limit

    return {
        "items": paged_items,
        "has_more": has_more,
        "total_returned": len(paged_items)
    }
