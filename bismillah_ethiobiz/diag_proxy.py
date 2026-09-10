import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

import json
import requests

url = "https://ethiobiz.et/api/method/bismillah_ethiobiz.api.chat_webhook_proxy"

# Test 1: Standard message payload from @n8n/chat widget
payload1 = {
    "action": "sendMessage",
    "sessionId": "test_session_123",
    "chatInput": "Hello",
    "metadata": {
        "source": "widget",
        "username": "Administrator",
        "full_name": "Administrator",
        "email": "admin@ethiobiz.et",
        "company": "Biz Technology Solutions"
    }
}

print("--- TESTING PROXY ENDPOINT ---")
try:
    resp = requests.post(url, json=payload1, headers={"Content-Type": "application/json"}, timeout=60)
    print("STATUS:", resp.status_code)
    print("HEADERS:", resp.headers.get("content-type"))
    print("BODY:", resp.text)
except Exception as e:
    print("ERROR:", str(e))

frappe.destroy()
