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
    Filters users based on the active session default company via
    Employee records and User Permissions.
    """
    try:
        # 1. Get the current active company
        active_company = frappe.defaults.get_user_default("Company")

        # 2. Find users belonging to this company
        if active_company:
            # From User Permission table
            user_perms = frappe.get_all(
                "User Permission",
                filters={"allow": "Company", "for_value": active_company},
                pluck="user",
            )

            # From Employee table
            employees = frappe.get_all(
                "Employee",
                filters={"company": active_company, "status": "Active"},
                pluck="user_id",
            )

            # Combine and deduplicate, excluding system accounts
            company_users = list(
                set((user_perms or []) + [e for e in (employees or []) if e])
                - {"Administrator", "Guest"}
            )

            if not company_users:
                company_users = ["__NO_MATCH__"]

            # 3. Fetch only company users who are active System Users
            users = frappe.get_all(
                "User",
                fields=["name as id", "full_name as value"],
                filters={
                    "name": ["in", company_users],
                    "allowed_in_mentions": True,
                    "user_type": "System User",
                    "enabled": True,
                },
            )
        else:
            # No company selected — show all mentionable users (standard behavior)
            users = frappe.get_all(
                "User",
                fields=["name as id", "full_name as value"],
                filters={
                    "name": ["not in", ("Administrator", "Guest")],
                    "allowed_in_mentions": True,
                    "user_type": "System User",
                    "enabled": True,
                },
            )

        # 4. Fetch User Groups (standard behavior)
        user_groups = frappe.cache.get_value("user_groups", get_user_groups)

        # 5. Filter by search term and format links
        filtered_mentions = []
        search_term = (search_term or "").lower()

        for mention_data in users + (user_groups or []):
            if search_term and search_term not in mention_data.get("value", "").lower():
                continue

            mention_data["link"] = frappe.utils.get_url_to_form(
                "User Group" if mention_data.get("is_group") else "User Profile",
                mention_data["id"],
            )
            filtered_mentions.append(mention_data)

        return sorted(filtered_mentions, key=lambda d: d.get("value", ""))

    except Exception:
        # Safety fallback: if anything fails, return standard unfiltered results
        frappe.log_error("Mentions Filter Error")
        from frappe.desk.search import get_names_for_mentions as original
        return original(search_term or "")
