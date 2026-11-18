"""Suite 86: IMMERSIVE FEED POST PAGE (/post) + SWIPE VIEWER APIS

Covers:
  * every live-feed family renders a full page (server-rendered first slide)
  * native CTA destinations stay untouched (product route, /social?post=,
    /forum?topic=, /jobs?job=, /doctor/<slug>, ...)
  * missing / removed posts degrade gracefully (HTTP 200, not a traceback)
  * English and Amharic server labels
  * post_api.get_post_queue / get_post_slide / get_post_comments
  * homepage feed payload carries post_url + feed_type for every card
"""
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
_save_results.suite_id = "86"

import requests as _req

print("\n" + "=" * 60)
print("SUITE 86: IMMERSIVE /post VIEWER + FEED POST APIS")
print("=" * 60)

BASE = "https://ethiobiz.et"


def page(path, cookies=None):
    r = _req.get(BASE + path, timeout=45, verify=False, allow_redirects=True, cookies=cookies or {})
    return r


def post_url(doctype, name, ft):
    from urllib.parse import quote
    return "/post?doctype=%s&name=%s&ft=%s" % (quote(doctype, safe=""), quote(name, safe=""), quote(ft, safe=""))


# ---------------------------------------------------------------- fixtures
def first(doctype, filters=None, field="name"):
    try:
        rows = frappe.get_all(doctype, filters=filters or {}, pluck=field, limit=1)
        return rows[0] if rows else None
    except Exception:
        return None


CASES = []

def add(label, doctype, name, ft, cta_fragment):
    if name:
        CASES.append({"label": label, "doctype": doctype, "name": name, "ft": ft, "cta": cta_fragment})


add("product", "Item", "ABABA-DATA-001", "products", "/sauce-condiment/ababa-data")
add("job", "Job Opening", "HR-OPN-2026-0002", "jobs", "/jobs?job=")
add("doctor", "Healthcare Practitioner", "DOC-005", "bizhealth", "/doctor/")
add("social", "Afocha Post", "AFO-2026-01144", "social", "/social?post=")
add("forum", "Walta Forum Topic", "TOPIC-1001-CLD", "forum", "/forum?topic=")
add("blog", "Blog Post", first("Blog Post"), "tibeb", "/blog/")
add("course", "LMS Course", first("LMS Course", {"name": ["not like", "test-%"]}) or first("LMS Course"), "dagu", "/lms/courses/")
add("property", "Property", first("Property"), "bizhome", "/bizhome?property=")
add("service", "BizService Listing", first("BizService Listing"), "bizfix", "/bizfix?service=")
add("booking", "BizBooking Resource", first("BizBooking Resource"), "bizhome", "/bizservice?resource=")

# ---------------------------------------------------------------- HTTP pages
for i, case in enumerate(CASES, start=1):
    try:
        r = page(post_url(case["doctype"], case["name"], case["ft"]))
        chk("86.%d.1 %s page HTTP 200" % (i, case["label"]), r.status_code == 200,
            "code=%s" % r.status_code)
        chk("86.%d.2 %s viewer shell" % (i, case["label"]),
            "ebpost-app" in r.text and "ebpost-slide" in r.text and "ebpost-topbar" in r.text)
        chk("86.%d.3 %s no template traceback" % (i, case["label"]),
            "Traceback (most recent call last)" not in r.text and "Error Code: 500" not in r.text)
        chk("86.%d.4 %s CTA destination preserved" % (i, case["label"]),
            case["cta"] in r.text, "expected fragment=%s" % case["cta"])
    except Exception as _e:
        fl("86.%s %s HTTP" % (i, case["label"]), str(_e)[:250])

# ---------------------------------------------------------------- analyze panel
try:
    r = page(post_url("Item", "ABABA-DATA-001", "products"))
    chk("86.29 analyze panel markup", "ebpost-analyze" in r.text and "data-eb-analyze" in r.text)
    chk("86.29b research action present", "Research this post" in r.text)
except Exception as _e:
    fl("86.29 analyze panel", str(_e)[:250])

# ---------------------------------------------------------------- missing post
try:
    r = page(post_url("Item", "NO-SUCH-POST-XYZ", "products"))
    chk("86.30 missing post HTTP 200", r.status_code == 200, "code=%s" % r.status_code)
    chk("86.31 missing post renders graceful state",
        "ebpost-missing" in r.text or "no longer available" in r.text.lower())
    chk("86.32 missing post keeps viewer shell", "ebpost-app" in r.text)
except Exception as _e:
    fl("86.30 missing post", str(_e)[:250])

