# -*- coding: utf-8 -*-
"""
EthioBiz Custom Mentions Logic
Bismillah Ar-Rahman Ar-Rahim

Overrides standard Frappe mention behavior to restrict the @mention user list
to users belonging to the current user's active session company.
"""

import frappe
from frappe.desk.search import get_user_groups

@frappe.whitelist()
def get_names_for_mentions(search_term=""):
    """
    Custom replacement for frappe.desk.search.get_names_for_mentions.
    Filters users based on the active session default company.
    """
    # 1. Get the current active company
    active_company = frappe.defaults.get_user_default("Company")
    
    # 2. Build standard filters for the User query
    filters = {
        "name": ["not in", ("Administrator", "Guest")],
        "allowed_in_mentions": True,
        "user_type": "System User",
        "enabled": True,
    }
    
    # Apply company filter safely
    if active_company:
        # Find users explicitly permitted to this company
        user_perms = frappe.get_all("User Permission", filters={"allow": "Company", "for_value": active_company}, pluck="user")
        
        # Find users linked via active Employee records for this company
        employees = frappe.get_all("Employee", filters={"company": active_company, "status": "Active"}, pluck="user_id")
        
        # Combine valid users
        company_users = set((user_perms or []) + [e for e in (employees or []) if e])
        
        if company_users:
            filters["name"] = ["in", list(company_users)]
        else:
            # If no users belong to the company, return none
            filters["name"] = ["in", ["_NO_USERS_FOUND_"]]
        
    # 3. Fetch filtered users directly from DB (bypassing the global cache)
    users = frappe.get_all(
        "User",
        fields=["name as id", "full_name as value"],
        filters=filters
    )
    
    # 4. Fetch User Groups (standard behavior)
    user_groups = frappe.cache().get_value("user_groups", get_user_groups)
    
    # 5. Filter by search term and format links
    filtered_mentions = []
    search_term = (search_term or "").lower()
    
    for mention_data in users + (user_groups or []):
        if search_term not in mention_data.get("value", "").lower():
            continue

        mention_data["link"] = frappe.utils.get_url_to_form(
            "User Group" if mention_data.get("is_group") else "User Profile", mention_data["id"]
        )
        filtered_mentions.append(mention_data)

    return sorted(filtered_mentions, key=lambda d: d.get("value", ""))
