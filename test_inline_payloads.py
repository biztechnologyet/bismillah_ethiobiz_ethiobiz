import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

import json
import requests

url = "https://bizflow.ethiobiz.et/webhook/b15677a6-6611-42c8-88e2-43e0eb66f1b6/chat"

# Payload A: Standard widget payload format
payload_a = {
    "action": "sendMessage",
    "sessionId": "Administrator",
    "chatInput": "Draft a professional response to a client",
    "metadata": {
        "source": "widget",
        "username": "Administrator"
    }
}

# Payload B: Without extra metadata fields that might trigger MemoryOfficer_MCP error
payload_b = {
    "action": "sendMessage",
    "sessionId": "Administrator",
    "chatInput": "Draft a professional response to a client"
}

print("=== TESTING PAYLOAD A (Widget source) ===")
try:
    resp = requests.post(url, json=payload_a, headers={"Content-Type": "application/json"}, timeout=60)
    print("STATUS A:", resp.status_code)
    print("BODY A:", repr(resp.text[:400]))
except Exception as e:
    print("ERROR A:", str(e))

print("\n=== TESTING PAYLOAD B (Minimal) ===")
try:
    resp = requests.post(url, json=payload_b, headers={"Content-Type": "application/json"}, timeout=60)
    print("STATUS B:", resp.status_code)
    print("BODY B:", repr(resp.text[:400]))
except Exception as e:
    print("ERROR B:", str(e))

frappe.destroy()
