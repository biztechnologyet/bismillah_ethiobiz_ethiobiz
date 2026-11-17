#!/usr/bin/env python3
"""Suite 46: Home page moved from Web Page doctype to www + home APIs.

Verifies the standalone www template, archived Web Page, CSRF bootstrap,
feature markers, and the four home-page APIs (plus ad click tracking).
"""
import os
import re
import sys
import json

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
            {"suite": "46", "passed": rp, "failed": rf, "total": len(TEST_RESULTS), "results": TEST_RESULTS},
            open(os.path.join(rdir, "suite_46_report.json"), "w"),
            indent=2,
        )
    except Exception:
        pass


import atexit

atexit.register(_save)

BASE = "https://ethiobiz.et"
S = requests.Session()
S.verify = False


def get(path, **kw):
    kw.setdefault("timeout", 60)
    return S.get(BASE + path, **kw)


print("\n" + "=" * 60)
print("SUITE 46: HOME PAGE WWW MIGRATION + HOME APIs")
print("=" * 60)

# --- 1. Standalone www template -------------------------------------------
for tid, path in (("46.01", "/"), ("46.02", "/ethiobiz_home_v1")):
    r = get(path)
    chk(
        "%s %s returns 200" % (tid, path),
        r.status_code == 200,
        "%s len=%d" % (r.status_code, len(r.text)),
        "template missing or route shadowed by published Web Page",
        "deploy www/ethiobiz_home_v1.html and archive the Web Page record",
    )
    chk(
        "%s %s has one html/body document" % (tid, path),
        r.text.lower().count("<html") == 1 and r.text.lower().count("<body") == 1,
        "html=%d body=%d" % (r.text.lower().count("<html"), r.text.lower().count("<body")),
        "Web Page wrapper still active",
        "unpublish/archive the Web Page record and clear website cache",
    )
    chk(
        "%s %s has CSRF bootstrap" % (tid, path),
        "window.csrf_token" in r.text and "window.frappe.session" in r.text,
        "bootstrap marker missing",
        "www controller did not pass csrf_token",
        "add context.csrf_token = frappe.sessions.get_csrf_token() and inject bootstrap",
    )

r = get("/ethiobiz_home_v1")
for marker, label in (
    ("hero-carousel-track", "hero carousel"),
    ("infinite-stream-container", "live feed"),
    ("home-omni-search", "search"),
    ("fab-master-trigger", "FAB"),
    ("rail-ad-box-1", "rail ads"),
    ("composer-destinations-bar", "composer destinations"),
):
    chk("46.03 feature marker: " + label, marker in r.text, marker + " missing", "", "")

# --- 2. Web Page archived + Website Settings home_page --------------------
previous_cwd = os.getcwd()
try:
    import frappe

    # frappe.logger() resolves <site>/logs relative to the current working
    # directory; the normal bench runner runs from the sites directory.
    os.chdir("/home/frappe/frappe-bench/sites")
    frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    wp = frappe.get_doc("Web Page", "ethiobiz")
    chk(
        "46.04 Web Page unpublished",
        int(wp.published or 0) == 0,
        "published=%s" % wp.published,
        "Web Page still published and shadows the www route",
        "set published=0 on Web Page ethiobiz",
    )
    chk(
        "46.05 Web Page route archived",
        str(wp.route or "").startswith("ethiobiz_home_v1-webpage-archived"),
        "route=%s" % wp.route,
        "route still collides with the www template",
        "rename route to ethiobiz_home_v1-webpage-archived-2026-11-17",
    )
    settings = frappe.get_single("Website Settings")
    chk(
        "46.06 Website Settings home_page intact",
        (settings.home_page or "") == "ethiobiz_home_v1",
        "home_page=%s" % settings.home_page,
        "home page setting changed",
        "set Website Settings.home_page = ethiobiz_home_v1",
    )
    frappe.destroy()
except Exception as exc:
    chk("46.04 Web Page archived check", False, str(exc)[:200], "frappe init failed", "inspect DB connectivity")
finally:
    try:
        os.chdir(previous_cwd)
    except Exception:
        pass

# --- 3. Home APIs ----------------------------------------------------------
api_checks = {
    "46.07 get_live_ticker_activities": "/api/method/bismillah_ethiobiz.home_api.get_live_ticker_activities?limit=8",
    "46.08 get_feed_filter_structure": "/api/method/bismillah_ethiobiz.home_api.get_feed_filter_structure",
    "46.09 get_floating_action_items": "/api/method/bismillah_ethiobiz.home_api.get_floating_action_items",
    "46.10 get_active_home_ads": "/api/method/bismillah_ethiobiz.home_api.get_active_home_ads?placement=homepage-rail",
}
payloads = {}
for name, path in api_checks.items():
    r = get(path)
    ok = r.status_code == 200
    chk(name, ok, "%s len=%d" % (r.status_code, len(r.text)), "endpoint missing/500", "deploy home_api.py and restart backend")
    if ok:
        try:
            payloads[name] = r.json().get("message")
        except Exception:
            payloads[name] = None

ticker = payloads.get("46.07 get_live_ticker_activities")
chk("46.11 ticker payload shape", isinstance(ticker, list), "expected list, got %r" % type(ticker).__name__, "", "")
if isinstance(ticker, list):
    chk(
        "46.12 ticker row keys",
        all(isinstance(row, dict) and {"text_en", "text_am", "url", "icon", "badge"}.issubset(row) for row in ticker),
        "one or more rows missing keys",
        "ticker mapping incomplete",
        "return text_en/text_am/url/icon/badge for every row",
    )
    chk(
        "46.13 ticker excludes obvious test/demo rows",
        not any(re.search(r"\d{9,}", str(row.get("text_en", ""))) for row in ticker),
        "long numeric test suffix present",
        "test data leaked into public ticker",
        "filter test markers and long numeric suffixes",
    )

filters = payloads.get("46.08 get_feed_filter_structure")
chk("46.14 filter structure is dict", isinstance(filters, dict) and bool(filters), "expected non-empty dict", "", "")
if isinstance(filters, dict):
    sample = next(iter(filters.values()), [])
    chk(
        "46.15 filter option keys",
        isinstance(sample, list) and all({"key", "label", "label_am"}.issubset(row) for row in sample),
        "filter option missing key/label/label_am",
        "filter payload shape wrong",
        "return {key,label,label_am} arrays",
    )

fab = payloads.get("46.09 get_floating_action_items")
chk("46.16 FAB payload is list", isinstance(fab, list), "expected list", "", "")
if isinstance(fab, list):
    chk(
        "46.17 FAB row keys",
        all({"icon", "title", "title_am", "link", "target"}.issubset(row) for row in fab),
        "FAB row missing keys",
        "theme child table mapping incomplete",
        "return icon/title/title_am/link/target",
    )

ads = payloads.get("46.10 get_active_home_ads")
chk("46.18 ads payload is list", isinstance(ads, list), "expected list", "", "")

r = get("/api/method/bismillah_ethiobiz.home_api.track_ad_click?campaign_name=__suite46_missing__")
chk(
    "46.19 track_ad_click safe on missing campaign",
    r.status_code == 200 and r.json().get("message", {}).get("ok") is False,
    "%s %s" % (r.status_code, r.text[:80]),
    "missing guard in track_ad_click",
    "return {'ok': False} for unknown campaign",
)

# --- 4. Legacy /home remains reachable ------------------------------------
r = get("/home")
chk("46.20 legacy /home still reachable", r.status_code == 200, str(r.status_code), "", "")

print("\nSUITE 46 RESULT: PASS=%d FAIL=%d" % (P, F))
sys.exit(0 if F == 0 else 1)
