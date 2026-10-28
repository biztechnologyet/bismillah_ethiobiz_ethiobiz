"""Suite 98: HOME FEED ENGAGEMENT layer — read-full-story bodies, likes, threaded comments.

Covers the whole 2026-10-05 engagement feature set, in four groups:

  A. Deployment integrity   - deployed bytes == committed bytes, LF-only, no backslash
                              artefacts, modules resolve to the canonical (not nested) path.
  B. Feed contract          - real article bodies, engagement fields on every item across
                              every vertical filter, search narrowing, image shown only when
                              a real image exists, forum items read-only, guest vs viewer.
  C. Engagement read path   - the five HTTP endpoints as a guest, the allowlist as a
                              security boundary, bulk cap/de-duplication/no-leak, and the
                              dot-form URL contract.
  D. Engagement write path  - like/unlike, comment post/read/delete, stored-XSS inertness,
                              length cap, ownership, pagination. Runs in-process so the
                              Frappe rate limiter (which needs frappe.request) is bypassed.

Every test that writes removes exactly what it created and restores native counters, so a
run leaves no residue. See ETHIOBIZ_EXPERT_SYSTEM/45_FEED_ENGAGEMENT_AND_READ_FULL_STORY.md.

Run:
  docker exec bismallah_ethiobiz_inshaallah-backend-1 bash -c \
    'cd /home/frappe/frappe-bench/tests && ./env/bin/python run_all_suites.py --suite 98'
"""
#!/usr/bin/env python3
import os
import sys
import json
import time
import atexit
import hashlib
import subprocess

os.chdir("/home/frappe/frappe-bench/sites")
sys.path.insert(0, "/home/frappe/frappe-bench/sites")

import frappe

frappe.init("ethiobiz.et")
frappe.connect()
frappe.db.sql("SET SESSION innodb_lock_wait_timeout = 120")
frappe.db.sql("SET SESSION lock_wait_timeout = 120")
frappe.set_user("Administrator")

import requests as _req
import urllib3

urllib3.disable_warnings()

APP = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz"
CANON = os.path.join(APP, "bismillah_ethiobiz")
NESTED = os.path.join(CANON, "bismillah_ethiobiz")
BASE = "https://ethiobiz.et"
API = "/api/method/bismillah_ethiobiz"
MARK = "suite98-%d" % int(time.time())

# Canonical path the live container must import. The nested duplicate is inert.
ENGAGEMENT_FIELDS = ("likes_count", "comments_count", "viewer_has_liked", "commentable")

P = 0
F = 0
S = 0
TEST_RESULTS = []


def _record(sid, status, msg):
    global P, F, S
    if status == "PASS":
        P += 1
    elif status == "FAIL":
        F += 1
    else:
        S += 1
    TEST_RESULTS.append({"id": sid, "status": status, "msg": str(msg)[:400]})
    print("  %-4s %s%s" % (status, sid, ("" if status == "PASS" else ": " + str(msg)[:300])))


def chk(sid, cond, msg=""):
    _record(sid, "PASS" if cond else "FAIL", msg if not cond else "ok")


def skip(sid, why):
    _record(sid, "SKIP", why)


def fl(sid, msg):
    _record(sid, "FAIL", msg)


def _save_results():
    try:
        os.makedirs("/home/frappe/frappe-bench/tests/results", exist_ok=True)
        with open("/home/frappe/frappe-bench/tests/results/suite_98_report.json", "w") as fh:
            json.dump(
                {
                    "suite": "98",
                    "name": "feed_engagement",
                    "passed": P,
                    "failed": F,
                    "skipped": S,
                    "total": P + F + S,
                    "results": TEST_RESULTS,
                },
                fh,
                indent=2,
            )
    except Exception:
        pass


atexit.register(_save_results)


def head(t):
    print("\n" + "=" * 66)
    print(t)
    print("=" * 66)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def http_get(method, params):
    """Guest GET. Returns (status_code, unwrapped_body)."""
    url = BASE + API + "." + method
    r = _req.get(url, params=params, timeout=30, verify=False)
    try:
        body = r.json()
    except Exception:
        body = {}
    # Frappe wraps whitelisted returns in {"message": ...}.
    return r.status_code, (body.get("message") if isinstance(body, dict) and "message" in body else body)


