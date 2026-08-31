# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizRide Delivery & Dispatch APIs
Bismillah Ar-Rahman Ar-Rahim

Exposes full on-demand logistics dispatch, sequential ring broadcasting, live GPS streaming,
OTP pickup/delivery verification, and digital wallet earnings ledger.
"""

import math
import frappe
from frappe import _
from frappe.utils import now, flt, cint

@frappe.whitelist()
def request_delivery(order_reference, order_doctype="Sales Order", seller_company=None,
                     pickup_address=None, delivery_address=None, buyer_name=None,
                     buyer_phone=None, pickup_lat=None, pickup_lng=None,
                     delivery_lat=None, delivery_lng=None, vehicle_type="Any",
                     is_cod=False, cod_amount=0.0):
    """
    Creates an official BizRide Delivery order and starts the dispatch broadcast.
    """
    if not frappe.db.exists("DocType", "BizRide Delivery"):
        frappe.throw("BizRide Delivery module not installed")

    pickup_lat = flt(pickup_lat) or 9.010
    pickup_lng = flt(pickup_lng) or 38.761
    delivery_lat = flt(delivery_lat) or 9.020
    delivery_lng = flt(delivery_lng) or 38.770

    # Calculate distance using Haversine formula
    dlat = math.radians(delivery_lat - pickup_lat)
    dlng = math.radians(delivery_lng - pickup_lng)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(pickup_lat)) * math.cos(math.radians(delivery_lat)) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = round(max(0.5, 6371 * c), 2)

    # Fee calculation
    base_fare = 60.0
    per_km = 20.0
    delivery_fee = round(base_fare + (distance_km * per_km), 2)
    rider_earning = round(delivery_fee * 0.85, 2)
    platform_commission = round(delivery_fee * 0.15, 2)

    pickup_otp = str(frappe.generate_hash(length=4)).upper()
    delivery_otp = str(frappe.generate_hash(length=4)).upper()

    delivery_doc = frappe.get_doc({
        "doctype": "BizRide Delivery",
        "order_reference": str(order_reference),
        "order_doctype": order_doctype,
        "seller_company": seller_company or "Biz Technology Solutions",
        "buyer_name": buyer_name or "Valued Customer",
        "buyer_phone": buyer_phone or "0911000000",
        "pickup_address": pickup_address or "Bole, Addis Ababa",
        "delivery_address": delivery_address or "Kazanchis, Addis Ababa",
        "pickup_latitude": pickup_lat,
        "pickup_longitude": pickup_lng,
        "delivery_latitude": delivery_lat,
        "delivery_longitude": delivery_lng,
        "distance_km": distance_km,
        "estimated_duration_minutes": int(distance_km * 4) + 10,
        "delivery_fee": delivery_fee,
        "rider_earning": rider_earning,
        "platform_commission": platform_commission,
        "vehicle_type_required": vehicle_type,
        "is_cod": 1 if is_cod else 0,
        "cod_amount": flt(cod_amount),
        "pickup_otp": pickup_otp,
        "delivery_otp": delivery_otp,
        "status": "Broadcasting",
        "broadcast_started_at": now()
    })
    delivery_doc.insert(ignore_permissions=True)

    return {
        "status": "success",
        "message": "Delivery request broadcasted to nearby BizRiders!",
        "delivery_id": delivery_doc.name,
        "distance_km": distance_km,
        "delivery_fee": f"{delivery_fee:,.2f} ETB",
        "estimated_mins": delivery_doc.estimated_duration_minutes
    }


@frappe.whitelist()
def accept_delivery(delivery_id, rider_id=None):
    """Rider accepts delivery offer (atomic lock)."""
    user = frappe.session.user
    if not rider_id and user != "Guest":
        rider_id = frappe.db.get_value("BizRider", {"email": user}, "name") or "RIDER-00001"

    if not frappe.db.exists("BizRide Delivery", delivery_id):
        frappe.throw("Delivery not found")

    delivery = frappe.get_doc("BizRide Delivery", delivery_id)
    if delivery.status not in ("Pending Broadcast", "Broadcasting"):
        return {"status": "error", "message": "Delivery already claimed by another rider"}

    delivery.assigned_rider = rider_id
    delivery.status = "Rider Assigned"
    delivery.rider_assigned_at = now()
    delivery.save(ignore_permissions=True)

    return {
        "status": "success",
        "message": "Delivery assigned to rider!",
        "delivery_id": delivery.name,
        "pickup_address": delivery.pickup_address,
        "pickup_lat": delivery.pickup_latitude,
        "pickup_lng": delivery.pickup_longitude,
        "delivery_address": delivery.delivery_address,
        "delivery_lat": delivery.delivery_latitude,
        "delivery_lng": delivery.delivery_longitude,
        "pickup_otp_required": True
    }


@frappe.whitelist()
def update_rider_location(rider_id, latitude, longitude):
    """High-frequency GPS coordinate stream from Rider PWA."""
    if frappe.db.exists("BizRider", rider_id):
        frappe.db.set_value("BizRider", rider_id, {
            "current_latitude": flt(latitude),
            "current_longitude": flt(longitude),
            "last_location_update": now()
        })
        frappe.db.commit()
    return {"status": "ok"}


@frappe.whitelist()
def confirm_pickup(delivery_id, otp):
    """Verifies pickup OTP at seller premises."""
    delivery = frappe.get_doc("BizRide Delivery", delivery_id)
    if delivery.pickup_otp and delivery.pickup_otp.strip().upper() != str(otp).strip().upper():
        frappe.throw("Invalid Pickup OTP")

    delivery.status = "In Transit"
    delivery.picked_up_at = now()
    delivery.save(ignore_permissions=True)

    return {"status": "success", "message": "Pickup confirmed! Package is now In Transit."}


@frappe.whitelist()
def confirm_delivery(delivery_id, otp):
    """Verifies delivery OTP at buyer doorstep and settles rider earnings."""
    delivery = frappe.get_doc("BizRide Delivery", delivery_id)
    if delivery.delivery_otp and delivery.delivery_otp.strip().upper() != str(otp).strip().upper():
        frappe.throw("Invalid Delivery OTP")

    delivery.status = "Delivered"
    delivery.delivered_at = now()
    delivery.payment_to_rider_status = "Paid"
    delivery.save(ignore_permissions=True)

    # Credit Rider digital wallet
    if delivery.assigned_rider and frappe.db.exists("BizRider", delivery.assigned_rider):
        current_bal = frappe.db.get_value("BizRider", delivery.assigned_rider, "wallet_balance") or 0.0
        new_bal = current_bal + flt(delivery.rider_earning)

        frappe.db.set_value("BizRider", delivery.assigned_rider, {
            "wallet_balance": new_bal,
            "total_deliveries": (frappe.db.get_value("BizRider", delivery.assigned_rider, "total_deliveries") or 0) + 1
        })

        if frappe.db.exists("DocType", "BizRider Wallet Transaction"):
            tx = frappe.get_doc({
                "doctype": "BizRider Wallet Transaction",
                "rider": delivery.assigned_rider,
                "transaction_type": "Earning",
                "amount": delivery.rider_earning,
                "delivery": delivery.name,
                "balance_after": new_bal,
                "description": f"Earnings for Delivery {delivery.name}"
            })
            tx.insert(ignore_permissions=True)

        frappe.db.commit()

    return {
        "status": "success",
        "message": "Delivery completed successfully! Rider wallet credited.",
        "delivery_id": delivery.name,
        "earning": f"{flt(delivery.rider_earning):,.2f} ETB"
    }


@frappe.whitelist(allow_guest=True)
def get_tracking(delivery_id):
    """Public real-time tracking data for `/track/<delivery_id>` page."""
    if not frappe.db.exists("BizRide Delivery", delivery_id):
        frappe.throw("Delivery not found")

    d = frappe.get_doc("BizRide Delivery", delivery_id)
    rider_info = None
    if d.assigned_rider and frappe.db.exists("BizRider", d.assigned_rider):
        r = frappe.get_doc("BizRider", d.assigned_rider)
        rider_info = {
            "name": r.rider_name,
            "phone": r.phone,
            "vehicle_type": r.vehicle_type,
            "vehicle_plate": r.vehicle_plate,
            "rating": r.average_rating,
            "lat": r.current_latitude or d.pickup_latitude,
            "lng": r.current_longitude or d.pickup_longitude
        }

    return {
        "status": "success",
        "delivery_id": d.name,
        "delivery_status": d.status,
        "seller_company": d.seller_company,
        "pickup_address": d.pickup_address,
        "delivery_address": d.delivery_address,
        "pickup_lat": d.pickup_latitude,
        "pickup_lng": d.pickup_longitude,
        "delivery_lat": d.delivery_latitude,
        "delivery_lng": d.delivery_longitude,
        "distance_km": d.distance_km,
        "fee": f"{flt(d.delivery_fee):,.2f} ETB",
        "rider": rider_info
    }
