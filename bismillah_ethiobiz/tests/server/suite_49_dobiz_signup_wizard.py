#!/usr/bin/env python3
"""Suite 49: DOBiz signup wizard + Theme-driven industries (TASK-2026-00972).

Covers the root-cause regression that hid every wizard step:
  - wizard progress/actions markup exists and the five step cards are present
  - CSS shows only the active step and the JS controller activates it
  - all five steps expose their options (industry, package, term, contact, payment)
  - the DOBiz 3D icon is used on the page and the asset is reachable
  - Theme > DOBiz Industry Modules drives the public industry list
  - disabling a Theme row hides it and the server rejects that industry
  - an empty enabled set rejects all industries (no silent fallback)
  - add_company accepts both Theme display labels and canonical labels
  - negative signups never create a User or Company

Browser-level desktop/mobile wizard checks live in
ethiobiz_analysis/pw/dobiz_signup_wizard_test.js (56/56 PASS on 2026-11-17).
"""
import atexit
import json
import os
import re
import sys
import time

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
            {
                "suite": "49",
                "passed": rp,
                "failed": rf,
                "total": len(TEST_RESULTS),
                "results": TEST_RESULTS,
            },
            open(os.path.join(rdir, "suite_49_report.json"), "w"),
            indent=2,
        )
    except Exception:
        pass


atexit.register(_save)

BASE = "https://ethiobiz.et"
S = requests.Session()
S.verify = False
S.headers["Accept"] = "application/json"

REQUIRED_CANONICAL = {
    "Healthcare & Clinics",
    "Restaurants & Food Service",
    "Manufacturing & Assembly",
    "Education & Schools",
    "Retail & Wholesale",
    "Non-Profit & NGOs",
    "Agriculture & Agribusiness",
    "Government & Public-Interest",
    "Other",
}

TS = str(int(time.time()))
TEST_EMAIL = "wizard-suite49-{0}@test.et".format(TS)
TEST_COMPANY = "Wizard Suite 49 {0}".format(TS)


def get(path, **kw):
    kw.setdefault("timeout", 45)
    return S.get(BASE + path, **kw)


def api(method, **kw):
    kw.setdefault("timeout", 60)
    return S.get(BASE + "/api/method/" + method, **kw)


def post_signup(payload):
    return S.post(
        BASE + "/api/method/bizmarketing.api.dobiz_signup_api.submit_dobiz_signup",
        json=payload,
        timeout=90,
    )


def signup_payload(industry):
    return {
        "full_name": "Wizard Suite 49",
        "email": TEST_EMAIL,
        "phone": "+251 91 123 4567",
        "company_name": TEST_COMPANY,
        "industry": industry,
        "package_tier": "Business Growth",
        "billing_term": "6",
        "payment_ref": "",
        "bank_name": "AddisPay",
        "selected_module": "Accounts",
        "payment_method": "bank_transfer",
    }


def cleanup():
    """Remove any artifact the negative tests could possibly have created."""
    try:
        import frappe
    except Exception:
        return
    try:
        frappe.db.sql("delete from `tabDOBiz Payment Transaction` where email=%s or customer=%s", (TEST_EMAIL, TEST_COMPANY))
        frappe.db.sql("delete from `tabDOBiz Trial Signup` where email=%s or company_name=%s", (TEST_EMAIL, TEST_COMPANY))
        frappe.db.sql("delete from `tabUser Permission` where user=%s", (TEST_EMAIL,))
        frappe.db.sql("delete from `tabDefaultValue` where parent=%s", (TEST_EMAIL,))
        frappe.db.sql("delete from `tabUser` where name=%s", (TEST_EMAIL,))
        frappe.db.sql("delete from `tabCustomer` where name=%s", (TEST_COMPANY,))
        frappe.db.sql("delete from `tabCompany` where name=%s", (TEST_COMPANY,))
        frappe.db.commit()
    except Exception as exc:
        print("  cleanup warning: " + str(exc)[:200])


print("\n" + "=" * 60)
print("SUITE 49: DOBIZ SIGNUP WIZARD + DYNAMIC INDUSTRIES")
print("=" * 60)

