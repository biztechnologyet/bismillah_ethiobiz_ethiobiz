#!/usr/bin/env python3
"""Suite 48: Home search autoscroll + circular live-feed FAB (TASK-2026-00970).

Checks the deployed home template for the in-flow search, the single circular
search/category FAB, the desktop popover / mobile bottom sheet, accessibility
hooks, translations, and the live feed filter API. Browser-level desktop/mobile
behavior is covered by ethiobiz_analysis/pw/task_00970_test.js.
"""
import json
import os
import re
import sys

import requests
import urllib3

urllib3.disable_warnings()

_orig_print = print


def print(*args, **kwargs):
    kwargs.setdefault("flush", True)
    _orig_print(*args, **kwargs)


P = 0
F = 0
TEST_RESULTS = []


def chk(name, cond, msg="", rc="", sol=""):
    global P, F
    if cond:
        P += 1
        TEST_RESULTS.append({"id": name, "status": "PASS", "msg": msg, "rc": rc, "sol": sol})
        print("  PASS " + str(name))
    else:
        F += 1
        TEST_RESULTS.append({"id": name, "status": "FAIL", "msg": msg, "rc": rc, "sol": sol})
        print("  FAIL " + str(name) + ": " + msg)


def _save():
    try:
        rdir = "/home/frappe/frappe-bench/tests/results"
        os.makedirs(rdir, exist_ok=True)
        rp = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
        rf = len(TEST_RESULTS) - rp
        json.dump(
            {"suite": "48", "passed": rp, "failed": rf, "total": len(TEST_RESULTS), "results": TEST_RESULTS},
            open(os.path.join(rdir, "suite_48_report.json"), "w"),
            indent=2,
        )
    except Exception:
        pass


import atexit

atexit.register(_save)

BASE = "https://ethiobiz.et"
S = requests.Session()
S.verify = False
APP = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz"
TEMPLATE = APP + "/www/ethiobiz_home_v1.html"


def css_block(html, selector):
    """Return the first CSS declaration block for a selector, or ''."""
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", html)
    return m.group(1) if m else ""


print("\n" + "=" * 60)
print("SUITE 48: HOME SEARCH AUTOSCROLL + LIVE-FEED FAB")
print("=" * 60)

# --- 1. Served home page ---------------------------------------------------
r = S.get(BASE + "/?suite48=1", timeout=90)
chk("48.01 home page returns 200", r.status_code == 200, str(r.status_code), "home route broken", "check Website Settings / www template")
html = r.text if r.status_code == 200 else ""
chk("48.02 home page is substantial", len(html) > 150000, "len=%d" % len(html), "template truncated", "redeploy ethiobiz_home_v1.html")

# --- 2. Markup: single circular FAB + sheet -------------------------------
chk(
    "48.03 circular FAB markup present",
    'id="ethio-feed-fab"' in html
    and 'aria-controls="ethio-feed-sheet"' in html
    and 'aria-expanded="false"' in html,
    "FAB/aria hooks missing",
    "TASK-2026-00970 not deployed",
    "add #ethio-feed-fab with aria-controls/aria-expanded",
)
chk(
    "48.04 old floating Live Feed pill removed",
    "btn-floating-live-feed" not in html and "btn-floating-live-feed" not in open(TEMPLATE, encoding="utf-8").read(),
    "old pill still present",
    "duplicate floating control",
    "remove the old btn-floating-live-feed markup/CSS/JS",
)
chk(
    "48.05 sheet overlay and dialog markup",
    'id="ethio-feed-sheet-overlay"' in html
    and 'id="ethio-feed-sheet"' in html
    and 'role="dialog"' in html
    and 'aria-modal="true"' in html
    and 'aria-labelledby="ethio-feed-sheet-title"' in html,
    "dialog/overlay/aria markup missing",
    "accessibility regression",
    "restore role=dialog/aria-modal/aria-labelledby and overlay",
)
chk(
    "48.06 search form, categories, close, jump controls",
    all(
        token in html
        for token in (
            'id="ethio-feed-search-form"',
            'id="ethio-feed-search"',
            'id="ethio-feed-sheet-cats"',
            'id="ethio-feed-sheet-close"',
            'id="ethio-feed-sheet-jump"',
        )
    ),
    "one or more sheet controls missing",
    "panel is not usable",
    "restore the search/category/close/jump controls",
)
chk(
    "48.07 closed sheet is inert and aria-hidden",
    re.search(r'<section[^>]+id="ethio-feed-sheet"[^>]*aria-hidden="true"[^>]*inert', html) is not None,
    "closed sheet not inert",
    "keyboard can tab into hidden sheet",
    "add inert + aria-hidden=true to the closed sheet",
)
chk(
    "48.08 no duplicate new IDs",
    all(len(re.findall(r'id="' + re.escape(i) + r'"', html)) == 1 for i in (
        "ethio-feed-fab",
        "ethio-feed-sheet",
        "ethio-feed-sheet-overlay",
        "ethio-feed-search",
        "ethio-feed-sheet-cats",
        "ethio-feed-sheet-close",
        "ethio-feed-sheet-jump",
    )),
    "duplicate ID found",
    "ambiguous DOM lookups",
    "keep exactly one instance of each new ID",
)

