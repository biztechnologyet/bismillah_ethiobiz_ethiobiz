import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

import json
import requests

# Test fetching n8n webhook directly and parsing its response
settings = frappe.get_single('HADEEDA Settings')
webhook_url = settings.chat_webhook_url
print("WEBHOOK_URL:", webhook_url)

test_payload = {
    "action": "sendMessage",
    "sessionId": "test::Biz Technology",
    "chatInput": "Hi",
    "metadata": {
        "source": "widget",
        "username": "test"
    }
}

try:
    resp = requests.post(webhook_url, json=test_payload, headers={"Content-Type": "application/json"}, timeout=30)
    print("N8N_STATUS:", resp.status_code)
    print("N8N_RAW_RESPONSE_HEAD:", repr(resp.text[:300]))

    # Now test NDJSON parser on real n8n response
    from bismillah_ethiobiz.api import _parse_ndjson
    parsed_output = _parse_ndjson(resp.text)
    print("PARSED_OUTPUT:", repr(parsed_output))
except Exception as e:
    print("N8N_FETCH_ERROR:", str(e))

frappe.destroy()
