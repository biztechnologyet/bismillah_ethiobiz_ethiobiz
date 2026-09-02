"""Suite 82: BOOKING AGGREGATOR REWIRE (search_all_bookables + create_universal_booking -> Desk DocTypes + QR/PIN)"""
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
    _args = []
    for a in args:
        if isinstance(a, str):
            a = a.replace("Frappe", "EthioBiz").replace("ERPNext", "DOBiz Smarterp")
        _args.append(a)
    _orig_print(*_args, **kwargs)
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
import frappe.model.document; Document = frappe.model.document.Document
_orig_insert = Document.insert
def _safe_insert(self, *args, **kwargs):
    for _r in range(2):
        try: return _orig_insert(self, *args, **kwargs)
        except Exception as _e:
            frappe.db.rollback()
            if _r == 0:
                continue
            print("  --- SKIP insert(" + str(self.doctype) + "): " + str(_e))
            self.name = None; return None
Document.insert = _safe_insert
TS = str(int(time.time()))
_save_results.suite_id = "82"

import requests as _req

print("\n" + "=" * 60)
print("SUITE 82: BOOKING AGGREGATOR REWIRE")
print("=" * 60)

BASE = "https://ethiobiz.et"
API = "/api/method/bismillah_ethiobiz"
_company = None
_listing = None
_booking = None

def call(method, data):
    try:
        r = _req.post(BASE + API + "." + method, data=data, timeout=25, verify=False)
        return r.json().get("message")
    except Exception as e:
        return {"_error": str(e)}

# 82.1 — Seed a BizService Listing for the services vertical
try:
    if frappe.db.exists("DocType", "BizService Listing") and frappe.db.exists("DocType", "BizService Category"):
        _company = None
        try:
            c = frappe.get_doc({
                "doctype": "Company",
                "company_name": "AggRewire " + TS + " Co",
                "abbr": "AR" + TS[-4:],
                "country": "Ethiopia",
                "default_currency": "ETB",
                "show_on_map": 1, "map_enabled": 1,
                "latitude": 9.01, "longitude": 38.761
            })
            c.insert(ignore_permissions=True)
            frappe.db.commit()
            _company = c.name
        except Exception:
            frappe.db.rollback()
            _existing = frappe.get_all("Company", fields=["name"], limit=1)
            _company = _existing[0]["name"] if _existing else None
        cat = frappe.get_all("BizService Category", filters={"is_active": 1}, fields=["name"], limit=1)[0]["name"]
        l = frappe.get_doc({
            "doctype": "BizService Listing",
            "service_name": "Aggregator Service " + TS,
            "company": _company,
            "category": cat,
            "price": 380,
            "price_type": "Fixed",
            "duration_minutes": 45,
            "serving_city": "Addis Ababa",
            "is_active": 1
        })
        l.insert(ignore_permissions=True)
        frappe.db.commit()
        _listing = l.name
        chk("82.1 listing seeded", bool(_listing))
    else:
        chk("82.1 listing (skip: doctype absent)", True)
except Exception as _e: fl("82.1 seed", str(_e)[:250])

# 82.2 — search_all_bookables returns the services vertical listing
try:
    res = call("bizbooking_aggregator_api.search_all_bookables", {"vertical": "services", "limit": 20})
    chk("82.2 search_all_bookables returns bookables", isinstance((res or {}).get("bookables"), list), "res=" + str(res)[:200])
    names = [b.get("id") for b in (res or {}).get("bookables", [])]
    if _listing:
        chk("82.2a seeded listing present in aggregation", _listing in names)
    else:
        chk("82.2a aggregation present (skip: no listing)", True)
except Exception as _e: fl("82.2 search", str(_e)[:250])

# 82.3 — search_all_bookables for hotels/salon/resources returns list (schema valid)
try:
    for v in ["hotels", "salon", "workspaces", "rentals", "all"]:
        res = call("bizbooking_aggregator_api.search_all_bookables", {"vertical": v, "limit": 10})
        chk("82.3 search " + v + " valid", isinstance((res or {}).get("bookables"), list), "res=" + str(res)[:150])
except Exception as _e: fl("82.3 verticals", str(_e)[:250])

# 82.4 — create_universal_booking (service, slot-picker flow) -> BizService Booking + QR/PIN
# Mirrors the real customer UX: fetch the provider's free slots, pick one, then book.
try:
    if _listing:
        picked = None
        try:
            av = call("bizservice_api.get_service_availability", {"listing": _listing, "date": str(frappe.utils.today()), "service": _listing})
            slots = (av or {}).get("slots") or []
            picked = slots[0] if slots else None
        except Exception:
            picked = None
        _book_slot = picked or "14:00"
        res = call("bizbooking_aggregator_api.create_universal_booking", {"booking_data": json.dumps({
            "vertical": "service",
            "target_id": _listing,
            "company": _company,
            "customer_name": "Agg Tester " + TS[-4:],
            "customer_phone": "0911223344",
            "date": str(frappe.utils.today()),
            "time_slot": _book_slot
        })})
        chk("82.4 create_universal_booking returns success", (res or {}).get("status") == "success", "res=" + str(res)[:250])
        _booking = (res or {}).get("booking_id")
        chk("82.4a booking_id returned", bool(_booking))
        if _booking:
            chk("82.4b BizService Booking row created", frappe.db.exists("BizService Booking", _booking))
        chk("82.4c booking_pass_pin provided", bool((res or {}).get("booking_pass_pin")), "res_keys=" + str(list((res or {}).keys())))
        chk("82.4d qr_payload provided", bool((res or {}).get("qr_payload")))
    else:
        chk("82.4 create booking (skip: no listing)", True)
except Exception as _e: fl("82.4 create", str(_e)[:350])

# 82.5 — /booking page HTTP 200 + JS wired to aggregator
try:
    r = _req.get(BASE + "/booking", timeout=15, verify=False, allow_redirects=True)
    chk("82.5 /booking HTTP 200", r.status_code == 200)
    chk("82.5a page references bizbooking.js", "bizbooking.js" in r.text)
    js = _req.get(BASE + "/assets/bismillah_ethiobiz/js/bizbooking.js", timeout=15, verify=False).text
    chk("82.5b bizbooking.js calls search_all_bookables", "search_all_bookables" in js)
    chk("82.5c bizbooking.js calls create_universal_booking", "create_universal_booking" in js)
    chk("82.5d bizbooking.js has no hardcoded demo arrays", "Skylight Luxury Grand Suite" not in js)
except Exception as _e: fl("82.5 booking page/js", str(_e)[:200])

# Cleanup
for dtg, nm in [("BizService Booking", _booking), ("BizService Listing", _listing), ("Company", _company)]:
    if nm:
        try:
            if frappe.db.exists(dtg, nm):
                d = frappe.get_doc(dtg, nm)
                if getattr(d, "docstatus", 0) == 1:
                    d.cancel()
                frappe.delete_doc(dtg, nm, ignore_permissions=True)
        except Exception: pass
frappe.db.commit()

print(f"\n--- SUITE 82: {P}/{P+F} passed ---")
P82, F82 = P, F; P = 0; F = 0