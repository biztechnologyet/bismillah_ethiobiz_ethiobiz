# -*- coding: utf-8 -*-
"""
EthioBiz Multi-Company Setup
Bismillah Ar-Rahman Ar-Rahim

Called after migrate to ensure all custom fields and property setters
are properly created for multi-company isolation.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from bismillah_ethiobiz.multi_company import get_custom_fields, get_property_setters


def after_migrate():
    """Called after bench migrate to apply multi-company custom fields and property setters."""
    try:
        print("EthioBiz: Applying multi-company isolation fields...")
        fix_bad_defaults()
        setup_custom_fields()
        setup_property_setters()
        update_existing_records()
        setup_user_telegram_field()
        print("EthioBiz: Multi-company isolation setup complete.")
    except Exception as e:
        print(f"EthioBiz: Error in multi-company setup: {e}")
        frappe.log_error(f"Multi-company setup error: {e}", "EthioBiz Multi-Company")


def setup_custom_fields():
    """Create custom 'company' fields on all DocTypes that need them."""
    custom_fields = get_custom_fields()
    
    if not custom_fields:
        return
    
    print(f"  Creating custom fields for {len(custom_fields)} DocTypes...")
    # This creates/updates the records in tabCustom Field
    create_custom_field_api = __import__("frappe.custom.doctype.custom_field.custom_field", fromlist=["create_custom_fields"]).create_custom_fields
    create_custom_field_api(custom_fields, update=True)
    
    # Force schema update to ensure the column is actually created in the DB table
    count = 0
    for doctype in custom_fields.keys():
        try:
            frappe.db.updatedb(doctype)
            count += 1
        except Exception as e:
            print(f"  Failed to update db schema for {doctype}: {e}")
            
    print(f"  {count} Custom fields schema updated successfully.")


def setup_property_setters():
    """Create Property Setters to enforce company default on native fields."""
    property_setters = get_property_setters()
    
    if not property_setters:
        return
    
    count = 0
    for ps in property_setters:
        try:
            # Check if this property setter already exists
            existing = frappe.db.exists("Property Setter", {
                "doc_type": ps["doc_type"],
                "field_name": ps["field_name"],
                "property": ps["property"],
            })
            
            if existing:
                # Update value if different
                current_value = frappe.db.get_value("Property Setter", existing, "value")
                if current_value != ps["value"]:
                    frappe.db.set_value("Property Setter", existing, "value", ps["value"])
                    count += 1
            else:
                frappe.make_property_setter({
                    "doctype_or_field": "DocField",
                    "doc_type": ps["doc_type"],
                    "field_name": ps["field_name"],
                    "property": ps["property"],
                    "value": ps["value"],
                    "property_type": ps["property_type"],
                    "is_system_generated": 0
                }, validate_fields_for_doctype=False)
                count += 1
        except Exception as e:
            # Skip silently - some DocTypes may not exist on this site
            pass
    
    frappe.db.commit()
    print(f"  Property setters: {count} created/updated out of {len(property_setters)} total.")


def update_existing_records():
    """Update existing records that have a newly added company field with NULL value."""
    custom_fields = get_custom_fields()
    default_company = "Biz Technology Solutions"
    
    # Verify the default company exists
    if not frappe.db.exists("Company", default_company):
        print(f"  WARNING: Default company '{default_company}' not found. Skipping record updates.")
        return
    
    total_updated = 0
    
    for dt_name in custom_fields:
        try:
            table_name = f"tab{dt_name}"
            
            # Check if the column exists in the table
            columns = frappe.db.sql(f"SHOW COLUMNS FROM `{table_name}` LIKE 'company'")
            if not columns:
                continue
            
            # Count and update records with NULL or 'Company'
            count = frappe.db.sql(
                f"SELECT COUNT(*) FROM `{table_name}` WHERE company IS NULL OR company = '' OR company = 'Company'",
                as_list=True
            )[0][0]
            
            if count > 0:
                frappe.db.sql(
                    f"UPDATE `{table_name}` SET company = %s WHERE company IS NULL OR company = '' OR company = 'Company'",
                    (default_company,)
                )
                total_updated += count
                print(f"  Updated {count} records in {dt_name}")
                
        except Exception:
            # Table may not exist, skip
            pass
    
    if total_updated > 0:
        frappe.db.commit()
        print(f"  Total existing records updated: {total_updated}")
    else:
        print(f"  No existing records needed updating.")


def fix_bad_defaults():
    """
    Fix property setters and custom fields that have default='Company'
    (literal string). These should be empty so Frappe falls through to
    frappe.defaults.get_user_default('company').
    """
    # Fix property setters
    ps_list = frappe.db.sql(
        "SELECT name, doc_type FROM `tabProperty Setter` "
        "WHERE field_name='company' AND property='default' AND value='Company'",
        as_dict=True
    )
    for ps in ps_list:
        frappe.db.set_value("Property Setter", ps.name, "value", "")
        print(f"  Fixed Property Setter: {ps.doc_type}.company default → ''")

    # Fix custom fields
    cf_list = frappe.db.sql(
        "SELECT name, dt FROM `tabCustom Field` "
        "WHERE fieldname='company' AND `default`='Company'",
        as_dict=True
    )
    for cf in cf_list:
        frappe.db.set_value("Custom Field", cf.name, "default", "")
        print(f"  Fixed Custom Field: {cf.dt}.company default → ''")

    if ps_list or cf_list:
        frappe.db.commit()
        print(f"  Fixed {len(ps_list)} property setters + {len(cf_list)} custom fields")
    else:
        print("  No bad defaults found.")


def setup_user_telegram_field():
    """Create the telegram_username custom field on the User doctype if missing."""
    if frappe.db.exists("Custom Field", {"dt": "User", "fieldname": "telegram_username"}):
        print("  telegram_username field already exists.")
        return

    create_custom_field(
        "User",
        {
            "fieldname": "telegram_username",
            "label": "Telegram Username",
            "fieldtype": "Data",
            "insert_after": "mobile_no",
            "no_copy": 1,
            "in_list_view": 0,
            "in_standard_filter": 0,
        },
        ignore_validate=True,
    )
    frappe.db.updatedb("User")
    frappe.db.commit()
    print("  Created telegram_username field on User.")
