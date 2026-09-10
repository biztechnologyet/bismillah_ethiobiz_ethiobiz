"""Bismillah — ANFRG-26-00063 Phase 1 SERVER-SIDE integration suite.

Runs INSIDE the backend container against the live site:

    docker exec -u frappe -w /home/frappe/frappe-bench/apps/bizmarketing \
        bismallah_ethiobiz_inshaallah-backend-1 \
        bench --site ethiobiz.et execute bizmarketing.anfrg_phase1_server_tests.run

Self-contained, idempotent, cleans up every record it creates.
"""
import json
import traceback

import frappe
from frappe.utils import now_datetime

RESULTS = []


def _record(name, ok, detail=""):
    RESULTS.append({"test": name, "ok": bool(ok), "detail": str(detail)[:300]})
    print(f"{'PASS' if ok else 'FAIL'} | {name} | {str(detail)[:160]}")


def _cleanup(names):
    for dt, n in names:
        try:
            if n and frappe.db.exists(dt, n):
                frappe.delete_doc(dt, n, force=True, ignore_permissions=True)
        except Exception:
            pass


def _ensure_customer(company):
    if not frappe.db.exists("Customer", company):
        cust_group = frappe.db.get_single_value("Selling Settings", "customer_group") or \
            "All Customer Groups"
        territory = frappe.db.get_single_value("Selling Settings", "territory") or \
            "All Territories"
        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": company,
            "customer_type": "Company",
            "customer_group": cust_group,
            "territory": territory,
        }).insert(ignore_permissions=True)


def _any_plan():
    return frappe.get_all("Subscription Plan", limit=1, pluck="name")[0]


def _base_signup(email, company):
    return frappe.get_doc({
        "doctype": "DOBiz Trial Signup",
        "full_name": "ANFRG Test User",
        "email": email,
        "phone": "+251900000000",
        "company_name": company,
        "industry": "Technology & IT",
        "package_tier": "Professional",
        "billing_term": "1",
        "status": "Pending",
    }).insert(ignore_permissions=True)


def _provisioned_user(email):
    """Signup after_insert provisions its own DISABLED user when manual
    review is enforced — reuse it instead of inserting a duplicate."""
    if frappe.db.exists("User", email):
        return frappe.get_doc("User", email)
    return frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": "ANFRG",
        "send_welcome_email": 0,
        "enabled": 0,
    }).insert(ignore_permissions=True)


