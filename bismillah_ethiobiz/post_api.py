# -*- coding: utf-8 -*-
"""
BISMALLAH AR-RAHMAN AR-RAHIM
EthioBiz Immersive Post Viewer API
==================================

The single-post page is a full-viewport, X.com-style reader:

* one post per screen, snap-scrolling vertically between posts
* a slide-in comments drawer
* a full-screen "read full" overlay for trimmed bodies
* every feed family keeps its own CTA and accent colour

This module only supplies data/fragments to that page. The initial post is
still server-rendered by ``www/post.py`` so SEO and first paint do not depend
on JavaScript.
"""

from urllib.parse import quote

import frappe
from frappe.utils import cint

from bismillah_ethiobiz.smart_feed_api import get_personalized_feed


def _login_url(doctype, name, feed_type):
    target = "/post?doctype=%s&name=%s&ft=%s" % (
        quote(str(doctype or ""), safe=""),
        quote(str(name or ""), safe=""),
        quote(str(feed_type or ""), safe=""),
    )
    return "/login?redirect-to=" + quote(target, safe="/?=&")


def _summary(post):
    style = post.get("style") or {}
    return {
        "doctype": post.get("doctype") or "",
        "name": post.get("name") or "",
        "feed_type": post.get("feed_type") or "all",
        "post_url": post.get("share_path") or "",
        "title": post.get("title") or "",
        "image": post.get("image") or "",
        "icon": style.get("icon") or "",
        "type_label": style.get("label") or post.get("portal_label") or "",
        "portal_label": post.get("portal_label") or "",
        "portal_url": post.get("portal_url") or "/",
        "can_engage": bool(post.get("can_engage")),
        "commentable": bool(post.get("commentable")),
        "likes_count": cint(post.get("likes_count")),
        "comments_count": cint(post.get("comments_count")),
        "reposts_count": cint(post.get("reposts_count")),
        "viewer_liked": bool(post.get("viewer_liked")),
        "viewer_reposted": bool(post.get("viewer_reposted")),
    }


def _queue_item(post):
    style = post.get("style") or {}
    return {
        "doctype": post.get("doctype") or "",
        "name": post.get("name") or "",
        "feed_type": post.get("feed_type") or "all",
        "post_url": post.get("share_path") or "",
        "title": post.get("title") or "",
        "image": post.get("image") or "",
        "icon": style.get("icon") or "",
        "type_label": style.get("label") or post.get("portal_label") or "",
        "portal_label": post.get("portal_label") or "",
    }


@frappe.whitelist(allow_guest=True)
def get_post_queue(doctype=None, name=None, ft=None, start=0, limit=16):
    """Ordered list of posts for vertical swipe navigation.

    The first request (start=0) puts the post currently open at the head of the
    queue, then follows the same personalised feed the homepage uses. Later
    requests simply continue that feed.
    """
    start = max(0, cint(start) or 0)
    limit = max(1, min(cint(limit) or 16, 30))

    from bismillah_ethiobiz.www.post import load_post

    items = []
    seen = set()

    def add(item):
        dt = (item.get("doctype") or "").strip()
        dn = (item.get("name") or "").strip()
        if not dt or not dn:
            return
        key = (dt, dn)
        if key in seen:
            return
        seen.add(key)
        items.append(item)

    if start == 0 and doctype and name:
        try:
            current = load_post(doctype, name, ft)
            if current.get("found"):
                add(_queue_item(current))
        except Exception:
            frappe.logger("post_api").warning(
                "Could not load current post for queue: %s %s", doctype, name
            )

    try:
        feed = get_personalized_feed(start=0, limit=60)
        feed_items = feed.get("items") or []
    except Exception:
        feed_items = []
        frappe.logger("post_api").warning("Feed queue lookup failed", exc_info=True)

    for item in feed_items:
        if not item.get("doctype") or not item.get("docname"):
            continue
        add({
            "doctype": item.get("doctype"),
            "name": item.get("docname"),
            "feed_type": item.get("feed_type") or "all",
            "post_url": item.get("post_url") or "",
            "title": item.get("title") or "",
            "image": item.get("image") or "",
            "icon": item.get("icon") or "",
            "type_label": item.get("badge") or item.get("feed_type") or "",
            "portal_label": item.get("feed_type") or "",
        })

    page = items[start:start + limit]
    return {
        "status": "success",
        "items": page,
        "start": start,
        "limit": limit,
        "total": len(items),
        "has_more": (start + limit) < len(items),
    }


@frappe.whitelist(allow_guest=True)
def get_post_slide(doctype=None, name=None, ft=None):
    """Render one slide fragment for the immersive viewer."""
    from bismillah_ethiobiz.www.post import load_post

    post = load_post(doctype, name, ft)
    login_url = _login_url(post.get("doctype") or doctype, post.get("name") or name,
                           post.get("feed_type") or ft)
    try:
        html = frappe.render_template(
            "templates/includes/ebpost_slide.html",
            {
                "post": post,
                "labels": post.get("labels") or {},
                "login_url": login_url,
                "is_logged_in": frappe.session.user not in (None, "", "Guest"),
            },
        )
    except Exception:
        frappe.logger("post_api").error(
            "Slide render failed for %s %s", doctype, name, exc_info=True
        )
        return {
            "status": "error",
            "message": "Could not render this post.",
            "post": _summary(post),
            "html": "",
        }

    return {
        "status": "success",
        "post": _summary(post),
        "html": html,
        "login_url": login_url,
    }


@frappe.whitelist(allow_guest=True)
def get_post_comments(doctype=None, name=None, ft=None):
    """Comments for the drawer. Forum topics return their native replies."""
    doctype = (doctype or "").strip()
    name = (name or "").strip()
    if not doctype or not name:
        return {"status": "error", "message": "Missing post reference.", "comments": []}

    if doctype == "Walta Forum Topic":
        try:
            from bismillah_ethiobiz import walta_forum_api

            payload = walta_forum_api.get_forum_topic_detail(name) or {}
            replies = payload.get("replies") or []
        except Exception:
            replies = []
            frappe.logger("post_api").warning(
                "Forum replies lookup failed for %s", name, exc_info=True
            )
        comments = []
        for reply in replies:
            comments.append({
                "author": reply.get("author_name") or reply.get("author") or "Walta member",
                "avatar": reply.get("author_image") or reply.get("avatar") or "",
                "time_ago": reply.get("creation_formatted") or reply.get("time_ago") or "",
                "content": reply.get("reply_text") or reply.get("content") or "",
            })
        return {
            "status": "success",
            "comments": comments,
            "count": len(comments),
            "commentable": False,
            "can_engage": False,
            "forum": True,
        }

    from bismillah_ethiobiz import feed_engagement_api as eng

    commentable = bool(eng._is_commentable_doctype(doctype))
    can_engage = bool(eng._session_user())
    comments = []
    if commentable:
        try:
            thread = eng.get_comments(doctype=doctype, name=name, limit=50) or {}
            comments = thread.get("comments") or []
        except Exception:
            frappe.logger("post_api").warning(
                "Comment lookup failed for %s %s", doctype, name, exc_info=True
            )

    return {
        "status": "success",
        "comments": comments,
        "count": len(comments),
        "commentable": commentable,
        "can_engage": can_engage,
        "forum": False,
    }
