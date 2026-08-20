import json
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_logged_user_info():
    """Returns the logged-in user profile with company, avatar image, and verified status."""
    user = frappe.session.user
    if not user or user == "Guest":
        return {
            "is_logged_in": False,
            "user": "Guest",
            "full_name": "EthioBiz Community Member",
            "company": "EthioBiz Enterprise",
            "handle": "@community",
            "user_image": "/assets/frappe/images/default-avatar.png",
            "is_verified": False
        }

    user_doc = frappe.get_doc("User", user)
    full_name = user_doc.full_name or user_doc.name
    if user == "Administrator":
        full_name = "EthioBiz Official"

    # Resolve company & employee image if any
    company = "EthioBiz Enterprise"
    user_image = user_doc.user_image

    emp = frappe.db.get_value("Employee", {"user_id": user}, ["name", "company", "image"], as_dict=True)
    if emp:
        if emp.company:
            company = emp.company
        if not user_image and emp.image:
            user_image = emp.image

    if not user_image:
        user_image = "/assets/frappe/images/default-avatar.png"

    handle = f"@{user.split('@')[0]}"

    return {
        "is_logged_in": True,
        "user": user,
        "full_name": full_name,
        "company": company,
        "handle": handle,
        "user_image": user_image,
        "is_verified": True
    }

@frappe.whitelist(allow_guest=True)
def get_social_feed(category=None, limit=20, start=0, post_id=None):
    """Retrieves Afocha posts with comments, poll results, and user profile images."""
    if post_id:
        if not frappe.db.exists("Afocha Post", post_id):
            return {"post": None, "comments": []}
        
        post = frappe.get_doc("Afocha Post", post_id)
        post_data = {
            "name": post.name,
            "author_name": post.author_name,
            "author_handle": post.author_handle or "@ethiobiz",
            "author_image": post.author_image or "/assets/frappe/images/default-avatar.png",
            "company": post.company or "EthioBiz Enterprise",
            "category_tag": post.category_tag,
            "post_date": str(post.post_date or post.creation),
            "is_verified": post.is_verified,
            "likes_count": post.likes_count or 0,
            "comments_count": post.comments_count or 0,
            "content": post.content,
            "post_image": post.post_image,
            "video_url": post.video_url,
            "is_poll": post.is_poll,
            "poll_data": _format_poll_data(post)
        }

        comments = []
        if frappe.db.exists("DocType", "Afocha Comment"):
            cmts = frappe.get_all(
                "Afocha Comment",
                filters={"parent_post": post.name},
                fields=["name", "author_name", "author_handle", "author_image", "comment_text", "comment_date"],
                order_by="creation asc"
            )
            for c in cmts:
                comments.append({
                    "name": c.name,
                    "author_name": c.author_name,
                    "author_handle": c.author_handle,
                    "author_image": c.author_image or "/assets/frappe/images/default-avatar.png",
                    "comment_text": c.comment_text,
                    "comment_date": str(c.comment_date or "")
                })

        return {"post": post_data, "comments": comments}

    # Fetch feed list
    filters = {}
    if category and category != "all":
        filters["category_tag"] = category

    posts = frappe.get_all(
        "Afocha Post",
        filters=filters,
        fields=[
            "name", "author_name", "author_handle", "author_image", "company",
            "category_tag", "post_date", "is_verified", "likes_count", "comments_count",
            "content", "post_image", "video_url", "is_poll", "creation"
        ],
        order_by="creation desc",
        limit_page_length=int(limit),
        limit_start=int(start)
    )

    feed = []
    for p in posts:
        poll_data = None
        if p.is_poll:
            doc = frappe.get_doc("Afocha Post", p.name)
            poll_data = _format_poll_data(doc)

        feed.append({
            "name": p.name,
            "author_name": p.author_name,
            "author_handle": p.author_handle or "@ethiobiz",
            "author_image": p.author_image or "/assets/frappe/images/default-avatar.png",
            "company": p.company or "EthioBiz Enterprise",
            "category_tag": p.category_tag,
            "post_date": str(p.post_date or p.creation),
            "is_verified": p.is_verified,
            "likes_count": p.likes_count or 0,
            "comments_count": p.comments_count or 0,
            "content": p.content,
            "post_image": p.post_image,
            "video_url": p.video_url,
            "is_poll": p.is_poll,
            "poll_data": poll_data
        })

    return {"posts": feed}

def _format_poll_data(post_doc):
    if not post_doc.is_poll or not post_doc.poll_options_json:
        return None
    try:
        options = json.loads(post_doc.poll_options_json)
        votes = json.loads(post_doc.poll_votes_json) if post_doc.poll_votes_json else [0] * len(options)
    except Exception:
        return None

    total_votes = sum(votes)
    formatted_opts = []
    for idx, opt in enumerate(options):
        v = votes[idx] if idx < len(votes) else 0
        pct = round((v / total_votes * 100), 1) if total_votes > 0 else 0
        formatted_opts.append({
            "index": idx,
            "text": opt,
            "votes": v,
            "percentage": pct
        })

    return {
        "question": post_doc.poll_question,
        "total_votes": total_votes,
        "options": formatted_opts
    }

