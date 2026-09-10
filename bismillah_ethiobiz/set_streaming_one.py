import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

# Set enable_streaming = 1 in tabSingles
try:
    frappe.db.sql("""
        DELETE FROM `tabSingles` 
        WHERE doctype='HADEEDA Settings' AND field='enable_streaming'
    """)
    frappe.db.sql("""
        INSERT INTO `tabSingles` (doctype, field, value)
        VALUES ('HADEEDA Settings', 'enable_streaming', '1')
    """)
    frappe.db.commit()
    print("SET_ENABLE_STREAMING_ONE_SUCCESS")
except Exception as e:
    print("SET_STREAMING_ERROR:", str(e))

frappe.clear_cache(doctype='HADEEDA Settings')
frappe.destroy()
