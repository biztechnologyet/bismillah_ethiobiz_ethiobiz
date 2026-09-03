import frappe
import json
import os

def execute():
	workspaces = [
		{
			"name": "EthioBiz Ads",
			"label": "EthioBiz Ads",
			"module": "Ethiobiz Theme",
			"json_path": "workspace/ethiobiz_ads/ethiobiz_ads.json"
		},
		{
			"name": "Salon & Spa Hub",
			"label": "Salon & Spa Hub",
			"module": "Ethiobiz Theme",
			"json_path": "workspace/salon_and_spa_hub/salon_and_spa_hub.json"
		},
		{
			"name": "DOBiz Subscription Management",
			"label": "DOBiz Subscription Management",
			"module": "Ethiobiz Theme",
			"json_path": "workspace/dobiz_subscription/dobiz_subscription.json"
		}
	]

	base_path = frappe.get_app_path("bismillah_ethiobiz", "ethiobiz_theme")

	for ws in workspaces:
		json_file = os.path.join(base_path, ws["json_path"])
		if os.path.exists(json_file):
			with open(json_file, "r", encoding="utf-8") as f:
				data = json.load(f)
			
			if frappe.db.exists("Workspace", ws["name"]):
				doc = frappe.get_doc("Workspace", ws["name"])
				doc.update(data)
				doc.save(ignore_permissions=True)
				print(f"Updated Workspace: {ws['name']}")
			else:
				doc = frappe.get_doc(data)
				doc.insert(ignore_permissions=True)
				print(f"Inserted Workspace: {ws['name']}")
		else:
			print(f"JSON file not found for {ws['name']} at {json_file}")
	
	frappe.db.commit()
