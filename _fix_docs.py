import frappe

frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
frappe.connect()


def show(tag):
    for dt in ("EthioBiz Card Portal Item", "EthioBiz Pillar Settings"):
        rows = frappe.get_all(
            "DocField",
            filters={"parent": dt, "fieldname": "subsystem_key"},
            fields=["options"],
        )
        print(tag, dt, rows)


show("BEFORE")
for dt in (
    "ethiobiz_pillar_settings",
    "ethiobiz_card_portal_item",
    "ethiobiz_theme",
):
    try:
        frappe.reload_doc("ethiobiz_theme", "doctype", dt, force=True)
        print("reloaded", dt)
    except Exception as exc:
        print("reload FAIL", dt, repr(exc))
frappe.db.commit()
frappe.clear_cache()
show("AFTER")
frappe.destroy()
