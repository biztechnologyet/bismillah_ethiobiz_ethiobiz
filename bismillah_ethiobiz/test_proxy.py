import os
os.chdir('/home/frappe/frappe-bench/sites')
import frappe
frappe.init('ethiobiz.et')
frappe.connect()

import json
from bismillah_ethiobiz.api import _parse_ndjson

# Test NDJSON parsing with actual data
test_ndjson = """{"type":"begin","metadata":{"nodeId":"7feefd16-de85-445c-82e2-0cf574ab299b","nodeName":"Formatter","itemIndex":0,"runIndex":0,"timestamp":1785608424617}}
{"type":"item","content":"Bismillah","metadata":{"nodeId":"7feefd16","itemIndex":0}}
{"type":"item","content":", InshaAllah.\\n\\nWelcome to Biz Technology.","metadata":{"nodeId":"7feefd16","itemIndex":0}}
{"type":"item","content":" How can I help you today?","metadata":{"nodeId":"7feefd16","itemIndex":0}}
{"type":"end","metadata":{"nodeId":"7feefd16","itemIndex":0}}"""

result = _parse_ndjson(test_ndjson)
print("NDJSON_PARSE_RESULT:", repr(result))
print("PARSE_SUCCESS:", result is not None)

# Test the output format
if result:
    output = json.dumps([{"output": result}])
    print("OUTPUT_FORMAT:", output[:200])

# Verify the proxy function exists and is importable
try:
    from bismillah_ethiobiz.api import chat_webhook_proxy
    print("PROXY_IMPORTABLE: True")
except Exception as e:
    print("PROXY_IMPORT_ERROR:", str(e))

# Verify the JS file on disk
js_path = '/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/public/js/ethiobiz_chat.js'
with open(js_path) as f:
    js_content = f.read()
print("JS_HAS_PROXY_URL:", 'chat_webhook_proxy' in js_content)
print("JS_HAS_NO_FETCH_PATCH:", 'originalFetch' not in js_content)

frappe.destroy()
