import frappe
from frappe import _
import json
import time

def ensure_tables_exist():
    """Ensure MariaDB tables for Walta Forum exist."""
    frappe.db.sql("""
        CREATE TABLE IF NOT EXISTS `tabWalta Forum Topic` (
            `name` VARCHAR(140) NOT NULL PRIMARY KEY,
            `creation` DATETIME(6),
            `modified` DATETIME(6),
            `modified_by` VARCHAR(140),
            `owner` VARCHAR(140),
            `docstatus` INT(1) DEFAULT 0,
            `parent` VARCHAR(140),
            `parentfield` VARCHAR(140),
            `parenttype` VARCHAR(140),
            `idx` INT(8) DEFAULT 0,
            `title` VARCHAR(255) NOT NULL,
            `category` VARCHAR(140) DEFAULT 'General Discussion',
            `author_name` VARCHAR(140),
            `author_handle` VARCHAR(140),
            `author_image` TEXT,
            `company` VARCHAR(140),
            `is_verified` INT(1) DEFAULT 1,
            `content` LONGTEXT,
            `tags` VARCHAR(255),
            `likes_count` INT(8) DEFAULT 0,
            `replies_count` INT(8) DEFAULT 0,
            `views_count` INT(8) DEFAULT 0,
            `is_pinned` INT(1) DEFAULT 0,
            `is_closed` INT(1) DEFAULT 0,
            `last_reply_on` DATETIME(6),
            INDEX (`category`),
            INDEX (`creation`),
            INDEX (`likes_count`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    frappe.db.sql("""
        CREATE TABLE IF NOT EXISTS `tabWalta Forum Reply` (
            `name` VARCHAR(140) NOT NULL PRIMARY KEY,
            `creation` DATETIME(6),
            `modified` DATETIME(6),
            `modified_by` VARCHAR(140),
            `owner` VARCHAR(140),
            `docstatus` INT(1) DEFAULT 0,
            `parent` VARCHAR(140),
            `parentfield` VARCHAR(140),
            `parenttype` VARCHAR(140),
            `idx` INT(8) DEFAULT 0,
            `topic` VARCHAR(140) NOT NULL,
            `author_name` VARCHAR(140),
            `author_handle` VARCHAR(140),
            `author_image` TEXT,
            `reply_text` LONGTEXT,
            `reply_date` DATETIME(6),
            INDEX (`topic`),
            INDEX (`creation`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def get_logged_user_info():
    user = frappe.session.user
    if not user or user == "Guest":
        return {
            "is_logged_in": False,
            "full_name": "Guest Explorer",
            "handle": "@guest",
            "user_image": "/assets/frappe/images/default-avatar.png",
            "company": "Public Visitor",
            "is_verified": False
        }

    user_doc = frappe.get_doc("User", user)
    full_name = user_doc.full_name or user_doc.first_name or user
    image = user_doc.user_image or "/assets/frappe/images/default-avatar.png"
    handle = f"@{user.split('@')[0]}"

    company = None
    if frappe.db.exists("DocType", "Employee"):
        emp = frappe.db.get_value("Employee", {"user_id": user}, "company")
        if emp:
            company = emp

    if not company:
        company = "EthioBiz Enterprise"

    return {
        "is_logged_in": True,
        "full_name": full_name,
        "handle": handle,
        "user_image": image,
        "company": company,
        "is_verified": True
    }

@frappe.whitelist(allow_guest=True)
def get_forum_topics(category=None, search=None, sort="latest", limit=30, start=0):
    ensure_tables_exist()

    conditions = []
    values = []

    if category and category != "all":
        conditions.append("category = %s")
        values.append(category)

    if search:
        conditions.append("(title LIKE %s OR content LIKE %s OR tags LIKE %s)")
        s_val = f"%{search}%"
        values.extend([s_val, s_val, s_val])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    order_by = "is_pinned DESC, creation DESC"
    if sort == "popular":
        order_by = "is_pinned DESC, likes_count DESC, replies_count DESC"
    elif sort == "replies":
        order_by = "is_pinned DESC, replies_count DESC"

    query = f"""
        SELECT 
            name, title, category, author_name, author_handle, author_image,
            company, is_verified, content, tags, likes_count, replies_count,
            views_count, is_pinned, is_closed, creation, last_reply_on
        FROM `tabWalta Forum Topic`
        {where_clause}
        ORDER BY {order_by}
        LIMIT %s OFFSET %s
    """
    values.extend([int(limit), int(start)])

    topics = frappe.db.sql(query, values, as_dict=True)

    # Format dates
    for t in topics:
        t["creation_formatted"] = frappe.utils.pretty_date(t.creation) if t.creation else ""
        t["last_reply_formatted"] = frappe.utils.pretty_date(t.last_reply_on) if t.last_reply_on else t["creation_formatted"]
        # Snippet
        clean_text = frappe.utils.strip_html(t.content or "")
        t["snippet"] = (clean_text[:140] + "...") if len(clean_text) > 140 else clean_text

    # Category stats count
    category_counts = frappe.db.sql("""
        SELECT category, COUNT(*) as count 
        FROM `tabWalta Forum Topic` 
        GROUP BY category
    """, as_dict=True)

    total_topics = frappe.db.sql("SELECT COUNT(*) as cnt FROM `tabWalta Forum Topic`")[0][0]

    return {
        "topics": topics,
        "category_counts": {c["category"]: c["count"] for c in category_counts},
        "total_topics": total_topics
    }

@frappe.whitelist(allow_guest=True)
def get_forum_topic_detail(topic_id):
    ensure_tables_exist()

    if not topic_id or not frappe.db.exists("Walta Forum Topic", topic_id):
        return {"error": "Topic not found"}

    # Increment views
    frappe.db.sql("""
        UPDATE `tabWalta Forum Topic` 
        SET views_count = views_count + 1 
        WHERE name = %s
    """, (topic_id,))
    frappe.db.commit()

    topic = frappe.db.sql("""
        SELECT * FROM `tabWalta Forum Topic` WHERE name = %s
    """, (topic_id,), as_dict=True)[0]

    topic["creation_formatted"] = frappe.utils.pretty_date(topic.creation) if topic.creation else ""

    replies = frappe.db.sql("""
        SELECT * FROM `tabWalta Forum Reply` 
        WHERE topic = %s 
        ORDER BY creation ASC
    """, (topic_id,), as_dict=True)

    for r in replies:
        r["creation_formatted"] = frappe.utils.pretty_date(r.creation) if r.creation else ""

    return {
        "topic": topic,
        "replies": replies
    }

@frappe.whitelist()
def create_forum_topic(title=None, category="General Discussion", content=None, tags=None):
    ensure_tables_exist()
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Authentication required. Please log in to start a forum discussion."), frappe.PermissionError)

    title = (title or frappe.form_dict.get("title") or "").strip()
    content = (content or frappe.form_dict.get("content") or "").strip()
    category = category or frappe.form_dict.get("category") or "General Discussion"
    tags = tags or frappe.form_dict.get("tags") or ""

    if not title or not content:
        frappe.throw(_("Topic title and discussion content are required."))

    user_info = get_logged_user_info()
    name = f"TOPIC-{int(time.time())}-{frappe.generate_hash(length=4).upper()}"

    now = frappe.utils.now()
    frappe.db.sql("""
        INSERT INTO `tabWalta Forum Topic` (
            name, creation, modified, modified_by, owner,
            title, category, author_name, author_handle, author_image,
            company, is_verified, content, tags, likes_count, replies_count,
            views_count, is_pinned, is_closed, last_reply_on
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, 0, 0,
            1, 0, 0, %s
        )
    """, (
        name, now, now, user, user,
        title, category, user_info["full_name"], user_info["handle"], user_info["user_image"],
        user_info["company"], 1 if user_info["is_verified"] else 0, content, tags, now
    ))
    frappe.db.commit()

    return {"status": "success", "name": name}

@frappe.whitelist()
def add_forum_reply(topic_id=None, reply_text=None):
    ensure_tables_exist()
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Authentication required. Please log in to post replies."), frappe.PermissionError)

    topic_id = topic_id or frappe.form_dict.get("topic_id")
    reply_text = (reply_text or frappe.form_dict.get("reply_text") or "").strip()

    if not topic_id or not reply_text:
        frappe.throw(_("Topic ID and reply content are required."))

    user_info = get_logged_user_info()
    name = f"REPLY-{int(time.time())}-{frappe.generate_hash(length=4).upper()}"
    now = frappe.utils.now()

    frappe.db.sql("""
        INSERT INTO `tabWalta Forum Reply` (
            name, creation, modified, modified_by, owner,
            topic, author_name, author_handle, author_image, reply_text, reply_date
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """, (
        name, now, now, user, user,
        topic_id, user_info["full_name"], user_info["handle"], user_info["user_image"], reply_text, now
    ))

    # Update topic reply count and last reply timestamp
    frappe.db.sql("""
        UPDATE `tabWalta Forum Topic` 
        SET replies_count = replies_count + 1, last_reply_on = %s 
        WHERE name = %s
    """, (now, topic_id))
    frappe.db.commit()

    return {"status": "success", "name": name}

@frappe.whitelist(allow_guest=True)
def like_forum_topic(topic_id=None):
    ensure_tables_exist()
    topic_id = topic_id or frappe.form_dict.get("topic_id")
    if not topic_id:
        return {"error": "Topic ID missing"}

    frappe.db.sql("""
        UPDATE `tabWalta Forum Topic` 
        SET likes_count = likes_count + 1 
        WHERE name = %s
    """, (topic_id,))
    frappe.db.commit()

    cnt = frappe.db.sql("SELECT likes_count FROM `tabWalta Forum Topic` WHERE name = %s", (topic_id,))[0][0]
    return {"status": "success", "likes_count": cnt}
