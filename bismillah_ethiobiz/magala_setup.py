# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz Magala Marketplace & Map Setup
Bismillah Ar-Rahman Ar-Rahim

Creates all custom DocTypes, fields, and seeds Ethiopian Regions for the Dikka Shop mega-upgrade.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def ensure_magala_doctypes():
    """Ensure all Magala Marketplace and dynamic filter DocTypes exist."""
    try:
        print("EthioBiz: Ensuring Magala Marketplace DocTypes...")
        _create_item_product_image_doctype()
        _create_item_highlight_doctype()
        _create_magala_filter_group_doctype()
        _create_magala_filter_definition_doctype()
        _create_ethiopian_region_doctype()
        _setup_magala_custom_fields()
        print("EthioBiz: Magala Marketplace DocTypes & Custom Fields verified successfully.")
    except Exception as e:
        print(f"EthioBiz: Error setting up Magala DocTypes: {e}")
        frappe.log_error(f"Magala DocType setup error: {e}", "Magala Marketplace")


def _create_item_product_image_doctype():
    if not frappe.db.exists("DocType", "Item Product Image"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Item Product Image",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "image", "label": "Product Image", "fieldtype": "Attach Image", "reqd": 1},
                {"fieldname": "caption", "label": "Caption", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "sort_order", "label": "Sort Order", "fieldtype": "Int", "default": 0, "in_list_view": 1},
                {"fieldname": "is_primary", "label": "Is Primary", "fieldtype": "Check", "default": 0, "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: Item Product Image")


def _create_item_highlight_doctype():
    if not frappe.db.exists("DocType", "Item Highlight"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Item Highlight",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "highlight_text", "label": "Highlight Text", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "highlight_icon", "label": "Icon Class / Emoji", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "sort_order", "label": "Sort Order", "fieldtype": "Int", "default": 0, "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: Item Highlight")


def _create_magala_filter_definition_doctype():
    if not frappe.db.exists("DocType", "Magala Filter Definition"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Magala Filter Definition",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "filter_label", "label": "Filter Label", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "filter_field", "label": "Attribute Fieldname", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "filter_type", "label": "Filter Type", "fieldtype": "Select", "options": "Checkbox List\nDropdown\nRange Slider\nRadio", "default": "Checkbox List", "in_list_view": 1},
                {"fieldname": "filter_options", "label": "Options (comma-separated)", "fieldtype": "Small Text", "in_list_view": 1},
                {"fieldname": "sort_order", "label": "Sort Order", "fieldtype": "Int", "default": 0, "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: Magala Filter Definition")


def _create_magala_filter_group_doctype():
    if not frappe.db.exists("DocType", "Magala Filter Group"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Magala Filter Group",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "autoname": "field:filter_group_name",
            "fields": [
                {"fieldname": "filter_group_name", "label": "Filter Group Name", "fieldtype": "Data", "reqd": 1, "unique": 1},
                {"fieldname": "item_group", "label": "Item Group / Category", "fieldtype": "Link", "options": "Item Group", "reqd": 1},
                {"fieldname": "is_active", "label": "Is Active", "fieldtype": "Check", "default": 1},
                {"fieldname": "filters_section", "label": "Filter Rules", "fieldtype": "Section Break"},
                {"fieldname": "filters", "label": "Filters", "fieldtype": "Table", "options": "Magala Filter Definition"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Item Manager", "read": 1, "write": 1, "create": 1, "delete": 0},
                {"role": "All", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: Magala Filter Group")


def _create_ethiopian_region_doctype():
    if not frappe.db.exists("DocType", "Ethiopian Region"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Ethiopian Region",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "is_tree": 1,
            "autoname": "field:region_name",
            "nsm_parent_field": "parent_ethiopian_region",
            "fields": [
                {"fieldname": "region_name", "label": "Region / Zone / Sub-City Name", "fieldtype": "Data", "reqd": 1, "unique": 1},
                {"fieldname": "parent_ethiopian_region", "label": "Parent Region", "fieldtype": "Link", "options": "Ethiopian Region"},
                {"fieldname": "region_type", "label": "Type", "fieldtype": "Select", "options": "Country\nState / Region\nSub-City / Zone\nWoreda", "default": "State / Region", "in_list_view": 1},
                {"fieldname": "is_group", "label": "Is Group", "fieldtype": "Check", "default": 0},
                {"fieldname": "latitude", "label": "Center Latitude", "fieldtype": "Float"},
                {"fieldname": "longitude", "label": "Center Longitude", "fieldtype": "Float"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: Ethiopian Region")


def _setup_magala_custom_fields():
    """Create custom fields on Item, Company, Healthcare Practitioner, Item Review, Item Group."""
    fields_to_add = [
        # Item DocType
        ("Item", {"fieldname": "product_images", "label": "Product Gallery", "fieldtype": "Table", "options": "Item Product Image", "insert_after": "image"}),
        ("Item", {"fieldname": "product_highlights", "label": "Key Highlights", "fieldtype": "Table", "options": "Item Highlight", "insert_after": "description"}),
        ("Item", {"fieldname": "product_video_url", "label": "Product Video URL", "fieldtype": "Data", "insert_after": "product_images"}),
        ("Item", {"fieldname": "average_product_rating", "label": "Average Rating", "fieldtype": "Float", "read_only": 1, "insert_after": "product_highlights"}),
        ("Item", {"fieldname": "total_product_reviews", "label": "Total Reviews", "fieldtype": "Int", "read_only": 1, "insert_after": "average_product_rating"}),

        # Company DocType (Storefront & Map Fields)
        ("Company", {"fieldname": "company_slug", "label": "Store URL Slug", "fieldtype": "Data", "unique": 0, "insert_after": "company_name"}),
        ("Company", {"fieldname": "company_banner", "label": "Store Banner", "fieldtype": "Attach Image", "insert_after": "company_slug"}),
        ("Company", {"fieldname": "company_description_public", "label": "Public Description", "fieldtype": "Text Editor", "insert_after": "company_banner"}),
        ("Company", {"fieldname": "store_tier", "label": "Store Tier", "fieldtype": "Select", "options": "Free\nPro\nEnterprise", "default": "Free", "insert_after": "company_description_public"}),
        ("Company", {"fieldname": "custom_theme_color", "label": "Brand Color", "fieldtype": "Color", "insert_after": "store_tier"}),
        ("Company", {"fieldname": "social_telegram", "label": "Telegram", "fieldtype": "Data", "insert_after": "custom_theme_color"}),
        ("Company", {"fieldname": "social_facebook", "label": "Facebook", "fieldtype": "Data", "insert_after": "social_telegram"}),
        ("Company", {"fieldname": "social_instagram", "label": "Instagram", "fieldtype": "Data", "insert_after": "social_facebook"}),
        ("Company", {"fieldname": "social_tiktok", "label": "TikTok", "fieldtype": "Data", "insert_after": "social_instagram"}),
        ("Company", {"fieldname": "established_year", "label": "Established Year", "fieldtype": "Int", "insert_after": "social_tiktok"}),
        ("Company", {"fieldname": "ethiopian_region", "label": "Region", "fieldtype": "Link", "options": "Ethiopian Region", "insert_after": "established_year"}),
        ("Company", {"fieldname": "store_page_views", "label": "Page Views", "fieldtype": "Int", "read_only": 1, "insert_after": "ethiopian_region"}),
        ("Company", {"fieldname": "latitude", "label": "GPS Latitude", "fieldtype": "Float", "insert_after": "store_page_views"}),
        ("Company", {"fieldname": "longitude", "label": "GPS Longitude", "fieldtype": "Float", "insert_after": "latitude"}),
        ("Company", {"fieldname": "map_address", "label": "Map Display Address", "fieldtype": "Small Text", "insert_after": "longitude"}),
        ("Company", {"fieldname": "map_category", "label": "Map Category", "fieldtype": "Select", "options": "shops\nservices\nrestaurants\nhealthcare\nhotels\neducation\nother", "default": "shops", "insert_after": "map_address"}),
        ("Company", {"fieldname": "map_pin_color", "label": "Map Pin Color", "fieldtype": "Color", "insert_after": "map_category"}),
        ("Company", {"fieldname": "map_enabled", "label": "Show on Public Map", "fieldtype": "Check", "default": 1, "insert_after": "map_pin_color"}),

        # Healthcare Practitioner DocType
        ("Healthcare Practitioner", {"fieldname": "public_profile_slug", "label": "Public Profile URL Slug", "fieldtype": "Data", "insert_after": "practitioner_name"}),
        ("Healthcare Practitioner", {"fieldname": "profile_photo_hd", "label": "HD Profile Photo", "fieldtype": "Attach Image", "insert_after": "public_profile_slug"}),
        ("Healthcare Practitioner", {"fieldname": "consultation_fee", "label": "Consultation Fee (ETB)", "fieldtype": "Currency", "insert_after": "profile_photo_hd"}),
        ("Healthcare Practitioner", {"fieldname": "accepting_online_appointments", "label": "Accept Online Appointments", "fieldtype": "Check", "default": 1, "insert_after": "consultation_fee"}),
        ("Healthcare Practitioner", {"fieldname": "teleconsultation_available", "label": "Video Consultation Available", "fieldtype": "Check", "default": 1, "insert_after": "accepting_online_appointments"}),
        ("Healthcare Practitioner", {"fieldname": "home_visit_available", "label": "Home Visit Available", "fieldtype": "Check", "default": 0, "insert_after": "teleconsultation_available"}),
        ("Healthcare Practitioner", {"fieldname": "average_rating", "label": "Average Rating", "fieldtype": "Float", "read_only": 1, "insert_after": "home_visit_available"}),
        ("Healthcare Practitioner", {"fieldname": "total_reviews", "label": "Total Reviews", "fieldtype": "Int", "read_only": 1, "insert_after": "average_rating"}),
        ("Healthcare Practitioner", {"fieldname": "spoken_languages_text", "label": "Languages (comma-separated)", "fieldtype": "Small Text", "insert_after": "total_reviews"}),
        ("Healthcare Practitioner", {"fieldname": "qualifications_display", "label": "Qualifications for Public Display", "fieldtype": "Small Text", "insert_after": "spoken_languages_text"}),

        # Item Review DocType
        ("Item Review", {"fieldname": "verified_purchase", "label": "Verified Purchase", "fieldtype": "Check", "default": 1, "insert_after": "review_title"}),
        ("Item Review", {"fieldname": "seller_response", "label": "Seller Response", "fieldtype": "Text", "insert_after": "comment"}),
        ("Item Review", {"fieldname": "helpful_count", "label": "Helpful Votes", "fieldtype": "Int", "default": 0, "insert_after": "seller_response"}),
        ("Item Review", {"fieldname": "reviewer_region", "label": "Reviewer Region", "fieldtype": "Link", "options": "Ethiopian Region", "insert_after": "helpful_count"}),

        # Item Group DocType
        ("Item Group", {"fieldname": "category_slug", "label": "URL Slug", "fieldtype": "Data", "insert_after": "item_group_name"}),
        ("Item Group", {"fieldname": "category_icon", "label": "Category Icon", "fieldtype": "Data", "insert_after": "category_slug"}),
        ("Item Group", {"fieldname": "category_banner", "label": "Category Banner", "fieldtype": "Attach Image", "insert_after": "category_icon"}),
        ("Item Group", {"fieldname": "show_on_shop", "label": "Show on Shop", "fieldtype": "Check", "default": 1, "insert_after": "category_banner"}),
    ]

    for dt, fdef in fields_to_add:
        if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fdef["fieldname"]}):
            try:
                create_custom_field(dt, fdef, ignore_validate=True)
                print(f"  Created custom field: {dt}.{fdef['fieldname']}")
            except Exception as e:
                print(f"  Failed custom field: {dt}.{fdef['fieldname']}: {e}")

    for doctype in ["Item", "Company", "Healthcare Practitioner", "Item Review", "Item Group"]:
        try:
            frappe.db.updatedb(doctype)
        except Exception:
            pass
    frappe.db.commit()


def seed_ethiopian_regions():
    """Seed Ethiopian Region hierarchy — idempotent."""
    try:
        if not frappe.db.exists("DocType", "Ethiopian Region"):
            return

        if not frappe.db.exists("Ethiopian Region", "Ethiopia"):
            root = frappe.get_doc({
                "doctype": "Ethiopian Region",
                "region_name": "Ethiopia",
                "region_type": "Country",
                "is_group": 1,
                "latitude": 9.145,
                "longitude": 40.4896
            })
            root.insert(ignore_permissions=True)
            print("  Seeded Root: Ethiopia")

        regions_data = {
            "Addis Ababa": {
                "lat": 9.010, "lng": 38.761,
                "sub": ["Bole", "Yeka", "Kirkos", "Lideta", "Arada", "Gulele", "Kolfe Keranio", "Nifas Silk-Lafto", "Akaky Kaliti", "Addis Ketema", "Lemi Kura"]
            },
            "Oromia": {
                "lat": 8.54, "lng": 39.27,
                "sub": ["East Shewa", "West Shewa", "Jimma", "Adama", "Bishoftu", "Shashamane", "Nekemte", "Ambo"]
            },
            "Amhara": {
                "lat": 11.60, "lng": 37.38,
                "sub": ["Bahir Dar", "Gondar", "Dessie", "Debre Markos", "Debre Birhan", "Woldia"]
            },
            "Tigray": {
                "lat": 13.49, "lng": 39.47,
                "sub": ["Mekelle", "Axum", "Adwa", "Shire", "Alamata"]
            },
            "Sidama": {
                "lat": 6.80, "lng": 38.50,
                "sub": ["Hawassa", "Yirgalem", "Aleta Wendo"]
            },
            "Somali": {
                "lat": 6.34, "lng": 43.79,
                "sub": ["Jijiga", "Degehabur", "Gode", "Kebri Dahar"]
            },
            "Afar": {
                "lat": 11.75, "lng": 40.95,
                "sub": ["Semera", "Asaita", "Awash"]
            },
            "Benishangul-Gumuz": {
                "lat": 10.06, "lng": 34.54,
                "sub": ["Assosa", "Kamashi", "Metekel"]
            },
            "Gambela": {
                "lat": 8.25, "lng": 34.58,
                "sub": ["Gambela City", "Itang"]
            },
            "South West Ethiopia": {
                "lat": 7.00, "lng": 36.00,
                "sub": ["Bonga", "Mizan Aman", "Tepi"]
            },
            "Dire Dawa": {
                "lat": 9.59, "lng": 41.86,
                "sub": ["Dire Dawa City"]
            },
            "Harari": {
                "lat": 9.31, "lng": 42.12,
                "sub": ["Harar City"]
            }
        }

        for state_name, info in regions_data.items():
            if not frappe.db.exists("Ethiopian Region", state_name):
                state_doc = frappe.get_doc({
                    "doctype": "Ethiopian Region",
                    "region_name": state_name,
                    "parent_ethiopian_region": "Ethiopia",
                    "region_type": "State / Region",
                    "is_group": 1 if info["sub"] else 0,
                    "latitude": info["lat"],
                    "longitude": info["lng"]
                })
                state_doc.insert(ignore_permissions=True)
                print(f"  Seeded Region: {state_name}")

            for sub_name in info["sub"]:
                if not frappe.db.exists("Ethiopian Region", sub_name):
                    sub_doc = frappe.get_doc({
                        "doctype": "Ethiopian Region",
                        "region_name": sub_name,
                        "parent_ethiopian_region": state_name,
                        "region_type": "Sub-City / Zone",
                        "is_group": 0,
                        "latitude": info["lat"],
                        "longitude": info["lng"]
                    })
                    sub_doc.insert(ignore_permissions=True)

        frappe.db.commit()
        print("EthioBiz: Ethiopian Regions seeded successfully.")
    except Exception as e:
        print(f"EthioBiz: Error seeding Ethiopian Regions: {e}")