def http_post(method, data):
    url = BASE + API + "." + method
    r = _req.post(url, data=data, timeout=30, verify=False)
    try:
        body = r.json()
    except Exception:
        body = {}
    return r.status_code, body


def clear_ratelimit_cache():
    """Repeat runs inside the 300s window would otherwise 429 on the guest-write checks."""
    try:
        cache = frappe.cache()
        for pat in ("*rl:*add_comment*", "*rl:*toggle_like*"):
            try:
                cache.delete_keys(pat)
            except Exception:
                pass
    except Exception:
        pass


# ---------------------------------------------------------------------------
# A. deployment integrity
# ---------------------------------------------------------------------------
def group_a():
    head("A. DEPLOYMENT INTEGRITY")
    from bismillah_ethiobiz import smart_feed_api, feed_engagement_api

    for name, mod in (("smart_feed_api.py", smart_feed_api), ("feed_engagement_api.py", feed_engagement_api)):
        path = os.path.join(CANON, name)
        chk("A1.%s exists" % name, os.path.isfile(path), path)
        # Resolved module must be the canonical file, not the nested duplicate.
        chk(
            "A2.%s imports from canonical path" % name,
            os.path.realpath(mod.__file__) == os.path.realpath(path),
            "resolved %s" % mod.__file__,
        )
        raw = open(path, "rb").read()
        chk("A3.%s is pure LF (no CRLF)" % name, b"\r\n" not in raw, "contains CRLF")
        chk("A4.%s has no lone CR" % name, b"\r" not in raw, "contains CR")
        chk("A5.%s non-empty" % name, len(raw) > 1000, "%d bytes" % len(raw))
        print("       sha256 %s = %s" % (name, sha256(path)))

    # The committed blob must equal the deployed bytes, or git and production disagree.
    try:
        for rel in ("bismillah_ethiobiz/smart_feed_api.py", "bismillah_ethiobiz/feed_engagement_api.py"):
            live = sha256(os.path.join(CANON, os.path.basename(rel)))
            committed = subprocess.run(
                ["git", "show", "HEAD:" + rel],
                cwd=APP,
                capture_output=True,
            ).stdout
            chk(
                "A6.%s deployed == committed" % os.path.basename(rel),
                committed and hashlib.sha256(committed).hexdigest() == live,
                "deployed %s vs committed %s"
                % (live[:16], hashlib.sha256(committed).hexdigest()[:16] if committed else "none"),
            )
    except Exception as exc:
        skip("A6 git parity", str(exc)[:120])

    # No literal-backslash filenames (the os.path.join Windows trap).
    junk = []
    for root, _dirs, files in os.walk(APP):
        for fn in files:
            if "\\" in fn:
                junk.append(os.path.join(root, fn))
        if len(junk) > 5:
            break
    chk("A7 no literal-backslash filenames", not junk, junk[:4])

    # The nested duplicate must never be the thing that gets edited by mistake.
    nested_smart = os.path.join(NESTED, "smart_feed_api.py")
    if os.path.isfile(nested_smart):
        print("       NOTE nested duplicate present and inert: %s" % nested_smart)
        chk(
            "A8 nested duplicate is stale, not the live copy",
            sha256(nested_smart) != sha256(os.path.join(CANON, "smart_feed_api.py")),
            "nested copy is identical to canonical - it will drift",
        )


# ---------------------------------------------------------------------------
# B. feed contract
# ---------------------------------------------------------------------------
VERTICALS = [
    ("all", 98),
    ("products", None),
    ("goods", None),
    ("shop", None),
    ("jobs", None),
    ("careers", None),
    ("health", None),
    ("doctors", None),
    ("clinics", None),
    ("bizhealth", None),
    ("fix", None),
    ("bizfix", None),
    ("maintenance", None),
    ("repair", None),
    ("services", None),
    ("bizservices", None),
    ("home", None),
    ("bizhome", None),
    ("property", None),
    ("social", None),
    ("afocha", None),
    ("blogs", None),
    ("tibeb", None),
    ("articles", None),
    ("courses", None),
    ("dagu", None),
    ("academy", None),
    ("forums", None),
    ("walta", None),
    ("discussions", None),
]


