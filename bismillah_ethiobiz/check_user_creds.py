import frappe

def run():
    frappe.init("ethiobiz.et")
    frappe.connect()
    users = frappe.db.sql("SELECT name, api_key, telegram_username FROM tabUser WHERE api_key IS NOT NULL OR telegram_username IS NOT NULL OR name='Administrator'", as_dict=True)
    print("USERS:", users)
    
    # Check HADEEDA settings
    settings = frappe.get_single("HADEEDA Settings")
    print("HADEEDA SETTINGS:", settings.enable_service_token_auth, getattr(settings, "default_service_user", None))
    try:
        from frappe.utils.password import get_decrypted_password
        pwd = get_decrypted_password("HADEEDA Settings", "HADEEDA Settings", "service_auth_token", raise_exception=False)
        print("TOKEN:", pwd)
    except Exception as e:
        print("TOKEN ERR:", e)

if __name__ == "__main__":
    run()
