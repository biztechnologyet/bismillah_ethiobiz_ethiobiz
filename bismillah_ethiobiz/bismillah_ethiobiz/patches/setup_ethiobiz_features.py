import os
import json
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.modules.import_file import import_file_by_path

def execute():
    """Automated migration hook to guarantee all EthioBiz features persist on fresh install/restart."""
    print("Running EthioBiz Canonical Ecosystem Patch...")
    frappe.flags.in_import = True
    frappe.flags.in_migrate = True

    # 1. Ensure HADEEDA Settings
    if frappe.db.exists("DocType", "HADEEDA Settings"):
        settings = frappe.get_single("HADEEDA Settings")
        settings.enabled = 1
        settings.bot_name = "Hadeeda AI"
        settings.welcome_message = "Assalamu Alaikum! Welcome to EthioBiz. How can I assist your business today?"
        settings.primary_color = "#008080"
        settings.enable_inline_ai = 1
        settings.inline_ai_trigger = "/"
        settings.n8n_webhook_url = "http://128.140.82.215:8601/webhook/hadeeda-chat"
        settings.flags.ignore_permissions = True
        settings.flags.ignore_mandatory = True
        settings.save()
        frappe.db.commit()

    # 2. Company Map Location Fields
    custom_fields = {
        "Company": [
            {
                "fieldname": "location_section",
                "fieldtype": "Section Break",
                "label": "WebShop Map & Location",
                "insert_after": "domain",
                "collapsible": 1
            },
            {
                "fieldname": "show_on_map",
                "fieldtype": "Check",
                "label": "Show on WebShop Map",
                "default": "1",
                "insert_after": "location_section",
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            {
                "fieldname": "business_category",
                "fieldtype": "Select",
                "label": "Business Category",
                "options": "\nHotel & Lodging\nRestaurant & Cafe\nRetail & Supermarket\nSalon & Beauty\nClinic & Healthcare\nReal Estate & Property\nIT & Professional Services\nOther",
                "insert_after": "show_on_map",
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            {
                "fieldname": "col_break_loc1",
                "fieldtype": "Column Break",
                "insert_after": "business_category"
            },
            {
                "fieldname": "latitude",
                "fieldtype": "Float",
                "label": "Latitude",
                "precision": "7",
                "insert_after": "col_break_loc1",
                "in_list_view": 1
            },
            {
                "fieldname": "longitude",
                "fieldtype": "Float",
                "label": "Longitude",
                "precision": "7",
                "insert_after": "latitude",
                "in_list_view": 1
            },
            {
                "fieldname": "gps_accuracy",
                "fieldtype": "Float",
                "label": "GPS Accuracy (Meters)",
                "read_only": 1,
                "insert_after": "longitude"
            },
            {
                "fieldname": "sec_break_loc2",
                "fieldtype": "Section Break",
                "insert_after": "gps_accuracy"
            },
            {
                "fieldname": "location_address",
                "fieldtype": "Small Text",
                "label": "Location Description / Landmark",
                "insert_after": "sec_break_loc2"
            },
            {
                "fieldname": "map_location",
                "fieldtype": "Geolocation",
                "label": "Map Pin Location",
                "insert_after": "location_address"
            }
        ]
    }
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()

    # P4-D: User per-user particles + Theme desk animation toggle
    p4_fields = {
        "User": [
            {
                "fieldname": "ethiobiz_enable_particles",
                "fieldtype": "Check",
                "label": "Enable Desk Particles",
                "default": "1",
                "insert_after": "last_active"
            }
        ],
        "EthioBiz Theme": [
            {
                "fieldname": "enable_desk_animation",
                "fieldtype": "Check",
                "label": "Enable Desk Animation (Global Default)",
                "default": "1",
                "insert_after": "enable_background_images"
            }
        ]
    }
    create_custom_fields(p4_fields, update=True)
    frappe.db.commit()

    # 3. Ensure Website Homepage is set to index
    if frappe.db.exists("DocType", "Website Settings"):
        frappe.db.set_value("Website Settings", "Website Settings", "home_page", "index")
        frappe.db.commit()

    print("EthioBiz Canonical Ecosystem Patch Applied Successfully!")
