import json
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_social_feed(category=None, limit=50, start=0, post_id=None):
    """Returns the latest public AFOCHA social posts or a single post with comments."""
    category = category or frappe.form_dict.get("category")
    post_id = post_id or frappe.form_dict.get("post_id") or frappe.form_dict.get("post")

    # If single post requested
    if post_id:
        if not frappe.db.exists("Afocha Post", post_id):
            frappe.throw(_("Post not found."))
        
        p = frappe.get_doc("Afocha Post", post_id)
        comments = []
        if frappe.db.exists("DocType", "Afocha Comment"):
            comments = frappe.get_all(
                "Afocha Comment",
                filters={"parent_post": post_id},
                fields=["name", "author_name", "author_handle", "comment_text", "comment_date", "likes_count"],
                order_by="comment_date asc"
            )

        poll_data = parse_poll_data(p)

        return {
            "status": "success",
            "is_single": True,
            "post": {
                "name": p.name,
                "author_name": p.author_name,
                "author_handle": p.author_handle,
                "is_verified": p.is_verified,
                "post_date": str(p.post_date),
                "category_tag": p.category_tag,
                "content": p.content,
                "post_image": p.post_image,
                "video_url": p.video_url,
                "is_poll": p.is_poll,
                "poll_question": p.poll_question,
                "poll_data": poll_data,
                "likes_count": p.likes_count or 0,
                "comments_count": p.comments_count or len(comments),
                "shares_count": p.shares_count or 0
            },
            "comments": comments
        }

    # Feed listing
    filters = {}
    if category and category.strip() and category.strip() != "All":
        filters["category_tag"] = category.strip()

    posts = frappe.get_all(
        "Afocha Post",
        filters=filters,
        fields=[
            "name", "author_name", "author_handle", "is_verified",
            "post_date", "category_tag", "content", "post_image",
            "video_url", "is_poll", "poll_question", "poll_options_json", "poll_votes_json",
            "likes_count", "comments_count", "shares_count", "pinned"
        ],
        order_by="pinned desc, post_date desc",
        limit_start=int(start or 0),
        limit_page_length=int(limit or 50)
    )

    enriched_posts = []
    for p in posts:
        poll_info = None
        if p.get("is_poll"):
            poll_info = parse_poll_data(p)
        
        enriched_posts.append({
            "name": p.name,
            "author_name": p.author_name,
            "author_handle": p.author_handle,
            "is_verified": p.is_verified,
            "post_date": str(p.post_date),
            "category_tag": p.category_tag,
            "content": p.content,
            "post_image": p.post_image,
            "video_url": p.video_url,
            "is_poll": p.is_poll,
            "poll_question": p.poll_question,
            "poll_data": poll_info,
            "likes_count": p.likes_count or 0,
            "comments_count": p.comments_count or 0,
            "shares_count": p.shares_count or 0,
            "permalink": f"/social?post={p.name}"
        })

    return {
        "status": "success",
        "total": len(enriched_posts),
        "posts": enriched_posts
    }

def parse_poll_data(post_doc):
    """Helper to parse poll options and calculate vote percentages."""
    options_raw = getattr(post_doc, "poll_options_json", None) or post_doc.get("poll_options_json")
    votes_raw = getattr(post_doc, "poll_votes_json", None) or post_doc.get("poll_votes_json")

    try:
        options = json.loads(options_raw) if options_raw else []
    except Exception:
        options = []

    try:
        votes = json.loads(votes_raw) if votes_raw else {}
    except Exception:
        votes = {}

    total_votes = sum(votes.values()) if votes else 0
    poll_results = []

    for idx, opt in enumerate(options):
        count = votes.get(str(idx), 0)
        pct = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        poll_results.append({
            "index": idx,
            "text": opt,
            "votes": count,
            "percentage": pct
        })

    return {
        "question": getattr(post_doc, "poll_question", None) or post_doc.get("poll_question"),
        "total_votes": total_votes,
        "options": poll_results
    }