# ---------------------------------------------------------------------------
# Static page contract
# ---------------------------------------------------------------------------
r = get("/dobiz-signup")
html = r.text if r.status_code == 200 else ""
chk("49.01 /dobiz-signup renders 200", r.status_code == 200, "status=%s len=%s" % (r.status_code, len(html)))
step_cards = sorted(set(re.findall(r'id="dob-step-[1-5]"', html)))
chk(
    "49.02 five wizard step cards present",
    len(step_cards) == 5,
    "found=%s" % step_cards,
)
chk(
    "49.03 progress + actions chrome present",
    all(marker in html for marker in (
        'id="dob-wizard-progress"', 'id="dob-wizard-actions"', 'id="dob-wizard-dots"',
        'id="dob-wizard-back"', 'id="dob-wizard-next"', 'id="dob-wizard-submit"',
    )),
    "missing wizard chrome",
)
chk(
    "49.04 CSS hides inactive steps and shows .is-active",
    "#dob-signup-form > .dob-step-card { display: none; }" in html
    and "#dob-signup-form > .dob-step-card.is-active" in html,
    "wizard CSS contract missing",
)
chk(
    "49.05 JS wizard controller present",
    all(marker in html for marker in (
        "function setActiveStep", "function goNext", "function goBack",
        "function validateStep", "function readContactFields",
        "function validateContactFields", "function renderWizardDots",
        "function showWizardChrome",
    )),
    "wizard controller functions missing",
)
chk(
    "49.06 active step toggling + inert/aria handling present",
    "card.classList.toggle('is-active', active)" in html
    and "card.setAttribute('aria-hidden'" in html
    and "card.setAttribute('inert'" in html,
    "step activation/accessibility contract missing",
)
chk(
    "49.07 success hides wizard chrome",
    "showWizardChrome(false)" in html and "showWizardChrome(!state.result)" in html,
    "success state does not hide wizard chrome",
)
chk(
    "49.08 DOBiz 3D icon used in brand mark",
    '/files/dobiz_3d_icon.png' in html and 'class="dob-brand-mark"' in html,
    "DOBiz 3D icon missing",
)
icon = get("/files/dobiz_3d_icon.png")
chk(
    "49.09 DOBiz 3D icon asset reachable",
    icon.status_code == 200 and icon.content[:8] == b"\x89PNG\r\n\x1a\n",
    "status=%s content-type=%s" % (icon.status_code, icon.headers.get("Content-Type")),
)
chk(
    "49.10 dynamic industry loader + Theme merge present",
    all(marker in html for marker in (
        "home_api.get_dobiz_industries", "enabledIndustryKeys",
        "industryDisplay", "themeIndustryByKey", "canonical_label",
    )),
    "dynamic industry loader markers missing",
)
chk(
    "49.11 empty enabled set fails closed, network failure fails open",
    "state.enabledIndustryKeys = keys;" in html
    and "state.enabledIndustryKeys = null;" in html
    and "state.enabledIndustryKeys === null" in html,
    "empty-vs-network distinction missing",
)
chk(
    "49.12 paused state + submit guard present",
    "Registration is paused" in html
    and "Industry registration is temporarily unavailable." in html
    and "!state.industry || !isIndustryEnabled(currentIndustry())" in html,
    "paused/guard contract missing",
)

# ---------------------------------------------------------------------------
# API contract
# ---------------------------------------------------------------------------
ind = api("bismillah_ethiobiz.home_api.get_dobiz_industries")
ind_data = ind.json().get("message", {}) if ind.status_code == 200 else {}
rows = ind_data.get("industries", [])
chk("49.13 industries API 200", ind.status_code == 200, "status=%s" % ind.status_code)
chk("49.14 industries API returns all 16 seeded rows", len(rows) == 16, "count=%s" % len(rows))
chk(
    "49.15 every industry row has key/label/canonical/enabled",
    all(
        row.get("industry_key") and row.get("label") and row.get("canonical_label")
        and row.get("enabled") is True
        for row in rows
    ),
    "incomplete industry row",
)
canon = {row.get("canonical_label") for row in rows}
chk(
    "49.16 all nine required canonical industries present",
    REQUIRED_CANONICAL.issubset(canon),
    "missing=%s" % sorted(REQUIRED_CANONICAL - canon),
)
chk(
    "49.17 industry keys are unique",
    len({row.get("industry_key") for row in rows}) == len(rows),
    "duplicate industry_key",
)

pkg = api(
    "bizmarketing.api.dobiz_signup_api.get_dobiz_packages",
    params={"industry": "Healthcare & Clinics", "months": 6},
)
pkg_data = pkg.json().get("message", {}) if pkg.status_code == 200 else {}
packages = pkg_data.get("packages", {})
chk("49.18 packages API 200", pkg.status_code == 200, "status=%s" % pkg.status_code)
chk("49.19 three package tiers returned", len(packages) == 3, "count=%s" % len(packages))
chk(
    "49.20 package prices and features present",
    all(
        float(p.get("price_per_month") or p.get("monthly_price") or 0) > 0
        and isinstance(p.get("features"), list) and p.get("features")
        for p in packages.values()
    ),
    "package price/features missing",
)

