"""Suite 84: BIZSERVICE MERGED PAGE (/bizservice) + legacy /book /booking /bizservices -> /bizservice redirects"""
#!/usr/bin/env python3
import os, sys, json, time, traceback, atexit
os.chdir("/home/frappe/frappe-bench/sites")
sys.path.insert(0, "/home/frappe/frappe-bench/sites")
import frappe
frappe.init("ethiobiz.et"); frappe.connect()
frappe.db.sql("SET SESSION innodb_lock_wait_timeout = 120")
frappe.db.sql("SET SESSION lock_wait_timeout = 120")
frappe.set_user("Administrator")
import urllib3; urllib3.disable_warnings()
_orig_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _orig_print(*args, **kwargs)
P = 0; F = 0
TEST_RESULTS = []
def ok(n): global P, TEST_RESULTS; P += 1; TEST_RESULTS.append({"id": n, "status": "PASS", "msg": "", "rc": "", "sol": ""}); print("  PASS " + str(n))
def fl(n, m): global F, TEST_RESULTS; F += 1; TEST_RESULTS.append({"id": n, "status": "FAIL", "msg": str(m), "rc": "", "sol": ""}); print("  FAIL " + str(n) + ": " + str(m))
def chk(n, cond, *args):
    try:
        msg = args[0] if len(args) > 0 else ""
        rc = args[1] if len(args) > 1 else ""
        sol = args[2] if len(args) > 2 else ""
        global P, F, TEST_RESULTS
        if cond:
            P += 1; TEST_RESULTS.append({"id": n, "status": "PASS", "msg": msg, "rc": rc, "sol": sol}); print("  PASS " + str(n))
        else:
            F += 1; TEST_RESULTS.append({"id": n, "status": "FAIL", "msg": msg, "rc": rc, "sol": sol}); print("  FAIL " + str(n) + ": " + msg)
    except Exception as _ce: fl(n, "EXCEPTION: " + str(_ce))
def _save_results():
    try:
        rdir = "/home/frappe/frappe-bench/tests/results"
        os.makedirs(rdir, exist_ok=True)
        sid = getattr(_save_results, "suite_id", "unknown")
        rp = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
        rf = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
        report = {"suite": sid, "passed": rp, "failed": rf, "total": rp + rf, "results": TEST_RESULTS}
        with open(os.path.join(rdir, "suite_{}_report.json".format(sid)), "w") as _f:
            json.dump(report, _f, indent=2)
    except: pass
atexit.register(_save_results)
_save_results.suite_id = "84"

import requests as _req

print("\n" + "=" * 60)
print("SUITE 84: BIZSERVICE MERGED PAGE + REDIRECTS")
print("=" * 60)

BASE = "https://ethiobiz.et"


def get_status(url):
    r = _req.get(BASE + url, timeout=20, verify=False, allow_redirects=False)
    return r.status_code, r.headers.get("Location", ""), r


# ---- Canonical merged page ----
try:
    code, loc, r = get_status("/bizservice")
    chk("84.1 /bizservice HTTP 200", code == 200, "code=" + str(code))
    chk("84.2 /bizservice serves services page", "bizservices-app" in r.text and "bs-modal" in r.text)
    chk("84.3 references bizservices.js", "bizservices.js" in r.text)
    chk("84.4 references bizservices.css", "bizservices.css" in r.text)
    chk("84.5 provider deep-link /bizservice?provider=x still 200",
        get_status("/bizservice?provider=demo")[0] == 200)
    chk("84.6 /bizservice no Hotels & Rooms vertical tab", "Hotel Room" not in r.text and "Hotel & Guesthouse" not in r.text)
except Exception as _e: fl("84 page", str(_e)[:250])

# ---- Legacy routes redirect to /bizservice (301) ----
for path, bid in [("/book", 10), ("/booking", 11), ("/bizservices", 12)]:
    pass
try:
    code, loc, r = get_status("/book")
    chk("84.10 /book 301/302", code in (301, 302), "code=" + str(code))
    chk("84.13 /book -> /bizservice", "/bizservice" in str(loc), "loc=" + str(loc))
except Exception as _e: fl("84 /book", str(_e)[:200])
try:
    code, loc, r = get_status("/booking")
    chk("84.11 /booking 301/302", code in (301, 302), "code=" + str(code))
    chk("84.14 /booking -> /bizservice", "/bizservice" in str(loc), "loc=" + str(loc))
except Exception as _e: fl("84 /booking", str(_e)[:200])
try:
    code, loc, r = get_status("/bizservices")
    chk("84.12 /bizservices 301/302", code in (301, 302), "code=" + str(code))
    chk("84.15 /bizservices -> /bizservice", "/bizservice" in str(loc), "loc=" + str(loc))
except Exception as _e: fl("84 /bizservices", str(_e)[:200])

# ---- /bizhome still serves lodging (hotels stay there) ----
try:
    code, loc, r = get_status("/bizhome")
    chk("84.20 /bizhome HTTP 200 (hotels/lodging live)", code == 200, "code=" + str(code))
except Exception as _e: fl("84 /bizhome", str(_e)[:200])

# ---- Services APIs intact behind the merged page ----
try:
    res = _req.get(BASE + "/api/method/bismillah_ethiobiz.bizservice_api.get_categories",
                   timeout=20, verify=False).json()
    chk("84.21 get_categories responds", res.get("message") is not None)
    res2 = _req.get(BASE + "/api/method/bismillah_ethiobiz.bizbooking_api.search_services",
                    params={"limit": 5}, timeout=20, verify=False).json()
    chk("84.22 search_services responds", res2.get("message") is not None)
except Exception as _e: fl("84 services api", str(_e)[:250])

frappe.db.rollback()
print(f"\n--- SUITE 84: {P}/{P+F} passed ---")
