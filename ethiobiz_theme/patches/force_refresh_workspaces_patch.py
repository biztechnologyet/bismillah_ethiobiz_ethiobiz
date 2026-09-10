import frappe
import json

def execute():
    workspaces = [
        {
            "name": "EthioBiz Ads",
            "title": "EthioBiz Ads",
            "module": "Ethiobiz Theme",
            "public": 1,
            "is_standard": 0,
            "sequence_id": 99.0,
            "icon": "folder-normal",
            "indicator_color": "green",
            "content": "[]"
        },
        {
            "name": "Salon & Spa Hub",
            "title": "Salon & Spa Hub",
            "module": "Ethiobiz Theme",
            "public": 1,
            "is_standard": 0,
            "sequence_id": 99.0,
            "icon": "folder-normal",
            "indicator_color": "green",
            "content": "[]"
        }
    ]

    for ws in workspaces:
        name = ws["name"]
        if frappe.db.exists("Workspace", name):
            doc = frappe.get_doc("Workspace", name)
            doc.update(ws)
            doc.save(ignore_permissions=True)
            print(f"Updated Workspace: {name}")
        else:
            doc = frappe.new_doc("Workspace")
            doc.update(ws)
            doc.insert(ignore_permissions=True)
            print(f"Inserted Workspace: {name}")

    frappe.db.commit()
    frappe.clear_cache()
    print("Workspaces force-refreshed and cache cleared successfully InSha'Allah!")
