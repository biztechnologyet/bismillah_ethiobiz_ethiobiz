import os, sys
os.chdir('/home/frappe/frappe-bench/sites')
os.makedirs('../logs', exist_ok=True)
os.makedirs('ethiobiz.et/logs', exist_ok=True)

import frappe
frappe.init('ethiobiz.et')
frappe.connect()

# Find the actual table name for HADEEDA Settings
try:
    # Check if it's a Singles table
    result = frappe.db.sql("SELECT value FROM `tabSingles` WHERE doctype='HADEEDA Settings' AND field='enabled'")
    print("SINGLES_TABLE_RESULT:", result)
except Exception as e:
    print("SINGLES_CHECK_ERROR:", str(e))

# Check all tables
try:
    tables = frappe.db.sql("SHOW TABLES LIKE '%hadeeda%'", as_list=True)
    print("HADEEDA_TABLES:", tables)
except Exception as e:
    print("TABLE_CHECK_ERROR:", str(e))

# Check if enable_streaming exists in tabSingles
try:
    result = frappe.db.sql("SELECT value FROM `tabSingles` WHERE doctype='HADEEDA Settings' AND field='enable_streaming'")
    print("STREAMING_IN_SINGLES:", result)
except Exception as e:
    print("STREAMING_SINGLES_ERROR:", str(e))

# List all fields for HADEEDA Settings in Singles
try:
    result = frappe.db.sql("SELECT field FROM `tabSingles` WHERE doctype='HADEEDA Settings'", as_list=True)
    print("ALL_SINGLES_FIELDS:", [r[0] for r in result])
except Exception as e:
    print("ALL_FIELDS_ERROR:", str(e))

frappe.destroy()
