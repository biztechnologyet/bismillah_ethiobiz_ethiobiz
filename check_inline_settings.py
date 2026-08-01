import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

import json
import requests

settings = frappe.get_single("HADEEDA Settings")
print("ENABLED:", settings.enabled)
print("INLINE_ENABLED:", settings.inline_ai_enabled)
print("INLINE_WEBHOOK_URL:", settings.inline_webhook_url)
print("CHAT_WEBHOOK_URL:", settings.chat_webhook_url)

# Test posting to inline_webhook_url directly or falling back to chat_webhook_url if empty!
inline_url = settings.inline_webhook_url or settings.chat_webhook_url
print("TARGET_URL:", inline_url)

payload = {
    "action": "sendMessage",
    "sessionId": "test_inline_session",
    "chatInput": "Draft a professional response to a client",
    "metadata": {
        "source": "inline",
        "username": "Administrator"
    }
}

try:
    resp = requests.post(inline_url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    print("INLINE_STATUS:", resp.status_code)
    print("INLINE_RAW_BODY:", repr(resp.text[:300]))
except Exception as e:
    print("INLINE_ERROR:", str(e))

frappe.destroy()
