import os, sys, json
import frappe

def clean_third_party_workspace_links():
    """
    BISMALLAH - Clean and remove all third-party and learn links across all Workspaces and Navbar Settings.
    """
    frappe.logger().info("BISMALLAH - Running workspace and navbar link cleaner...")
    
    # 1. Delete third-party shortcuts from tabWorkspace Shortcut
    frappe.db.sql("""
        DELETE FROM `tabWorkspace Shortcut`
        WHERE url LIKE '%frappe%' 
           OR url LIKE '%erpnext%' 
           OR url LIKE '%school%' 
           OR url LIKE '%marketplace%'
           OR label LIKE 'Learn%'
    """)
    frappe.db.commit()
    print("CLEANED_WORKSPACE_SHORTCUTS")

    # 2. Hide Navbar Settings Help Dropdown Items (Frappe standard requirement: set hidden=1)
    try:
        if frappe.db.exists("DocType", "Navbar Settings"):
            navbar = frappe.get_single("Navbar Settings")
            target_labels = ["Frappe School", "Frappe Support", "User Forum", "Documentation"]
            
            hidden_count = 0
            for item in navbar.help_dropdown:
                if item.item_label in target_labels or any(k in (item.action or '').lower() for k in ["frappe", "school"]):
                    item.hidden = 1
                    hidden_count += 1
            
            navbar.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"HIDDEN_NAVBAR_ITEMS: {hidden_count} items hidden")
    except Exception as e:
        print(f"NAVBAR_CLEAN_ERROR: {str(e)}")

    # 3. Clear cache
    frappe.clear_cache()
    print("CACHE_CLEARED_SUCCESSFULLY")

def sanitize_boot_workspaces(bootinfo):
    """
    Session boot filter hook to ensure third-party shortcuts are stripped from frontend payload.
    """
    try:
        if hasattr(bootinfo, "allowed_workspaces") and bootinfo.allowed_workspaces:
            for ws in bootinfo.allowed_workspaces:
                if isinstance(ws, dict) and "shortcuts" in ws:
                    ws["shortcuts"] = [
                        s for s in ws.get("shortcuts", [])
                        if not any(k in (s.get("url") or "").lower() or k in (s.get("label") or "").lower() 
                                   for k in ["frappe", "erpnext", "school", "marketplace", "learn"])
                    ]
    except Exception as e:
        pass
