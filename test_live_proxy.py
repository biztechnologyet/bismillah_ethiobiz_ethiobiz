import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

import json
import requests

# Test posting directly to our proxy endpoint
url = "https://ethiobiz.et/api/method/bismillah_ethiobiz.api.chat_webhook_proxy"
payload = {
    "action": "sendMessage",
    "sessionId": "test_user_session",
    "chatInput": "HI",
    "metadata": {
        "source": "widget",
        "username": "Administrator"
    }
}

try:
    resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    print("PROXY_HTTP_STATUS:", resp.status_code)
    print("PROXY_RESPONSE_BODY:", resp.text)
except Exception as e:
    print("PROXY_TEST_ERROR:", str(e))

frappe.destroy()
