# -*- coding: utf-8 -*-
"""
BISMALLAH AR-RAHMAN AR-RAHIM
EthioBiz Home Feed - Likes & Comments API

Canonical storage is Frappe's own `Comment` DocType:
    comment_type = 'Like'     -> a like
    comment_type = 'Comment'  -> a written comment
    comment_type = 'Shared'   -> an in-EthioBiz repost (frappe.desk.share's own
                                 option; "Repost" is NOT in the Select list and
                                 _validate_selects would reject it)

This is the same convention Frappe's desk (`frappe.desk.like.toggle_like`) and
website (`frappe.templates.includes.likes.likes.like`) use, so nothing here is
custom or parallel to the framework.

Design notes
------------
* Reads are guest-open (matching the feed's own `allow_guest=True`).
* Writes require a real login. The parent DocType is NOT made writable for
  guests: `Item`, `Property`, `Job Opening` and `BizBooking Resource` are
  deliberately desk-only, and opening them up so that people could comment
  would be a privilege-escalation hole. Instead each write endpoint does its own
  explicit session check and then inserts the Comment with
  `ignore_permissions=True` - the same trusted pattern already used by
  `afocha_api.add_post_comment`.
* Every write is sanitised server-side (`strip_html_tags`, length capped) and
  escaped again client-side, so stored XSS has two layers of defence.
* Writes are rate limited per user to keep the comment box from being spammed.
* Denormalised counter columns that predate this module (`Afocha Post`,
  `tabWalta Forum Topic`) are kept in sync so their existing pages keep working.
"""

import json

import frappe
from frappe import _
from frappe.utils import cint, now_datetime, strip_html_tags

# A comment longer than this is rejected. Generous for real conversation,
# small enough that the thread stays readable.
MAX_COMMENT_LENGTH = 2000

# Read amplification guard for the thread endpoint.
MAX_COMMENTS_PER_PAGE = 50

# Read amplification guard for the batch-counts endpoint. The feed renders a
# page of cards at a time, so the real batches are well under this ceiling.
MAX_BULK_TARGETS = 60

# Per-user write ceilings inside a rolling 300-second window. Generous for
# real people, tight for a scripted spam run. See _rate_limit() below for why
# this is a hand-rolled helper instead of frappe.rate_limiter.rate_limit.
RATE_LIMIT_SECONDS = 300
RATE_LIMITS = {
    "comment": 20,
    "like": 60,
    "repost": 30,
}

# The ONLY documents that may be read or written through this module.
#
# This is an allowlist, not a blocklist, and that is deliberate. `_validate_target`
# only proves that a DocType and a document exist, which means without this list
# `get_comments` would happily read private threads off any DocType on the desk
# and `add_comment` would write into any document at all - User, Payroll Entry,
# whatever an authenticated session cared to name. A comment store reachable by
# URL is a data-leak surface unless its contents are decided in code.
#
# One entry per feed vertical that has a real Frappe DocType. Deliberately absent:
#   * "EthioBiz Ad Campaign" - ads are not a discussion surface.
#   * "Walta Forum Topic"   - a raw-SQL table with no DocType; its discussion
#                             already lives at /forum and is deep-linked.
FEED_COMMENTABLE_DOCTYPES = (
    "Item",                    # products
    "Job Opening",             # jobs & careers
    "Healthcare Practitioner", # doctors
    "BizService Listing",      # services
    "BizBooking Resource",     # bookings
    "Property",                # real estate
    "Afocha Post",             # social
    "Blog Post",               # blog
    "LMS Course",              # courses
)


def _is_commentable_doctype(doctype):
    return doctype in FEED_COMMENTABLE_DOCTYPES


# ---------------------------------------------------------------------------
# internals
# ---------------------------------------------------------------------------

def _session_user():
    """Return the logged-in username, or None for a guest/anonymous session."""
    if frappe.session and frappe.session.user and frappe.session.user != "Guest":
        return frappe.session.user
    return None


def _require_login():
    user = _session_user()
    if not user:
        frappe.throw(
            _("Authentication required. Please log in to continue."),
            frappe.PermissionError,
        )
    return user