def group_b():
    head("B. FEED CONTRACT")
    from bismillah_ethiobiz import smart_feed_api as s

    base = s.get_personalized_feed(filter_type="all", limit=12)
    items = base.get("items") or []
    chk("B1 all returns a total and items", base.get("total", 0) > 0 and len(items) > 0, "total=%s" % base.get("total"))

    missing = {}
    for it in items:
        for f in ENGAGEMENT_FIELDS:
            if f not in it:
                missing.setdefault(f, it.get("id"))
    chk("B2 every item carries all engagement fields", not missing, missing)

    # Read Full Story needs a real body to expand.
    withbody = [it for it in items if (it.get("content") or "").strip()]
    chk("B3 items carry real article bodies", len(withbody) == len(items), "%d/%d non-empty" % (len(withbody), len(items)))

    # Image shown only when a real image is attached.
    placeholders = set(getattr(s, "_FEED_IMAGE_PLACEHOLDERS", ()) or ())
    bad = []
    for it in items:
        img = it.get("image")
        if img is None:
            continue
        if not isinstance(img, str) or not img.strip():
            bad.append((it.get("id"), repr(img)))
            continue
        low = img.lower()
        if any(tok in low for tok in placeholders):
            bad.append((it.get("id"), img[:40]))
    chk("B4 no placeholder artwork shown", not bad, bad[:3])

    # Forum rows are read-only: native counters, no comment UI.
    forum = [it for it in items if it.get("type") == "forum"]
    if forum:
        chk(
            "B5 forum items are not commentable",
            all(not it.get("commentable") for it in forum),
            [it.get("id") for it in forum if it.get("commentable")][:3],
        )
    else:
        skip("B5 forum commentable", "no forum rows on first page")

    # Every vertical filter must serve items with engagement fields.
    empty, fieldless = [], []
    for name, _expected in VERTICALS:
        r = s.get_personalized_feed(filter_type=name, limit=5)
        its = r.get("items") or []
        if not its:
            empty.append((name, r.get("total")))
        for it in its:
            for f in ENGAGEMENT_FIELDS:
                if f not in it:
                    fieldless.append((name, it.get("id"), f))
    chk("B6 all %d vertical filters return items" % len(VERTICALS), not empty, empty[:6])
    chk("B7 engagement fields present in every vertical", not fieldless, fieldless[:6])

    # Search must actually narrow.
    narrowed = []
    for name in ("all", "services", "forums", "blogs"):
        full = s.get_personalized_feed(filter_type=name, limit=5).get("total", 0)
        srch = s.get_personalized_feed(filter_type=name, limit=5, search="a").get("total", 0)
        if not (srch <= full):
            narrowed.append((name, srch, full))
    chk("B8 search narrows results", not narrowed, narrowed)

    # Viewer state: guest must never see viewer_has_liked True.
    frappe.set_user("Guest")
    try:
        r = s.get_personalized_feed(filter_type="all", limit=12)
        leaked = [it.get("id") for it in (r.get("items") or []) if it.get("viewer_has_liked")]
        chk("B9 guest never sees viewer_has_liked", not leaked, leaked[:5])
    finally:
        frappe.set_user("Administrator")


# ---------------------------------------------------------------------------
# C. engagement read path over HTTP, as a guest
# ---------------------------------------------------------------------------
def find_clean_target():
    """An allowlisted doc with zero likes and zero comments, so cleanup is a no-op.

    Prefers a non-Afocha doc because _sync_native_counters only writes Afocha columns.
    """
    from bismillah_ethiobiz import smart_feed_api as s
    from bismillah_ethiobiz import feed_engagement_api as fea

    cands, afocha, seen = [], [], set()
    for name, _ in VERTICALS:
        for it in (s.get_personalized_feed(filter_type=name, limit=12).get("items") or []):
            dt, dn = it.get("doctype"), it.get("docname")
            if not dt or not dn or dt not in fea.FEED_COMMENTABLE_DOCTYPES:
                continue
            if (dt, dn) in seen:
                continue
            seen.add((dt, dn))
            if not frappe.db.exists(dt, dn):
                continue
            counts = fea._counts(dt, dn)
            if counts["likes"] or counts["comments"]:
                continue
            (afocha if dt == "Afocha Post" else cands).append((dt, dn))
    if cands:
        return cands[0]
    if afocha:
        return afocha[0]
    return None


