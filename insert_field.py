import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

# For custom doctypes, we need to insert the field directly into tabDocField
# First check the current max idx for insertion ordering
try:
    max_idx = frappe.db.sql("""
        SELECT MAX(idx) as max_idx FROM `tabDocField` 
        WHERE parent='HADEEDA Settings'
    """)[0][0] or 0
    print("Current max idx:", max_idx)
    
    # Find the idx of chat_enabled to insert enable_streaming right after it
    chat_enabled_idx = frappe.db.sql("""
        SELECT idx FROM `tabDocField` 
        WHERE parent='HADEEDA Settings' AND fieldname='chat_enabled'
    """)
    print("chat_enabled idx:", chat_enabled_idx)
    
    if chat_enabled_idx:
        insert_idx = chat_enabled_idx[0][0] + 1
        
        # Shift all fields after chat_enabled by 1
        frappe.db.sql("""
            UPDATE `tabDocField` SET idx = idx + 1 
            WHERE parent='HADEEDA Settings' AND idx >= %s
        """, insert_idx)
        
        # Insert the enable_streaming field
        doc = frappe.get_doc({
            'doctype': 'DocField',
            'parent': 'HADEEDA Settings',
            'parenttype': 'DocType',
            'parentfield': 'fields',
            'fieldname': 'enable_streaming',
            'fieldtype': 'Check',
            'label': 'Enable Streaming Responses',
            'default': '0',
            'idx': insert_idx
        })
        doc.db_insert()
        frappe.db.commit()
        print("FIELD_INSERTED at idx:", insert_idx)
    else:
        print("ERROR: chat_enabled field not found!")
        
except Exception as e:
    print("INSERT_ERROR:", str(e))
    import traceback
    traceback.print_exc()

# Verify
try:
    result = frappe.db.sql("""
        SELECT fieldname, fieldtype, label, idx FROM `tabDocField` 
        WHERE parent='HADEEDA Settings' AND fieldname='enable_streaming'
    """, as_dict=True)
    print("VERIFICATION:", result)
except Exception as e:
    print("VERIFY_ERROR:", str(e))

# Clear cache so the meta is refreshed
try:
    frappe.clear_cache(doctype='HADEEDA Settings')
    print("CACHE_CLEARED")
except Exception as e:
    print("CACHE_ERROR:", str(e))

frappe.destroy()
