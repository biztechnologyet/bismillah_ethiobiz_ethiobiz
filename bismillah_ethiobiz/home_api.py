import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_infinite_feed(start=0, limit=12, filter_type=None, search=None):
    """Unified multi-vertical feed endpoint for the dynamic infinite-scroll homepage."""
    start = int(start or 0)
    limit = int(limit or 12)
    filter_type = (filter_type or "all").lower().strip()
    feed_items = []

    # 1. Afocha Social Posts
    if filter_type in ("all", "social"):
        social_filters = {}
        if search:
            social_filters["content"] = ["like", f"%{search}%"]
        
        posts = frappe.get_all(
            "Afocha Post",
            filters=social_filters,
            fields=["name", "author_name", "author_handle", "content", "category_tag", "post_date", "post_image", "video_url", "likes_count", "comments_count", "pinned"],
            order_by="pinned desc, post_date desc",
            limit_start=0 if filter_type == "all" else start,
            limit_page_length=3 if filter_type == "all" else limit
        )
        for p in posts:
            feed_items.append({
                "type": "social",
                "badge": f"🌟 {p.category_tag or 'Afocha Story'}",
                "badge_class": "badge-social",
                "title": p.author_name or "EthioBiz Community",
                "subtitle": f"{p.author_handle or '@ethiobiz'} • {str(p.post_date).split(' ')[0] if p.post_date else 'Recent'}",
                "content": p.content or "",
                "image": p.post_image or None,
                "price": None,
                "action_url": f"/social?post={p.name}",
                "action_label": "Engage on Afocha &rarr;",
                "stats": f"❤️ {p.likes_count or 0} • 💬 {p.comments_count or 0}",
                "id": p.name
            })

    # 2. Products & Services from Magala / WebShop
    if filter_type in ("all", "products"):
        prod_filters = {}
        if search:
            prod_filters["web_item_name"] = ["like", f"%{search}%"]

        items = frappe.get_all(
            "Website Item",
            filters=prod_filters,
            fields=["name", "web_item_name", "item_group", "website_image", "short_description", "route"],
            order_by="creation desc",
            limit_start=0 if filter_type == "all" else start,
            limit_page_length=4 if filter_type == "all" else limit
        )
        for itm in items:
            feed_items.append({
                "type": "product",
                "badge": f"🛍️ {itm.item_group or 'Product'}",
                "badge_class": "badge-product",
                "title": itm.web_item_name or itm.name,
                "subtitle": itm.item_group or "Magala Marketplace",
                "content": itm.short_description or "Available now on MagalaShop with nationwide delivery across Ethiopia.",
                "image": itm.website_image if itm.website_image and itm.website_image != "None" else None,
                "price": None,
                "action_url": f"/{itm.route}" if itm.route else "/all-products",
                "action_label": "Order on Magala &rarr;",
                "stats": "⚡ Instant Order",
                "id": itm.name
            })

    # 3. Blog Articles & Insights from Tibeb
    if filter_type in ("all", "blogs"):
        blog_filters = {}
        if search:
            blog_filters["title"] = ["like", f"%{search}%"]

        blogs = frappe.get_all(
            "Blog Post",
            filters=blog_filters,
            fields=["name", "title", "blogger", "blog_intro", "meta_image", "published_on", "route"],
            order_by="published_on desc, creation desc",
            limit_start=0 if filter_type == "all" else start,
            limit_page_length=2 if filter_type == "all" else limit
        )
        for b in blogs:
            feed_items.append({
                "type": "blog",
                "badge": "📝 Tibeb Article",
                "badge_class": "badge-blog",
                "title": b.title or "Business Insights",
                "subtitle": f"By {b.blogger or 'EthioBiz'} • {str(b.published_on) if b.published_on else 'Recent'}",
                "content": b.blog_intro or "Explore in-depth business analyses, ERP guides, and market trends.",
                "image": b.meta_image or None,
                "price": None,
                "action_url": f"/{b.route}" if b.route else "/tibeb",
                "action_label": "Read Article &rarr;",
                "stats": "📖 3 min read",
                "id": b.name
            })

    # 4. Courses from Dagu LMS
    if filter_type in ("all", "courses"):
        if frappe.db.exists("DocType", "LMS Course"):
            course_filters = {}
            if search:
                course_filters["title"] = ["like", f"%{search}%"]

            courses = frappe.get_all(
                "LMS Course",
                filters=course_filters,
                fields=["name", "title", "short_introduction", "image", "category"],
                order_by="creation desc",
                limit_start=0 if filter_type == "all" else start,
                limit_page_length=3 if filter_type == "all" else limit
            )
            for c in courses:
                feed_items.append({
                    "type": "course",
                    "badge": f"🎓 {c.category or 'Dagu Course'}",
                    "badge_class": "badge-course",
                    "title": c.title or c.name,
                    "subtitle": "Dagu Online Academy",
                    "content": c.short_introduction or "Master modern vocational, digital, and management skills with expert instruction.",
                    "image": c.image or None,
                    "price": None,
                    "action_url": f"/courses/{c.name}",
                    "action_label": "Enroll Course &rarr;",
                    "stats": "🎓 Certification",
                    "id": c.name
                })

    # 5. Bookable Resources from BizBooking
    if filter_type in ("all", "bookings"):
        if frappe.db.exists("DocType", "BizBooking Resource"):
            res_filters = {}
            if search:
                res_filters["resource_name"] = ["like", f"%{search}%"]

            resources = frappe.get_all(
                "BizBooking Resource",
                filters=res_filters,
                fields=["name", "resource_name", "company", "category", "base_rate", "description"],
                order_by="creation desc",
                limit_start=0 if filter_type == "all" else start,
                limit_page_length=3 if filter_type == "all" else limit
            )
            for r in resources:
                feed_items.append({
                    "type": "booking",
                    "badge": f"⚡ {r.category}",
                    "badge_class": "badge-booking",
                    "title": r.resource_name or "Service Resource",
                    "subtitle": f"Provider: {r.company}",
                    "content": r.description or f"Reserve {r.resource_name} with confirmed instant time slot booking.",
                    "image": None,
                    "price": f"{r.base_rate:,.2f} ETB" if r.base_rate else "Instant Booking",
                    "action_url": "/book",
                    "action_label": "Reserve Now &rarr;",
                    "stats": "📅 Live Slots",
                    "id": r.name
                })

    return {
        "status": "success",
        "total_returned": len(feed_items),
        "start": start,
        "filter_type": filter_type,
        "has_more": len(feed_items) >= (3 if filter_type == "all" else limit),
        "items": feed_items
    }
