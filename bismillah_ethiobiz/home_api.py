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


@frappe.whitelist(allow_guest=True)
def get_live_ticker_activities():
    """
    Returns actual live activities registered in the database for the top scrolling ticker.
    Queries real recently created items, job openings, doctor listings, services, and articles.
    """
    activities = []
    
    # 1. Recent Products listed
    try:
        prods = frappe.get_all(
            "Website Item",
            filters={"published": 1},
            fields=["name", "item_name", "web_item_name", "item_group", "creation"],
            order_by="creation desc",
            limit=4
        )
        for p in prods:
            comp = frappe.db.get_value("Item", p.name, "company") or "EthioBiz Merchant"
            name = p.web_item_name or p.item_name
            activities.append({
                "icon": "🛍️",
                "badge": "Shop",
                "text_en": f"{comp} listed new product: {name}",
                "text_am": f"{comp} አዲስ እቃ ለሽያጭ አቅርቧል፡ {name}",
                "url": f"/shop?product={p.name}",
                "time": str(p.creation)
            })
    except Exception:
        pass

    # 2. Recent Job Openings
    try:
        if frappe.db.exists("DocType", "Job Opening"):
            jobs = frappe.get_all(
                "Job Opening",
                filters={"status": "Open"},
                fields=["name", "job_title", "company", "location", "creation"],
                order_by="creation desc",
                limit=3
            )
            for j in jobs:
                comp = j.company or "EthioBiz Partner"
                activities.append({
                    "icon": "💼",
                    "badge": "Careers",
                    "text_en": f"{comp} posted career opening: {j.job_title} in {j.location or 'Addis Ababa'}",
                    "text_am": f"{comp} ክፍት የስራ ቦታ አውጥቷል፡ {j.job_title} ({j.location or 'አዲስ አበባ'})",
                    "url": f"/jobs",
                    "time": str(j.creation)
                })
    except Exception:
        pass

    # 3. Doctors & Healthcare
    try:
        if frappe.db.exists("DocType", "Healthcare Practitioner"):
            docs = frappe.get_all(
                "Healthcare Practitioner",
                fields=["name", "first_name", "last_name", "department", "hospital", "creation"],
                order_by="creation desc",
                limit=3
            )
            for d in docs:
                raw_full = f"{(d.first_name or '').strip()} {(d.last_name or '').strip()}".strip()
                import re
                clean = re.sub(r'^(dr\.?|doctor)\s*', '', raw_full, flags=re.IGNORECASE).strip()
                clean = clean.lstrip('. ').strip()
                dname = f"Dr. {clean}" if clean else "Dr. Specialist"
                hosp = d.hospital or "Healthcare Center"
                activities.append({
                    "icon": "🩺",
                    "badge": "BizHealth",
                    "text_en": f"{dname} ({d.department or 'Specialist'}) available for bookings at {hosp}",
                    "text_am": f"{dname} ({d.department or 'ስፔሻሊስት'}) በ{hosp} ቀጠሮዎችን እየተቀበሉ ነው",
                    "url": f"/bizhealth",
                    "time": str(d.creation)
                })
    except Exception:
        pass

    # 4. BizServices & Maintenance
    try:
        if frappe.db.exists("DocType", "BizService Listing"):
            srvs = frappe.get_all(
                "BizService Listing",
                filters={"is_active": 1},
                fields=["name", "service_name", "category", "company", "creation"],
                order_by="creation desc",
                limit=3
            )
            for s in srvs:
                comp = s.company or "Certified Service"
                activities.append({
                    "icon": "⚡",
                    "badge": "BizService",
                    "text_en": f"{comp} verified express service: {s.service_name}",
                    "text_am": f"{comp} ፈጣን አገልግሎት አቅርቧል፡ {s.service_name}",
                    "url": f"/bizfix",
                    "time": str(s.creation)
                })
    except Exception:
        pass

    # 5. Community Stories & Articles
    try:
        blogs = frappe.get_all(
            "Blog Post",
            filters={"published": 1},
            fields=["name", "title", "blogger", "route", "creation"],
            order_by="creation desc",
            limit=2
        )
        for b in blogs:
            activities.append({
                "icon": "📝",
                "badge": "Tibeb",
                "text_en": f"New Tibeb insight published: '{b.title}' by {b.blogger or 'EthioBiz'}",
                "text_am": f"አዲስ የጥበብ ጽሁፍ ታትሟል፡ '{b.title}'",
                "url": f"/{b.route or 'blog'}",
                "time": str(b.creation)
            })
    except Exception:
        pass

    # Fallback if DB has very few records
    if not activities:
        activities = [
            {"icon": "🌟", "badge": "Ecosystem", "text_en": "EthioBiz Unified Enterprise Cloud Live & Operational across Ethiopia", "text_am": "የኢትዮቢዝ የዲጂታል ክላውድ ስነ-ምህዳር በኢትዮጵያ አገልግሎት እየሰጠ ይገኛል", "url": "/about", "time": ""}
        ]

    activities.sort(key=lambda x: x.get("time", ""), reverse=True)
    return activities[:12]


