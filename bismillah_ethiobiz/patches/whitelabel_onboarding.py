"""
BISMALLAH — Whitelabel Onboarding Patch for EthioBiz.ET INSHA'ALLAH
Rebrands all Frappe/ERPNext Module Onboarding & Onboarding Steps to EthioBiz brand.
"""
import frappe


def execute():
    """Whitelabel all Frappe/ERPNext onboarding content to EthioBiz brand."""
    brand_name = "EthioBiz"
    brand_full = "EthioBiz.ET"

    # 1. Rebrand Module Onboarding titles and subtitles
    if frappe.db.exists("DocType", "Module Onboarding"):
        onboardings = frappe.get_all("Module Onboarding", fields=["name", "title", "subtitle", "success_message"])
        for ob in onboardings:
            updates = {}
            title = ob.get("title") or ""
            subtitle = ob.get("subtitle") or ""
            success = ob.get("success_message") or ""

            # Replace generic brand references
            for old_brand in ["Frappe", "ERPNext", "frappe", "erpnext"]:
                if old_brand in title:
                    title = title.replace(old_brand, brand_full)
                    updates["title"] = title
                if old_brand in subtitle:
                    subtitle = subtitle.replace(old_brand, brand_full)
                    updates["subtitle"] = subtitle
                if old_brand in success:
                    success = success.replace(old_brand, brand_full)
                    updates["success_message"] = success

            if updates:
                frappe.db.set_value("Module Onboarding", ob["name"], updates, update_modified=False)
                frappe.log_error(f"Whitelabeled Module Onboarding: {ob['name']}", "Onboarding Whitelabel Patch")

    # 2. Rebrand Onboarding Steps
    if frappe.db.exists("DocType", "Onboarding Step"):
        steps = frappe.get_all("Onboarding Step", fields=["name", "title", "description"])
        for step in steps:
            updates = {}
            title = step.get("title") or ""
            desc = step.get("description") or ""

            for old_brand in ["Frappe", "ERPNext", "frappe", "erpnext"]:
                if old_brand in title:
                    title = title.replace(old_brand, brand_full)
                    updates["title"] = title
                if old_brand in desc:
                    desc = desc.replace(old_brand, brand_full)
                    updates["description"] = desc

            if updates:
                frappe.db.set_value("Onboarding Step", step["name"], updates, update_modified=False)

    # 3. Ensure onboarding is enabled site-wide
    if frappe.db.exists("DocType", "System Settings"):
        try:
            frappe.db.set_value("System Settings", "System Settings", "setup_complete", 1, update_modified=False)
        except Exception:
            pass

    # 4. Set Website Settings brand name
    if frappe.db.exists("DocType", "Website Settings"):
        try:
            ws = frappe.get_single("Website Settings")
            if not ws.app_name or ws.app_name in ("Frappe", "ERPNext"):
                ws.app_name = brand_full
                ws.flags.ignore_permissions = True
                ws.save(ignore_permissions=True)
        except Exception:
            pass

    frappe.db.commit()
    print(f"✅ BISMALLAH — Onboarding whitelabeled to {brand_full} INSHA'ALLAH")
