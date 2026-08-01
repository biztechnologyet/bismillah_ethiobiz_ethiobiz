import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

# Check if the DocField exists for HADEEDA Settings
try:
    result = frappe.db.sql("""
        SELECT name, fieldname, fieldtype, label 
        FROM `tabDocField` 
        WHERE parent='HADEEDA Settings' AND fieldname='enable_streaming'
    """, as_dict=True)
    print("DOCFIELD_EXISTS:", bool(result))
    if result:
        print("DOCFIELD_DETAILS:", result)
except Exception as e:
    print("DOCFIELD_ERROR:", str(e))

# Check if HADEEDA Settings doctype is custom
try:
    meta = frappe.get_meta('HADEEDA Settings')
    field_names = [f.fieldname for f in meta.fields]
    print("META_FIELDS:", field_names)
    print("META_HAS_STREAMING:", 'enable_streaming' in field_names)
    print("META_CUSTOM:", meta.custom)
    print("META_MODULE:", meta.module)
except Exception as e:
    print("META_ERROR:", str(e))

# Try to get the doc and see attributes
try:
    s = frappe.get_single('HADEEDA Settings')
    print("DOC_ATTRS:", [k for k in s.as_dict().keys() if not k.startswith('_')])
    print("HAS_STREAMING:", 'enable_streaming' in s.as_dict())
except Exception as e:
    print("DOC_ERROR:", str(e))

frappe.destroy()
