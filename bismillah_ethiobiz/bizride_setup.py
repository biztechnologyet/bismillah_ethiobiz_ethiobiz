# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizRide Logistics & Delivery Setup
Bismillah Ar-Rahman Ar-Rahim

Creates all custom DocTypes for BizRide on-demand delivery (Rider profiles, Delivery trips, Settings, Wallet ledger).
"""

import frappe

def ensure_bizride_doctypes():
    """Ensure all BizRide Delivery & Logistics DocTypes exist."""
    try:
        print("EthioBiz: Ensuring BizRide Delivery DocTypes...")
        _create_bizride_surge_tier_doctype()
        _create_bizrider_doctype()
        _create_bizride_broadcast_log_doctype()
        _create_bizride_delivery_doctype()
        _create_bizrider_wallet_transaction_doctype()
        _create_bizride_settings_doctype()
        print("EthioBiz: BizRide Delivery DocTypes verified successfully.")
    except Exception as e:
        print(f"EthioBiz: Error setting up BizRide DocTypes: {e}")
        frappe.log_error(f"BizRide DocType setup error: {e}", "BizRide")


def _create_bizride_surge_tier_doctype():
    if not frappe.db.exists("DocType", "BizRide Surge Tier"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizRide Surge Tier",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "tier_name", "label": "Tier Name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "multiplier", "label": "Multiplier", "fieldtype": "Float", "default": 1.0, "in_list_view": 1},
                {"fieldname": "description", "label": "Trigger Description", "fieldtype": "Small Text", "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)


def _create_bizride_broadcast_log_doctype():
    if not frappe.db.exists("DocType", "BizRide Broadcast Log"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizRide Broadcast Log",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "rider", "label": "Rider", "fieldtype": "Link", "options": "BizRider", "in_list_view": 1},
                {"fieldname": "notified_at", "label": "Notified At", "fieldtype": "Datetime", "in_list_view": 1},
                {"fieldname": "response", "label": "Response", "fieldtype": "Select", "options": "Pending\nAccepted\nRejected\nTimeout", "default": "Pending", "in_list_view": 1},
                {"fieldname": "responded_at", "label": "Responded At", "fieldtype": "Datetime", "in_list_view": 1},
                {"fieldname": "distance_km", "label": "Distance (km)", "fieldtype": "Float", "in_list_view": 1}
            ],
            "permissions": []
        })
        doc.insert(ignore_permissions=True)


def _create_bizrider_wallet_transaction_doctype():
    if not frappe.db.exists("DocType", "BizRider Wallet Transaction"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizRider Wallet Transaction",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "autoname": "WAL-TX-.YYYY.-.#####",
            "fields": [
                {"fieldname": "rider", "label": "Rider", "fieldtype": "Link", "options": "BizRider", "reqd": 1, "in_list_view": 1},
                {"fieldname": "transaction_type", "label": "Type", "fieldtype": "Select", "options": "Earning\nWithdrawal\nCommission Deduction\nBonus\nPenalty\nCOD Collection", "reqd": 1, "in_list_view": 1},
                {"fieldname": "amount", "label": "Amount (ETB)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "delivery", "label": "Related Delivery", "fieldtype": "Link", "options": "BizRide Delivery", "in_list_view": 1},
                {"fieldname": "balance_after", "label": "Balance After (ETB)", "fieldtype": "Currency", "in_list_view": 1},
                {"fieldname": "description", "label": "Description", "fieldtype": "Data"},
                {"fieldname": "payout_reference", "label": "Payout Reference (Telebirr/Bank)", "fieldtype": "Data"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: BizRider Wallet Transaction")


def _create_bizrider_doctype():
    if not frappe.db.exists("DocType", "BizRider"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizRider",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "autoname": "RIDER-.#####",
            "fields": [
                {"fieldname": "rider_name", "label": "Full Name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "phone", "label": "Mobile Phone", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "email", "label": "Email Address", "fieldtype": "Data"},
                {"fieldname": "vehicle_type", "label": "Vehicle Type", "fieldtype": "Select", "options": "Bajaj\nMotorcycle\nCar\nPickup Truck\nTruck", "default": "Motorcycle", "in_list_view": 1},
                {"fieldname": "vehicle_plate", "label": "License Plate", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Available\nOn Delivery\nOffline\nSuspended", "default": "Offline", "in_list_view": 1},
                {"fieldname": "verification_status", "label": "Verification", "fieldtype": "Select", "options": "Pending\nVerified\nRejected", "default": "Pending", "in_list_view": 1},
                {"fieldname": "wallet_balance", "label": "Wallet Balance (ETB)", "fieldtype": "Currency", "default": 0.0, "in_list_view": 1},
                {"fieldname": "average_rating", "label": "Rating", "fieldtype": "Float", "default": 5.0, "read_only": 1},
                {"fieldname": "total_deliveries", "label": "Total Deliveries", "fieldtype": "Int", "default": 0, "read_only": 1},
                {"fieldname": "ethiopian_region", "label": "Operating Region", "fieldtype": "Link", "options": "Ethiopian Region"},
                {"fieldname": "geo_section", "label": "Live Location", "fieldtype": "Section Break"},
                {"fieldname": "current_latitude", "label": "Current Latitude", "fieldtype": "Float"},
                {"fieldname": "current_longitude", "label": "Current Longitude", "fieldtype": "Float"},
                {"fieldname": "last_location_update", "label": "Last Location Update", "fieldtype": "Datetime"},
                {"fieldname": "docs_section", "label": "Verification Documents", "fieldtype": "Section Break"},
                {"fieldname": "license_number", "label": "Driver License Number", "fieldtype": "Data"},
                {"fieldname": "license_photo", "label": "License Photo", "fieldtype": "Attach Image"},
                {"fieldname": "id_photo", "label": "National ID Photo", "fieldtype": "Attach Image"},
                {"fieldname": "vehicle_photo", "label": "Vehicle Photo", "fieldtype": "Attach Image"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1, "create": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: BizRider")


def _create_bizride_delivery_doctype():
    if not frappe.db.exists("DocType", "BizRide Delivery"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizRide Delivery",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "autoname": "BIZRIDE-.YYYY.-.#####",
            "fields": [
                {"fieldname": "order_reference", "label": "Order Reference", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "order_doctype", "label": "Order DocType", "fieldtype": "Link", "options": "DocType"},
                {"fieldname": "seller_company", "label": "Seller / Origin Company", "fieldtype": "Link", "options": "Company", "reqd": 1, "in_list_view": 1},
                {"fieldname": "seller_contact_phone", "label": "Seller Phone", "fieldtype": "Data"},
                {"fieldname": "buyer_name", "label": "Recipient Name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "buyer_phone", "label": "Recipient Phone", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
                {"fieldname": "assigned_rider", "label": "Assigned Rider", "fieldtype": "Link", "options": "BizRider", "in_list_view": 1},
                {"fieldname": "vehicle_type_required", "label": "Vehicle Type Required", "fieldtype": "Select", "options": "Any\nBajaj\nMotorcycle\nCar\nTruck", "default": "Any"},
                {"fieldname": "status", "label": "Delivery Status", "fieldtype": "Select", "options": "Pending Broadcast\nBroadcasting\nRider Assigned\nPickup In Progress\nPicked Up\nIn Transit\nDelivered\nCancelled\nFailed", "default": "Pending Broadcast", "in_list_view": 1},
                {"fieldname": "route_section", "label": "Route & Geolocation", "fieldtype": "Section Break"},
                {"fieldname": "pickup_address", "label": "Pickup Address", "fieldtype": "Small Text"},
                {"fieldname": "delivery_address", "label": "Delivery Address", "fieldtype": "Small Text"},
                {"fieldname": "pickup_latitude", "label": "Pickup Latitude", "fieldtype": "Float"},
                {"fieldname": "pickup_longitude", "label": "Pickup Longitude", "fieldtype": "Float"},
                {"fieldname": "delivery_latitude", "label": "Delivery Latitude", "fieldtype": "Float"},
                {"fieldname": "delivery_longitude", "label": "Delivery Longitude", "fieldtype": "Float"},
                {"fieldname": "distance_km", "label": "Distance (km)", "fieldtype": "Float", "in_list_view": 1},
                {"fieldname": "estimated_duration_minutes", "label": "Estimated Duration (Mins)", "fieldtype": "Int"},
                {"fieldname": "pricing_section", "label": "Pricing & Settlement", "fieldtype": "Section Break"},
                {"fieldname": "delivery_fee", "label": "Total Delivery Fee (ETB)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "rider_earning", "label": "Rider Earning (ETB)", "fieldtype": "Currency"},
                {"fieldname": "platform_commission", "label": "Platform Commission (ETB)", "fieldtype": "Currency"},
                {"fieldname": "payment_to_rider_status", "label": "Rider Payout Status", "fieldtype": "Select", "options": "Pending\nPaid\nSettled", "default": "Pending"},
                {"fieldname": "is_cod", "label": "Is COD Cash Collection", "fieldtype": "Check", "default": 0},
                {"fieldname": "cod_amount", "label": "COD Amount to Collect (ETB)", "fieldtype": "Currency", "default": 0.0},
                {"fieldname": "cod_collected", "label": "COD Cash Collected", "fieldtype": "Check", "default": 0},
                {"fieldname": "security_section", "label": "Verification & Proof", "fieldtype": "Section Break"},
                {"fieldname": "pickup_otp", "label": "Pickup OTP", "fieldtype": "Data"},
                {"fieldname": "delivery_otp", "label": "Delivery OTP", "fieldtype": "Data"},
                {"fieldname": "pickup_photo", "label": "Pickup Photo Proof", "fieldtype": "Attach Image"},
                {"fieldname": "delivery_photo", "label": "Delivery Photo Proof", "fieldtype": "Attach Image"},
                {"fieldname": "buyer_rating_for_rider", "label": "Buyer Rating", "fieldtype": "Rating"},
                {"fieldname": "rider_rating_for_buyer", "label": "Rider Rating", "fieldtype": "Rating"},
                {"fieldname": "broadcast_logs", "label": "Broadcast History", "fieldtype": "Table", "options": "BizRide Broadcast Log"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1, "write": 1, "create": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: BizRide Delivery")


def _create_bizride_settings_doctype():
    if not frappe.db.exists("DocType", "BizRide Settings"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "BizRide Settings",
            "module": "Ethiobiz Theme",
            "custom": 1,
            "issingle": 1,
            "fields": [
                {"fieldname": "fares_section", "label": "Base Fares & Rates", "fieldtype": "Section Break"},
                {"fieldname": "base_fare_bajaj", "label": "Base Fare - Bajaj (ETB)", "fieldtype": "Currency", "default": 50.0},
                {"fieldname": "base_fare_motorcycle", "label": "Base Fare - Motorcycle (ETB)", "fieldtype": "Currency", "default": 60.0},
                {"fieldname": "base_fare_car", "label": "Base Fare - Car (ETB)", "fieldtype": "Currency", "default": 100.0},
                {"fieldname": "base_fare_truck", "label": "Base Fare - Truck (ETB)", "fieldtype": "Currency", "default": 250.0},
                {"fieldname": "per_km_rate", "label": "Per Kilometer Rate (ETB)", "fieldtype": "Currency", "default": 20.0},
                {"fieldname": "per_minute_rate", "label": "Per Minute Rate (ETB)", "fieldtype": "Currency", "default": 2.0},
                {"fieldname": "platform_commission_percent", "label": "Platform Commission (%)", "fieldtype": "Percent", "default": 15.0},
                {"fieldname": "dispatch_section", "label": "Dispatch Rules", "fieldtype": "Section Break"},
                {"fieldname": "broadcast_radius_km", "label": "Initial Search Radius (km)", "fieldtype": "Float", "default": 5.0},
                {"fieldname": "broadcast_timeout_seconds", "label": "Offer Timeout (Seconds)", "fieldtype": "Int", "default": 15},
                {"fieldname": "max_broadcast_rounds", "label": "Max Candidate Rounds", "fieldtype": "Int", "default": 5},
                {"fieldname": "radius_expansion_km", "label": "Radius Expansion per Round (km)", "fieldtype": "Float", "default": 2.0},
                {"fieldname": "cod_collection_enabled", "label": "Allow Cash on Delivery Collection", "fieldtype": "Check", "default": 1},
                {"fieldname": "surge_tiers", "label": "Surge Pricing Tiers", "fieldtype": "Table", "options": "BizRide Surge Tier"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("  Created DocType: BizRide Settings")
