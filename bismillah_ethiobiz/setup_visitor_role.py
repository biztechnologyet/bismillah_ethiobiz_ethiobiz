import frappe

def setup_website_member_role():
    """Creates Website Member role with social/LMS access and blocks Desk."""
    frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()

    if not frappe.db.exists("Role", "Website Member"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Website Member",
            "desk_access": 0,
            "is_custom": 1
        })
        role.insert(ignore_permissions=True)
        print("Created Role: Website Member")
    else:
        print("Role Website Member already exists")

    # Configure Custom DocPerm entries
    social_doctypes = ["Afocha Post", "Afocha Comment", "AF Social Follow", "AF Social Share", "LMS Course", "LMS Lesson"]
    for dt in social_doctypes:
        if frappe.db.exists("DocType", dt):
            existing = frappe.db.get_value("Custom DocPerm", {"parent": dt, "role": "Website Member"}, "name")
            if not existing:
                perm = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": dt,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": "Website Member",
                    "read": 1,
                    "write": 1 if "LMS" not in dt else 0,
                    "create": 1 if "LMS" not in dt else 0
                })
                perm.insert(ignore_permissions=True)
                print(f"Set permissions for Website Member on {dt}")

    # Set Guest permissions on Lead for trial signup
    if frappe.db.exists("DocType", "Lead"):
        guest_lead = frappe.db.get_value("Custom DocPerm", {"parent": "Lead", "role": "Guest"}, "name")
        if not guest_lead:
            try:
                g_perm = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": "Lead",
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": "Guest",
                    "read": 1,
                    "create": 1,
                    "write": 0
                })
                g_perm.insert(ignore_permissions=True)
                print("Set Guest permissions on Lead")
            except Exception as e:
                print(f"Guest perm notice: {e}")

    frappe.db.commit()
    print("Role & Permission Setup Completed Successfully!")

if __name__ == "__main__":
    setup_website_member_role()
