# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizBooking & Universal Service Setup
Bismillah Ar-Rahman Ar-Rahim

Creates all custom DocTypes for universal multi-vertical service booking (Salons, Spas, Technicians, etc.).
"""

import frappe

def ensure_booking_doctypes():
    """Ensure all BizService Universal Booking DocTypes exist."""
    try:
        print("EthioBiz: Ensuring BizService Universal Booking DocTypes...")
        _create_bizservice_image_doctype()
        _create_bizservice_practitioner_doctype()
        _create_bizservice_booking_field_doctype()
        _create_bizservice_category_doctype()
        _create_bizservice_listing_doctype()
        _create_bizservice_booking_doctype()
        _seed_default_service_categories()
        print("EthioBiz: BizService Booking DocTypes verified successfully.")
    except Exception as e:
        print(f"EthioBiz: Error setting up BizBooking DocTypes: {e}")
        frappe.log_error(f"BizBooking DocType setup error: {e}", "BizBooking")


def _create_bizservice_image_doctype():
    if not frappe.db.exists("DocType", "BizService Image"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizService Image",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "image", "label": "Image", "fieldtype": "Attach Image", "reqd": 1},
                {"fieldname": "caption", "label": "Caption", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "is_primary", "label": "Primary", "fieldtype": "Check", "default": 0, "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)


def _create_bizservice_practitioner_doctype():
    if not frappe.db.exists("DocType", "BizService Practitioner"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizService Practitioner",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "practitioner_name", "label": "Professional Name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "role_title", "label": "Role / Specialty", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "phone", "label": "Phone Number", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "is_active", "label": "Active", "fieldtype": "Check", "default": 1, "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)


def _create_bizservice_booking_field_doctype():
    if not frappe.db.exists("DocType", "BizService Booking Field"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizService Booking Field",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "field_label", "label": "Field Label", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "field_type", "label": "Type", "fieldtype": "Select", "options": "Data\nSelect\nCheck\nSmall Text\nDate", "default": "Data", "in_list_view": 1},
                {"fieldname": "field_options", "label": "Options", "fieldtype": "Small Text", "in_list_view": 1},
                {"fieldname": "is_mandatory", "label": "Mandatory", "fieldtype": "Check", "default": 0, "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)


def _create_bizservice_category_doctype():
    if not frappe.db.exists("DocType", "BizService Category"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizService Category",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "autoname": "field:category_name",
            "fields": [
                {"fieldname": "category_name", "label": "Category Name", "fieldtype": "Data", "reqd": 1, "unique": 1},
                {"fieldname": "category_icon", "label": "Icon Class / Emoji", "fieldtype": "Data"},
                {"fieldname": "slug", "label": "URL Slug", "fieldtype": "Data"},
                {"fieldname": "parent_category", "label": "Parent Category", "fieldtype": "Link", "options": "BizService Category"},
                {"fieldname": "is_active", "label": "Is Active", "fieldtype": "Check", "default": 1},
                {"fieldname": "description", "label": "Description", "fieldtype": "Small Text"},
                {"fieldname": "booking_fields_section", "label": "Custom Booking Form Fields", "fieldtype": "Section Break"},
                {"fieldname": "booking_fields", "label": "Booking Fields", "fieldtype": "Table", "options": "BizService Booking Field"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: BizService Category")


def _create_bizservice_listing_doctype():
    if not frappe.db.exists("DocType", "BizService Listing"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizService Listing",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "autoname": "BIZ-SRV-.#####",
            "fields": [
                {"fieldname": "service_name", "label": "Service Name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1, "in_list_view": 1},
                {"fieldname": "category", "label": "Service Category", "fieldtype": "Link", "options": "BizService Category", "reqd": 1, "in_list_view": 1},
                {"fieldname": "slug", "label": "URL Slug", "fieldtype": "Data"},
                {"fieldname": "price", "label": "Price (ETB)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "price_type", "label": "Price Type", "fieldtype": "Select", "options": "Fixed\nStarting From\nHourly\nCustom Quote", "default": "Fixed"},
                {"fieldname": "duration_minutes", "label": "Duration (Minutes)", "fieldtype": "Int", "default": 30},
                {"fieldname": "requires_travel", "label": "Requires Travel (Home Dispatch via BizRide)", "fieldtype": "Check", "default": 0},
                {"fieldname": "average_rating", "label": "Average Rating", "fieldtype": "Float", "read_only": 1},
                {"fieldname": "total_bookings", "label": "Total Bookings", "fieldtype": "Int", "read_only": 1, "default": 0},
                {"fieldname": "is_active", "label": "Active", "fieldtype": "Check", "default": 1},
                {"fieldname": "details_section", "label": "Details & Description", "fieldtype": "Section Break"},
                {"fieldname": "description", "label": "Description", "fieldtype": "Text Editor"},
                {"fieldname": "images", "label": "Service Gallery", "fieldtype": "Table", "options": "BizService Image"},
                {"fieldname": "practitioners", "label": "Assigned Staff", "fieldtype": "Table", "options": "BizService Practitioner"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: BizService Listing")


def _create_bizservice_booking_doctype():
    if not frappe.db.exists("DocType", "BizService Booking"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizService Booking",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "autoname": "BIZSVC-.YYYY.-.#####",
            "fields": [
                {"fieldname": "customer_name", "label": "Customer Name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "customer_phone", "label": "Customer Phone", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "customer_email", "label": "Customer Email", "fieldtype": "Data"},
                {"fieldname": "service", "label": "Service", "fieldtype": "Link", "options": "BizService Listing", "reqd": 1, "in_list_view": 1},
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1, "in_list_view": 1},
                {"fieldname": "practitioner_name", "label": "Assigned Professional", "fieldtype": "Data"},
                {"fieldname": "booking_date", "label": "Booking Date", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
                {"fieldname": "booking_time", "label": "Booking Time", "fieldtype": "Time", "reqd": 1, "in_list_view": 1},
                {"fieldname": "duration_minutes", "label": "Duration (Mins)", "fieldtype": "Int", "default": 30},
                {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Pending\nConfirmed\nIn-Progress\nCompleted\nCancelled\nNo-Show", "default": "Pending", "in_list_view": 1},
                {"fieldname": "payment_status", "label": "Payment Status", "fieldtype": "Select", "options": "Unpaid\nPartial\nPaid\nRefunded", "default": "Unpaid", "in_list_view": 1},
                {"fieldname": "total_amount", "label": "Total Amount (ETB)", "fieldtype": "Currency", "reqd": 1},
                {"fieldname": "customer_address", "label": "Customer Address (for Home Visit)", "fieldtype": "Small Text"},
                {"fieldname": "customer_notes", "label": "Customer Notes / Requests", "fieldtype": "Small Text"},
                {"fieldname": "bizride_delivery", "label": "Linked BizRide Dispatch", "fieldtype": "Link", "options": "BizRide Delivery"},
                {"fieldname": "rating", "label": "Customer Rating", "fieldtype": "Rating"},
                {"fieldname": "review", "label": "Customer Review", "fieldtype": "Small Text"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1, "create": 1, "write": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: BizService Booking")


def _seed_default_service_categories():
    categories = [
        {"name": "Beauty, Salon & Spa", "icon": "💇", "slug": "beauty-salon-spa", "desc": "Haircuts, styling, spa, massages, manicures and facial treatments"},
        {"name": "Healthcare & Clinics", "icon": "🩺", "slug": "healthcare-clinics", "desc": "Doctor consultations, dental, optical and medical specialists"},
        {"name": "Hotels & Stays", "icon": "🏨", "slug": "hotels-stays", "desc": "Hotel rooms, motels, resorts and guest house bookings"},
        {"name": "Auto & Vehicle Care", "icon": "🚗", "slug": "auto-vehicle-care", "desc": "Car wash, mechanics, oil change, tire and auto diagnostic services"},
        {"name": "Home Maintenance & Repairs", "icon": "🔧", "slug": "home-repairs", "desc": "Plumbing, electrical, painting, cleaning and carpentry"},
        {"name": "Professional & Legal", "icon": "⚖️", "slug": "professional-legal", "desc": "Legal consultations, accounting, business consulting and translation"},
        {"name": "Tutoring & Education", "icon": "📚", "slug": "tutoring-education", "desc": "Private tutoring, language classes, Quran lessons and music training"},
        {"name": "Events & Photography", "icon": "📸", "slug": "events-photography", "desc": "Photographers, videographers, DJs, caterers and event planners"}
    ]
    for c in categories:
        if not frappe.db.exists("BizService Category", c["name"]):
            cat_doc = frappe.get_doc({
                "doctype": "BizService Category",
                "category_name": c["name"],
                "category_icon": c["icon"],
                "slug": c["slug"],
                "description": c["desc"],
                "is_active": 1
            })
            cat_doc.insert(ignore_permissions=True)
    frappe.db.commit()
