# -*- coding: utf-8 -*-
"""
Bismillah — EthioBiz Live News Feed API (InSha'Allah)
TASK-2026-00830: Customizable News Feed in EthioBiz Feed

Provides live multi-category news (World, Sports, Tech, Business, Politics, Health, Science, Culture)
with rich images, live RSS ingestion from top Ethiopian and global sources, caching, and user preference storage.
"""

import os
import re
import json
import html
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
import frappe

# Available news categories with metadata
NEWS_CATEGORIES = [
    {"id": "business", "label": "Business & Economy", "am_label": "ንግድ እና ኢኮኖሚ", "icon": "💼", "badge_color": "#0d9488"},
    {"id": "tech", "label": "Tech & Innovation", "am_label": "ቴክኖሎጂ እና ፈጠራ", "icon": "💻", "badge_color": "#2563eb"},
    {"id": "ethiopia", "label": "Ethiopia & Horn", "am_label": "ኢትዮጵያ እና ቀንድ አፍሪካ", "icon": "🇪🇹", "badge_color": "#059669"},
    {"id": "world", "label": "World News", "am_label": "ዓለም አቀፍ ዜና", "icon": "🌍", "badge_color": "#7c3aed"},
    {"id": "sport", "label": "Sports", "am_label": "ስፖርት", "icon": "⚽", "badge_color": "#ea580c"},
    {"id": "politics", "label": "Politics & Governance", "am_label": "ፖለቲካ እና አስተዳደር", "icon": "🏛️", "badge_color": "#475569"},
    {"id": "health", "label": "Health & Life", "am_label": "ጤና እና አኗኗር", "icon": "🏥", "badge_color": "#e11d48"},
    {"id": "science", "label": "Science & Climate", "am_label": "ሳይንስ እና የአየር ንብረት", "icon": "🔬", "badge_color": "#0891b2"},
    {"id": "culture", "label": "Culture & Heritage", "am_label": "ባህል እና ቅርስ", "icon": "🎭", "badge_color": "#b45309"},
]

CATEGORY_MAP = {c["id"]: c for c in NEWS_CATEGORIES}

