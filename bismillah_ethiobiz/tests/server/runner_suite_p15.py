import json

import frappe

frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
frappe.connect()

from bizmarketing.phase15_csrf_server_tests import run

summary = run()
with open("/tmp/anfrg_phase15_results.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)
print("RESULTS_SAVED=/tmp/anfrg_phase15_results.json")
