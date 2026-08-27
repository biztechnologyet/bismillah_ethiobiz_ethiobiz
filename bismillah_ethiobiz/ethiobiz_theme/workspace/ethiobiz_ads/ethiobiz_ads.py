import frappe

def get_data():
	return {
		"label": "EthioBiz Ads",
		"icon": "bullhorn",
		"type": "Workspace",
		"is_standard": 1,
		"module": "Ethiobiz Theme",
		"public": 1,
		"content": [
			{"type": "header", "data": {"text": "EthioBiz Ads Overview", "level": 3, "col": 12}},
			{"type": "shortcut", "data": {"shortcut_name": "EthioBiz Ads Settings", "col": 4}},
			{"type": "shortcut", "data": {"shortcut_name": "EthioBiz Ad Campaign", "col": 4}},
			{"type": "shortcut", "data": {"shortcut_name": "EthioBiz Ad Slot", "col": 4}},
		],
		"links": [
			{"label": "EthioBiz Ads Settings", "link_to": "EthioBiz Ads Settings", "link_type": "DocType", "type": "Link"},
			{"label": "EthioBiz Ad Campaign", "link_to": "EthioBiz Ad Campaign", "link_type": "DocType", "type": "Link"},
			{"label": "EthioBiz Ad Slot", "link_to": "EthioBiz Ad Slot", "link_type": "DocType", "type": "Link"}
		]
	}
