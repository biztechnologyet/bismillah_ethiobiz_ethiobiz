# -*- coding: utf-8 -*-
"""
Bismillah — Tibeb Holy Scriptures REST API (Insha'Allah)
Provides structured, fast database access for Quran, Gospel, Torah, Psalm, and Hadeeth.
"""

import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_holy_books():
    """Returns all available Holy Books with their chapter and verse counts."""
    return frappe.get_all(
        "Tibeb Holy Book",
        fields=["name", "book_name", "amharic_name", "arabic_name", "scripture_type", "total_chapters", "total_verses", "original_language", "icon", "color", "description", "description_amharic"],
        order_by="creation asc"
    )

@frappe.whitelist(allow_guest=True)
def get_book_chapters(holy_book):
    """Returns chapters for a given Holy Book."""
    if not holy_book:
        return []
    return frappe.get_all(
        "Tibeb Chapter",
        filters={"holy_book": holy_book},
        fields=["name", "chapter_number", "title_en", "title_am", "title_original", "revelation_place", "verses_count", "summary"],
        order_by="chapter_number asc"
    )

@frappe.whitelist(allow_guest=True)
def get_chapter_verses(holy_book, chapter_number, page=1, limit=50):
    """Returns verses for a specific chapter with original text, Amharic, and English."""
    chapter_number = int(chapter_number)
    page = max(1, int(page or 1))
    limit = max(1, min(100, int(limit or 50)))
    start = (page - 1) * limit

    verses = frappe.get_all(
        "Tibeb Verse",
        filters={"holy_book": holy_book, "chapter_number": chapter_number},
        fields=["name", "chapter_number", "verse_number", "text_original", "text_amharic", "text_english", "tafsir_commentary", "audio_url"],
        order_by="verse_number asc",
        start=start,
        page_length=limit
    )

    total = frappe.db.count("Tibeb Verse", {"holy_book": holy_book, "chapter_number": chapter_number})

    return {
        "holy_book": holy_book,
        "chapter_number": chapter_number,
        "verses": verses,
        "page": page,
        "total": total,
        "has_more": (start + len(verses)) < total
    }

@frappe.whitelist(allow_guest=True)
def search_scriptures(query, holy_book=None, lang="am", limit=20):
    """Full-text search across holy books in Amharic, English, or Original text."""
    if not query:
        return []

    filters = []
    values = []

    if holy_book:
        filters.append("holy_book = %s")
        values.append(holy_book)

    search_term = f"%{query}%"
    if lang == "am":
        filters.append("text_amharic LIKE %s")
        values.append(search_term)
    elif lang == "en":
        filters.append("text_english LIKE %s")
        values.append(search_term)
    else:
        filters.append("(text_original LIKE %s OR text_amharic LIKE %s OR text_english LIKE %s)")
        values.extend([search_term, search_term, search_term])

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""
    values.append(int(limit or 20))

    return frappe.db.sql(f"""
        SELECT name, holy_book, chapter_number, verse_number, text_original, text_amharic, text_english
        FROM `tabTibeb Verse`
        {where_clause}
        ORDER BY holy_book, chapter_number, verse_number
        LIMIT %s
    """, tuple(values), as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_hadeeth_collections():
    """Returns distinct Hadeeth collections."""
    return frappe.db.sql("""
        SELECT collection_name, COUNT(name) as total_hadeeths
        FROM `tabTibeb Hadeeth`
        GROUP BY collection_name
    """, as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_hadeeths(collection_name=None, page=1, limit=20):
    """Returns hadeeths with genuine pagination."""
    filters = {}
    if collection_name:
        filters["collection_name"] = collection_name

    page = max(1, int(page or 1))
    limit = max(1, min(50, int(limit or 20)))
    start = (page - 1) * limit

    items = frappe.get_all(
        "Tibeb Hadeeth",
        filters=filters,
        fields=["name", "collection_name", "book_number", "hadeeth_number", "narrator", "text_arabic", "text_amharic", "text_english", "grade", "explanation"],
        order_by="hadeeth_number asc",
        start=start,
        page_length=limit
    )

    total = frappe.db.count("Tibeb Hadeeth", filters)

    return {
        "items": items,
        "page": page,
        "total": total,
        "has_more": (start + len(items)) < total
    }

@frappe.whitelist(allow_guest=True)
def get_daily_verse_of_wisdom():
    """Returns a daily featured verse of wisdom for the Tibeb portal and homepage banner."""
    cache_key = "tibeb_daily_wisdom"
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached

    # Rotate or pick a high-wisdom verse
    verse = frappe.db.sql("""
        SELECT name, holy_book, chapter_number, verse_number, text_original, text_amharic, text_english
        FROM `tabTibeb Verse`
        ORDER BY RAND()
        LIMIT 1
    """, as_dict=True)

    result = verse[0] if verse else {
        "holy_book": "Quran",
        "chapter_number": 1,
        "verse_number": 1,
        "text_original": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "text_amharic": "በአላህ ስም እጅግ በጣም ሩኅሩህ በጣም አዛኝ በሆነው።",
        "text_english": "In the name of Allah, the Entirely Merciful, the Especially Merciful."
    }

    frappe.cache().set_value(cache_key, result, expires_in_sec=3600)
    return result
