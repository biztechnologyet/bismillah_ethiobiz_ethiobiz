#!/usr/bin/env python3
"""Suite 47: Sidebar theme regression (v2.5.2 mobile close stacking).

Checks the deployed theme asset, cache-buster versions, mobile drawer rules,
close-button stacking fix, invisible-backdrop guard, and form-sidebar cleanup
markers. Browser-level behavior is covered by the Playwright checks in
BISMA_Plans / ethiobiz_analysis/pw (v250/v251/v252).
"""
import hashlib
import json
import os
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
            {"suite": "47", "passed": rp, "failed": rf, "total": len(TEST_RESULTS), "results": TEST_RESULTS},
            open(os.path.join(rdir, "suite_47_report.json"), "w"),
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
THEME_PATH = APP + "/public/js/ethiobiz_theme.js"
FLAT_PATH = "/home/frappe/frappe-bench/sites/assets_flat/bismillah_ethiobiz/js/ethiobiz_theme.js"
BUILD_MARKER = "2026-11-18-v2.5.5-title-preserve"
VERSION = "2.5.5"

print("\n" + "=" * 60)
print("SUITE 47: SIDEBAR THEME REGRESSION (v" + VERSION + ")")
print("=" * 60)

# --- 1. Deployed asset -----------------------------------------------------
r = S.get(BASE + "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js?v=" + VERSION, timeout=60)
chk("47.01 theme asset returns 200", r.status_code == 200, str(r.status_code), "asset missing", "deploy ethiobiz_theme.js")
asset = r.text if r.status_code == 200 else ""
chk("47.02 theme asset is substantial", len(asset) > 100000, "len=%d" % len(asset), "truncated deploy", "redeploy the full theme source")
chk("47.03 build marker " + BUILD_MARKER, BUILD_MARKER in asset, "marker missing", "stale asset", "bump build marker and redeploy")

# --- 2. Mobile close-button stacking fix ----------------------------------
chk(
    "47.04 open drawer raises .container.page-body to 1001",
    "body.sidebar-mobile-open .container.page-body" in asset and "z-index: 1001 !important" in asset,
    "scoped page-body rule missing",
    "close button still trapped below page actions",
    "add body.sidebar-mobile-open .container.page-body { z-index: 1001 !important; }",
)
chk(
    "47.05 invisible modal backdrop cannot swallow taps",
    ".modal-backdrop.fade:not(.show)" in asset and "pointer-events: none !important" in asset,
    "backdrop guard missing",
    "stale backdrop blocks the close button",
    "hide/disable non-.show modal backdrops",
)
chk(
    "47.06 close button and overlay hooks present",
    'id="ethio-sidebar-close"' in asset or "ethio-sidebar-close" in asset,
    "close button hook missing",
    "",
    "",
)
chk(
    "47.07 mobile drawer geometry",
    "min(86vw, 320px)" in asset and "calc(100dvh - 50px)" in asset,
    "mobile drawer width/height rule missing",
    "drawer geometry regressed",
    "restore min(86vw, 320px) and calc(100dvh - 50px)",
)
chk(
    "47.08 mobile overlay and hamburger exist",
    "ethio-mobile-overlay" in asset and "ethio-mobile-hamburger" in asset,
    "overlay/hamburger hooks missing",
    "",
    "",
)
chk(
    "47.09 desktop rail stays 230px",
    "--sidebar-width: 230px" in asset and "width: 230px" in asset,
    "230px rail missing",
    "desktop layout regressed",
    "restore --sidebar-width: 230px",
)
chk(
    "47.10 ethio-no-sidebar only hides empty sidebars",
    "body.ethio-no-sidebar .layout-side-section" in asset
    and "body.ethio-no-sidebar #ethio-mobile-hamburger" in asset,
    "ethio-no-sidebar rule missing",
    "",
    "",
)
chk(
    "47.11 form-sidebar cleanup markers",
    ".ethio-empty-sidebar-item" in asset
    and "body .layout-side-section .form-sidebar .hide" in asset
    and "body .layout-side-section .form-sidebar .ethio-empty-sidebar-item" in asset,
    "form cleanup selectors missing",
    "empty Follow/page-view/auto-repeat rows can reappear",
    "restore form-sidebar cleanup selectors",
)

# --- 3. Cache-buster versions on disk -------------------------------------
try:
    hooks = open(APP + "/hooks.py").read()
    api = open(APP + "/api.py").read()
    chk(
        "47.12 hooks.py uses theme v" + VERSION,
        hooks.count("ethiobiz_theme.js?v=" + VERSION) == 2,
        "found %d occurrences" % hooks.count("ethiobiz_theme.js?v=" + VERSION),
        "browser may keep an old theme",
        "bump both app_include_js and web_include_js cache-busters",
    )
    chk(
        "47.13 api.py uses theme v" + VERSION,
        ("ethiobiz_theme.js?v=" + VERSION) in api,
        "api.py cache-buster missing",
        "Desk may keep an old theme",
        "bump api.py theme include",
    )
except Exception as exc:
    chk("47.12 hooks.py/api.py readable", False, str(exc)[:200], "", "")

# --- 4. Secondary flat asset matches app asset ----------------------------
try:
    app_hash = hashlib.sha256(open(THEME_PATH, "rb").read()).hexdigest()
    flat_hash = hashlib.sha256(open(FLAT_PATH, "rb").read()).hexdigest()
    chk(
        "47.14 assets_flat copy matches app asset",
        app_hash == flat_hash,
        "hashes differ",
        "nginx may serve a stale copy",
        "copy app public/js/ethiobiz_theme.js to sites/assets_flat",
    )
except Exception as exc:
    chk("47.14 assets_flat copy", False, str(exc)[:200], "", "")

# --- 5. Served asset matches disk -----------------------------------------
try:
    served_hash = hashlib.sha256(asset.encode("utf-8")).hexdigest()
    disk_hash = hashlib.sha256(open(THEME_PATH, "rb").read()).hexdigest()
    chk(
        "47.15 served theme matches app file",
        served_hash == disk_hash,
        "served/disk hashes differ",
        "nginx cache or symlink stale",
        "clear cache and verify the public symlink",
    )
except Exception as exc:
    chk("47.15 served theme matches app file", False, str(exc)[:200], "", "")

print("\nSUITE 47 RESULT: PASS=%d FAIL=%d" % (P, F))
sys.exit(0 if F == 0 else 1)