# Curated, reliable RSS Feeds categorized
RSS_SOURCES = {
    "business": [
        {"name": "Addis Standard Business", "url": "https://addisstandard.com/category/economy/feed/", "default_img": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=80"},
        {"name": "Capital Ethiopia", "url": "https://www.capitalethiopia.com/feed/", "default_img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&auto=format&fit=crop&q=80"},
    ],
    "tech": [
        {"name": "TechCrunch Africa", "url": "https://techcrunch.com/tag/africa/feed/", "default_img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80"},
        {"name": "Disrupt Africa", "url": "https://disrupt-africa.com/feed/", "default_img": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80"},
    ],
    "ethiopia": [
        {"name": "Addis Standard", "url": "https://addisstandard.com/feed/", "default_img": "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800&auto=format&fit=crop&q=80"},
        {"name": "Ethiopian Monitor", "url": "https://ethiopianmonitor.com/feed/", "default_img": "https://images.unsplash.com/photo-1523821741446-edb2b68bb7a0?w=800&auto=format&fit=crop&q=80"},
    ],
    "world": [
        {"name": "BBC Africa", "url": "https://feeds.bbci.co.uk/news/world/africa/rss.xml", "default_img": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&auto=format&fit=crop&q=80"},
        {"name": "Al Jazeera World", "url": "https://www.aljazeera.com/xml/rss/all.xml", "default_img": "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&auto=format&fit=crop&q=80"},
    ],
    "sport": [
        {"name": "BBC Sport Football", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml", "default_img": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800&auto=format&fit=crop&q=80"},
    ],
    "health": [
        {"name": "WHO Africa", "url": "https://www.afro.who.int/rss/news.xml", "default_img": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800&auto=format&fit=crop&q=80"},
    ],
    "science": [
        {"name": "ScienceDaily", "url": "https://www.sciencedaily.com/rss/top/science.xml", "default_img": "https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=800&auto=format&fit=crop&q=80"},
    ],
    "culture": [
        {"name": "African Culture & Arts", "url": "https://addisstandard.com/category/art-culture/feed/", "default_img": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=800&auto=format&fit=crop&q=80"},
    ],
}

# Curated fallback news in case of internet timeout
FALLBACK_NEWS = [
    {
        "id": "eth-fin-2026-01",
        "title": "National Bank of Ethiopia Advances Digital Currency & Financial Modernization",
        "am_title": "የኢትዮጵያ ብሔራዊ ባንክ የዲጂታል ክፍያ እና የፋይናንስ ሥርዓትን ማሻሻሉን ቀጥሏል",
        "summary": "Recent policy reforms and digital banking acceleration drive historic trade and commercial modernization across Ethiopian private and public sectors.",
        "category": "Business & Economy",
        "category_id": "business",
        "source": "EthioBiz Business Wire",
        "published_at": "Today, 10:30 AM",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=80",
        "url": "https://ethiobiz.et/blog",
        "badge_color": "#0d9488",
        "icon": "💼"
    },
    {
        "id": "eth-tech-2026-02",
        "title": "Ethiopian Tech Ecosystem Expands with Artificial Intelligence & Cloud Solutions",
        "am_title": "በኢትዮጵያ የሰው ሰራሽ አስተውሎት (AI) እና የክላውድ ቴክኖሎጂዎች ዕድገት እያሳዩ ነው",
        "summary": "Local tech innovators and software enterprises in Hawassa and Addis Ababa deploy scalable cloud workflows and ERP automation for retail and manufacturing.",
        "category": "Tech & Innovation",
        "category_id": "tech",
        "source": "EthioBiz Tech Review",
        "published_at": "Today, 09:15 AM",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
        "url": "https://ethiobiz.et/blog",
        "badge_color": "#2563eb",
        "icon": "💻"
    },
    {
        "id": "eth-sp-2026-03",
        "title": "Ethiopian Premier League Thrills Fans with Spectacular Weekend Matches",
        "am_title": "የኢትዮጵያ ፕሪሚየር ሊግ በደማቅ የሳምንቱ መጨረሻ ጨዋታዎች ቀጥሏል",
        "summary": "Exciting competition and record attendance mark the latest round of the Ethiopian Premier League across regional stadiums.",
        "category": "Sports",
        "category_id": "sport",
        "source": "EthioBiz Sports",
        "published_at": "Today, 08:45 AM",
        "image_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800&auto=format&fit=crop&q=80",
        "url": "https://ethiobiz.et/social",
        "badge_color": "#ea580c",
        "icon": "⚽"
    },
    {
        "id": "eth-cult-2026-04",
        "title": "Tibeb Wisdom: Celebrating African Philosophy and Living Cultural Heritage",
        "am_title": "ጥበብ፡ የአፍሪካ ፍልስፍና እና የሕያው ባህላዊ ቅርስ ክብረ በዓል",
        "summary": "EthioBiz Tibeb portal documents traditional craftsmanship, poetry, and shared values connecting communities across the Horn of Africa.",
        "category": "Culture & Heritage",
        "category_id": "culture",
        "source": "Tibeb Quarterly",
        "published_at": "Yesterday",
        "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=800&auto=format&fit=crop&q=80",
        "url": "https://ethiobiz.et/tibeb",
        "badge_color": "#b45309",
        "icon": "🎭"
    },
    {
        "id": "eth-wrld-2026-05",
        "title": "Global Trade Routes & Green Energy Investments Shape Emerging Markets",
        "am_title": "ዓለም አቀፍ የንግድ መስመሮች እና የአረንጓዴ ኢነርጂ ኢንቨስትመንቶች",
        "summary": "International renewable energy partnerships and industrial parks create new export opportunities for African economies.",
        "category": "World News",
        "category_id": "world",
        "source": "Global Wire",
        "published_at": "Today, 07:00 AM",
        "image_url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&auto=format&fit=crop&q=80",
        "url": "https://ethiobiz.et/social",
        "badge_color": "#7c3aed",
        "icon": "🌍"
    }
]

def _clean_html(raw_html):
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", "", raw_html)
    return html.unescape(clean).strip()

def _clean_text_key(txt):
    if not txt:
        return ""
    return re.sub(r"[\W_]+", "", txt.lower()).strip()

def _extract_image(item, default_img):
    # 1. Direct children tags including namespaced tags
    for elem in item:
        tag = elem.tag.lower()
        if "content" in tag or "thumbnail" in tag:
            url = elem.attrib.get("url")
            if url and (url.startswith("http://") or url.startswith("https://")):
                return url
        if "enclosure" in tag:
            url = elem.attrib.get("url")
            type_attr = elem.attrib.get("type", "")
            if url and ("image" in type_attr or url.startswith("http://") or url.startswith("https://")):
                return url

    # 2. Search entire XML element subtree for any image url attribute
    for elem in item.iter():
        tag = elem.tag.lower()
        if any(k in tag for k in ["thumbnail", "image", "content", "enclosure"]):
            url = elem.attrib.get("url") or elem.attrib.get("src")
            if url and (url.startswith("http://") or url.startswith("https://")):
                if not any(tracker in url.lower() for tracker in ["1x1", "pixel", "tracker", "ad."]):
                    return url

    # 3. Check HTML in content:encoded or description
    for child in item:
        if any(k in child.tag.lower() for k in ["description", "encoded", "body"]):
            text = child.text or ""
            if "<img" in text:
                match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.IGNORECASE)
                if match:
                    src = match.group(1)
                    if src.startswith("http://") or src.startswith("https://"):
                        if not any(tracker in src.lower() for tracker in ["1x1", "pixel", "tracker"]):
                            return src

    return default_img

def _fetch_rss_category(cat_id, limit=8):
    sources = RSS_SOURCES.get(cat_id, [])
    cat_meta = CATEGORY_MAP.get(cat_id, {"label": cat_id.title(), "icon": "📰", "badge_color": "#0d9488"})
    results = []

    for src in sources:
        try:
            req = urllib.request.Request(
                src["url"],
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EthioBizNewsBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)

                # Channel items
                items = root.findall(".//item")
                for it in items[:limit]:
                    title_elem = it.find("title")
                    link_elem = it.find("link")
                    desc_elem = it.find("description")
                    pub_elem = it.find("pubDate")

                    title = _clean_html(title_elem.text if title_elem is not None else "")
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    desc = _clean_html(desc_elem.text if desc_elem is not None else "")
                    pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

                    if not title or len(title) < 5:
                        continue

                    # Truncate summary nicely
                    if len(desc) > 240:
                        desc = desc[:237] + "..."

                    # Image extraction
                    img = _extract_image(it, src.get("default_img"))

                    # Unique id
                    item_id = "news-" + re.sub(r"\W+", "-", title[:35].lower()).strip("-")

                    results.append({
                        "id": item_id,
                        "title": title,
                        "summary": desc,
                        "category": cat_meta["label"],
                        "category_id": cat_id,
                        "source": src["name"],
                        "published_at": pub_date[:16] if pub_date else "Recent",
                        "image_url": img,
                        "url": link,
                        "badge_color": cat_meta["badge_color"],
                        "icon": cat_meta["icon"]
                    })
        except Exception:
            # RSS fetch error, skip source gracefully
            pass

    return results

@frappe.whitelist(allow_guest=True)
def get_news_categories():
    """Return available news categories for user selection."""
    return {"status": "success", "categories": NEWS_CATEGORIES}

@frappe.whitelist(allow_guest=True)
def get_live_news(categories=None, limit=12, page=1):
    """
    Fetch live news items with strict deduplication and genuine pagination.
    """
    page = max(1, int(page or 1))
    limit = max(1, min(50, int(limit or 12)))

    if isinstance(categories, str):
        try:
            categories = json.loads(categories)
        except Exception:
            categories = [c.strip() for c in categories.split(",") if c.strip()]

    if not categories:
        if frappe.session.user and frappe.session.user != "Guest":
            try:
                cached_pref = frappe.cache().hget("user_news_pref", frappe.session.user)
                if cached_pref:
                    categories = json.loads(cached_pref)
            except Exception:
                pass

    if not categories:
        categories = ["business", "tech", "ethiopia", "sport", "world"]

    cache_key = f"ebz_live_news_{'_'.join(sorted(categories))}"
    cached_pool = frappe.cache().get_value(cache_key)

    if not cached_pool:
        collected = []
        for cat in categories:
            cat_items = _fetch_rss_category(cat, limit=10)
            collected.extend(cat_items)

        # Fallbacks if few items found
        if len(collected) < 6:
            filtered_fallbacks = [f for f in FALLBACK_NEWS if f["category_id"] in categories or not categories]
            if not filtered_fallbacks:
                filtered_fallbacks = FALLBACK_NEWS
            collected.extend(filtered_fallbacks)

        # Strict deduplication by normalized title and URL
        seen_keys = set()
        deduped = []
        for item in collected:
            t_key = _clean_text_key(item.get("title"))
            u_key = (item.get("url") or "").strip().rstrip("/").lower()
            if not t_key:
                continue
            if t_key in seen_keys or (u_key and u_key in seen_keys):
                continue
            seen_keys.add(t_key)
            if u_key:
                seen_keys.add(u_key)
            deduped.append(item)

        # Interleave across categories to provide rich diversity
        grouped = {}
        for item in deduped:
            grouped.setdefault(item["category_id"], []).append(item)

        interleaved = []
        max_len = max(len(v) for v in grouped.values()) if grouped else 0
        for i in range(max_len):
            for cat in categories:
                if cat in grouped and i < len(grouped[cat]):
                    interleaved.append(grouped[cat][i])

        cached_pool = interleaved if interleaved else deduped

        try:
            frappe.cache().set_value(cache_key, cached_pool, expires_in_sec=900)
        except Exception:
            pass

    # Genuine pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_items = cached_pool[start_idx:end_idx]

    return {
        "status": "success",
        "news": page_items,
        "page": page,
        "limit": limit,
        "total": len(cached_pool),
        "has_more": end_idx < len(cached_pool),
        "cached": bool(cached_pool)
    }

@frappe.whitelist()
def save_user_news_preferences(categories):
    """Save selected news categories for the logged-in user."""
    if not frappe.session.user or frappe.session.user == "Guest":
        return {"status": "error", "message": "Must be logged in to save preferences"}

    if isinstance(categories, list):
        categories_str = json.dumps(categories)
    else:
        categories_str = str(categories)

    # Ensure field exists or save in User Settings
    frappe.cache().hset("user_news_pref", frappe.session.user, categories_str)
    return {"status": "success", "preferences": categories}

@frappe.whitelist(allow_guest=True)
def get_user_news_preferences():
    """Retrieve saved news preferences for the user."""
    if not frappe.session.user or frappe.session.user == "Guest":
        return {"status": "guest", "preferences": ["business", "tech", "ethiopia", "sport", "world"]}

    pref = frappe.cache().hget("user_news_pref", frappe.session.user)
    if pref:
        try:
            return {"status": "success", "preferences": json.loads(pref)}
        except Exception:
            pass
    return {"status": "default", "preferences": ["business", "tech", "ethiopia", "sport", "world"]}
