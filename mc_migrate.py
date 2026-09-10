import frappe, os
os.environ[HOME] = /home/frappe
frappe.init(sites_dir=/home/frappe/frappe-bench/sites)
frappe.connect(ethiobiz.et)
frappe.migrate()
frappe.destroy()
print(MIGRATE_DONE)
PYEOF
echo Script written
