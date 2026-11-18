# -*- coding: utf-8 -*-
"""
BISMALLAH AR-RAHMAN AR-RAHIM
EthioBiz Single-Post Permalink (/post)
======================================

One beautiful, shareable page for every card family that appears in the
homepage live feed:

    products, jobs, doctors, services, bookings, property, Afocha social,
    Walta forum, Tibeb articles, Dagu courses, sponsored ads, live news.

The live-feed card *body* opens this page. The card's CTA button keeps its
native destination (published product page, /jobs?job=..., /forum?topic=...),
so nothing that already worked changes behaviour.

Design notes
------------
* Server-rendered (SEO + instant paint) with a scoped ``.ebpost-*`` design
  system so it cannot collide with the theme or any other page.
* Colours come from EthioBiz Theme -> Feed Type Styles, exactly like the
  homepage cards and toggle buttons.
* Engagement (like / comment / repost) reuses ``feed_engagement_api`` so the
  allowlist, rate limits and counters stay in one place.
"""

import re
from urllib.parse import quote

import frappe
from frappe.utils import cint, flt, get_url, pretty_date
from frappe.utils.html_utils import sanitize_html

from bismillah_ethiobiz.home_api import (
    FEED_SOURCE_DEFAULTS,
    _feed_style_payload,
    _theme_feed_styles,
)


# ---------------------------------------------------------------------------
# Type maps
# ---------------------------------------------------------------------------

FEED_TYPE_BY_DOCTYPE = {
    "Item": "products",
    "Website Item": "products",
    "Job Opening": "jobs",
    "Healthcare Practitioner": "bizhealth",
    "BizService Listing": "bizfix",
    "BizBooking Resource": "bizservices",
    "Property": "bizhome",
    "Afocha Post": "social",
    "Walta Forum Topic": "forum",
    "Blog Post": "tibeb",
    "LMS Course": "dagu",
    "EthioBiz Ad Campaign": "ad",
    "News": "news",
}

PORTAL = {
    "products":   {"label": "Dikka Shop",     "url": "/shop"},
    "jobs":       {"label": "Oosoo Jobs",     "url": "/jobs"},
    "bizservices": {"label": "BizServices",   "url": "/bizservices"},
    "bizhealth":  {"label": "BizHealth",      "url": "/bizhealth"},
    "bizhome":    {"label": "BizHome",        "url": "/bizhome"},
    "bizfix":     {"label": "BizFix",         "url": "/bizfix"},
    "dagu":       {"label": "Dagu Academy",   "url": "/courses"},
    "tibeb":      {"label": "Tibeb",          "url": "/tibeb"},
    "social":     {"label": "Afocha Social",  "url": "/social"},
    "forum":      {"label": "Walta Forum",    "url": "/forum"},
    "news":       {"label": "Live News",      "url": "/#live-feed-section"},
    "ad":         {"label": "Sponsored",      "url": "/shop"},
}

# CTA defaults per doctype. Each loader may override label/url/note.
CTA_BY_DOCTYPE = {
    "Item":                   ("Order Product",     "🛒", "Secure checkout on Dikka Shop"),
    "Job Opening":            ("Apply Now",         "💼", "Submit your application in under a minute"),
    "Healthcare Practitioner": ("Book Consultation", "🩺", "Choose a clinic or teleconsultation slot"),
    "BizService Listing":     ("Book Service",      "🧰", "Verified provider · instant request"),
    "BizBooking Resource":    ("Reserve Now",       "📅", "Check live availability and reserve"),
    "Property":               ("View Property",     "🏠", "Schedule a viewing with the lister"),
    "Afocha Post":            ("Join Conversation", "💬", "Open this story on Afocha Social"),
    "Walta Forum Topic":      ("Join Topic",        "🗣️", "Continue the discussion on Walta Forum"),
    "Blog Post":              ("Read Full Article", "📖", "Open the complete Tibeb article"),
    "LMS Course":             ("Enroll in Course",  "🎓", "Start learning with Dagu Academy"),
    "EthioBiz Ad Campaign":   ("Learn More",        "📢", "Visit the sponsor's destination"),
    "News":                   ("Read Full Story",   "📰", "Continue at the original news source"),
}

# Localised CTA copy. The loaders keep the icon; label/note come from here so a
# reader whose preferred_language is Amharic never sees an English button.
CTA_LABELS = {
    "en": {
        "products": ("Order Product", "Secure checkout on Dikka Shop"),
        "jobs": ("Apply Now", "Submit your application in under a minute"),
        "bizhealth": ("Book Consultation", "Choose a clinic or teleconsultation slot"),
        "bizfix": ("Book Service", "Verified provider · instant request"),
        "bizservices": ("Reserve Now", "Check live availability and reserve"),
        "bizhome": ("View Property", "Schedule a viewing with the lister"),
        "social": ("Join Conversation", "Open this story on Afocha Social"),
        "forum": ("Join Topic", "Continue the discussion on Walta Forum"),
        "tibeb": ("Read Full Article", "Open the complete Tibeb article"),
        "dagu": ("Enroll in Course", "Start learning with Dagu Academy"),
        "ad": ("Learn More", "Visit the sponsor's destination"),
        "news": ("Read Full Story", "Continue at the original news source"),
    },
    "am": {
        "products": ("ምርቱን ይዘዙ", "በዲካ ሱቅ ደህንነቱ የተጠበቀ ክፍያ"),
        "jobs": ("አሁን ያመልክቱ", "ማመልከቻዎን በአንድ ደቂቃ ያስገቡ"),
        "bizhealth": ("ቀጠሮ ይያዙ", "ክሊኒክ ወይም የቴሌ ምክር ቀጠሮ ይምረጡ"),
        "bizfix": ("አገልግሎት ይዘዙ", "የተረጋገጠ አገልግሎት · ፈጣን ጥያቄ"),
        "bizservices": ("አሁን ያስይዙ", "ቀጥታ ዝግጁነትን ይመልከቱ እና ያስይዙ"),
        "bizhome": ("ቤቱን ይመልከቱ", "ከማስታወቂያ ባለቤቱ ጋር ጉብኝት ያስይዙ"),
        "social": ("ውይይቱን ይቀላቀሉ", "ይህን ታሪክ በአፎቻ ሶሻል ይክፈቱ"),
        "forum": ("ርዕሱን ይቀላቀሉ", "ውይይቱን በዋልታ ፎረም ይቀጥሉ"),
        "tibeb": ("ሙሉ ጽሑፉን ያንብቡ", "ሙሉውን የጥበብ ጽሑፍ ይክፈቱ"),
        "dagu": ("በኮርሱ ይመዝገቡ", "በዳጉ አካዳሚ መማር ይጀምሩ"),
        "ad": ("ተጨማሪ ይወቁ", "የስፖንሰሩን መዳረሻ ይጎብኙ"),
        "news": ("ሙሉውን ታሪክ ያንብቡ", "በዋናው የዜና ምንጭ ይቀጥሉ"),
    },
}