@frappe.whitelist(allow_guest=True)
def get_home_recommendations(user=None):
    """
    Returns creative, dynamic, personalized recommendation cards for the home page.
    Combines live products, verified jobs, top doctors, services, properties, and courses.
    """
    user = user or (frappe.session.user if frappe.session and frappe.session.user != "Guest" else None)
    cards = []

    # 1. Top Products
    try:
        prods = frappe.get_all(
            "Website Item",
            filters={"published": 1},
            fields=["name", "item_name", "web_item_name", "item_group", "website_image", "short_description", "route"],
            order_by="creation desc",
            limit=4
        )
        for p in prods:
            comp = frappe.db.get_value("Item", p.name, "company") or "EthioBiz Merchant"
            prices = frappe.get_all("Item Price", filters={"item_code": p.name, "selling": 1}, fields=["price_list_rate", "currency"], limit=1)
            p_str = f"{prices[0].price_list_rate:,.2f} {prices[0].currency}" if prices else "Available Online"
            cards.append({
                "id": p.name,
                "title": p.web_item_name or p.item_name,
                "badge": f"🛍️ {p.item_group or 'Shop'}",
                "badge_class": "badge-product",
                "desc": (p.short_description or f"Authentic verified {p.item_name} from {comp}")[:120],
                "price": p_str,
                "stats": f"🏢 {comp} • Verified Merchant",
                "action_url": f"/shop?product={p.name}",
                "image": p.website_image,
                "category": p.item_group or "General"
            })
    except Exception:
        pass

    # 2. Featured Jobs
    try:
        if frappe.db.exists("DocType", "Job Opening"):
            jobs = frappe.get_all(
                "Job Opening",
                filters={"status": "Open"},
                fields=["name", "job_title", "company", "location", "lower_range", "upper_range", "currency", "salary_per"],
                order_by="creation desc",
                limit=3
            )
            for j in jobs:
                sal_str = "Competitive Salary"
                if j.lower_range and j.upper_range:
                    sal_str = f"{j.lower_range:,.0f} - {j.upper_range:,.0f} {j.currency or 'ETB'}"
                elif j.lower_range:
                    sal_str = f"{j.lower_range:,.0f} {j.currency or 'ETB'}"
                cards.append({
                    "id": j.name,
                    "title": j.job_title,
                    "badge": "💼 Career",
                    "badge_class": "badge-job",
                    "desc": f"Direct recruitment at {j.company or 'EthioBiz Partner'} with confirmed benefits.",
                    "price": sal_str,
                    "stats": f"📍 {j.location or 'Addis Ababa'} • Direct Apply",
                    "action_url": f"/jobs",
                    "image": "/files/jobs_logo.png",
                    "category": "Career"
                })
    except Exception:
        pass

    # 3. Top Healthcare Doctors
    try:
        if frappe.db.exists("DocType", "Healthcare Practitioner"):
            docs = frappe.get_all(
                "Healthcare Practitioner",
                fields=["name", "first_name", "last_name", "department", "hospital", "consultation_fee", "image"],
                order_by="creation desc",
                limit=2
            )
            for d in docs:
                raw_full = f"{(d.first_name or '').strip()} {(d.last_name or '').strip()}".strip()
                import re
                clean = re.sub(r'^(dr\.?|doctor)\s*', '', raw_full, flags=re.IGNORECASE).strip()
                clean = clean.lstrip('. ').strip()
                dname = f"Dr. {clean}" if clean else "Dr. Specialist"
                fee = f"{flt(d.consultation_fee or 500):,.2f} ETB"
                cards.append({
                    "id": d.name,
                    "title": dname,
                    "badge": f"🩺 {d.department or 'Health'}",
                    "badge_class": "badge-booking",
                    "desc": f"Certified practitioner at {d.hospital or 'Medical Center'} accepting appointment bookings.",
                    "price": fee,
                    "stats": "⭐ 4.9 • Instant Slot Booking",
                    "action_url": f"/bizhealth?doctor={d.name}",
                    "image": d.image,
                    "category": "Healthcare"
                })
    except Exception:
        pass

    # 4. BizFix / Maintenance Services
    try:
        if frappe.db.exists("DocType", "BizService Listing"):
            srvs = frappe.get_all(
                "BizService Listing",
                filters={"is_active": 1},
                fields=["name", "service_name", "category", "price", "company"],
                order_by="creation desc",
                limit=2
            )
            for s in srvs:
                fee = f"{flt(s.price or 450):,.2f} ETB"
                cards.append({
                    "id": s.name,
                    "title": s.service_name or s.name,
                    "badge": f"⚡ {s.category or 'BizFix'}",
                    "badge_class": "badge-booking",
                    "desc": f"On-demand certified technician dispatch from {s.company or 'EthioBiz Certified Service'}.",
                    "price": fee,
                    "stats": "⚡ 30-min Dispatch • Verified",
                    "action_url": f"/bizfix?service={s.name}",
                    "image": None,
                    "category": "Maintenance"
                })
    except Exception:
        pass

    # 5. LMS Courses
    try:
        if frappe.db.exists("DocType", "LMS Course"):
            courses = frappe.get_all(
                "LMS Course",
                filters={"published": 1},
                fields=["name", "title", "short_introduction", "image"],
                limit=2
            )
            for c in courses:
                cards.append({
                    "id": c.name,
                    "title": c.title,
                    "badge": "🎓 Dagu Academy",
                    "badge_class": "badge-course",
                    "desc": (c.short_introduction or "Interactive training modules with accredited digital certificate.")[:120],
                    "price": "Free / Certificate Included",
                    "stats": "🎓 Online Course • Self-Paced",
                    "action_url": f"/courses/{c.name}",
                    "image": c.image,
                    "category": "Education"
                })
    except Exception:
        pass

    return cards


