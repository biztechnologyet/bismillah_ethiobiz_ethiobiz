"""Seed the home flip cards and card-back portals into EthioBiz Theme.

Idempotent: existing admin-edited values are preserved. The patch only fills
blank fields and appends missing rows. Run once through ``patches.txt``.
"""

import frappe

from bismillah_ethiobiz.ethiobiz_theme.home_system_defaults import (
    PORTAL_DEFAULTS,
    PORTAL_TITLE_AM,
    SYSTEM_DEFAULTS,
    split_bilingual,
    subsystem_for_url,
)

PILLARS = ["Tibeb", "Dagu", "Magala", "DOBiz", "Walta", "Afocha"]


def _v(row, key, default=None):
    return getattr(row, key, default)


def _set_if_blank(theme, row, key, value):
    if value in (None, ""):
        return
    current = _v(row, key)
    if current in (None, ""):
        setattr(row, key, value)


def _seed_systems(theme):
    existing = {}
    for row in getattr(theme, "pillars", []) or []:
        key = (_v(row, "pillar_key") or "").strip()
        name = (_v(row, "pillar_name") or "").strip()
        if key and key not in existing:
            existing[key] = row
        elif name and name not in existing:
            existing[name] = row

    for default in SYSTEM_DEFAULTS:
        row = existing.get(default["pillar_key"]) or existing.get(default["pillar_name"])
        if row is None:
            row = theme.append("pillars", {})
        for field, value in default.items():
            _set_if_blank(theme, row, field, value)
        if _v(row, "is_enabled", None) is None:
            row.is_enabled = 1
        if not _v(row, "subsystem_key"):
            row.subsystem_key = default["subsystem_key"]


def _seed_portals(theme):
    existing = list(getattr(theme, "card_portal_items", []) or [])
    seen = set()
    next_sort = {pillar: 10 for pillar in PILLARS}

    for row in existing:
        pillar = (_v(row, "pillar") or "").strip()
        if pillar not in PILLARS:
            continue

        title_en, title_am = split_bilingual(_v(row, "title"))
        subtitle_en, subtitle_am = split_bilingual(_v(row, "subtitle"))

        if not _v(row, "title") and title_en:
            row.title = title_en
        if not _v(row, "title_am") and title_am:
            row.title_am = title_am
        if not _v(row, "subtitle") and subtitle_en:
            row.subtitle = subtitle_en
        if not _v(row, "subtitle_am") and subtitle_am:
            row.subtitle_am = subtitle_am

        # Older live rows used "none" for every portal, which leaked disabled
        # systems onto card backs. Derive the owner from the URL.
        if (_v(row, "subsystem_key") or "none") in ("", "none"):
            row.subsystem_key = subsystem_for_url(_v(row, "url"))
        if not _v(row, "icon"):
            row.icon = "🌐"
        if _v(row, "is_enabled", None) is None:
            row.is_enabled = 1
        if not _v(row, "sort_order"):
            row.sort_order = next_sort[pillar]
        next_sort[pillar] = max(next_sort[pillar], int(row.sort_order or 0)) + 10

        if not _v(row, "title_am"):
            fallback = PORTAL_TITLE_AM.get(_v(row, "title") or "")
            if fallback:
                row.title_am, row.subtitle_am = fallback

        seen.add((pillar, _v(row, "url") or "", _v(row, "title") or ""))

    for pillar in PILLARS:
        for default in PORTAL_DEFAULTS.get(pillar, []):
            identity = (pillar, default["url"], default["title"])
            if identity in seen:
                continue
            # Also avoid adding a row when the same URL already exists with the
            # English title but a different legacy title.
            url_key = (pillar, default["url"], "")
            if any(key[0] == pillar and key[1] == default["url"] for key in seen):
                continue
            row = theme.append("card_portal_items", {})
            row.pillar = pillar
            row.title = default["title"]
            row.title_am = default["title_am"]
            row.subtitle = default["subtitle"]
            row.subtitle_am = default["subtitle_am"]
            row.url = default["url"]
            row.icon = default["icon"]
            row.subsystem_key = default["subsystem_key"]
            row.is_enabled = 1
            row.sort_order = next_sort[pillar]
            next_sort[pillar] += 10
            seen.add(identity)


def seed(dry_run=False):
    theme = frappe.get_single("EthioBiz Theme")
    _seed_systems(theme)
    _seed_portals(theme)
    if dry_run:
        return theme
    theme.flags.ignore_permissions = True
    theme.flags.ignore_validate_update_after_submit = True
    theme.save(ignore_permissions=True)
    frappe.clear_cache()
    frappe.db.commit()
    print(
        "Seeded EthioBiz home cards: %s cards, %s portals"
        % (len(theme.pillars or []), len(theme.card_portal_items or []))
    )
    return theme


def execute():
    seed(dry_run=False)
