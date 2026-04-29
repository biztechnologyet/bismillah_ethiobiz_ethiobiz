# -*- coding: utf-8 -*-
"""
EthioBiz Multi-Company Setup
Bismillah Ar-Rahman Ar-Rahim

Called after migrate to ensure all custom fields and property setters
are properly created for multi-company isolation.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from bismillah_ethiobiz.multi_company import get_custom_fields, get_property_setters


def after_migrate():
    """Called after bench migrate to apply multi-company custom fields and property setters."""
    try:
        print("EthioBiz: Applying multi-company isolation fields...")
        setup_custom_fields()
        setup_property_setters()
        update_existing_records()
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
    create_custom_fields(custom_fields, update=True)
    print(f"  Custom fields created/updated successfully.")


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
                frappe.make_property_setter(ps, validate_fields_for_doctype=False)
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
            
            # Count and update records with NULL company
            count = frappe.db.sql(
                f"SELECT COUNT(*) FROM `{table_name}` WHERE company IS NULL OR company = ''",
                as_list=True
            )[0][0]
            
            if count > 0:
                frappe.db.sql(
                    f"UPDATE `{table_name}` SET company = %s WHERE company IS NULL OR company = ''",
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
