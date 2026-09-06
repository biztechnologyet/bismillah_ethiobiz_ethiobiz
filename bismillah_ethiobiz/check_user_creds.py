import frappe

def run():
    frappe.init("ethiobiz.et")
    frappe.connect()
    users = frappe.db.sql("SELECT name, api_key, telegram_username FROM tabUser WHERE api_key IS NOT NULL OR telegram_username IS NOT NULL OR name='Administrator'", as_dict=True)
    print("USERS:", users)
    
    # Check HADEEDA settings
    settings = frappe.get_single("HADEEDA Settings")
    print("HADEEDA SETTINGS:", settings.enable_service_token_auth, getattr(settings, "default_service_user", None))
    import requests
    print("Testing webhook:", settings.chat_webhook_url)
    try:
        r = requests.post(settings.chat_webhook_url, json={"action": "sendMessage", "chatInput": "test message", "sessionId": "test"}, timeout=15)
        print("WEBHOOK RESP:", r.status_code, r.text[:300])
    except Exception as e:
        print("WEBHOOK ERR:", e)
    todo = frappe.db.get_value("ToDo", "33sjrj7bco", ["name", "description", "status"], as_dict=True)
    print("TODO:", todo)
    
    wi = frappe.db.get_value("Website Item", "WEB-ITM-0137", ["name", "item_code", "website_image", "thumbnail"], as_dict=True)
    print("WEBSITE ITEM:", wi)
    
    files = frappe.db.sql("select file_url, attached_to_doctype, attached_to_name from tabFile where attached_to_name in ('WEB-ITM-0137', 'PROD-YIRGACHEFFE-COFFEE-03')", as_dict=True)
    print("ATTACHED FILES:", files)

if __name__ == "__main__":
    run()