@frappe.whitelist(allow_guest=True)
def create_social_post(
    author_name=None, author_handle=None, category_tag="Business & Trade",
    content=None, post_image=None, video_url=None, is_poll=0,
    poll_question=None, poll_options=None
):
    """Creates a post enforcing logged-in user profile, company, and avatar."""
    content = content or frappe.form_dict.get("content")
    if not content:
        frappe.throw(_("Post content is required."))

    # Resolve logged-in user identity
    user_info = get_logged_user_info()
    if user_info.get("is_logged_in"):
        author_name = user_info["full_name"]
        author_handle = user_info["handle"]
        author_image = user_info["user_image"]
        company = user_info["company"]
        is_verified = 1
    else:
        author_name = author_name or frappe.form_dict.get("author_name") or "Community Member"
        author_handle = author_handle or frappe.form_dict.get("author_handle") or "@community"
        author_image = "/assets/frappe/images/default-avatar.png"
        company = "EthioBiz Community"
        is_verified = 0

    category_tag = category_tag or frappe.form_dict.get("category_tag") or "Business & Trade"
    post_image = post_image or frappe.form_dict.get("post_image")
    video_url = video_url or frappe.form_dict.get("video_url")
    is_poll = int(is_poll or frappe.form_dict.get("is_poll") or 0)
    poll_question = poll_question or frappe.form_dict.get("poll_question")
    poll_options = poll_options or frappe.form_dict.get("poll_options")

    post_doc = frappe.get_doc({
        "doctype": "Afocha Post",
        "author_name": author_name,
        "author_handle": author_handle,
        "author_image": author_image,
        "company": company,
        "category_tag": category_tag,
        "post_date": frappe.utils.now(),
        "is_verified": is_verified,
        "content": content,
        "post_image": post_image,
        "video_url": video_url,
        "is_poll": is_poll,
        "poll_question": poll_question,
        "poll_options_json": poll_options if is_poll else None,
        "poll_votes_json": json.dumps([0]*len(json.loads(poll_options))) if (is_poll and poll_options) else None
    })
    post_doc.flags.ignore_permissions = True
    post_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success", "name": post_doc.name}

@frappe.whitelist(allow_guest=True)
def add_post_comment(post_id=None, author_name=None, author_handle=None, comment_text=None):
    """Adds a comment capturing user profile."""
    post_id = post_id or frappe.form_dict.get("post_id")
    comment_text = comment_text or frappe.form_dict.get("comment_text")

    if not post_id or not comment_text:
        frappe.throw(_("Post ID and comment text are required."))

    user_info = get_logged_user_info()
    if user_info.get("is_logged_in"):
        author_name = user_info["full_name"]
        author_handle = user_info["handle"]
        author_image = user_info["user_image"]
    else:
        author_name = author_name or frappe.form_dict.get("author_name") or "Community Member"
        author_handle = author_handle or frappe.form_dict.get("author_handle") or "@community"
        author_image = "/assets/frappe/images/default-avatar.png"

    cmt = frappe.get_doc({
        "doctype": "Afocha Comment",
        "parent_post": post_id,
        "author_name": author_name,
        "author_handle": author_handle,
        "author_image": author_image,
        "comment_text": comment_text,
        "comment_date": frappe.utils.now()
    })
    cmt.flags.ignore_permissions = True
    cmt.insert(ignore_permissions=True)

    # Increment comment count
    post = frappe.get_doc("Afocha Post", post_id)
    post.comments_count = (post.comments_count or 0) + 1
    post.flags.ignore_permissions = True
    post.save(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success", "comments_count": post.comments_count}

@frappe.whitelist(allow_guest=True)
def like_social_post(post_id=None):
    post_id = post_id or frappe.form_dict.get("post_id")
    if not post_id or not frappe.db.exists("Afocha Post", post_id):
        return {"likes_count": 0}
    
    post = frappe.get_doc("Afocha Post", post_id)
    post.likes_count = (post.likes_count or 0) + 1
    post.flags.ignore_permissions = True
    post.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "likes_count": post.likes_count}

@frappe.whitelist(allow_guest=True)
def vote_poll(post_id=None, option_index=0):
    post_id = post_id or frappe.form_dict.get("post_id")
    option_index = int(option_index or frappe.form_dict.get("option_index") or 0)

    if not post_id or not frappe.db.exists("Afocha Post", post_id):
        return {"status": "error"}

    post = frappe.get_doc("Afocha Post", post_id)
    if not post.is_poll or not post.poll_options_json:
        return {"status": "error"}

    options = json.loads(post.poll_options_json)
    votes = json.loads(post.poll_votes_json) if post.poll_votes_json else [0] * len(options)

    if option_index < len(votes):
        votes[option_index] += 1
        post.poll_votes_json = json.dumps(votes)
        post.flags.ignore_permissions = True
        post.save(ignore_permissions=True)
        frappe.db.commit()

    return {"status": "success", "poll_data": _format_poll_data(post)}
