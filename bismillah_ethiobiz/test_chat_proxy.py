import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

import json
import requests

from bismillah_ethiobiz.api import chat_webhook_proxy, _get_hadeeda_settings

settings = _get_hadeeda_settings()
print("CHAT_WEBHOOK_URL:", settings.chat_webhook_url)

payload = {
    "action": "sendMessage",
    "sessionId": "Administrator",
    "chatInput": "Hi",
    "metadata": {
        "source": "widget",
        "username": "Administrator",
        "full_name": "Hadi",
        "company": "EthioBiz"
    }
}

headers = {"Content-Type": "application/json"}
if settings.webhook_auth_header and settings.get_password("webhook_auth_value"):
    headers[settings.webhook_auth_header] = settings.get_password("webhook_auth_value")

try:
    resp = requests.post(settings.chat_webhook_url, json=payload, headers=headers, timeout=60)
    print("STATUS:", resp.status_code)
    print("RAW_RESPONSE:", repr(resp.text[:500]))
except Exception as e:
    print("ERROR:", str(e))

frappe.destroy()