def group_c(target):
    head("C. ENGAGEMENT READ PATH (HTTP, guest)")
    clear_ratelimit_cache()

    if not target:
        skip("C* engagement HTTP", "no allowlisted document available to address")
        return
    dt, dn = target
    print("       target: %s %s" % (dt, dn))

    code, body = http_get("feed_engagement_api.get_comments", {"doctype": dt, "name": dn})
    chk("C1 get_comments 200 for allowlisted target", code == 200, "got %s" % code)
    chk("C2 get_comments unwraps to status=success", isinstance(body, dict) and body.get("status") == "success", body)
    chk(
        "C3 get_comments reports is_logged_in False for guest",
        isinstance(body, dict) and body.get("is_logged_in") is False,
        body.get("is_logged_in") if isinstance(body, dict) else body,
    )

    code, _ = http_get("feed_engagement_api.get_comments", {"doctype": dt})
    chk("C4 missing name rejected 417", code == 417, "got %s" % code)

    code, _ = http_get("feed_engagement_api.get_comments", {"doctype": "Payroll Entry", "name": "PE-00001"})
    chk("C5 private DocType refused 417", code == 417, "got %s" % code)

    code, _ = http_get("feed_engagement_api.get_comments", {"doctype": "User", "name": "Administrator"})
    chk("C6 User doctype refused 417", code == 417, "got %s" % code)

    code, _ = http_get("feed_engagement_api.get_comments", {"doctype": dt, "name": "no-such-doc-xyz"})
    chk("C7 nonexistent document rejected", code in (404, 417), "got %s" % code)

    # Guest writes must be refused.
    code, _ = http_post("feed_engagement_api.add_comment", {"doctype": dt, "name": dn, "content": "guest probe"})
    chk("C8 guest add_comment refused 403", code == 403, "got %s" % code)
    code, _ = http_post("feed_engagement_api.toggle_like", {"doctype": dt, "name": dn})
    chk("C9 guest toggle_like refused 403", code == 403, "got %s" % code)

    # Bulk: allowlist, de-duplication, ceiling, and no private leakage.
    code, body = http_get(
        "feed_engagement_api.bulk_engagement",
        {
            "items": json.dumps(
                [
                    {"doctype": dt, "docname": dn},
                    {"doctype": dt, "docname": dn},
                    {"doctype": "Payroll Entry", "docname": "PE-00001"},
                    {"doctype": "User", "docname": "Administrator"},
                ]
            )
        },
    )
    counts = (body or {}).get("counts") or {}
    chk("C10 bulk_engagement 200", code == 200, "got %s" % code)
    chk("C11 bulk returns exactly one de-duplicated key", len(counts) == 1, list(counts)[:4])
    chk("C12 bulk leaks no private DocType", not [k for k in counts if k.startswith(("Payroll Entry|", "User|"))], list(counts)[:4])
    chk("C13 bulk key format doctype|docname", list(counts) == ["%s|%s" % (dt, dn)], list(counts))

    many = [{"doctype": dt, "docname": "%s-probe-%d" % (MARK, i)} for i in range(120)]
    # POST, not GET: 120 serialised targets overflows practical URL length limits.
    _code, raw = http_post("feed_engagement_api.bulk_engagement", {"items": json.dumps(many)})
    body = raw.get("message") if isinstance(raw, dict) and "message" in raw else raw
    capped = (body or {}).get("counts") or {}
    chk("C14 bulk honours the 60-target ceiling", len(capped) <= 60, "returned %d" % len(capped))

    code, body = http_get("feed_engagement_api.bulk_engagement", {})
    chk("C15 bulk with no items returns empty counts", code == 200 and (body or {}).get("counts") == {}, body)

    # Dot form is the contract; the path form must stay rejected so nobody "fixes" it.
    r = _req.get(BASE + "/api/method/bismillah_ethiobiz/smart_feed_api/get_personalized_feed?limit=1", timeout=30, verify=False)
    chk("C16 path-form URL still rejected 417", r.status_code == 417, "got %s" % r.status_code)

    # Feed over HTTP must serve the engagement fields.
    code, body = http_get("smart_feed_api.get_personalized_feed", {"filter_type": "all", "limit": 5})
    http_items = (body or {}).get("items") or []
    miss = [f for it in http_items for f in ENGAGEMENT_FIELDS if f not in it]
    chk("C17 HTTP feed unwraps and serves engagement fields", code == 200 and http_items and not miss, "missing %s" % miss[:4])


