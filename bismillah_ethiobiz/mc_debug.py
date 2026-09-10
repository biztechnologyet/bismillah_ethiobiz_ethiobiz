import os, traceback
os.chdir('/home/frappe/frappe-bench/sites')
os.makedirs('../logs', exist_ok=True)
os.makedirs('ethiobiz.et/logs', exist_ok=True)

import frappe
frappe.init(site='ethiobiz.et')
frappe.connect()
try:
    # Try to clear cache (this is what SiteMigration.setUp does first)
    frappe.clear_cache()
except Exception:
    traceback.print_exc()
frappe.destroy()