@frappe.whitelist(allow_guest=True)
def create_social_post(author_name=None, author_handle=None, content=None, category_tag="Business & Trade", post_image=None, video_url=None, is_poll=0, poll_question=None, poll_options=None):
    """Creates a new post on AFOCHA with rich media & poll support."""
    author_name = author_name or frappe.form_dict.get("author_name")
    author_handle = author_handle or frappe.form_dict.get("author_handle")
    content = content or frappe.form_dict.get("content")
    category_tag = category_tag or frappe.form_dict.get("category_tag", "Business & Trade")
    post_image = post_image or frappe.form_dict.get("post_image")
    video_url = video_url or frappe.form_dict.get("video_url")
    is_poll = cint(is_poll or frappe.form_dict.get("is_poll", 0))
    poll_question = poll_question or frappe.form_dict.get("poll_question")
    poll_options = poll_options or frappe.form_dict.get("poll_options")

    if not author_name or not content:
        frappe.throw(_("Author Name and Post Content are required."))

    poll_options_json = None
    poll_votes_json = None
    if is_poll and poll_options:
        if isinstance(poll_options, str):
            try:
                opts = json.loads(poll_options)
            except Exception:
                opts = [o.strip() for o in poll_options.split("\n") if o.strip()]
        else:
            opts = poll_options
        
        poll_options_json = json.dumps(opts)
        poll_votes_json = json.dumps({str(i): 0 for i in range(len(opts))})

    doc = frappe.get_doc({
        "doctype": "Afocha Post",
        "author_name": str(author_name).strip(),
        "author_handle": str(author_handle).strip() if author_handle else "@ethiobiz",
        "content": str(content).strip(),
        "category_tag": str(category_tag).strip() if category_tag else "Business & Trade",
        "post_image": post_image,
        "video_url": video_url,
        "is_poll": is_poll,
        "poll_question": poll_question if is_poll else None,
        "poll_options_json": poll_options_json,
        "poll_votes_json": poll_votes_json,
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
        "permalink": f"/social?post={doc.name}"
    }

@frappe.whitelist(allow_guest=True)
def add_post_comment(post_id=None, author_name=None, author_handle=None, comment_text=None):
    """Adds a new comment to an Afocha Post."""
    post_id = post_id or frappe.form_dict.get("post_id")
    author_name = author_name or frappe.form_dict.get("author_name") or "Community Member"
    author_handle = author_handle or frappe.form_dict.get("author_handle") or "@community"
    comment_text = comment_text or frappe.form_dict.get("comment_text")

    if not post_id or not comment_text:
        frappe.throw(_("Post ID and Comment Text are required."))

    if not frappe.db.exists("Afocha Post", post_id):
        frappe.throw(_("Post does not exist."))

    # Insert comment doc
    comment_doc = frappe.get_doc({
        "doctype": "Afocha Comment",
        "parent_post": post_id,
        "author_name": str(author_name).strip(),
        "author_handle": str(author_handle).strip(),
        "comment_text": str(comment_text).strip(),
        "comment_date": frappe.utils.now_datetime(),
        "likes_count": 0
    })
    comment_doc.flags.ignore_permissions = True
    comment_doc.insert(ignore_permissions=True)

    # Increment comments_count on parent post
    current_count = frappe.db.get_value("Afocha Post", post_id, "comments_count") or 0
    new_count = current_count + 1
    frappe.db.set_value("Afocha Post", post_id, "comments_count", new_count)
    frappe.db.commit()

    return {
        "status": "success",
        "message": "Comment added successfully!",
        "comments_count": new_count,
        "comment": {
            "name": comment_doc.name,
            "author_name": comment_doc.author_name,
            "author_handle": comment_doc.author_handle,
            "comment_text": comment_doc.comment_text,
            "comment_date": str(comment_doc.comment_date)
        }
    }

@frappe.whitelist(allow_guest=True)
def vote_poll(post_id=None, option_index=None):
    """Casts a vote on an interactive Afocha poll and returns updated percentages."""
    post_id = post_id or frappe.form_dict.get("post_id")
    option_index = option_index if option_index is not None else frappe.form_dict.get("option_index")

    if not post_id or option_index is None:
        frappe.throw(_("Post ID and Option Index are required."))

    if not frappe.db.exists("Afocha Post", post_id):
        frappe.throw(_("Post not found."))

    post = frappe.get_doc("Afocha Post", post_id)
    if not post.is_poll or not post.poll_options_json:
        frappe.throw(_("This post is not an active poll."))

    try:
        votes = json.loads(post.poll_votes_json) if post.poll_votes_json else {}
    except Exception:
        votes = {}

    opt_key = str(option_index)
    votes[opt_key] = votes.get(opt_key, 0) + 1

    post.poll_votes_json = json.dumps(votes)
    post.flags.ignore_permissions = True
    post.save()
    frappe.db.commit()

    updated_poll = parse_poll_data(post)

    return {
        "status": "success",
        "message": "Vote recorded!",
        "poll_data": updated_poll
    }

@frappe.whitelist(allow_guest=True)
def like_social_post(post_id=None):
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

def cint(val):
    try:
        return int(val)
    except Exception:
        return 0