# ---------------------------------------------------------------------------
# D. engagement write path, in-process (rate limiter bypassed), self-cleaning
# ---------------------------------------------------------------------------
CREATED = []


def cleanup():
    """Remove every Comment this suite created and restore native counters."""
    if not CREATED:
        return
    try:
        from bismillah_ethiobiz import feed_engagement_api as fea

        for cid, (dt, dn) in list(CREATED):
            try:
                if frappe.db.exists("Comment", cid):
                    frappe.delete_doc("Comment", cid, force=True, ignore_permissions=True)
            except Exception:
                pass
            try:
                fea._sync_native_counters(dt, dn)
            except Exception:
                pass
        frappe.db.commit()
        print("       cleanup removed %d comment row(s)" % len(CREATED))
    except Exception as exc:
        print("       cleanup error: %s" % exc)
    finally:
        del CREATED[:]


atexit.register(cleanup)


def group_d(target):
    head("D. ENGAGEMENT WRITE PATH (in-process, Administrator)")
    from bismillah_ethiobiz import feed_engagement_api as fea

    if not target:
        skip("D* engagement writes", "no clean allowlisted target available")
        return
    dt, dn = target
    print("       target: %s %s" % (dt, dn))
    frappe.set_user("Administrator")

    base = fea._counts(dt, dn)
    chk("D0 target starts with no engagement", base == {"likes": 0, "comments": 0}, base)

    # Rows of other comment_types (Attachment, Info, ...) are editorial data this
    # feature does not own. Record them so we can prove we did not touch them.
    others_before = frappe.db.count(
        "Comment",
        {"reference_doctype": dt, "reference_name": dn, "comment_type": ("not in", ("Comment", "Like"))},
    )
    print("       pre-existing non-engagement rows on target: %d" % others_before)

    try:
        # --- like / unlike -------------------------------------------------
        r = fea.toggle_like(doctype=dt, name=dn)
        CREATED.append((r and _last_like(dt, dn), (dt, dn)))
        chk("D1 like reports liked=True", r.get("liked") is True, r)
        chk("D2 like count becomes 1", r.get("likes_count") == 1, r)
        chk("D3 viewer_has_liked True for the actor", r.get("viewer_has_liked") is True, r)

        r2 = fea.toggle_like(doctype=dt, name=dn)
        chk("D4 second toggle un-likes", r2.get("liked") is False, r2)
        chk("D5 like count returns to 0", r2.get("likes_count") == 0, r2)

        # --- comment round trip -------------------------------------------
        text = "hello from %s" % MARK
        rc = fea.add_comment(doctype=dt, name=dn, content=text)
        cid = (rc or {}).get("comment", {}).get("id")
        CREATED.append((cid, (dt, dn)))
        chk("D6 add_comment succeeds", bool(cid), rc)
        chk("D7 comments_count becomes 1", rc.get("comments_count") == 1, rc)
        chk("D8 returned content matches", rc.get("comment", {}).get("content") == text, rc.get("comment"))

        g = fea.get_comments(doctype=dt, name=dn)
        found = [c for c in g.get("comments", []) if c.get("id") == cid]
        chk("D9 comment appears in the thread", len(found) == 1, "total=%s" % g.get("total"))
        chk("D10 author flagged as owner", bool(found and found[0].get("is_owner")), found[:1])
        chk("D11 author display resolved", bool(found and found[0].get("author")), found[:1])
        chk("D12 thread total is 1", g.get("total") == 1, g.get("total"))

        # --- stored XSS must be inert -------------------------------------
        xss = fea.add_comment(doctype=dt, name=dn, content="<script>alert(1)</script><img src=x onerror=alert(2)>")
        xid = (xss or {}).get("comment", {}).get("id")
        CREATED.append((xid, (dt, dn)))
        stored = (xss or {}).get("comment", {}).get("content") or ""
        chk("D13 XSS payload stored without <script", "<script" not in stored.lower(), stored[:80])
        chk("D14 XSS payload stored without onerror", "onerror" not in stored.lower(), stored[:80])
        chk("D15 XSS payload is plain text", "alert(1)" in stored, stored[:80])

        # --- length cap and empty body ------------------------------------
        try:
            fea.add_comment(doctype=dt, name=dn, content="x" * (fea.MAX_COMMENT_LENGTH + 50))
            fl("D16 over-length comment rejected", "no exception raised")
        except Exception as exc:
            chk("D16 over-length comment rejected", True, "")
            chk("D17 rejection is a ValidationError", "ValidationError" in type(exc).__name__, type(exc).__name__)

        try:
            fea.add_comment(doctype=dt, name=dn, content="   ")
            fl("D18 empty comment rejected", "no exception raised")
        except Exception as exc:
            chk("D18 empty comment rejected", "ValidationError" in type(exc).__name__, type(exc).__name__)

        # --- pagination ----------------------------------------------------
        page = fea.get_comments(doctype=dt, name=dn, limit=1)
        chk("D19 limit is honoured", len(page.get("comments", [])) == 1, len(page.get("comments", [])))
        chk("D20 has_more True when truncated", page.get("has_more") is True, page.get("has_more"))

        page2 = fea.get_comments(doctype=dt, name=dn, limit=1, offset=1)
        chk("D21 offset advances the page", bool(page2.get("comments")), page2.get("total"))

        # --- deletion ------------------------------------------------------
        dr = fea.delete_comment(comment=cid)
        chk("D22 author can delete own comment", (dr or {}).get("status") == "success", dr)
        chk("D23 comments_count back to 1 (XSS row remains)", dr.get("comments_count") == 1, dr)
        if cid in [c[0] for c in CREATED]:
            CREATED.remove((cid, (dt, dn)))

        try:
            fea.delete_comment(comment="no-such-comment-xyz")
            fl("D24 deleting a missing comment raises", "no exception")
        except Exception as exc:
            chk("D24 deleting a missing comment raises", True, "")

    finally:
        cleanup()

    # --- after cleanup the target must be exactly as we found it ----------
    after = fea._counts(dt, dn)
    chk("D25 target restored to zero engagement", after == {"likes": 0, "comments": 0}, after)

    # Only the engagement comment_types are ours. Attachment/Info rows are
    # editorial data and must survive untouched (see trap 7 in guide 45).
    residue = frappe.db.count(
        "Comment",
        {"reference_doctype": dt, "reference_name": dn, "comment_type": ("in", ("Comment", "Like"))},
    )
    chk("D26 no engagement Comment residue left on target", residue == 0, "residue=%s" % residue)

    others_after = frappe.db.count(
        "Comment",
        {"reference_doctype": dt, "reference_name": dn, "comment_type": ("not in", ("Comment", "Like"))},
    )
    chk(
        "D27 pre-existing non-engagement rows untouched",
        others_after == others_before,
        "before=%s after=%s" % (others_before, others_after),
    )


def _last_like(dt, dn):
    rows = frappe.get_all(
        "Comment",
        filters={"comment_type": "Like", "reference_doctype": dt, "reference_name": dn},
        fields=["name"],
        limit=1,
    )
    return rows[0].name if rows else None


# ---------------------------------------------------------------------------
def main():
    print("\n" + "=" * 66)
    print("SUITE 98: HOME FEED ENGAGEMENT (bodies, likes, threaded comments)")
    print("marker: %s" % MARK)
    print("=" * 66)

    target = None
    try:
        group_a()
        group_b()
        try:
            target = find_clean_target()
        except Exception as exc:
            fl("target discovery", exc)
        group_c(target)
        group_d(target)
    except Exception as exc:
        import traceback

        fl("suite aborted", traceback.format_exc()[-500:])
    finally:
        cleanup()
        frappe.db.rollback()

    print("\n" + "=" * 66)
    print("SUITE 98 RESULT: %d passed, %d failed, %d skipped" % (P, F, S))
    print("=" * 66)
    return 0 if F == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
