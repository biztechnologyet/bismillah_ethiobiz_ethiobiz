import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

frappe.set_user('Administrator')

from bismillah_ethiobiz.api import chat_inline

print("=== TESTING LIVE CHAT_INLINE FUNCTION ===")
try:
    res = chat_inline(prompt="Draft a polite thank you note to a client for choosing EthioBiz")
    print("LIVE_INLINE_RESULT:", res)
except Exception as e:
    print("LIVE_INLINE_ERROR:", str(e))

frappe.destroy()
