import frappe
from frappe.utils.password import set_encrypted_password

def run():
    frappe.init(site="ethiobiz.et", sites_path="sites")
    frappe.connect()

    settings = frappe.get_single("HADEEDA Settings")
    settings.enable_service_token_auth = 1
    settings.default_service_user = "Administrator"
    settings.save(ignore_permissions=True)

    token = "HADEEDA_SECURE_TOKEN_2026_INSHAALLAH"
    set_encrypted_password("HADEEDA Settings", "HADEEDA Settings", token, "service_auth_token")
    frappe.db.commit()
    print("SUCCESS: HADEEDA Settings updated with token and default_service_user")

if __name__ == "__main__":
    run()