LABELS = {
    "en": {
        "back": "Back to live feed",
        "home": "Home",
        "feed": "Live feed",
        "overview": "Overview",
        "highlights": "Highlights",
        "details": "Details",
        "reviews": "Reviews",
        "comments": "Comments",
        "discussion": "Discussion & Feedback",
        "replies": "Replies",
        "like": "Like",
        "comment": "Comment",
        "repost": "Repost",
        "share": "Share",
        "post_comment": "Post comment",
        "login_to_comment": "Log in to join the conversation",
        "be_first": "Be the first to comment.",
        "write_comment": "Write a thoughtful comment…",
        "about": "About",
        "verified": "Verified",
        "posted_by": "Posted by",
        "published": "Published",
        "price": "Price",
        "status": "Status",
        "category": "Category",
        "location": "Location",
        "salary": "Salary",
        "type": "Type",
        "experience": "Experience",
        "qualifications": "Qualifications",
        "languages": "Languages",
        "fee": "Consultation fee",
        "availability": "Availability",
        "clinic": "Clinic",
        "duration": "Duration",
        "rating": "Rating",
        "not_found_title": "This post is no longer available",
        "not_found_text": "It may have been removed, sold, filled, or unpublished. Explore the live ecosystem instead.",
        "explore": "Explore the ecosystem",
        "more_from": "More from",
        "sponsored": "Sponsored",
        "source": "Source",
        "read_at_source": "Read at source",
        "apply_title": "Apply for this role",
        "full_name": "Full name",
        "email": "Email",
        "phone": "Phone",
        "cover_letter": "Cover letter",
        "send_application": "Send application",
        "cancel": "Cancel",
        "application_sent": "Application sent. The hiring team will contact you.",
        "login_required": "Please log in to continue.",
        "share_copied": "Link copied to clipboard.",
        "replies_count": "replies",
        "views": "views",
        "related": "You may also like",
        "open_portal": "Open",
        "engagement": "Engagement",
        "seller_reply": "Seller reply",
        "verified_customer": "Verified customer",
        "signed_in_as": "Signed in as",
        "copy_link": "Copy this link",
        "reposted": "Reposted to your feed.",
        "repost_removed": "Repost removed.",
        "comment_posted": "Comment posted.",
        "just_now": "just now",
        "you": "You",
        "gallery": "Gallery",
        "breadcrumb": "Breadcrumb",
        "read_full": "Read full",
        "show_less": "Show less",
        "swipe_next": "Swipe up for next",
        "comments_title": "Comments",
        "no_comments": "No comments yet. Start the conversation.",
        "comment_placeholder": "Write a comment…",
        "post": "Post",
        "comments_closed": "Comments are closed for this post.",
        "forum_cta": "Continue on Walta Forum",
        "news_comments": "Live news is discussed at the source.",
        "login_to_engage": "Log in to like, comment and repost.",
        "next": "Next",
        "previous": "Previous",
        "close": "Close",
        "see_all_reviews": "See all reviews",
        "replies_title": "Replies",
        "analyze": "Analyze",
        "analyze_title": "Post intelligence",
        "analyze_sub": "A quick read of what this post offers and what to check next.",
        "analyze_note": "Use the official action button to continue. Verify the seller, employer or provider before paying or sharing personal information.",
        "research": "Research this post",
        "none": "-",
    },
    "am": {
        "back": "ወደ ቀጥታ ፍሰት ተመለስ",
        "home": "መነሻ",
        "feed": "ቀጥታ ፍሰት",
        "overview": "አጠቃላይ እይታ",
        "highlights": "ዋና ነጥቦች",
        "details": "ዝርዝሮች",
        "reviews": "አስተያየቶች",
        "comments": "አስተያየቶች",
        "discussion": "ውይይት እና አስተያየት",
        "replies": "መልሶች",
        "like": "ወደድኩት",
        "comment": "አስተያየት",
        "repost": "አጋራ",
        "share": "አጋራ",
        "post_comment": "አስተያየት ላክ",
        "login_to_comment": "ውይይቱን ለመቀላቀል ይግቡ",
        "be_first": "የመጀመሪያው አስተያየት ይስጡ።",
        "write_comment": "አስተያየትዎን ይጻፉ…",
        "about": "ስለ",
        "verified": "የተረጋገጠ",
        "posted_by": "የተለጠፈው በ",
        "published": "የታተመ",
        "price": "ዋጋ",
        "status": "ሁኔታ",
        "category": "ምድብ",
        "location": "አካባቢ",
        "salary": "ደመወዝ",
        "type": "ዓይነት",
        "experience": "ልምድ",
        "qualifications": "ብቃቶች",
        "languages": "ቋንቋዎች",
        "fee": "የምክር ክፍያ",
        "availability": "ዝግጁነት",
        "clinic": "ክሊኒክ",
        "duration": "ቆይታ",
        "rating": "ደረጃ",
        "not_found_title": "ይህ ጽሑፍ አይገኝም",
        "not_found_text": "ተወግዶ፣ ተሽጦ፣ ተሞልቶ ወይም ካልታተመ ሊሆን ይችላል። ሌሎችን ያስሱ።",
        "explore": "ስነ-ምህዳሩን ያስሱ",
        "more_from": "ተጨማሪ ከ",
        "sponsored": "ተስፋፊ",
        "source": "ምንጭ",
        "read_at_source": "በምንጩ ያንብቡ",
        "apply_title": "ለዚህ ስራ ያመልክቱ",
        "full_name": "ሙሉ ስም",
        "email": "ኢሜይል",
        "phone": "ስልክ",
        "cover_letter": "የሽፋን ደብዳቤ",
        "send_application": "ማመልከቻ ላክ",
        "cancel": "ሰርዝ",
        "application_sent": "ማመልከቻው ተልኳል። የቅጥር ቡድኑ ያገኝዎታል።",
        "login_required": "ለመቀጠል እባክዎ ይግቡ።",
        "share_copied": "አገናኙ ተቀድቷል።",
        "replies_count": "መልሶች",
        "views": "እይታዎች",
        "related": "እነዚህንም ይወዱ ይሆናል",
        "open_portal": "ክፈት",
        "engagement": "ተሳትፎ",
        "seller_reply": "የሻጭ ምላሽ",
        "verified_customer": "የተረጋገጠ ደንበኛ",
        "signed_in_as": "እንደ ገባችሁ",
        "copy_link": "ይህን አገናኝ ይቅዱ",
        "reposted": "ወደ ፍሰትዎ ተጋርቷል።",
        "repost_removed": "አጋራ ተወግዷል።",
        "comment_posted": "አስተያየት ተለጥፏል።",
        "just_now": "አሁን",
        "you": "እርስዎ",
        "gallery": "ጋለሪ",
        "breadcrumb": "የገጽ መንገድ",
        "read_full": "ሙሉውን ያንብቡ",
        "show_less": "ያሳጥሩ",
        "swipe_next": "ለቀጣዩ ወደ ላይ ያንሸራትቱ",
        "comments_title": "አስተያየቶች",
        "no_comments": "እስካሁን አስተያየት የለም። ውይይቱን ይጀምሩ።",
        "comment_placeholder": "አስተያየት ይጻፉ…",
        "post": "ለጥፍ",
        "comments_closed": "ለዚህ ጽሑፍ አስተያየት ተዘግቷል።",
        "forum_cta": "በዋልታ ፎረም ይቀጥሉ",
        "news_comments": "ቀጥታ ዜና በምንጩ ይወያያል።",
        "login_to_engage": "ለመውደድ፣ አስተያየት ለመስጠት እና ለማጋራት ይግቡ።",
        "next": "ቀጣይ",
        "previous": "ቀዳሚ",
        "close": "ዝጋ",
        "see_all_reviews": "ሁሉንም አስተያየቶች ይመልከቱ",
        "replies_title": "መልሶች",
        "analyze": "ትንተና",
        "analyze_title": "የፖስት ትንተና",
        "analyze_sub": "ይህ ፖስት ምን እንደሚያቀርብ እና ቀጥሎ ምን ማረጋገጥ እንዳለብዎ ፈጣን እይታ።",
        "analyze_note": "ለመቀጠል ኦፊሴላዊውን የድርጊት ቁልፍ ይጠቀሙ። ከመክፈል ወይም የግል መረጃ ከማጋራት በፊት ሻጩን፣ ቀጣሪውን ወይም አገልግሎት ሰጪውን ያረጋግጡ።",
        "research": "ይህን ፖስት ይመርምሩ",
        "none": "-",
    },
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _lang():
    try:
        return "am" if str(frappe.local.lang or "").lower().startswith("am") else "en"
    except Exception:
        return "en"


def _labels():
    return LABELS[_lang()]


def _s(value):
    return "" if value is None else str(value).strip()


def _first(*values):
    for value in values:
        if value is not None and str(value).strip() not in ("", "None"):
            return value
    return ""


def _rich_html(value):
    """Turn stored rich-text or Markdown into safe display HTML."""
    raw = _s(value)
    if not raw:
        return ""
    if re.search(r"<(p|div|br|ul|ol|li|h[1-6]|strong|em|b|i|a|img|table|blockquote|figure)\b", raw, re.I):
        try:
            return sanitize_html(raw, always_sanitize=True)
        except Exception:
            return raw
    try:
        return frappe.utils.markdown(raw, sanitize=True, linkify=True)
    except Exception:
        return sanitize_html("<p>%s</p>" % raw, always_sanitize=True)


def _plain(value, limit=None):
    text = re.sub(r"<[^>]+>", " ", _s(value))
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[: max(0, limit - 1)].rstrip() + "…"
    return text


def _image(value):
    value = _s(value)
    if not value:
        return ""
    if value.startswith(("http://", "https://", "/", "data:")):
        return value
    return "/" + value.lstrip("/")


def _time_ago(value):
    if not value:
        return ""
    try:
        return pretty_date(value) or ""
    except Exception:
        return ""


def _hex_rgb(value):
    value = _s(value).lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        return "13, 148, 136"
    try:
        return "%d, %d, %d" % tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return "13, 148, 136"


def _feed_style(feed_type):
    feed_type = (feed_type or "all").strip().lower()
    overrides = {}
    try:
        overrides = _theme_feed_styles() or {}
    except Exception:
        overrides = {}
    base = next(
        (row for row in FEED_SOURCE_DEFAULTS if row.get("feed_type") == feed_type),
        None,
    )
    if not base:
        base = {
            "feed_type": feed_type,
            "label": feed_type.replace("-", " ").title() or "Live Feed",
            "label_am": feed_type,
            "icon": "✨",
            "accent_color": "#0d9488",
            "gradient_start": "#0f766e",
            "gradient_end": "#14b8a6",
            "text_color": "#ffffff",
        }
    merged = dict(base)
    merged.update(overrides.get(feed_type) or {})
    style = _feed_style_payload(merged)
    if _lang() == "am":
        style["label"] = style.get("label_am") or style.get("label")
    style["accent_rgb"] = _hex_rgb(style.get("accent_color"))
    return style


def _base_post(doctype, name, feed_type):
    style = _feed_style(feed_type)
    labels = _labels()
    portal = PORTAL.get(feed_type) or {"label": "EthioBiz", "url": "/"}
    return {
        "found": True,
        "doctype": doctype,
        "name": name,
        "feed_type": feed_type,
        "style": style,
        "accent_rgb": style.get("accent_rgb"),
        "portal_label": portal["label"],
        "portal_url": portal["url"],
        "title": "",
        "subtitle": "",
        "category": "",
        "kicker": "",
        "body_html": "",
        "body_text": "",
        "image": "",
        "gallery": [],
        "author_name": "",
        "author_company": "",
        "author_handle": "",
        "author_avatar": "",
        "author_url": "",
        "created": None,
        "time_ago": "",
        "price": "",
        "price_label": labels["price"],
        "status": "",
        "stock_status": "",
        "highlights": [],
        "specs": [],
        "offers": [],
        "reviews": [],
        "review_summary": {},
        "rating": 0,
        "total_reviews": 0,
        "cta_label": "",
        "cta_icon": "",
        "cta_url": "",
        "cta_note": "",
        "likes_count": 0,
        "comments_count": 0,
        "reposts_count": 0,
        "viewer_liked": False,
        "viewer_reposted": False,
        "commentable": False,
        "can_engage": False,
        "comments": [],
        "replies": [],
        "external_url": "",
        "share_url": "",
        "meta_title": "",
        "meta_description": "",
        "labels": labels,
        "job": None,
        "doctor": None,
        "property": None,
        "news": None,
        "is_news": feed_type == "news",
        "is_job": feed_type == "jobs",
        "is_product": feed_type == "products",
        "is_doctor": feed_type == "bizhealth",
        "is_social": feed_type == "social",
        "is_forum": feed_type == "forum",
        "is_course": feed_type == "dagu",
        "is_property": feed_type == "bizhome",
        "is_ad": feed_type == "ad",
    }


def _finish(post):
    """Shared polish: CTA fallback, share URL, meta, engagement state."""
    if not post.get("found"):
        return post

    labels = post["labels"]
    doctype = post.get("doctype")
    name = post.get("name")

    cta_copy = CTA_LABELS[_lang()].get(post.get("feed_type") or "")
    if cta_copy:
        post["cta_label"], post["cta_note"] = cta_copy
    if not post.get("cta_label"):
        label, icon, note = CTA_BY_DOCTYPE.get(doctype, ("Explore", "✨", ""))
        post["cta_label"] = label
        post["cta_icon"] = icon
        post["cta_note"] = note
    if not post.get("cta_url"):
        post["cta_url"] = post.get("external_url") or post.get("portal_url") or "/"

    if not post.get("title"):
        post["title"] = name or labels["feed"]
    # A short description that merely repeats the title adds noise, not context.
    if post.get("subtitle"):
        subtitle_l = _plain(post["subtitle"]).strip().lower()
        title_l = _plain(post["title"]).strip().lower()
        if subtitle_l and (
            subtitle_l == title_l
            or (title_l.startswith(subtitle_l) and len(subtitle_l) >= max(8, len(title_l) // 2))
        ):
            post["subtitle"] = ""
    if not post.get("meta_title"):
        post["meta_title"] = "%s — EthioBiz.ET" % post["title"]
    if not post.get("meta_description"):
        post["meta_description"] = _plain(post.get("body_html") or post.get("subtitle"), 160)

    share = "/post?doctype=%s&name=%s&ft=%s" % (
        quote(str(doctype or ""), safe=""),
        quote(str(name or ""), safe=""),
        quote(str(post.get("feed_type") or ""), safe=""),
    )
    post["share_path"] = share
    try:
        post["share_url"] = get_url() + share
    except Exception:
        post["share_url"] = share

    # Engagement state (only for allowlisted, real doctypes).
    try:
        from bismillah_ethiobiz import feed_engagement_api as eng

        if eng._is_commentable_doctype(doctype):
            post["commentable"] = True
            post["can_engage"] = bool(eng._session_user())
            counts = eng._counts(doctype, name)
            post["likes_count"] = cint(counts.get("likes"))
            post["comments_count"] = cint(counts.get("comments"))
            post["reposts_count"] = cint(eng._repost_count(doctype, name))
            post["viewer_liked"] = bool(eng._viewer_has_liked(doctype, name))
            post["viewer_reposted"] = bool(eng._viewer_has_reposted(doctype, name))
            if post["comments_count"]:
                thread = eng.get_comments(doctype=doctype, name=name, limit=50)
                post["comments"] = thread.get("comments") or []
    except Exception as exc:
        frappe.logger("post_page").warning("Engagement lookup failed for %s %s: %s", doctype, name, exc)

    return post


def _not_found(doctype="", name="", feed_type="all"):
    post = _base_post(doctype, name, feed_type)
    post["found"] = False
    post["title"] = post["labels"]["not_found_title"]
    post["meta_title"] = post["title"]
    post["meta_description"] = post["labels"]["not_found_text"]
    return post


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_product(identifier, feed_type="products"):
    from bismillah_ethiobiz.dikka_catalog import get_website_item_detail

    product = get_website_item_detail(identifier)
    if not product:
        return None

    post = _base_post("Item", product.get("item_code") or identifier, "products")
    gallery = product.get("gallery") or []
    primary_image = (gallery[0].get("image") if gallery else "") or product.get("primary_image") or ""
    post.update({
        "title": product.get("item_name") or identifier,
        "subtitle": product.get("short_description") or "",
        "category": product.get("item_group") or "Dikka Shop",
        "kicker": "Dikka Shop · Verified product",
        "body_html": _rich_html(product.get("description") or product.get("website_content")),
        "body_text": product.get("description_text") or "",
        "gallery": gallery,
        "image": primary_image,
        "price": product.get("formatted_price") or "",
        "status": product.get("stock_status") or "",
        "stock_status": product.get("stock_status") or "",
        "highlights": product.get("highlights") or [],
        "specs": product.get("specs") or [],
        "offers": product.get("offers") or [],
        "reviews": (product.get("reviews") or [])[:8],
        "review_summary": product.get("review_summary") or {},
        "rating": product.get("rating") or 0,
        "total_reviews": product.get("total_reviews") or 0,
        "cta_label": "Order Product",
        "cta_icon": "🛒",
        "cta_url": product.get("detail_url") or ("/product/%s" % quote(str(identifier), safe="")),
        "cta_note": "Secure checkout on Dikka Shop",
    })

    company = product.get("company_name") or product.get("company") or ""
    post["author_name"] = company or "Verified Merchant"
    post["author_company"] = company
    post["author_url"] = "/shop"
    post["kicker"] = "Dikka Shop · %s" % (product.get("item_group") or "Product")
    return post


def _load_job(name):
    if not frappe.db.exists("Job Opening", name):
        return None
    job = frappe.get_doc("Job Opening", name)
    post = _base_post("Job Opening", name, "jobs")

    lower = flt(job.get("lower_range") or 0)
    upper = flt(job.get("upper_range") or 0)
    currency = job.get("currency") or "ETB"
    per = job.get("salary_per") or "Month"
    if lower and upper:
        salary = "%s %s – %s %s / %s" % (currency, f"{lower:,.0f}", f"{upper:,.0f}", currency, per)
    elif lower:
        salary = "%s %s / %s" % (currency, f"{lower:,.0f}", per)
    else:
        salary = "Competitive compensation"

    post.update({
        "title": job.get("job_title") or name,
        "subtitle": " ".join(x for x in [job.get("company") or "", job.get("location") or ""] if x),
        "category": job.get("designation") or "Career",
        "kicker": "Oosoo Jobs · Verified opening",
        "body_html": _rich_html(job.get("description")),
        "author_name": job.get("company") or "EthioBiz Partner",
        "author_company": job.get("company") or "",
        "author_url": "/jobs",
        "created": job.get("posted_on") or job.get("creation"),
        "time_ago": _time_ago(job.get("posted_on") or job.get("creation")),
        "price": salary,
        "price_label": post["labels"]["salary"],
        "status": job.get("status") or "Open",
        "highlights": [
            {"icon": "💼", "text": job.get("employment_type") or "Full-time"},
            {"icon": "📍", "text": job.get("location") or "Ethiopia"},
            {"icon": "🏢", "text": job.get("company") or "EthioBiz Partner"},
            {"icon": "💰", "text": salary},
        ],
        "specs": [
            {"label": "Designation", "description": job.get("designation") or ""},
            {"label": "Employment type", "description": job.get("employment_type") or ""},
            {"label": "Location", "description": job.get("location") or ""},
            {"label": "Salary", "description": salary},
            {"label": "Status", "description": job.get("status") or ""},
        ],
        "cta_label": "Apply Now",
        "cta_icon": "💼",
        "cta_url": "/jobs?job=%s" % quote(str(name), safe=""),
        "cta_note": "Submit your application in under a minute",
        "job": {
            "name": name,
            "job_title": job.get("job_title") or name,
            "company": job.get("company") or "",
            "location": job.get("location") or "",
        },
    })
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _load_doctor(name):
    try:
        from bismillah_ethiobiz.bizhealth_api import get_doctor_detail
        payload = get_doctor_detail(doctor_id=name) or {}
    except Exception:
        payload = {}
    doctor = payload.get("doctor") or {}
    if not doctor:
        return None

    post = _base_post("Healthcare Practitioner", name, "bizhealth")
    availability = doctor.get("availability") or {}
    slots = availability.get("slots") or []
    institutes = doctor.get("institutes") or []

    post.update({
        "title": doctor.get("name") or name,
        "subtitle": "%s · %s" % (doctor.get("specialty") or "Specialist", doctor.get("clinic") or ""),
        "category": doctor.get("specialty") or "Healthcare",
        "kicker": "BizHealth · Verified specialist",
        "body_html": _rich_html(doctor.get("bio")),
        "image": _image(doctor.get("image")),
        "gallery": [{"image": _image(doctor.get("image")), "caption": doctor.get("name") or ""}]
        if doctor.get("image") else [],
        "author_name": doctor.get("name") or name,
        "author_company": doctor.get("clinic") or "",
        "author_avatar": _image(doctor.get("image")),
        "author_url": doctor.get("profile_url") or ("/doctor/%s" % quote(str(name), safe="")),
        "price": doctor.get("fee_formatted") or "",
        "price_label": post["labels"]["fee"],
        "rating": doctor.get("rating") or 0,
        "total_reviews": doctor.get("total_reviews") or 0,
        "status": "Available",
        "highlights": [
            {"icon": "🩺", "text": doctor.get("specialty") or "Specialist"},
            {"icon": "🏥", "text": doctor.get("clinic") or ""},
            {"icon": "💬", "text": doctor.get("languages") or "Amharic, English"},
            {"icon": "💳", "text": doctor.get("fee_formatted") or ""},
        ],
        "specs": [
            {"label": "Qualifications", "description": doctor.get("qualifications") or ""},
            {"label": "Clinic", "description": doctor.get("clinic") or ""},
            {"label": "Languages", "description": doctor.get("languages") or ""},
            {"label": "Consultation fee", "description": doctor.get("fee_formatted") or ""},
            {"label": "Availability", "description": (", ".join(slots[:6]) if slots else "Contact clinic")},
        ],
        "cta_label": "Book Consultation",
        "cta_icon": "🩺",
        "cta_url": doctor.get("profile_url") or ("/doctor/%s" % quote(str(name), safe="")),
        "cta_note": "Choose a clinic or teleconsultation slot",
        "doctor": doctor,
    })
    post["highlights"] = [h for h in post["highlights"] if h.get("text")]
    post["specs"] = [s for s in post["specs"] if s["description"]]
    if institutes:
        post["offers"] = [
            {
                "offer_title": inst.get("institute_name") or "Clinic",
                "offer_subtitle": inst.get("days_display") or "",
                "offer_details": "%s · %s · %s ETB" % (
                    inst.get("hours") or "",
                    inst.get("room_unit") or "",
                    f"{flt(inst.get('consultation_fee') or 0):,.0f}",
                ),
            }
            for inst in institutes
        ]
    return post


def _load_service(name, feed_type="bizfix"):
    if not frappe.db.exists("BizService Listing", name):
        return None
    doc = frappe.get_doc("BizService Listing", name)
    post = _base_post("BizService Listing", name, feed_type)

    price = flt(doc.get("price") or doc.get("base_rate") or 0)
    price_str = "%s %s" % (f"{price:,.2f}", doc.get("currency") or "ETB") if price > 0 else "Request a quote"
    duration = doc.get("duration_minutes") or doc.get("duration") or 0

    post.update({
        "title": doc.get("service_name") or name,
        "subtitle": " ".join(x for x in [doc.get("company") or "", doc.get("category") or ""] if x),
        "category": doc.get("category") or "Service",
        "kicker": "BizServices · Verified provider",
        "body_html": _rich_html(_first(doc.get("description"), doc.get("details"), doc.get("overview"))),
        "image": _image(doc.get("image") or doc.get("service_image")),
        "author_name": doc.get("company") or "Verified Provider",
        "author_company": doc.get("company") or "",
        "author_url": "/bizservices",
        "created": doc.get("creation"),
        "time_ago": _time_ago(doc.get("creation")),
        "price": price_str,
        "status": "Active" if cint(doc.get("is_active", 1)) else "Inactive",
        "rating": flt(doc.get("average_rating") or 0),
        "total_reviews": cint(doc.get("total_reviews") or 0),
        "highlights": [
            {"icon": "🧰", "text": doc.get("category") or "Service"},
            {"icon": "🏢", "text": doc.get("company") or ""},
            {"icon": "💰", "text": price_str},
            {"icon": "⏱️", "text": ("%s minutes" % duration) if duration else "Flexible"},
        ],
        "specs": [
            {"label": "Category", "description": doc.get("category") or ""},
            {"label": "Provider", "description": doc.get("company") or ""},
            {"label": "Price", "description": price_str},
            {"label": "Duration", "description": ("%s minutes" % duration) if duration else ""},
        ],
        "cta_label": "Book Service",
        "cta_icon": "🧰",
        "cta_url": "/bizfix?service=%s" % quote(str(name), safe=""),
        "cta_note": "Verified provider · instant request",
    })
    post["highlights"] = [h for h in post["highlights"] if h.get("text")]
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _load_booking(name):
    if not frappe.db.exists("BizBooking Resource", name):
        return None
    doc = frappe.get_doc("BizBooking Resource", name)
    post = _base_post("BizBooking Resource", name, "bizservices")

    rate = flt(doc.get("base_rate") or doc.get("price") or 0)
    rate_str = "%s ETB" % f"{rate:,.2f}" if rate > 0 else "Check availability"

    post.update({
        "title": doc.get("resource_name") or name,
        "subtitle": " ".join(x for x in [doc.get("company") or "", doc.get("category") or ""] if x),
        "category": doc.get("category") or "Booking",
        "kicker": "BizServices · Live availability",
        "body_html": _rich_html(_first(doc.get("description"), doc.get("details"))),
        "author_name": doc.get("company") or "EthioBiz Partner",
        "author_company": doc.get("company") or "",
        "author_url": "/bizservices",
        "created": doc.get("creation"),
        "time_ago": _time_ago(doc.get("creation")),
        "price": rate_str,
        "status": "Available" if cint(doc.get("is_active", 1)) else "Unavailable",
        "rating": flt(doc.get("average_rating") or 0),
        "total_reviews": cint(doc.get("total_reviews") or 0),
        "highlights": [
            {"icon": "📅", "text": "Instant reservation"},
            {"icon": "🏢", "text": doc.get("company") or ""},
            {"icon": "💰", "text": rate_str},
        ],
        "specs": [
            {"label": "Category", "description": doc.get("category") or ""},
            {"label": "Provider", "description": doc.get("company") or ""},
            {"label": "Base rate", "description": rate_str},
        ],
        "cta_label": "Reserve Now",
        "cta_icon": "📅",
        "cta_url": "/bizservice?resource=%s" % quote(str(name), safe=""),
        "cta_note": "Check live availability and reserve",
    })
    post["highlights"] = [h for h in post["highlights"] if h.get("text")]
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _property_row(name):
    """Read a Property row without importing its (missing) ``propms`` controller.

    The site stores PropMS rows in ``tabProperty`` but the PropMS app is not
    installed, so ``frappe.get_doc("Property", ...)`` raises ImportError. The
    live-feed card still links here, so fall back to a raw table read.
    """
    if not frappe.db.table_exists("Property"):
        return None
    row = frappe.db.get_value("Property", name, "*", as_dict=True)
    if not row:
        return None

    def pick(*keys):
        for key in keys:
            value = row.get(key)
            if value not in (None, ""):
                return value
        return None

    offer = str(pick("shop_offer_type", "tenure") or "")
    return {
        "name": row.get("name") or name,
        "title": pick("name1", "property_name", "title") or name,
        "property_type": pick("type", "property_type") or "Residential",
        "tenure": offer or "Monthly Rental",
        "price": flt(pick("shop_price", "rent", "price") or 0),
        "price_unit": "night" if "Day" in offer else "month",
        "city": pick("city") or "Addis Ababa",
        "subcity": pick("territory", "subcity") or "",
        "bedrooms": cint(pick("bedroom", "bedrooms") or 0),
        "bathrooms": cint(pick("common_bathroom", "bathroom", "bathrooms") or 0),
        "area_sqm": flt(pick("builtup_area", "carpet_area", "area_sqm") or 0),
        "furnished": cint(pick("furnished") or 0),
        "amenities": [],
        "image": pick("shop_image", "photo", "image"),
        "rating": flt(pick("rating") or 0),
        "reviews_count": cint(pick("reviews_count") or 0),
        "status": pick("status") or "Available",
        "description": pick("description") or "",
        "company": pick("company") or "",
    }


def _load_property(name):
    payload = {}
    try:
        from bismillah_ethiobiz.bizhome_api import get_property_details
        payload = get_property_details(name) or {}
    except Exception:
        payload = {}
    prop = payload.get("property") or _property_row(name) or {}
    if not prop:
        return None

    post = _base_post("Property", name, "bizhome")
    price = flt(prop.get("price") or 0)
    price_str = "%s ETB / %s" % (f"{price:,.0f}", prop.get("price_unit") or "month") if price else "Price on request"
    amenities = prop.get("amenities") or []

    post.update({
        "title": prop.get("title") or name,
        "subtitle": " ".join(x for x in [prop.get("property_type") or "", prop.get("city") or "", prop.get("subcity") or ""] if x),
        "category": prop.get("property_type") or "Property",
        "kicker": "BizHome · Verified listing",
        "body_html": _rich_html(prop.get("description")),
        "image": _image(prop.get("image")),
        "gallery": [{"image": _image(prop.get("image")), "caption": prop.get("title") or ""}]
        if prop.get("image") else [],
        "author_name": prop.get("company") or "Verified Lister",
        "author_company": prop.get("company") or "",
        "author_url": "/bizhome",
        "price": price_str,
        "status": prop.get("status") or "Available",
        "rating": flt(prop.get("rating") or 0),
        "total_reviews": cint(prop.get("reviews_count") or 0),
        "highlights": [
            {"icon": "🛏️", "text": ("%s bedrooms" % cint(prop.get("bedrooms"))) if cint(prop.get("bedrooms")) else ""},
            {"icon": "🛁", "text": ("%s bathrooms" % cint(prop.get("bathrooms"))) if cint(prop.get("bathrooms")) else ""},
            {"icon": "📐", "text": ("%s m²" % f"{flt(prop.get('area_sqm') or 0):,.0f}") if flt(prop.get("area_sqm") or 0) else ""},
            {"icon": "📍", "text": prop.get("subcity") or prop.get("city") or ""},
        ],
        "specs": [
            {"label": "Type", "description": prop.get("property_type") or ""},
            {"label": "Tenure", "description": prop.get("tenure") or ""},
            {"label": "City", "description": prop.get("city") or ""},
            {"label": "Sub-city", "description": prop.get("subcity") or ""},
            {"label": "Price", "description": price_str},
        ],
        "offers": [{"offer_title": "Amenities", "offer_subtitle": "", "offer_details": " · ".join(amenities)}]
        if amenities else [],
        "cta_label": "View Property",
        "cta_icon": "🏠",
        "cta_url": "/bizhome?property=%s" % quote(str(name), safe=""),
        "cta_note": "Schedule a viewing with the lister",
        "property": prop,
    })
    post["highlights"] = [h for h in post["highlights"] if h.get("text")]
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _load_afocha(name):
    if not frappe.db.exists("Afocha Post", name):
        return None
    doc = frappe.get_doc("Afocha Post", name)
    post = _base_post("Afocha Post", name, "social")

    image = _image(doc.get("post_image"))
    gallery = []
    if image:
        gallery.append({"image": image, "caption": ""})
    for field in ("image_2", "image_3", "image_4", "gallery_image"):
        try:
            extra = _image(doc.get(field))
        except Exception:
            extra = ""
        if extra and extra not in [g["image"] for g in gallery]:
            gallery.append({"image": extra, "caption": ""})

    post.update({
        "title": _first(doc.get("title"), doc.get("category_tag"), "Afocha story"),
        "subtitle": "",
        "category": doc.get("category_tag") or "Afocha Story",
        "kicker": "Afocha Social · Community story",
        "body_html": _rich_html(doc.get("content")),
        "body_text": _plain(doc.get("content")),
        "image": image,
        "gallery": gallery,
        "author_name": doc.get("author_name") or doc.get("author") or "Afocha Member",
        "author_company": doc.get("company") or "",
        "author_handle": doc.get("author_handle") or "",
        "author_avatar": _image(doc.get("author_image")),
        "author_url": "/social",
        "created": doc.get("creation"),
        "time_ago": _time_ago(doc.get("creation")),
        "likes_count": cint(doc.get("likes_count") or 0),
        "comments_count": cint(doc.get("comments_count") or 0),
        "cta_label": "Join Conversation",
        "cta_icon": "💬",
        "cta_url": "/social?post=%s" % quote(str(name), safe=""),
        "cta_note": "Open this story on Afocha Social",
    })
    return post


def _load_forum(name):
    try:
        from bismillah_ethiobiz.walta_forum_api import get_forum_topic_detail
        payload = get_forum_topic_detail(name) or {}
    except Exception:
        payload = {}
    topic = payload.get("topic") or {}
    if not topic:
        return None

    replies = []
    for row in payload.get("replies") or []:
        replies.append({
            "id": row.get("name"),
            "author": row.get("author_name") or row.get("author") or "Walta Member",
            "avatar": _image(row.get("author_image")),
            "content": _rich_html(row.get("reply_text") or row.get("content")),
            "time_ago": row.get("creation_formatted") or _time_ago(row.get("creation")),
            "likes_count": cint(row.get("likes_count") or 0),
        })

    post = _base_post("Walta Forum Topic", name, "forum")
    post.update({
        "title": topic.get("title") or name,
        "subtitle": topic.get("category") or "Community discussion",
        "category": topic.get("category") or "General Discussion",
        "kicker": "Walta Forum · Sovereign discussion",
        "body_html": _rich_html(topic.get("content")),
        "body_text": _plain(topic.get("content")),
        "image": _image(topic.get("image")),
        "gallery": [{"image": _image(topic.get("image")), "caption": ""}] if topic.get("image") else [],
        "author_name": topic.get("author_name") or "Walta Member",
        "author_company": topic.get("company") or "",
        "author_handle": topic.get("author_handle") or "",
        "author_avatar": _image(topic.get("author_image")),
        "author_url": "/forum",
        "created": topic.get("creation"),
        "time_ago": topic.get("creation_formatted") or _time_ago(topic.get("creation")),
        "likes_count": cint(topic.get("likes_count") or 0),
        "comments_count": cint(topic.get("replies_count") or len(replies)),
        "replies": replies,
        "cta_label": "Join Topic",
        "cta_icon": "🗣️",
        "cta_url": "/forum?topic=%s" % quote(str(name), safe=""),
        "cta_note": "Continue the discussion on Walta Forum",
        "status": "Open",
        "specs": [
            {"label": "Category", "description": topic.get("category") or ""},
            {"label": "Replies", "description": str(len(replies))},
            {"label": "Views", "description": str(cint(topic.get("views_count") or 0))},
        ],
    })
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _load_blog(name):
    if not frappe.db.exists("Blog Post", name):
        return None
    doc = frappe.get_doc("Blog Post", name)
    route = _s(doc.get("route"))
    post = _base_post("Blog Post", name, "tibeb")

    content = _first(doc.get("content"), doc.get("blog_intro"))
    post.update({
        "title": doc.get("title") or name,
        "subtitle": _plain(doc.get("blog_intro"), 200),
        "category": doc.get("blog_category") or "Tibeb Wisdom",
        "kicker": "Tibeb · Ethiopian wisdom & insight",
        "body_html": _rich_html(content),
        "body_text": _plain(content),
        "image": _image(doc.get("meta_image")),
        "gallery": [{"image": _image(doc.get("meta_image")), "caption": doc.get("title") or ""}]
        if doc.get("meta_image") else [],
        "author_name": doc.get("blogger") or "EthioBiz Editorial Team",
        "author_company": "EthioBiz",
        "author_avatar": _image(doc.get("blogger_image")),
        "author_url": "/tibeb",
        "created": doc.get("published_on") or doc.get("creation"),
        "time_ago": _time_ago(doc.get("published_on") or doc.get("creation")),
        "cta_label": "Read Full Article",
        "cta_icon": "📖",
        "cta_url": ("/" + route.lstrip("/")) if route else "/tibeb",
        "cta_note": "Open the complete Tibeb article",
    })
    return post


def _load_course(name):
    if not frappe.db.exists("LMS Course", name):
        return None
    doc = frappe.get_doc("LMS Course", name)

    lessons = 0
    try:
        if frappe.db.table_exists("Course Lesson"):
            lessons = cint(frappe.db.count("Course Lesson", {"course": name}))
    except Exception:
        lessons = 0

    post = _base_post("LMS Course", name, "dagu")
    post.update({
        "title": doc.get("title") or name,
        "subtitle": _plain(doc.get("short_introduction"), 200),
        "category": doc.get("course_category") or "Dagu Academy",
        "kicker": "Dagu Academy · Practical course",
        "body_html": _rich_html(_first(doc.get("description"), doc.get("short_introduction"))),
        "body_text": _plain(doc.get("description")),
        "image": _image(doc.get("image")),
        "gallery": [{"image": _image(doc.get("image")), "caption": doc.get("title") or ""}]
        if doc.get("image") else [],
        "author_name": "Dagu Academy",
        "author_company": "EthioBiz",
        "author_url": "/courses",
        "created": doc.get("creation"),
        "time_ago": _time_ago(doc.get("creation")),
        "rating": flt(doc.get("rating") or 0),
        "status": "Published" if cint(doc.get("published", 1)) else "Draft",
        "highlights": [
            {"icon": "🎓", "text": "Certificate of completion"},
            {"icon": "📚", "text": ("%s lessons" % lessons) if lessons else "Self-paced"},
            {"icon": "💻", "text": "Learn online"},
        ],
        "specs": [
            {"label": "Category", "description": doc.get("course_category") or ""},
            {"label": "Lessons", "description": str(lessons) if lessons else ""},
            {"label": "Level", "description": doc.get("level") or ""},
        ],
        "cta_label": "Enroll in Course",
        "cta_icon": "🎓",
        "cta_url": "/lms/courses/%s" % quote(str(name), safe=""),
        "cta_note": "Start learning with Dagu Academy",
    })
    post["highlights"] = [h for h in post["highlights"] if h.get("text")]
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _load_ad(name):
    if not frappe.db.exists("EthioBiz Ad Campaign", name):
        return None
    doc = frappe.get_doc("EthioBiz Ad Campaign", name)
    destination = _first(doc.get("campaign_url"), doc.get("click_url"), "/shop")
    post = _base_post("EthioBiz Ad Campaign", name, "ad")
    post.update({
        "title": doc.get("campaign_name") or name,
        "subtitle": doc.get("alt_text") or "Sponsored feature from a verified EthioBiz partner",
        "category": "Sponsored",
        "kicker": "Sponsored · EthioBiz partner",
        "body_html": _rich_html(doc.get("alt_text") or "Discover featured enterprise solutions and exclusive offers from verified partners."),
        "image": _image(doc.get("creative_image")),
        "gallery": [{"image": _image(doc.get("creative_image")), "caption": doc.get("alt_text") or ""}]
        if doc.get("creative_image") else [],
        "author_name": doc.get("company") or "EthioBiz Partner",
        "author_company": doc.get("company") or "",
        "author_url": "/shop",
        "created": doc.get("creation"),
        "time_ago": _time_ago(doc.get("creation")),
        "external_url": destination,
        "cta_label": "Learn More",
        "cta_icon": "📢",
        "cta_url": destination,
        "cta_note": "Visit the sponsor's destination",
        "specs": [
            {"label": "Company", "description": doc.get("company") or ""},
            {"label": "Vertical", "description": doc.get("target_vertical") or ""},
            {"label": "Slot", "description": doc.get("slot") or ""},
        ],
    })
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _load_news(item_id):
    try:
        from bismillah_ethiobiz.news_api import get_news_item
        payload = get_news_item(item_id) or {}
    except Exception:
        payload = {}
    item = payload.get("news") or {}
    if not item:
        return None

    source = item.get("source") or "EthioBiz Live News"
    category = item.get("category_label") or item.get("category") or "News"
    published = item.get("published") or item.get("published_at") or item.get("pub_date") or ""
    post = _base_post("News", item_id, "news")
    post.update({
        "title": item.get("title") or "Live news story",
        "subtitle": source,
        "category": category,
        "kicker": "Live News · %s" % source,
        "body_html": _rich_html(item.get("summary") or item.get("description")),
        "body_text": _plain(item.get("summary")),
        "image": _image(item.get("image") or item.get("image_url")),
        "gallery": [{"image": _image(item.get("image") or item.get("image_url")), "caption": item.get("title") or ""}]
        if (item.get("image") or item.get("image_url")) else [],
        "author_name": source,
        "author_company": source,
        "author_url": item.get("url") or "/",
        "created": published,
        "time_ago": published,
        "external_url": item.get("url") or "",
        "cta_label": "Read Full Story",
        "cta_icon": "📰",
        "cta_url": item.get("url") or "/",
        "cta_note": "Continue at the original news source",
        "specs": [
            {"label": "Source", "description": source},
            {"label": "Category", "description": category},
            {"label": "Published", "description": _s(published)},
        ],
        "news": item,
    })
    post["specs"] = [s for s in post["specs"] if s["description"]]
    return post


def _load_generic(doctype, name, feed_type):
    try:
        if not frappe.db.exists(doctype, name):
            return None
        doc = frappe.get_doc(doctype, name)
    except Exception:
        return None

    meta = frappe.get_meta(doctype)
    title = _first(
        doc.get("title") if meta.has_field("title") else "",
        doc.get("subject") if meta.has_field("subject") else "",
        doc.get("name1") if meta.has_field("name1") else "",
        name,
    )
    body = ""
    for field in ("description", "content", "details", "notes"):
        if meta.has_field(field):
            body = doc.get(field)
            if body:
                break

    post = _base_post(doctype, name, feed_type)
    post.update({
        "title": title,
        "subtitle": "",
        "category": doctype,
        "kicker": "EthioBiz · %s" % doctype,
        "body_html": _rich_html(body),
        "body_text": _plain(body),
        "created": doc.get("creation"),
        "time_ago": _time_ago(doc.get("creation")),
        "author_name": doc.get("owner") or "EthioBiz",
        "author_company": "",
    })
    return post


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

def _resolve(doctype, name, feed_type):
    doctype = (doctype or "").strip()
    name = (name or "").strip()
    feed_type = (feed_type or "").strip().lower()

    if not feed_type:
        feed_type = FEED_TYPE_BY_DOCTYPE.get(doctype, "all")

    if doctype == "News" or feed_type == "news":
        post = _load_news(name)
        return post or _not_found(doctype or "News", name, "news")

    if doctype in ("Item", "Website Item") or feed_type == "products":
        post = _load_product(name, "products")
        return post or _not_found(doctype or "Item", name, "products")

    if doctype == "Job Opening" or feed_type == "jobs":
        post = _load_job(name)
        return post or _not_found(doctype or "Job Opening", name, "jobs")

    if doctype == "Healthcare Practitioner" or feed_type == "bizhealth":
        post = _load_doctor(name)
        return post or _not_found(doctype or "Healthcare Practitioner", name, "bizhealth")

    if doctype == "BizService Listing":
        post = _load_service(name, feed_type or "bizfix")
        return post or _not_found(doctype, name, feed_type or "bizfix")

    if doctype == "BizBooking Resource" or feed_type == "bizservices":
        post = _load_booking(name)
        return post or _not_found(doctype or "BizBooking Resource", name, "bizservices")

    if doctype == "Property" or feed_type == "bizhome":
        post = _load_property(name)
        return post or _not_found(doctype or "Property", name, "bizhome")

    if doctype == "Afocha Post" or feed_type == "social":
        post = _load_afocha(name)
        return post or _not_found(doctype or "Afocha Post", name, "social")

    if doctype == "Walta Forum Topic" or feed_type == "forum":
        post = _load_forum(name)
        return post or _not_found(doctype or "Walta Forum Topic", name, "forum")

    if doctype == "Blog Post" or feed_type == "tibeb":
        post = _load_blog(name)
        return post or _not_found(doctype or "Blog Post", name, "tibeb")

    if doctype == "LMS Course" or feed_type == "dagu":
        post = _load_course(name)
        return post or _not_found(doctype or "LMS Course", name, "dagu")

    if doctype == "EthioBiz Ad Campaign" or feed_type == "ad":
        post = _load_ad(name)
        return post or _not_found(doctype or "EthioBiz Ad Campaign", name, "ad")

    if doctype and name:
        post = _load_generic(doctype, name, feed_type)
        return post or _not_found(doctype, name, feed_type)

    return _not_found(doctype, name, feed_type or "all")


# ---------------------------------------------------------------------------
# Frappe entry point
# ---------------------------------------------------------------------------

def load_post(doctype, name, feed_type=""):
    """Public helper shared by the page controller and the slide API."""
    return _finish(_resolve(_s(doctype), _s(name), _s(feed_type)))


def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False
    context.body_class = ((context.get("body_class") or "") + " ebpost-body").strip()

    doctype = _s(frappe.form_dict.get("doctype"))
    name = _s(
        frappe.form_dict.get("name")
        or frappe.form_dict.get("docname")
        or frappe.form_dict.get("id")
    )
    feed_type = _s(frappe.form_dict.get("ft"))

    # Friendly aliases: /post?type=news&id=..., /post?post=...
    if not feed_type:
        feed_type = _s(frappe.form_dict.get("type"))
    if not name:
        name = _s(frappe.form_dict.get("post"))

    post = _finish(_resolve(doctype, name, feed_type))

    context.post = post
    context.title = post.get("meta_title") or post.get("title") or "EthioBiz"
    context.metatags = {
        "title": context.title,
        "description": post.get("meta_description") or "",
        "image": post.get("image") or "",
        "author": post.get("author_name") or "",
        "published_on": post.get("created") or "",
    }
    context.parents = [
        {"name": "Home", "route": "/"},
        {"name": "Live feed", "route": "/#live-feed-section"},
    ]
    if post.get("found"):
        context.parents.append({
            "name": post.get("portal_label") or post.get("feed_type") or "Feed",
            "route": post.get("portal_url") or "/",
        })
    context.labels = post.get("labels") or LABELS["en"]
    context.feed_style = post.get("style") or {}
    context.is_logged_in = frappe.session.user not in (None, "", "Guest")
    context.login_url = "/login?redirect-to=" + quote(
        "/post?doctype=%s&name=%s&ft=%s" % (
            quote(doctype, safe=""),
            quote(name, safe=""),
            quote(feed_type, safe=""),
        ),
        safe="/?=&",
    )
    try:
        context.csrf_token = frappe.sessions.get_csrf_token()
    except Exception:
        context.csrf_token = ""
    return context