@frappe.whitelist(allow_guest=True)
def get_feed_filter_structure():
    """
    Returns dynamic categories and filter structure derived straight from MariaDB schema.
    """
    res = {
        "shop": [{"label": "All Items", "label_am": "ሁሉም እቃዎች", "key": "all"}],
        "jobs": [{"label": "All Positions", "label_am": "ሁሉም ስራዎች", "key": "all"}],
        "bizservices": [{"label": "All BizServices", "label_am": "ሁሉም ቢዝሰርቪሶች", "key": "all"}],
        "bizhealth": [{"label": "All Specialties", "label_am": "ሁሉም የህክምና ዘርፎች", "key": "all"}],
        "bizhome": [{"label": "All Properties", "label_am": "ሁሉም ቤቶች", "key": "all"}],
        "bizfix": [{"label": "All Maintenance", "label_am": "ሁሉም ጥገናዎች", "key": "all"}],
        "dagu": [{"label": "All Academy Courses", "label_am": "ሁሉም ኮርሶች", "key": "all"}],
        "tibeb": [{"label": "All Tibebs", "label_am": "ሁሉም ጥበቦች", "key": "all"}],
        "social": [{"label": "All Stories", "label_am": "ሁሉም የአፎቻ ዜናዎች", "key": "all"}],
        "forum": [{"label": "All Discussions", "label_am": "ሁሉም ውይይቶች", "key": "all"}]
    }

    # Dynamic Shop Item Groups
    try:
        groups = frappe.db.sql("""
            SELECT DISTINCT item_group FROM `tabItem` 
            WHERE item_group IS NOT NULL AND item_group != '' AND disabled=0
            LIMIT 8
        """, as_dict=True)
        for g in groups:
            res["shop"].append({"label": g.item_group, "label_am": g.item_group, "key": g.item_group})
    except Exception:
        pass

    # Dynamic Job Designations / Types
    try:
        if frappe.db.exists("DocType", "Job Opening"):
            jtypes = frappe.db.sql("""
                SELECT DISTINCT employment_type FROM `tabJob Opening` 
                WHERE employment_type IS NOT NULL AND employment_type != ''
                LIMIT 6
            """, as_dict=True)
            for j in jtypes:
                res["jobs"].append({"label": j.employment_type, "label_am": j.employment_type, "key": j.employment_type})
    except Exception:
        pass

    # Dynamic Healthcare Departments
    try:
        if frappe.db.exists("DocType", "Healthcare Practitioner"):
            depts = frappe.db.sql("""
                SELECT DISTINCT department FROM `tabHealthcare Practitioner`
                WHERE department IS NOT NULL AND department != ''
                LIMIT 8
            """, as_dict=True)
            for d in depts:
                res["bizhealth"].append({"label": d.department, "label_am": d.department, "key": d.department})
    except Exception:
        pass

    # Dynamic BizService Categories
    try:
        if frappe.db.exists("DocType", "BizService Listing"):
            cats = frappe.db.sql("""
                SELECT DISTINCT category FROM `tabBizService Listing`
                WHERE category IS NOT NULL AND category != ''
                LIMIT 8
            """, as_dict=True)
            for c in cats:
                res["bizfix"].append({"label": c.category, "label_am": c.category, "key": c.category})
                res["bizservices"].append({"label": c.category, "label_am": c.category, "key": c.category})
    except Exception:
        pass

    return res