# --- 3. In-flow search -----------------------------------------------------
search_css = css_block(html, ".top-search-section")
chk(
    "48.09 search is in-flow, not fixed/sticky",
    "position: relative" in search_css and "position: fixed" not in search_css and "position: sticky" not in search_css,
    "search CSS=%r" % search_css[:160],
    "search still floats instead of scrolling",
    "keep .top-search-section position: relative",
)
chk(
    "48.10 in-flow search input + button present",
    'id="home-omni-search"' in html and 'id="btn-omni-search"' in html,
    "main search input/button missing",
    "search behavior regressed",
    "restore #home-omni-search and #btn-omni-search",
)

# --- 4. FAB / sheet CSS ----------------------------------------------------
fab_css = css_block(html, ".ethio-feed-fab")
dock_css = css_block(html, ".ethio-feed-dock")
chk(
    "48.11 FAB is circular (50px desktop, 46px mobile)",
    "width: 50px" in fab_css
    and "height: 50px" in fab_css
    and "border-radius: 50%" in fab_css
    and "width: 46px" in html
    and "height: 46px" in html,
    "FAB geometry=%r" % fab_css[:160],
    "FAB not circular",
    "keep the circular dock FAB at 50px desktop / 46px mobile",
)
chk(
    "48.12 FAB dock sits above content below chat/modals",
    "z-index: 1100" in dock_css,
    "FAB dock z-index missing",
    "FAB may be hidden or cover chat",
    "keep the dock z-index 1100 (chat 99999, modals 9999)",
)
sheet_css = css_block(html, ".ethio-feed-sheet")
overlay_css = css_block(html, ".ethio-feed-sheet-overlay")
chk(
    "48.13 sheet/overlay z-index below modals",
    "z-index: 1201" in sheet_css and "z-index: 1200" in overlay_css,
    "sheet/overlay z-index wrong",
    "sheet may render below/above modals incorrectly",
    "keep overlay 1200 and sheet 1201",
)
chk(
    "48.14 desktop popover width and gap",
    "width: min(560px" in sheet_css and "bottom: calc(96px" in sheet_css,
    "desktop panel width/gap missing",
    "panel placement regressed",
    "restore min(560px, calc(100vw - 28px)) and bottom 96px",
)
mobile_css = ""
mm = re.search(
    r"\.ethio-feed-sheet\s*\{\s*left:\s*0;\s*right:\s*0;\s*bottom:\s*0;[^}]*\}",
    html,
)
if mm:
    mobile_css = mm.group(0)
chk(
    "48.15 mobile bottom sheet rule",
    "left: 0" in mobile_css and "right: 0" in mobile_css and "bottom: 0" in mobile_css
    and "transform: translateY(100%)" in mobile_css and "border-radius: 24px 24px 0 0" in mobile_css,
    "mobile sheet rule incomplete",
    "mobile panel may be a desktop popover",
    "restore the max-width:720px bottom-sheet block",
)
chk(
    "48.16 reduced-motion support",
    "prefers-reduced-motion: reduce" in html and ".ethio-feed-dock" in html,
    "reduced-motion rule missing",
    "animation ignores accessibility preference",
    "add prefers-reduced-motion: reduce for the FAB/sheet",
)