def run():
    from bizmarketing.api.dobiz_manual_activation import (
        activate_account,
        approve_bank_payment,
        manual_review_required,
        online_auto_activation_enabled,
        reject_bank_payment,
    )

    stamp = now_datetime().strftime("%Y%m%d%H%M%S")
    suffix = f"anfrg{stamp}"
    email_a = f"{suffix}a@test.local"
    email_b = f"{suffix}b@test.local"
    comp_a = f"ANFRG Test Co A {stamp}"
    comp_b = f"ANFRG Test Co B {stamp}"
    created = []

    try:
        # ---- TC-a/b: settings flags exist & defaults safe -----------------
        _record("TC-a manual_review_required callable",
                isinstance(manual_review_required(), bool))
        _record("TC-b online gate callable",
                isinstance(online_auto_activation_enabled(), bool))

        # ---- TC1: signup creates DISABLED user + Trialling sub ------------
        # (signup API path exercised indirectly: emulate its artifacts)
        _ensure_customer(comp_a)
        signup_a = _base_signup(email_a, comp_a)
        created.append(("DOBiz Trial Signup", signup_a.name))
        user_a = _provisioned_user(email_a)
        created.append(("User", user_a.name))
        sub_a = frappe.get_doc({
            "doctype": "Subscription",
            "party_type": "Customer",
            "party": comp_a,
            "company": "Biz Technology Solutions",
            "status": "Trialling",
            "plans": [{"plan": _any_plan(), "qty": 1}],
            "current_invoice_start": frappe.utils.today(),
        }).insert(ignore_permissions=True)
        created.append(("Subscription", sub_a.name))

        pay_a = frappe.get_doc({
            "doctype": "DOBiz Payment Transaction",
            "subscription": sub_a.name,
            "customer": comp_a,
            "email": email_a,
            "paid_by": "ANFRG Test User",
            "bank_name": "CBE",
            "reference_no": f"TESTREF-{stamp}-A",
            "amount": 9500.0,
            "status": "Pending",
            "payment_status": "Pending",
            "linked_signup": signup_a.name,
            "notes": "ANFRG-26-00063 automated test",
        }).insert(ignore_permissions=True)
        created.append(("DOBiz Payment Transaction", pay_a.name))

        # ---- TC2/TC5: admin approve activates everything -------------------
        approve_bank_payment(pay_a.name, confirmed=1)
        pay_a.reload()
        user_a.reload()
        signup_a.reload()
        sub_a.reload()
        _record("TC2 payment Approved after admin approve",
                pay_a.payment_status == "Approved")
        _record("TC5a user enabled after approve",
                int(user_a.enabled or 0) == 1)
        _record("TC5b signup Converted after approve",
                signup_a.status == "Converted")
        _record("TC5c subscription Active after approve",
                sub_a.status == "Active")

        # ---- TC6/TC12: double approve is an IDEMPOTENT NO-OP ---------------
        dup = approve_bank_payment(pay_a.name, confirmed=1)
        _record("TC6 duplicate approve is safe no-op",
                isinstance(dup, dict) and dup.get("status") == "already_approved")

        # ---- TC7: rejection keeps account locked --------------------------
        _ensure_customer(comp_b)
        signup_b = _base_signup(email_b, comp_b)
        created.append(("DOBiz Trial Signup", signup_b.name))
        user_b = _provisioned_user(email_b)
        created.append(("User", user_b.name))
        sub_b = frappe.get_doc({
            "doctype": "Subscription",
            "party_type": "Customer",
            "party": comp_b,
            "company": "Biz Technology Solutions",
            "status": "Trialling",
            "plans": [{"plan": _any_plan(), "qty": 1}],
        }).insert(ignore_permissions=True)
        created.append(("Subscription", sub_b.name))
        pay_b = frappe.get_doc({
            "doctype": "DOBiz Payment Transaction",
            "subscription": sub_b.name,
            "customer": comp_b,
            "email": email_b,
            "paid_by": "ANFRG Test User",
            "bank_name": "Telebirr",
            "reference_no": f"TESTREF-{stamp}-B",
            "amount": 100.0,
            "payment_status": "Pending",
            "linked_signup": signup_b.name,
        }).insert(ignore_permissions=True)
        created.append(("DOBiz Payment Transaction", pay_b.name))

        blocked = False
        try:
            reject_bank_payment(pay_b.name, reason="")
        except Exception:
            blocked = True
        _record("TC7a rejection without reason blocked", blocked)

        reject_bank_payment(pay_b.name, reason="Test funds not received")
        pay_b.reload()
        user_b.reload()
        _record("TC7b payment Rejected", pay_b.payment_status == "Rejected")
        _record("TC7c user still disabled after rejection",
                int(user_b.enabled or 0) == 0)

        # ---- TC8: cron skips Pending signups -------------------------------
        from bizmarketing.api import subscription_cron
        before = frappe.db.get_value("DOBiz Trial Signup", signup_b.name, "status")
        subscription_cron.sync_trial_signup_status()
        after = frappe.db.get_value("DOBiz Trial Signup", signup_b.name, "status")
        _record("TC8 cron leaves Pending untouched", before == after == "Pending")

        # ---- TC-deploy: custom fields exist --------------------------------
        cf = frappe.get_meta("DOBiz SaaS Settings").get_field(
            "require_manual_bank_review")
        cf2 = frappe.get_meta("DOBiz SaaS Settings").get_field(
            "auto_activate_online_payments")
        _record("DEPLOY custom fields exist", bool(cf and cf2))

    except Exception as e:
        _record("SUITE unexpected error", False, f"{e}\n{traceback.format_exc()}")
    finally:
        _cleanup(created)
        frappe.db.commit()

    failed = [r for r in RESULTS if not r["ok"]]
    summary = {
        "total": len(RESULTS),
        "passed": len(RESULTS) - len(failed),
        "failed": len(failed),
        "results": RESULTS,
    }
    print("\n=== ANFRG-26-00063 PHASE 1 SERVER SUITE ===")
    print(json.dumps(summary, indent=2))
    return summary