# ---------------------------------------------------------------- Amharic
try:
    r = page(post_url("Item", "ABABA-DATA-001", "products"), cookies={"preferred_language": "am"})
    chk("86.35 Amharic page HTTP 200", r.status_code == 200, "code=%s" % r.status_code)
    chk("86.36 Amharic labels present", "አስተያየቶች" in r.text or "ሙሉውን ያንብቡ" in r.text)
    chk("86.37 Amharic back label", "ወደ ቀጥታ ፍሰት ተመለስ" in r.text)
    chk("86.38 Amharic analyze labels", "ትንተና" in r.text and "ይህን ፖስት ይመርምሩ" in r.text)
except Exception as _e:
    fl("86.35 Amharic page", str(_e)[:250])

# ---------------------------------------------------------------- direct render (all families)
frappe.local.lang = "en"
try:
    from bismillah_ethiobiz.www.post import load_post, LABELS
    rendered = 0
    for case in CASES:
        try:
            post = load_post(case["doctype"], case["name"], case["ft"])
            html = frappe.render_template(
                "templates/includes/ebpost_slide.html",
                {"post": post, "labels": post.get("labels") or LABELS["en"],
                 "login_url": "/login", "is_logged_in": False},
            )
            if post.get("found") and "ebpost-slide" in html and "ebpost-actionbar" in html:
                rendered += 1
            else:
                fl("86.40 render %s" % case["label"], "found=%s html=%s" % (post.get("found"), len(html)))
        except Exception as _e:
            fl("86.40 render %s" % case["label"], str(_e)[:200])
    chk("86.41 all feed families render the slide partial", rendered == len(CASES),
        "rendered=%s/%s" % (rendered, len(CASES)))
except Exception as _e:
    fl("86.41 direct render", str(_e)[:250])

# ---------------------------------------------------------------- viewer APIs
try:
    from bismillah_ethiobiz import post_api
    q = post_api.get_post_queue(doctype="Item", name="ABABA-DATA-001", ft="products", start=0, limit=8)
    chk("86.45 queue responds", q.get("status") == "success", str(q)[:120])
    items = q.get("items") or []
    chk("86.46 queue starts with current post", bool(items) and items[0].get("name") == "ABABA-DATA-001")
    chk("86.47 queue items carry doctype/name/feed_type/post_url",
        bool(items) and all(x.get("doctype") and x.get("name") and x.get("feed_type") and x.get("post_url") for x in items))
    chk("86.48 queue has_more/total", "has_more" in q and q.get("total", 0) >= len(items))
    s = post_api.get_post_slide(doctype="Item", name="ABABA-DATA-001", ft="products")
    chk("86.49 slide responds", s.get("status") == "success" and "ebpost-slide" in (s.get("html") or ""))
    c = post_api.get_post_comments(doctype="Item", name="ABABA-DATA-001", ft="products")
    chk("86.50 product comments payload", c.get("status") == "success" and c.get("commentable") is True)
    f = post_api.get_post_comments(doctype="Walta Forum Topic", name="TOPIC-1001-CLD", ft="forum")
    chk("86.51 forum comments payload", f.get("status") == "success" and f.get("forum") is True)
    n = post_api.get_post_comments(doctype="News", name="no-such-news", ft="news")
    chk("86.52 news comments payload", n.get("status") == "success" and n.get("commentable") is False)
    p = post_api.get_post_slide(doctype="Property", name=first("Property"), ft="bizhome")
    chk("86.53 property slide (raw-table fallback)", p.get("status") == "success" and "ebpost-slide" in (p.get("html") or ""))
except Exception as _e:
    fl("86.45 viewer APIs", str(_e)[:300])

# ---------------------------------------------------------------- homepage payloads
try:
    from bismillah_ethiobiz import smart_feed_api, home_api
    feed = smart_feed_api.get_personalized_feed(start=0, limit=8)
    feed_items = feed.get("items") or []
    chk("86.55 feed returns cards", len(feed_items) > 0, "items=%s" % len(feed_items))
    chk("86.56 every card has post_url", all(x.get("post_url") for x in feed_items))
    chk("86.57 every card has feed_type", all(x.get("feed_type") for x in feed_items))
    sources = home_api.get_feed_sources()
    chk("86.58 feed sources respond", (sources.get("sources") or sources.get("feed_sources")) is not None)
    chk("86.59 feed styles respond", len(sources.get("styles") or sources.get("feed_styles") or []) >= 8)
    recs = home_api.get_home_recommendations()
    rec_items = recs if isinstance(recs, list) else (recs.get("items") or recs.get("recommendations") or [])
    chk("86.60 recommendations carry post_url", bool(rec_items) and all(x.get("post_url") for x in rec_items))
except Exception as _e:
    fl("86.55 homepage payloads", str(_e)[:300])

frappe.db.rollback()
print(f"\n--- SUITE 86: {P}/{P+F} passed ---")