# --- 5. JavaScript behavior hooks -----------------------------------------
chk(
    "48.17 category render/select hooks",
    "function renderCategories()" in html and "function selectCategory(filter)" in html and "sourceFilterButtons()" in html,
    "category JS missing",
    "FAB categories do not render/filter",
    "restore renderCategories/selectCategory",
)
chk(
    "48.18 close/escape/focus-trap hooks",
    "e.key === 'Escape'" in html and "e.key === 'Tab'" in html and "e.shiftKey" in html and "closeSheet(false)" in html,
    "keyboard close/trap hooks missing",
    "keyboard users can get trapped or cannot close",
    "restore Escape/Tab focus trap",
)
chk(
    "48.19 search handoff to existing omni search",
    "getElementById('home-omni-search')" in html and "mainSearch.value = q" in html and "mainSearchBtn.click()" in html,
    "search handoff missing",
    "FAB search does not reuse the main search",
    "set #home-omni-search and click #btn-omni-search",
)
chk(
    "48.20 language switch updates FAB labels",
    "data-i18n-aria-label" in html and "feedSearchInput.placeholder" in html and "ethiobiz-lang-changed" in html,
    "FAB i18n hooks missing",
    "Amharic labels stale",
    "update aria-label/placeholder/categories on language change",
)

# --- 6. Translations -------------------------------------------------------
chk(
    "48.21 English + Amharic FAB keys",
    html.count('"feed-fab-title":') == 2
    and html.count('"feed-fab-placeholder":') == 2
    and html.count('"feed-fab-aria":') == 2,
    "translation key count=%d/%d/%d" % (
        html.count('"feed-fab-title":'),
        html.count('"feed-fab-placeholder":'),
        html.count('"feed-fab-aria":'),
    ),
    "one language missing FAB labels",
    "add feed-fab-* keys to both translation objects",
)

# --- 7. Feed categories and API -------------------------------------------
chk(
    "48.22 at least nine feed category buttons",
    len(re.findall(r'<button[^>]+class="stream-filter-btn[^"]*"', html)) >= 9,
    "found %d" % len(re.findall(r'<button[^>]+class="stream-filter-btn[^"]*"', html)),
    "category source list incomplete",
    "restore the stream-filter-btn list",
)
r = S.get(BASE + "/api/method/bismillah_ethiobiz.home_api.get_feed_filter_structure", timeout=60)
ok = r.status_code == 200
chk("48.23 filter structure API returns 200", ok, str(r.status_code), "endpoint missing/500", "deploy home_api.py")
filters = None
if ok:
    try:
        filters = r.json().get("message")
    except Exception:
        filters = None
chk("48.24 filter structure is non-empty dict", isinstance(filters, dict) and bool(filters), "type=%r" % type(filters).__name__, "filter API shape wrong", "return FEED_FILTER_STRUCTURE")
if isinstance(filters, dict):
    sample = next(iter(filters.values()), [])
    chk(
        "48.25 filter option keys intact",
        isinstance(sample, list) and all({"key", "label", "label_am"}.issubset(row) for row in sample),
        "option keys missing",
        "panel category labels may break",
        "return key/label/label_am arrays",
    )
r = S.get(
    BASE + "/api/method/bismillah_ethiobiz.smart_feed_api.get_personalized_feed?start=0&limit=3&filter_type=all",
    timeout=90,
)
ok = r.status_code == 200
chk("48.26 live feed API returns 200", ok, str(r.status_code), "feed endpoint broken", "check smart_feed_api.py and backend logs")
if ok:
    try:
        feed = r.json().get("message")
    except Exception:
        feed = None
    chk(
        "48.27 live feed payload shape",
        isinstance(feed, list) or (isinstance(feed, dict) and isinstance(feed.get("items"), list)),
        "type=%r" % type(feed).__name__,
        "feed payload shape changed",
        "return a list or {status,total,items,...} from get_personalized_feed",
    )

# --- 8. Disk template matches served HTML --------------------------------
try:
    disk = open(TEMPLATE, encoding="utf-8").read()
    chk(
        "48.28 served home contains the deployed FAB",
        'id="ethio-feed-fab"' in disk and 'id="ethio-feed-sheet"' in disk,
        "disk template missing FAB",
        "server file not updated",
        "copy the updated template to the app www directory",
    )
except Exception as exc:
    chk("48.28 served home contains the deployed FAB", False, str(exc)[:200], "", "")

print("\nSUITE 48 RESULT: PASS=%d FAIL=%d" % (P, F))
sys.exit(0 if F == 0 else 1)
