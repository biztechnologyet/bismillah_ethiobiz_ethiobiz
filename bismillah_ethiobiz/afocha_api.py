import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_social_feed(category=None, limit=50, start=0):
    """Returns the latest public AFOCHA social posts for the home feed and social page."""
    filters = {}
    if category and category.strip() and category.strip() != "All":
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
        limit_start=int(start),
        limit_page_length=int(limit)
    )

    return {
        "status": "success",
        "total": len(posts),
        "posts": posts
    }

@frappe.whitelist(allow_guest=True)
def create_social_post(author_name=None, author_handle=None, content=None, category_tag="Business & Trade", post_image=None):
    """Creates a new post on the AFOCHA social feed."""
    # Handle both JSON body and form parameters
    if not author_name or not content:
        # Check frappe.form_dict
        author_name = author_name or frappe.form_dict.get("author_name")
        author_handle = author_handle or frappe.form_dict.get("author_handle")
        content = content or frappe.form_dict.get("content")
        category_tag = category_tag or frappe.form_dict.get("category_tag", "Business & Trade")
        post_image = post_image or frappe.form_dict.get("post_image")

    if not author_name or not content:
        frappe.throw(_("Author Name and Post Content are required."))

    # Generate document ignoring guest permission restrictions
    doc = frappe.get_doc({
        "doctype": "Afocha Post",
        "author_name": str(author_name).strip(),
        "author_handle": str(author_handle).strip() if author_handle else "@ethiobiz",
        "content": str(content).strip(),
        "category_tag": str(category_tag).strip() if category_tag else "Business & Trade",
        "post_image": post_image,
        "post_date": frappe.utils.now_datetime(),
        "is_verified": 1 if any(k in (author_handle or "").lower() for k in ["@biz", "@ethio", "official"]) else 0,
        "likes_count": 0,
        "comments_count": 0,
        "shares_count": 0
    })
    doc.flags.ignore_permissions = True
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "message": "Post published successfully!",
        "post_name": doc.name,
        "post": {
            "name": doc.name,
            "author_name": doc.author_name,
            "author_handle": doc.author_handle,
            "content": doc.content,
            "category_tag": doc.category_tag,
            "post_date": str(doc.post_date),
            "is_verified": doc.is_verified,
            "likes_count": 0,
            "comments_count": 0
        }
    }

@frappe.whitelist(allow_guest=True)
def like_social_post(post_id):
    """Increments the likes counter for an Afocha post."""
    post_id = post_id or frappe.form_dict.get("post_id")
    if not post_id or not frappe.db.exists("Afocha Post", post_id):
        frappe.throw(_("Post not found."))

    current_likes = frappe.db.get_value("Afocha Post", post_id, "likes_count") or 0
    new_likes = current_likes + 1
    frappe.db.set_value("Afocha Post", post_id, "likes_count", new_likes)
    frappe.db.commit()

    return {
        "status": "success",
        "likes_count": new_likes
    }
