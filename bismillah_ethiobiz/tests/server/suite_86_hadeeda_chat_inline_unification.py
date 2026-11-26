"""Suite 86: Hadeeda chat/inline unification, guest routing, and Desk/UI contract checks."""
#!/usr/bin/env python3
import os, sys, json, atexit
os.chdir("/home/frappe/frappe-bench/sites")
sys.path.insert(0, "/home/frappe/frappe-bench/sites")
import frappe
frappe.init("ethiobiz.et"); frappe.connect()
frappe.db.sql("SET SESSION innodb_lock_wait_timeout = 120")
frappe.db.sql("SET SESSION lock_wait_timeout = 120")
frappe.set_user("Administrator")
import urllib3; urllib3.disable_warnings()
import requests as _req

_orig_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _orig_print(*args, **kwargs)

P = 0; F = 0
TEST_RESULTS = []

def _save_results():
    try:
        rdir = "/home/frappe/frappe-bench/tests/results"
        os.makedirs(rdir, exist_ok=True)
        sid = getattr(_save_results, "suite_id", "86")
        rp = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
        rf = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
        with open(os.path.join(rdir, "suite_{}_report.json".format(sid)), "w") as _f:
            json.dump({"suite": sid, "passed": rp, "failed": rf, "total": rp+rf, "results": TEST_RESULTS}, _f, indent=2)
    except Exception:
        pass
atexit.register(_save_results)
_save_results.suite_id = "86"

def chk(n, cond, msg=""):
    global P, F, TEST_RESULTS
    try:
        if cond:
            P += 1; TEST_RESULTS.append({"id": n, "status": "PASS", "msg": msg}); print("  PASS " + str(n))
        else:
            F += 1; TEST_RESULTS.append({"id": n, "status": "FAIL", "msg": msg}); print("  FAIL " + str(n) + ": " + str(msg))
    except Exception as e:
        F += 1; TEST_RESULTS.append({"id": n, "status": "FAIL", "msg": "EXC: " + str(e)}); print("  FAIL " + str(n) + ": EXC " + str(e))

BASE = "https://ethiobiz.et"

print("\n" + "="*60)
print("SUITE 86: HADEEDA CHAT/INLINE UNIFICATION")
print("="*60)

# 1. get_chat_config guest contract
try:
    frappe.set_user("Guest")
    from bismillah_ethiobiz.api import get_chat_config
    c = get_chat_config()
    chk("86.1 guest is_guest", c.get("is_guest") is True)
    chk("86.2 guest has guest webhook", bool(c.get("webhook_url")))
    for k in ["chat_floating_button_label","chat_floating_button_icon","inline_widget_title","inline_widget_icon","inline_badge_text","bot_avatar"]:
        chk("86.3 guest has "+k, k in c, "missing "+k)
    chk("86.4 guest no api_key", not c.get("api_key"))
    chk("86.5 guest no api_secret", not c.get("api_secret"))
except Exception as e:
    chk("86.1-5 guest config", False, str(e))
finally:
    frappe.set_user("Administrator")

# 2. get_chat_config logged-in has new fields
try:
    frappe.set_user("Administrator")
    from bismillah_ethiobiz.api import get_chat_config
    c = get_chat_config()
    chk("86.6 admin is_guest false", c.get("is_guest") is False)
    for k in ["chat_floating_button_label","inline_widget_title","inline_badge_text"]:
        chk("86.7 admin has "+k, k in c, "missing "+k)
except Exception as e:
    chk("86.6-7 admin config", False, str(e))
finally:
    frappe.set_user("Administrator")

# 3. chat_inline guest routing / sanitization
try:
    import inspect, bismillah_ethiobiz.api as api_mod
    src = inspect.getsource(api_mod.chat_inline)
    chk("86.8 chat_inline allow_guest", "allow_guest=True" in src)
    chk("86.9 chat_inline uses guest webhook", "chat_webhook_url_guest" in src)
    chk("86.10 chat_inline sanitizes guest secrets", 'api_key, api_secret = "", ""' in src or 'api_key": api_key or ""' in src)
    chk("86.11 chat_inline no private guest doc content", "document_content = \"\"" in src)
except Exception as e:
    chk("86.8-11 chat_inline source", False, str(e))

# 4. settings doctype has guest webhook field
try:
    p = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/ethiobiz_theme/doctype/hadeeda_settings/hadeeda_settings.json"
    d = json.load(open(p))
    fields = {f.get("fieldname") for f in d.get("fields", [])}
    chk("86.12 settings has chat_webhook_url_guest", "chat_webhook_url_guest" in fields)
    chk("86.13 settings has chat_floating_button_label", "chat_floating_button_label" in fields)
    chk("86.14 settings has inline_widget_title", "inline_widget_title" in fields)
except Exception as e:
    chk("86.12-14 settings", False, str(e))

# 5. deployed assets contain key strings
try:
    checks = [
        ("86.15 chat js no 850 max", "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.6.1", "850", False),
        ("86.16 chat js full width", "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.6.0", "window.innerWidth - 16", True),
        ("86.17 inline js select-all", "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.7.0", "select-all", True),
        ("86.18 inline js getPageContext", "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.7.0", "getPageContext", True),
        ("86.19 thread js markdown", "/assets/bismillah_ethiobiz/js/hadeeda_inline_thread.js?v=1.2.2", "renderMarkdown", True),
        ("86.20 thread js insert at cursor", "/assets/bismillah_ethiobiz/js/hadeeda_inline_thread.js?v=1.2.2", "Insert at cursor", True),
    ]
    for nid, path, needle, should_exist in checks:
        r = _req.get(BASE + path, timeout=20, verify=False)
        has = needle in r.text
        chk(nid, has if should_exist else (not has), "status={} has={}".format(r.status_code, has))
except Exception as e:
    chk("86.15-20 assets", False, str(e))

frappe.db.rollback()
print(f"\n--- SUITE 86: {P}/{P+F} passed ---")
if F:
    sys.exit(1)