def _rate_limit(bucket, limit=None):
    """
    Rolling per-USER write ceiling, stored under the `rl:` key prefix so the
    suite's cache-clearing globs still see it.

    Why not frappe.rate_limiter.rate_limit? Its identity is `request_ip:` for
    these endpoints (the decorator's `key` field, "reference", never appears in
    form_dict), i.e. every user behind one CGNAT/school NAT shares a single
    20-comments-per-5-minutes budget. This helper keys on the session user
    instead. Guests and in-process callers are skipped deliberately:
      * guests are rejected by _require_login() milliseconds later anyway,
      * the suite's group D/E run in-process (no frappe.request) and must be
        able to exercise write paths repeatedly within one window - the same
        bypass frappe's own decorator applies (`if not frappe.request`).
    """
    if not frappe.request:
        return
    user = _session_user()
    if not user:
        return

    ceiling = int(limit if limit is not None else RATE_LIMITS.get(bucket, 60))
    key = "rl:fea:%s:%s" % (bucket, user)
    try:
        cache = frappe.cache()
        value = cache.incr(key)
        if value == 1:
            cache.expire(key, RATE_LIMIT_SECONDS)
    except Exception:
        # A cache hiccup must never block a legitimate write.
        return

    if value > ceiling:
        frappe.throw(
            _("You're doing that too often. Please wait a moment and try again."),
            frappe.RateLimitExceededError,
        )


def _validate_target(doctype, name):
    """
    Reject anything that is not a commentable feed document.

    Order matters: the allowlist is checked before the database is touched, so an
    unknown DocType is refused without leaking whether it exists.
    """
    if not doctype or not name:
        frappe.throw(_("Missing document reference."), frappe.ValidationError)

    if not _is_commentable_doctype(doctype):
        frappe.throw(_("This content cannot be commented on."), frappe.ValidationError)

    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Unsupported content type."), frappe.ValidationError)

    if not frappe.db.exists(doctype, name):
        frappe.throw(_("This item is no longer available."), frappe.DoesNotExistError)

    return doctype, name


def _clean_text(value):
    """Strip all markup and collapse whitespace. Never returns raw HTML."""
    text = strip_html_tags(value or "")
    text = " ".join(str(text).split())
    if len(text) > MAX_COMMENT_LENGTH:
        frappe.throw(
            _("Your comment is too long. Please keep it under {0} characters.").format(
                MAX_COMMENT_LENGTH
            ),
            frappe.ValidationError,
        )
    return text


def _author_display(comment):
    """Best available display name + avatar for a comment author."""
    user = comment.comment_email or comment.comment_by or ""
    name = user
    if user and "@" not in user:
        try:
            full = frappe.db.get_value("User", user, "full_name")
            if full:
                name = full
        except Exception:
            pass
    if not name:
        name = user or _("Guest")

    avatar = None
    if user:
        try:
            avatar = frappe.db.get_value("User", user, "user_image")
        except Exception:
            avatar = None

    return {
        "author": name,
        "author_email": user,
        "avatar": avatar,
        "time_ago": _time_ago(comment.creation),
        "is_owner": bool(user) and user == _session_user(),
    }


