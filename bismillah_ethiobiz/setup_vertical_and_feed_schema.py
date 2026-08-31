# -*- coding: utf-8 -*-
"""
BISMALLAH AR-RAHMAN AR-RAHIM
EthioBiz Smart Feed, User Interactions & Ad Management Schema Setup
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def setup_smart_feed_and_tracking_doctypes():
    """Create EthioBiz User Interaction & EthioBiz User Preference DocTypes idempotently."""
    print("--- [1/3] Provisioning User Interaction & Preference Tracking Schema ---")

    # 1. EthioBiz User Interaction
    if not frappe.db.exists("DocType", "EthioBiz User Interaction"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "EthioBiz User Interaction",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "is_submittable": 0,
            "track_changes": 0,
            "fields": [
                {"fieldname": "user", "label": "User", "fieldtype": "Data", "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "session_id", "label": "Session ID", "fieldtype": "Data"},
                {"fieldname": "col_break1", "fieldtype": "Column Break"},
                {"fieldname": "interaction_type", "label": "Interaction Type", "fieldtype": "Select",
                 "options": "view\nclick\ndwell\nlike\ncomment\nshare\ncart_add\nbook\ncall", "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "content_type", "label": "Content Type", "fieldtype": "Select",
                 "options": "product\nsocial_post\nblog\njob\ncourse\ndoctor\nfix_service\nhotel\nride\nad\nforum_topic", "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "sec_break1", "fieldtype": "Section Break", "label": "Content Details"},
                {"fieldname": "content_id", "label": "Content ID", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "content_category", "label": "Content Category", "fieldtype": "Data", "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "col_break2", "fieldtype": "Column Break"},
                {"fieldname": "content_company", "label": "Content Company", "fieldtype": "Link", "options": "Company"},
                {"fieldname": "dwell_time_ms", "label": "Dwell Time (ms)", "fieldtype": "Int", "default": 0},
                {"fieldname": "source_page", "label": "Source Page", "fieldtype": "Data"},
                {"fieldname": "timestamp", "label": "Timestamp", "fieldtype": "Datetime", "in_list_view": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1, "create": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: EthioBiz User Interaction")

    # 2. EthioBiz User Preference
    if not frappe.db.exists("DocType", "EthioBiz User Preference"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "EthioBiz User Preference",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "is_submittable": 0,
            "track_changes": 0,
            "fields": [
                {"fieldname": "user", "label": "User", "fieldtype": "Data", "in_list_view": 1, "unique": 1},
                {"fieldname": "interaction_count", "label": "Total Interactions", "fieldtype": "Int", "default": 0, "in_list_view": 1},
                {"fieldname": "col_break1", "fieldtype": "Column Break"},
                {"fieldname": "last_computed", "label": "Last Computed", "fieldtype": "Datetime", "in_list_view": 1},
                {"fieldname": "sec_break1", "fieldtype": "Section Break", "label": "Affinity Vectors"},
                {"fieldname": "preferred_categories", "label": "Category Affinities (JSON)", "fieldtype": "Code", "options": "JSON"},
                {"fieldname": "preferred_content_types", "label": "Content Type Affinities (JSON)", "fieldtype": "Code", "options": "JSON"},
                {"fieldname": "preferred_companies", "label": "Company Affinities (JSON)", "fieldtype": "Code", "options": "JSON"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: EthioBiz User Preference")

    frappe.db.commit()


def seed_universal_maintenance_categories():
    """Seed the 8 Universal Maintenance Categories."""
    print("--- [2/3] Seeding 8 Universal Maintenance Categories ---")
    if not frappe.db.exists("DocType", "BizService Category"):
        return

    categories = [
        {"name": "Electrical & Power", "icon": "⚡", "desc": "Domestic wiring, solar inverters, backup generators, circuit panels"},
        {"name": "Plumbing & Water", "icon": "🚿", "desc": "Leak repair, water pumps, pipefitting, drainage, water tank cleaning"},
        {"name": "HVAC & Appliances", "icon": "❄️", "desc": "Refrigeration, commercial cold rooms, AC, washing machines, ovens"},
        {"name": "Auto Mechanics", "icon": "🚗", "desc": "On-demand mobile mechanics, battery jumpstarts, tire change, computerized diagnostics"},
        {"name": "IT & Security", "icon": "💻", "desc": "Laptop/PC repairs, CCTV security systems, network cabling, PBX phones"},
        {"name": "Facility Maintenance", "icon": "🏢", "desc": "Office handyman, drywall, aluminum partitioning, masonry, door locks"},
        {"name": "Carpentry & Woodwork", "icon": "🪵", "desc": "Custom furniture repair, kitchen cabinets, door and window framing"},
        {"name": "Sanitation & Cleaning", "icon": "🧹", "desc": "Deep house cleaning, commercial fumigation, pest control, tank disinfection"}
    ]

    for cat in categories:
        if not frappe.db.exists("BizService Category", cat["name"]):
            doc = frappe.get_doc({
                "doctype": "BizService Category",
                "category_name": cat["name"],
                "category_icon": cat["icon"],
                "description": cat["desc"],
                "is_active": 1
            })
            doc.insert(ignore_permissions=True)
            print(f"  Seeded Maintenance Category: {cat['name']}")

    frappe.db.commit()


def seed_sample_vertical_records():
    """Seed sample doctors, maintenance services, and ad campaigns for complete test coverage."""
    print("--- [3/3] Seeding Sample Vertical Hub Data ---")
    
    # 1. Doctors
    specialties = [
        ("Dr. Sarah Ahmed", "Cardiology", 600.0, 400.0, 4.9, "St. Paul Hospital, Addis Ababa"),
        ("Dr. Dawit Mengistu", "Dermatology", 500.0, 350.0, 4.8, "Bole Medical Center, Addis Ababa"),
        ("Dr. Bethlehem Tadesse", "Pediatrics", 450.0, 300.0, 5.0, "Yekatit 12 Hospital, Addis Ababa"),
        ("Dr. Michael Girma", "Orthopedics", 700.0, 450.0, 4.7, "Black Lion Hospital, Addis Ababa"),
        ("Dr. Helen Kebede", "General Medicine", 400.0, 250.0, 4.9, "Kazanchis Clinic, Addis Ababa"),
        ("Dr. Yonas Bekele", "Dental", 550.0, 300.0, 4.8, "Piazza Dental Clinic, Addis Ababa")
    ]
    for name, dept, fee, tele_fee, rating, hosp in specialties:
        if not frappe.db.exists("Healthcare Practitioner", name):
            try:
                frappe.get_doc({
                    "doctype": "Healthcare Practitioner",
                    "first_name": name,
                    "department": dept,
                    "consultation_fee": fee,
                    "telehealth_fee": tele_fee,
                    "doctor_rating": rating,
                    "total_patient_reviews": 32,
                    "hospital_affiliation": hosp,
                    "show_on_booking": 1
                }).insert(ignore_permissions=True)
                print(f"  Seeded Doctor: {name} ({dept})")
            except Exception as e:
                pass

    # 2. Maintenance Services
    services = [
        ("FIX-ELEC-01", "Emergency Electrical & Generator Inspection", "Electrical & Power", 450.0, 60),
        ("FIX-PLUMB-01", "Water Leak Detection & Pipe Repair", "Plumbing & Water", 350.0, 45),
        ("FIX-HVAC-01", "AC & Commercial Cold Room Maintenance", "HVAC & Appliances", 600.0, 90),
        ("FIX-AUTO-01", "Mobile Roadside Engine Diagnostic", "Auto Mechanics", 500.0, 45),
        ("FIX-IT-01", "CCTV Security Camera Setup & PC Repair", "IT & Security", 400.0, 60),
        ("FIX-FACILITY-01", "Office Handyman & Aluminum Partitioning", "Facility Maintenance", 500.0, 120),
        ("FIX-WOOD-01", "Custom Kitchen Cabinet & Wood Restoration", "Carpentry & Woodwork", 550.0, 90),
        ("FIX-CLEAN-01", "Deep Fumigation & Post-Construction Cleaning", "Sanitation & Cleaning", 650.0, 180)
    ]
    for code, title, cat, price, dur in services:
        if not frappe.db.exists("BizService Listing", code):
            try:
                frappe.get_doc({
                    "doctype": "BizService Listing",
                    "name": code,
                    "service_title": title,
                    "category": cat,
                    "base_price": price,
                    "duration_minutes": dur,
                    "is_active": 1,
                    "is_emergency_dispatch": 1
                }).insert(ignore_permissions=True)
                print(f"  Seeded Maintenance Service: {title}")
            except Exception as e:
                pass

    # 3. Ad Campaigns
    ads = [
        ("CAMP-DIKKA-FLASH-SALE", "Dikka Shop 50% Tech Flash Sale", "https://ethiobiz.et/shop?category=Electronics", "/assets/bismillah_ethiobiz/img/walta_real_logo.png", 5000.0, 1000.0),
        ("CAMP-BIZHEALTH-CHECKUP", "Comprehensive Annual Health Checkup", "https://ethiobiz.et/bizhealth", "/assets/bismillah_ethiobiz/img/walta_real_logo.png", 4000.0, 800.0),
        ("CAMP-BIZFIX-EMERGENCY", "24/7 Certified Electrical & Plumbing Fix", "https://ethiobiz.et/bizfix", "/assets/bismillah_ethiobiz/img/walta_real_logo.png", 3000.0, 600.0)
    ]
    for name, title, url, img, total_b, daily_b in ads:
        if not frappe.db.exists("EthioBiz Ad Campaign", name):
            try:
                frappe.get_doc({
                    "doctype": "EthioBiz Ad Campaign",
                    "name": name,
                    "campaign_name": title,
                    "click_url": url,
                    "creative_image": img,
                    "status": "Active",
                    "impressions": 120,
                    "clicks": 18
                }).insert(ignore_permissions=True)
                print(f"  Seeded Ad Campaign: {title}")
            except Exception as e:
                pass

    frappe.db.commit()


if __name__ == "__main__":
    setup_smart_feed_and_tracking_doctypes()
    seed_universal_maintenance_categories()
    seed_sample_vertical_records()
    print("ALL VERTICAL & FEED SCHEMAS PROVISIONED SUCCESSFULLY ALHAMDULILLAH!")
