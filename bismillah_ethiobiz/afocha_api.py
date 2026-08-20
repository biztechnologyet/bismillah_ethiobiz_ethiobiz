import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_social_feed(category=None, limit=20):
    """Returns the latest public AFOCHA social posts for the home feed and social page."""
    filters = {}
    if category and category.strip():
        filters["category_tag"] = category.strip()

    posts = frappe.get_all(
        "Afocha Post",
        filters=filters,
        fields=[
            "name", "author_name", "author_handle", "is_verified",
            "post_date", "category_tag", "content", "post_image",
            "video_url", "likes_count", "comments_count", "shares_count", "pinned"
        ],
        order_by="pinned desc, post_date desc",
        limit=limit
    )

    return {
        "status": "success",
        "total": len(posts),
        "posts": posts
    }

@frappe.whitelist(allow_guest=True)
def create_social_post(author_name, author_handle, content, category_tag="Business & Trade", post_image=None):
    """Creates a new post on the AFOCHA social feed."""
    if not author_name or not content:
        frappe.throw(_("Author Name and Content are required."))

    doc = frappe.get_doc({
        "doctype": "Afocha Post",
        "author_name": author_name.strip(),
        "author_handle": author_handle.strip() if author_handle else "@user",
        "content": content.strip(),
        "category_tag": category_tag,
        "post_image": post_image,
        "post_date": frappe.utils.now_datetime(),
        "is_verified": 1 if "@biz" in (author_handle or "").lower() else 0,
        "likes_count": 0,
        "comments_count": 0,
        "shares_count": 0
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "message": "Post published successfully!",
        "post_name": doc.name
    }

@frappe.whitelist(allow_guest=True)
def like_social_post(post_id):
    """Increments the likes counter for an Afocha post."""
    if not frappe.db.exists("Afocha Post", post_id):
        frappe.throw(_("Post not found."))

    current_likes = frappe.db.get_value("Afocha Post", post_id, "likes_count") or 0
    new_likes = current_likes + 1
    frappe.db.set_value("Afocha Post", post_id, "likes_count", new_likes)
    frappe.db.commit()

    return {
        "status": "success",
        "likes_count": new_likes
    }
