import os

import frappe

frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
frappe.connect()

import bismillah_ethiobiz

print("python package:", bismillah_ethiobiz.__file__)
print("get_app_path:", frappe.get_app_path("bismillah_ethiobiz"))
for fn in ("get_app_source_path", "get_pymodule_path", "get_module_path"):
    if hasattr(frappe, fn):
        try:
            print(fn + ":", getattr(frappe, fn)("bismillah_ethiobiz") if fn != "get_module_path" else getattr(frappe, fn)("EthioBiz Theme"))
        except Exception as exc:
            print(fn, "ERR", exc)

paths = [
    "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/patches.txt",
    "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/patches.txt",
    "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/ethiobiz_theme/doctype/ethiobiz_card_portal_item/ethiobiz_card_portal_item.json",
    "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/ethiobiz_theme/doctype/ethiobiz_card_portal_item/ethiobiz_card_portal_item.json",
    "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/www/dobiz-signup.html",
    "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/www/dobiz-signup.html",
]
for p in paths:
    print(os.path.exists(p), p)

print("doctype module (DB):", frappe.db.get_value("DocType", "EthioBiz Card Portal Item", "module"))
frappe.destroy()