def _time_ago(value):
    from frappe.utils import get_datetime

    try:
        dt = get_datetime(value)
        if not dt:
            return None
        seconds = (now_datetime() - dt).total_seconds()
    except Exception:
        return None

    if seconds < 60:
        return _("Just now")
    if seconds < 3600:
        return _("%dm ago") % int(seconds // 60)
    if seconds < 86400:
        return _("%dh ago") % int(seconds // 3600)
    if seconds < 2592000:
        return _("%dd ago") % int(seconds // 86400)
    if seconds < 31536000:
        return _("%dmo ago") % int(seconds // 2592000)
    return _("%dy ago") % int(seconds // 31536000)


def _counts(doctype, name):
    return {
        "likes": cint(
            frappe.db.count(
                "Comment",
                {"comment_type": "Like", "reference_doctype": doctype, "reference_name": name},
            )
        ),
        "comments": cint(
            frappe.db.count(
                "Comment",
                {"comment_type": "Comment", "reference_doctype": doctype, "reference_name": name},
            )
        ),
    }


def _viewer_has_liked(doctype, name):
    user = _session_user()
    if not user:
        return False
    return bool(
        frappe.db.exists(
            "Comment",
            {
                "comment_type": "Like",
                "reference_doctype": doctype,
                "reference_name": name,
                "comment_email": user,
            },
        )
    )


def _repost_count(doctype, name):
    return cint(
        frappe.db.count(
            "Comment",
            {"comment_type": "Shared", "reference_doctype": doctype, "reference_name": name},
        )
    )


def _viewer_has_reposted(doctype, name):
    user = _session_user()
    if not user:
        return False
    return bool(
        frappe.db.exists(
            "Comment",
            {
                "comment_type": "Shared",
                "reference_doctype": doctype,
                "reference_name": name,
                "comment_email": user,
            },
        )
    )


def _sync_native_counters(doctype, name):
    """
    Keep pre-existing denormalised counter columns in step with the canonical
    Comment store, so `/social` (Afocha) and `/forum` (Walta) keep rendering the
    same numbers they always have.
    """
    try:
        data = _counts(doctype, name)
    except Exception:
        return

    if doctype == "Afocha Post" and frappe.db.has_column("Afocha Post", "likes_count"):
        frappe.db.set_value("Afocha Post", name, "likes_count", data["likes"], update_modified=False)
    if doctype == "Afocha Post" and frappe.db.has_column("Afocha Post", "comments_count"):
        frappe.db.set_value("Afocha Post", name, "comments_count", data["comments"], update_modified=False)


# ---------------------------------------------------------------------------
# read endpoints
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def get_comments(doctype=None, name=None, limit=20, offset=0):
    """Paginated comment thread for one feed item. Guests may read."""
    doctype, name = _validate_target(doctype, name)

    limit = min(max(cint(limit) or 20, 1), MAX_COMMENTS_PER_PAGE)
    offset = max(cint(offset) or 0, 0)

    rows = frappe.get_all(
        "Comment",
        filters={
            "comment_type": "Comment",
            "reference_doctype": doctype,
            "reference_name": name,
        },
        fields=["name", "comment_email", "comment_by", "content", "creation", "owner"],
        order_by="creation asc",
        limit_start=offset,
        limit_page_length=limit,
    )

    comments = []
    for row in rows:
        entry = _author_display(row)
        entry["id"] = row.name
        entry["content"] = row.content or ""
        comments.append(entry)

    total = cint(
        frappe.db.count(
            "Comment",
            {"comment_type": "Comment", "reference_doctype": doctype, "reference_name": name},
        )
    )

    return {
        "status": "success",
        "doctype": doctype,
        "name": name,
        "total": total,
        "comments": comments,
        "has_more": (offset + len(comments)) < total,
        "is_logged_in": bool(_session_user()),
    }


@frappe.whitelist(allow_guest=True)
def bulk_engagement(items=None):
    """
    Like/comment counts for many feed items in a single round trip.

    Accepts the JSON array the feed already returns, or a list of
    {"doctype": ..., "docname": ...} dicts. Returns a map keyed by
    "doctype|docname".
    """
    if not items:
        return {"status": "success", "counts": {}}

    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            frappe.throw(_("Invalid payload."), frappe.ValidationError)

    pairs = []
    for entry in items:
        if isinstance(entry, dict):
            pairs.append((entry.get("doctype"), entry.get("docname") or entry.get("name")))
        elif isinstance(entry, (list, tuple)) and len(entry) == 2:
            pairs.append((entry[0], entry[1]))

    # This endpoint is guest-readable and, unlike the other three, cannot call
    # `_validate_target` per row without a query per row. Filtering in memory
    # keeps the same allowlist guarantee while costing one pass over a list that
    # is already capped in length. Without this, any anonymous caller could
    # enumerate counts for private documents on any DocType.
    pairs = [
        (doctype, docname)
        for (doctype, docname) in pairs
        if doctype and docname and _is_commentable_doctype(doctype)
    ]

    # De-duplicate so a caller cannot inflate our own query cost by repeating
    # the same row, then apply the ceiling.
    seen = set()
    unique = []
    for pair in pairs:
        if pair in seen:
            continue
        seen.add(pair)
        unique.append(pair)
    pairs = unique[:MAX_BULK_TARGETS]

    if not pairs:
        return {"status": "success", "counts": {}}

    # Local import avoids a circular import at module load time.
    from bismillah_ethiobiz.smart_feed_api import _feed_engagement_counts

    counts = _feed_engagement_counts(pairs)

    out = {}
    for (doctype, docname), data in counts.items():
        out["%s|%s" % (doctype, docname)] = data

    return {"status": "success", "counts": out}


# ---------------------------------------------------------------------------
# write endpoints
# ---------------------------------------------------------------------------

@frappe.whitelist()
def add_comment(doctype=None, name=None, docname=None, content=None):
    """Post a comment. Requires login.

    `name` is the canonical parameter; `docname` is accepted as an alias so the
    feed's own payload (which addresses every card by doctype/docname) works
    even if a client sends its natural key. Without this, get_newargs silently
    drops an unknown `docname` kwarg and _validate_target later throws
    "Missing document reference." for a perfectly valid request.
    """
    user = _require_login()
    _rate_limit("comment")
    doctype, name = _validate_target(doctype, name or docname)

    text = _clean_text(content)
    if not text:
        frappe.throw(_("Please write something before posting."), frappe.ValidationError)

    comment = frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": doctype,
            "reference_name": name,
            "comment_email": user,
            "comment_by": user,
            "content": text,
        }
    )
    # The parent DocType stays desk-only for guests; this single Comment insert is
    # authorised explicitly above, so it is the only place we bypass permissions.
    comment.flags.ignore_permissions = True
    comment.flags.ignore_mandatory = True
    comment.insert(ignore_permissions=True)

    _sync_native_counters(doctype, name)
    frappe.db.commit()

    data = _counts(doctype, name)

    entry = {
        "id": comment.name,
        "author": frappe.db.get_value("User", user, "full_name") or user,
        "author_email": user,
        "avatar": frappe.db.get_value("User", user, "user_image"),
        "content": text,
        "time_ago": _("Just now"),
        "is_owner": True,
    }

    return {
        "status": "success",
        "comment": entry,
        "comments_count": data["comments"],
        "likes_count": data["likes"],
    }


@frappe.whitelist()
def delete_comment(comment=None):
    """Delete your own comment. Authors and System Managers only."""
    user = _require_login()

    if not comment or not frappe.db.exists("Comment", comment):
        frappe.throw(_("Comment not found."), frappe.DoesNotExistError)

    row = frappe.db.get_value(
        "Comment", comment, ["comment_email", "comment_by", "reference_doctype", "reference_name"], as_dict=True
    )
    if not row:
        frappe.throw(_("Comment not found."), frappe.DoesNotExistError)

    is_author = user in (row.comment_email, row.comment_by)
    is_admin = user == "Administrator" or "System Manager" in frappe.get_roles(user)
    if not (is_author or is_admin):
        frappe.throw(_("You can only delete your own comments."), frappe.PermissionError)

    doctype, name = row.reference_doctype, row.reference_name
    frappe.delete_doc("Comment", comment, force=True, ignore_permissions=True)

    if doctype and name:
        _sync_native_counters(doctype, name)
    frappe.db.commit()

    data = _counts(doctype, name) if (doctype and name) else {"likes": 0, "comments": 0}

    return {
        "status": "success",
        "comments_count": data["comments"],
        "likes_count": data["likes"],
    }


@frappe.whitelist()
def toggle_like(doctype=None, name=None):
    """
    Like or unlike an item. Idempotent per user: liking twice un-likes.
    Returns the authoritative counts so the client never has to guess.
    """
    user = _require_login()
    _rate_limit("like")
    doctype, name = _validate_target(doctype, name)

    existing = frappe.get_all(
        "Comment",
        filters={
            "comment_type": "Like",
            "reference_doctype": doctype,
            "reference_name": name,
            "comment_email": user,
        },
        fields=["name"],
        limit=1,
    )

    if existing:
        frappe.delete_doc("Comment", existing[0].name, force=True, ignore_permissions=True)
        liked = False
    else:
        like = frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Like",
                "reference_doctype": doctype,
                "reference_name": name,
                "comment_email": user,
                "comment_by": user,
                "content": _("Liked"),
            }
        )
        like.flags.ignore_permissions = True
        like.flags.ignore_mandatory = True
        like.insert(ignore_permissions=True)
        liked = True

    _sync_native_counters(doctype, name)
    frappe.db.commit()

    data = _counts(doctype, name)

    return {
        "status": "success",
        "liked": liked,
        "likes_count": data["likes"],
        "comments_count": data["comments"],
        "viewer_has_liked": liked,
    }


@frappe.whitelist()
def toggle_repost(doctype=None, name=None, note=None, docname=None):
    """
    Repost (or undo a repost of) an item so it appears in the EthioBiz feed.

    Storage is a Frappe `Comment` row with comment_type='Shared' - an option
    that already exists in the DocType's Select list (frappe.desk.share uses it
    for "shared with X"). The obvious-looking value, 'Repost', is NOT in the
    list and base_document._validate_selects would reject it, so 'Shared' keeps
    this feature schema-free. get_comments() filters on comment_type='Comment'
    and the native-counter sync only counts Like/Comment, so these rows stay
    invisible to every other surface.

    Toggle semantics mirror the like button: reposting twice removes the
    repost. One row per (user, target) is the de-duplication rule.
    """
    user = _require_login()
    _rate_limit("repost")
    doctype, name = _validate_target(doctype, name or docname)

    existing = frappe.get_all(
        "Comment",
        filters={
            "comment_type": "Shared",
            "reference_doctype": doctype,
            "reference_name": name,
            "comment_email": user,
        },
        fields=["name"],
        limit=1,
    )

    if existing:
        frappe.delete_doc("Comment", existing[0].name, force=True, ignore_permissions=True)
        reposted = False
    else:
        # An empty note stores an empty `content` (ignore_mandatory is set), so
        # the feed reader can tell "reposted silently" from "reposted with a
        # note" without guessing at a translated default string.
        text = _clean_text(note) if note else ""
        row = frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Shared",
                "reference_doctype": doctype,
                "reference_name": name,
                "comment_email": user,
                "comment_by": user,
                "content": text,
            }
        )
        row.flags.ignore_permissions = True
        row.flags.ignore_mandatory = True
        row.insert(ignore_permissions=True)
        reposted = True

    frappe.db.commit()

    return {
        "status": "success",
        "reposted": reposted,
        "reposts_count": _repost_count(doctype, name),
        "viewer_has_reposted": reposted,
    }
