import os, sys
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

# Check if the column exists in the DB
try:
    result = frappe.db.sql("SHOW COLUMNS FROM `tabHADEEDA Settings` LIKE 'enable_streaming'")
    print("DB_COLUMN_EXISTS:", bool(result))
except Exception as e:
    print("DB_COLUMN_CHECK_ERROR:", str(e))

# Check the JSON schema on disk
try:
    import json
    schema_path = '/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/doctype/hadeeda_settings/hadeeda_settings.json'
    with open(schema_path) as f:
        schema = json.load(f)
    field_names = [f.get('fieldname') for f in schema.get('fields', [])]
    print("SCHEMA_HAS_ENABLE_STREAMING:", 'enable_streaming' in field_names)
    print("ALL_FIELDS:", field_names)
except Exception as e:
    print("SCHEMA_CHECK_ERROR:", str(e))

# Check API response
try:
    s = frappe.get_single('HADEEDA Settings')
    print("DOC_HAS_ATTR:", hasattr(s, 'enable_streaming'))
    print("DOC_VALUE:", getattr(s, 'enable_streaming', 'MISSING'))
except Exception as e:
    print("DOC_CHECK_ERROR:", str(e))

# Check the api.py file
try:
    api_path = '/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/api.py'
    with open(api_path) as f:
        content = f.read()
    print("API_HAS_ENABLE_STREAMING:", 'enable_streaming' in content)
except Exception as e:
    print("API_CHECK_ERROR:", str(e))

frappe.destroy()
