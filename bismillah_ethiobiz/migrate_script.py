import os
os.chdir('/home/frappe/frappe-bench/sites')
os.makedirs('../logs', exist_ok=True)
os.makedirs('ethiobiz.et/logs', exist_ok=True)

from frappe.migrate import SiteMigration
migrator = SiteMigration(skip_failing=False, skip_search_index=False)
migrator.run('ethiobiz.et')
print('MIGRATE_DONE')
