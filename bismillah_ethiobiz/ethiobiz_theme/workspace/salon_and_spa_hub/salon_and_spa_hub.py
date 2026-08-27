import frappe

def get_data():
	return {
		"label": "Salon & Spa Hub",
		"icon": "scissors",
		"type": "Workspace",
		"is_standard": 1,
		"module": "Ethiobiz Theme",
		"public": 1,
		"content": [
			{"type": "header", "data": {"text": "Salon & Spa Hub Overview", "level": 3, "col": 12}},
			{"type": "shortcut", "data": {"shortcut_name": "Salon Settings", "col": 4}},
			{"type": "shortcut", "data": {"shortcut_name": "Salon Appointment", "col": 4}},
			{"type": "shortcut", "data": {"shortcut_name": "Salon Service", "col": 4}},
			{"type": "shortcut", "data": {"shortcut_name": "Salon Stylist", "col": 4}},
		],
		"links": [
			{"label": "Salon Settings", "link_to": "Salon Settings", "link_type": "DocType", "type": "Link"},
			{"label": "Salon Appointment", "link_to": "Salon Appointment", "link_type": "DocType", "type": "Link"},
			{"label": "Salon Service", "link_to": "Salon Service", "link_type": "DocType", "type": "Link"},
			{"label": "Salon Stylist", "link_to": "Salon Stylist", "link_type": "DocType", "type": "Link"},
			{"label": "Salon Stylist Service", "link_to": "Salon Stylist Service", "link_type": "DocType", "type": "Link"},
			{"label": "Salon Appointment Service", "link_to": "Salon Appointment Service", "link_type": "DocType", "type": "Link"}
		]
	}