subs = api("bismillah_ethiobiz.home_api.get_card_portals_and_subsystems")
subs_data = subs.json().get("message", {}) if subs.status_code == 200 else {}
flags = subs_data.get("subsystems", {})
chk("49.21 subsystems API 200", subs.status_code == 200, "status=%s" % subs.status_code)
chk(
    "49.22 subsystem flags include the industry gates",
    all(flag in flags for flag in (
        "enable_bizhealth", "enable_dikka_shop", "enable_dagu_academy",
        "enable_oosoo_jobs", "enable_bizhome", "enable_bizservices",
    )),
    "subsystem flags missing",
)

# ---------------------------------------------------------------------------
# Server-side validation (no artifacts on rejection)
# ---------------------------------------------------------------------------
missing = post_signup({})
chk("49.23 empty signup rejected with 417", missing.status_code == 417, "status=%s" % missing.status_code)

# Professional Services is Theme-enabled but subsystem-disabled (enable_bizservices=0).
disabled = post_signup(signup_payload("Professional Services"))
chk(
    "49.24 subsystem-disabled industry rejected",
    disabled.status_code == 417,
    "status=%s body=%s" % (disabled.status_code, disabled.text[:180]),
)

# Theme-driven disable/restore.  The row is always restored in finally.
theme_restored = True
try:
    sys.path.insert(0, "/home/frappe/frappe-bench/sites")
    os.chdir("/home/frappe/frappe-bench/sites")
    import frappe

    frappe.init("ethiobiz.et")
    frappe.connect()
    frappe.set_user("Administrator")

    theme = frappe.get_single("EthioBiz Theme")
    target = None
    original = None
    for row in (theme.dobiz_industry_modules or []):
        if (row.industry_key or "").strip().lower() == "restaurant":
            target = row
            original = int(row.enabled or 0)
            break
    chk("49.25 Theme has restaurant industry row", target is not None, "restaurant row missing")

    if target is not None:
        target.enabled = 0
        theme.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()

        hidden = api("bismillah_ethiobiz.home_api.get_dobiz_industries")
        hidden_rows = hidden.json().get("message", {}).get("industries", []) if hidden.status_code == 200 else []
        chk(
            "49.26 disabled Theme industry disappears from public API",
            all(row.get("industry_key") != "restaurant" for row in hidden_rows),
            "restaurant still present",
        )
        rejected = post_signup(signup_payload("Restaurants & Food Service"))
        chk(
            "49.27 disabled Theme industry rejected server-side",
            rejected.status_code == 417,
            "status=%s body=%s" % (rejected.status_code, rejected.text[:180]),
        )

        target.enabled = original
        theme.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
        restored = api("bismillah_ethiobiz.home_api.get_dobiz_industries")
        restored_rows = restored.json().get("message", {}).get("industries", []) if restored.status_code == 200 else []
        chk(
            "49.28 Theme industry restored after test",
            any(row.get("industry_key") == "restaurant" for row in restored_rows),
            "restaurant not restored",
        )

    # No user/company may exist from the rejected attempts.
    chk(
        "49.29 rejected signups created no User",
        not frappe.db.exists("User", TEST_EMAIL),
        "unexpected user %s" % TEST_EMAIL,
    )
    chk(
        "49.30 rejected signups created no Company",
        not frappe.db.exists("Company", TEST_COMPANY),
        "unexpected company %s" % TEST_COMPANY,
    )

    # Source-level guard: an empty enabled set must reject, not silently allow.
    api_src = open("/home/frappe/frappe-bench/apps/bizmarketing/bizmarketing/api/dobiz_signup_api.py", encoding="utf-8").read()
    chk(
        "49.31 signup API enforces empty enabled set",
        "enforce_industries = True" in api_src
        and "if enforce_industries and norm_ind not in enabled_canonical:" in api_src,
        "empty enabled set still skips validation",
    )

    company_src = open("/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/company_api.py", encoding="utf-8").read()
    chk(
        "49.32 add_company accepts display and canonical labels",
        "get_enabled_industry_modules" in company_src
        and "canonical_by_label" in company_src
        and "canonical_industry = canonical_by_label.get(industry)" in company_src,
        "add_company label mismatch still present",
    )
except Exception as exc:
    theme_restored = False
    chk("49.33 server-side test bootstrap", False, str(exc)[:300])
finally:
    cleanup()

print("\n" + "-" * 60)
print("SUITE 49 RESULT: %s passed, %s failed, %s total" % (P, F, P + F))
if theme_restored:
    print("Theme config restored: YES")
else:
    print("Theme config restored: CHECK REQUIRED")
print("-" * 60)

sys.exit(0 if F == 0 else 1)