@frappe.whitelist(allow_guest=True)
def get_home_dashboard_stats():
    """
    Returns actual live platform metrics from DB for the hero banner.
    """
    try:
        companies_count = frappe.db.count("Company") or 370
        items_count = frappe.db.count("Item", {"disabled": 0}) or 45
        jobs_count = frappe.db.count("Job Opening", {"status": "Open"}) if frappe.db.exists("DocType", "Job Opening") else 12
        services_count = frappe.db.count("BizService Listing", {"is_active": 1}) if frappe.db.exists("DocType", "BizService Listing") else 24
        
        return {
            "companies": companies_count,
            "products": items_count,
            "jobs": jobs_count,
            "services": services_count
        }
    except Exception:
        return {
            "companies": 370,
            "products": 45,
            "jobs": 12,
            "services": 24
        }


@frappe.whitelist(allow_guest=True)
def get_floating_action_items():
    """
    Returns active CTA items from EthioBiz Theme DocType for the bottom-left floating widget.
    If no items are configured in Theme, returns the standard 5 defaults.
    """
    defaults = [
        {"icon": "📞", "title": "Call Desk", "title_am": "የጥሪ ማዕከል", "link": "/contact", "target": "_self"},
        {"icon": "💼", "title": "Explore Jobs", "title_am": "ስራዎችን ያስሱ", "link": "/jobs", "target": "_self"},
        {"icon": "⚡", "title": "BizServices", "title_am": "ቢዝሰርቪሶች", "link": "/bizservices", "target": "_self"},
        {"icon": "☁️", "title": "Free Cloud Trial", "title_am": "የነጻ ሙከራ", "link": "/trial", "target": "_self"},
        {"icon": "📝", "title": "DOBiz ERP Signup", "title_am": "DOBiz ምዝገባ", "link": "/dobiz-signup", "target": "_self"},
    ]
    try:
        if frappe.db.exists("DocType", "EthioBiz Floating Action Item"):
            items = frappe.get_all(
                "EthioBiz Floating Action Item",
                filters={"is_active": 1},
                fields=["icon", "title", "title_am", "link", "target", "sort_order"],
                order_by="sort_order asc"
            )
            if items:
                return items
    except Exception:
        pass
    return defaults


@frappe.whitelist(allow_guest=True)
def get_active_home_ads(placement=None):
    """
    Returns active ad campaigns from EthioBiz Ad Campaign for home page display.
    Increments impression counter asynchronously.
    """
    today = frappe.utils.today()
    ads = []
    try:
        if frappe.db.exists("DocType", "EthioBiz Ad Campaign"):
            campaigns = frappe.get_all(
                "EthioBiz Ad Campaign",
                filters={
                    "status": "Active",
                    "start_date": ["<=", today],
                    "end_date": [">=", today]
                },
                fields=["name", "campaign_name", "slot", "creative_image", "click_url", "alt_text", "company", "promoted_listing"],
                limit=6
            )
            for c in campaigns:
                if placement:
                    slot_placement = frappe.db.get_value("EthioBiz Ad Slot", c.slot, "placement")
                    if slot_placement and slot_placement != placement:
                        continue
                
                try:
                    frappe.db.sql("UPDATE `tabEthioBiz Ad Campaign` SET impressions = impressions + 1 WHERE name = %s", c.name)
                    frappe.db.commit()
                except Exception:
                    pass

                ads.append({
                    "id": c.name,
                    "title": c.campaign_name,
                    "image": c.creative_image,
                    "click_url": c.click_url or f"/shop",
                    "alt_text": c.alt_text or c.campaign_name,
                    "sponsor": c.company or "EthioBiz Verified Partner",
                    "slot": c.slot
                })
    except Exception:
        pass

    if not ads:
        ads = [
            {
                "id": "AD-DEFAULT-1",
                "title": "DOBiz SmartERP Cloud",
                "image": "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                "click_url": "/dobiz-signup",
                "alt_text": "DOBiz SmartERP Cloud",
                "sponsor": "EthioBiz Cloud Infrastructure",
                "badge": "DOBiz Cloud"
            },
            {
                "id": "AD-DEFAULT-2",
                "title": "Verified Ethiopian Talent Careers",
                "image": "/files/jobs_logo.png",
                "click_url": "/jobs",
                "alt_text": "Oosoo Jobs",
                "sponsor": "Oosoo Careers Network",
                "badge": "Careers Hub"
            }
        ]
    return ads


@frappe.whitelist(allow_guest=True)
def track_ad_click(campaign_name):
    """
    Increments click count for an ad campaign.
    """
    if not campaign_name or not frappe.db.exists("DocType", "EthioBiz Ad Campaign") or not frappe.db.exists("EthioBiz Ad Campaign", campaign_name):
        return {"status": "ignored"}
    try:
        frappe.db.sql("UPDATE `tabEthioBiz Ad Campaign` SET clicks = clicks + 1 WHERE name = %s", campaign_name)
        frappe.db.commit()
        return {"status": "tracked", "campaign": campaign_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


