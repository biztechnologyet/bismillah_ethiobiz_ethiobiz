import requests
import json

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

resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
print("EXACT_HTTP_STATUS:", resp.status_code)
print("EXACT_HTTP_HEADERS:", resp.headers.get("Content-Type"))
print("EXACT_HTTP_BODY_REPR:", repr(resp.text))
