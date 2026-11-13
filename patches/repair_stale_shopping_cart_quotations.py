"""Repair stale Magala / Webshop shopping-cart quotations.

A Shopping Cart quotation can outlive a Website Item. The webshop cart renderer
then calls ``d.update(None)`` and raises ``TypeError`` on ``/cart``. This patch
removes only those orphan rows, preserves valid rows, and cancels quotations
that become empty.

Run once through ``patches.txt``. For a dry run, call::

    from bismillah_ethiobiz.patches.repair_stale_shopping_cart_quotations import repair
    repair(dry_run=True)
"""

import json

import frappe


def _website_item_name(item_code):
    if not item_code:
        return None
    return frappe.db.get_value("Website Item", {"item_code": item_code}, "name")


def _repair_quotation(name, dry_run=False):
    qtn = frappe.get_doc("Quotation", name)
    rows = list(getattr(qtn, "items", []) or [])
    keep = []
    removed = []

    for row in rows:
        code = getattr(row, "item_code", None)
        if _website_item_name(code):
            keep.append(row)
        else:
            removed.append(
                {
                    "item_code": code,
                    "item_name": getattr(row, "item_name", None),
                    "qty": getattr(row, "qty", 0),
                    "rate": getattr(row, "rate", 0),
                    "amount": getattr(row, "amount", 0),
                }
            )

    if not removed:
        return {"quotation": name, "removed": [], "cancelled": False}

    report = {
        "quotation": name,
        "customer": getattr(qtn, "party_name", None),
        "removed": removed,
        "kept": [
            {
                "item_code": getattr(row, "item_code", None),
                "qty": getattr(row, "qty", 0),
                "rate": getattr(row, "rate", 0),
            }
            for row in keep
        ],
        "cancelled": False,
    }

    if dry_run:
        return report

    qtn.set("items", keep)
    try:
        qtn.calculate_taxes_and_totals()
    except Exception:
        pass

    if not keep:
        try:
            qtn.cancel()
            report["cancelled"] = True
        except Exception as exc:
            frappe.logger("ethiobiz").error(
                "Could not cancel empty stale cart %s: %s", name, exc
            )
            try:
                qtn.delete(ignore_permissions=True)
                report["deleted"] = True
            except Exception as delete_exc:
                frappe.logger("ethiobiz").error(
                    "Could not delete empty stale cart %s: %s", name, delete_exc
                )
    else:
        qtn.flags.ignore_permissions = True
        qtn.flags.ignore_mandatory = True
        qtn.save(ignore_permissions=True)

    return report


def repair(dry_run=True):
    names = frappe.get_all(
        "Quotation",
        filters={"order_type": "Shopping Cart", "docstatus": 0},
        pluck="name",
        limit_page_length=0,
    )
    reports = []
    for name in names:
        try:
            report = _repair_quotation(name, dry_run=dry_run)
            if report.get("removed"):
                reports.append(report)
        except Exception as exc:
            frappe.logger("ethiobiz").error(
                "Stale cart repair failed for %s: %s", name, exc
            )
            reports.append({"quotation": name, "error": str(exc)})

    if not dry_run:
        try:
            frappe.clear_cache()
        except Exception:
            pass
        try:
            frappe.cache().delete_keys("magala_cart:*")
        except Exception:
            pass
        frappe.db.commit()

    print("Stale cart repair report:")
    print(json.dumps(reports, indent=2, default=str))
    return reports


def execute():
    repair(dry_run=False)
