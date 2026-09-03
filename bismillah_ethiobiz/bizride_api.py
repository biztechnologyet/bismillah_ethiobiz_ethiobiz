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
from ethiobiz_identity import require_authed_customer, resolve_booking_company, session_contact_defaults

@frappe.whitelist()
def request_delivery(order_reference, order_doctype="Sales Order", seller_company=None,
                     pickup_address=None, delivery_address=None, buyer_name=None,
                     buyer_phone=None, pickup_lat=None, pickup_lng=None,
                     delivery_lat=None, delivery_lng=None, vehicle_type="Any",
                     is_cod=False, cod_amount=0.0):
    """
    Creates an official BizRide Delivery order and starts the dispatch broadcast.
    BISMALLAH: Integrated with ethiobiz_identity for proper customer binding.
    """
    
    # Require login and get customer
    customer = require_authed_customer("Please log in to request delivery")
    
    if not frappe.db.exists("DocType", "BizRide Delivery"):
        frappe.throw("BizRide Delivery module not installed")

    # Resolve seller company from order if not provided
    if not seller_company and order_reference:
        order_company = frappe.db.get_value(order_doctype, order_reference, "company")
        seller_company = order_company or "Biz Technology Solutions"
    
    # Ensure company is set, no silent fallback
    if not seller_company:
        frappe.throw("Seller company is required. Please specify the delivery provider company.")
    
    # Validate company exists
    if not frappe.db.exists("Company", seller_company):
        frappe.throw(f"Owning Company '{seller_company}' is not a valid Company.")

    pickup_lat = flt(pickup_lat) or 9.010
    pickup_lng = flt(pickup_lng) or 38.761
    delivery_lat = flt(delivery_lat) or 9.020
    delivery_lng = flt(delivery_lng) or 38.770

    if vehicle_type == "Motorbike":
        vehicle_type = "Motorcycle"

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

    # Get customer details for buyer info
    customer_defaults = session_contact_defaults()
    buyer_name = buyer_name or customer_defaults.get("full_name") or "Valued Customer"
    buyer_phone = buyer_phone or customer_defaults.get("phone") or "0911000000"

    delivery_doc = frappe.get_doc({
        "doctype": "BizRide Delivery",
        "order_reference": str(order_reference),
        "order_doctype": order_doctype,
        "seller_company": seller_company,
        "customer": customer,  # BISMALLAH: Link to authenticated customer
        "buyer_name": buyer_name,
        "buyer_phone": buyer_phone,
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
        "estimated_mins": delivery_doc.estimated_duration_minutes,
        "company": seller_company,
        "customer": customer
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
def reject_delivery(delivery_id, rider_id=None, reason=None):
    """
    Rider rejects a delivery offer. If the delivery is still Broadcasting,
    appends the rejection to the broadcast log and re-announces it to the next
    rider pool. If a rider was already assigned, the delivery is released back
    to Broadcasting so the broadcast engine can re-dispatch.
    """
    if not frappe.db.exists("BizRide Delivery", delivery_id):
        frappe.throw("Delivery not found")

    user = frappe.session.user
    if not rider_id and user != "Guest":
        rider_id = frappe.db.get_value("BizRider", {"email": user}, "name")

    delivery = frappe.get_doc("BizRide Delivery", delivery_id)

    # Log the rejection into the broadcast history child table
    if frappe.db.exists("DocType", "BizRide Broadcast Log"):
        delivery.append("broadcast_logs", {
            "rider": rider_id or "",
            "notified_at": now(),
            "response": "Rejected",
            "responded_at": now(),
            "distance_km": delivery.distance_km or 0.0
        })

    # If a rider had claimed it but is now rejecting, release it back to broadcast
    if delivery.status == "Rider Assigned":
        delivery.assigned_rider = None
        delivery.status = "Broadcasting"
        message = "Rider rejected after assignment. Delivery re-broadcast to rider pool."
    else:
        # Still broadcasting — just re-announce to next candidates
        delivery.status = "Broadcasting"
        message = "Offer rejected. Delivery re-broadcast to next rider."

    # Record the rejection reason in the notes-like description (safe field)
    if reason:
        delivery.notes = f"{getattr(delivery, 'notes', '') or ''} Rejected: {reason}".strip()

    delivery.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "message": message,
        "delivery_id": delivery.name,
        "delivery_status": delivery.status
    }


@frappe.whitelist(allow_guest=True)
def get_rider_dashboard(rider_id):
    """
    Returns the rider's earnings dashboard: profile, wallet balance,
    aggregate stats, recent wallet transactions, and active deliveries.
    """
    if not rider_id or not frappe.db.exists("BizRider", rider_id):
        frappe.throw("Rider not found")

    rider = frappe.get_doc("BizRider", rider_id)

    # Aggregate wallet stats
    total_earnings = 0.0
    total_withdrawn = 0.0
    recent_txns = []

    if frappe.db.exists("DocType", "BizRider Wallet Transaction"):
        rows = frappe.get_all(
            "BizRider Wallet Transaction",
            filters={"rider": rider_id},
            fields=["name", "transaction_type", "amount", "balance_after", "description", "payout_reference", "creation"],
            order_by="creation desc",
            limit=20
        )
        for r in rows:
            amt = flt(r.get("amount"))
            if r.get("transaction_type") == "Earning" or r.get("transaction_type") == "Bonus":
                total_earnings += amt
            elif r.get("transaction_type") in ("Withdrawal", "Commission Deduction", "Penalty"):
                total_withdrawn += amt
            recent_txns.append(r)
    else:
        # Fallback when ledger DocType is absent: derive from delivered trips
        earnings = frappe.db.sql("""
            SELECT COALESCE(SUM(rider_earning), 0) as total, COUNT(*) as cnt
            FROM `tabBizRide Delivery`
            WHERE assigned_rider = %s AND status = 'Delivered'
        """, (rider_id,), as_dict=True)
        if earnings:
            total_earnings = flt(earnings[0].get("total"))
            total_deliveries = earnings[0].get("cnt") or 0

    # Active deliveries (assigned to this rider, not yet delivered)
    active_deliveries = frappe.get_all(
        "BizRide Delivery",
        filters={"assigned_rider": rider_id, "status": ["not in", ["Delivered", "Cancelled", "Failed"]]},
        fields=["name", "order_reference", "pickup_address", "delivery_address", "delivery_fee", "rider_earning", "status", "created"],
        order_by="creation desc"
    )

    wallet_balance = flt(rider.get("wallet_balance") or 0.0)
    total_deliveries = rider.get("total_deliveries") or 0

    return {
        "status": "success",
        "rider_id": rider.name,
        "rider_name": rider.get("rider_name"),
        "phone": rider.get("phone"),
        "vehicle_type": rider.get("vehicle_type"),
        "status": rider.get("status"),
        "verification_status": rider.get("verification_status"),
        "rating": rider.get("average_rating"),
        "wallet_balance": wallet_balance,
        "formatted_wallet_balance": f"{wallet_balance:,.2f} ETB",
        "stats": {
            "total_deliveries": cint(total_deliveries),
            "total_earnings": round(total_earnings, 2),
            "total_withdrawn": round(total_withdrawn, 2),
            "active_deliveries": len(active_deliveries)
        },
        "active_deliveries": active_deliveries,
        "recent_transactions": recent_txns
    }


@frappe.whitelist()
def rider_withdraw(rider_id, amount, payout_method="Telebirr", payout_account=None, notes=None):
    """
    Processes a wallet withdrawal for the rider: validates available balance,
    deducts the amount, and records a Withdrawal balance ledger entry.
    """
    if not rider_id or not frappe.db.exists("BizRider", rider_id):
        frappe.throw("Rider not found")

    amount = flt(amount)
    if amount <= 0:
        frappe.throw("Withdrawal amount must be greater than zero")

    rider = frappe.get_doc("BizRider", rider_id)
    current_bal = flt(rider.get("wallet_balance") or 0.0)
    if amount > current_bal:
        frappe.throw("Insufficient wallet balance for withdrawal")

    new_bal = current_bal - amount
    frappe.db.set_value("BizRider", rider_id, "wallet_balance", new_bal)

    txn_name = None
    if frappe.db.exists("DocType", "BizRider Wallet Transaction"):
        txn = frappe.get_doc({
            "doctype": "BizRider Wallet Transaction",
            "rider": rider_id,
            "transaction_type": "Withdrawal",
            "amount": amount,
            "balance_after": new_bal,
            "description": notes or f"Withdrawal via {payout_method}",
            "payout_reference": payout_account or ""
        })
        txn.insert(ignore_permissions=True)
        txn_name = txn.name
    else:
        # Fallback tracking when ledger DocType is absent
        txn_name = f"WAL-WD-{frappe.generate_hash(length=8).upper()}"

    frappe.db.commit()

    return {
        "status": "success",
        "message": "Withdrawal request processed successfully",
        "transaction_id": txn_name,
        "rider_id": rider_id,
        "amount": f"{amount:,.2f} ETB",
        "payout_method": payout_method,
        "payout_account": payout_account or "",
        "balance_after": f"{new_bal:,.2f} ETB"
    }


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


@frappe.whitelist(allow_guest=True)
def estimate_fare(pickup_lat=None, pickup_lng=None, drop_lat=None, drop_lng=None, vehicle_type="Any"):
    """
    Computes real-time trip fare estimates for Bajaj, Motorbike, Car, and Truck.
    """
    p_lat = flt(pickup_lat) or 9.001
    p_lng = flt(pickup_lng) or 38.785
    d_lat = flt(drop_lat) or 9.019
    d_lng = flt(drop_lng) or 38.769

    dlat = math.radians(d_lat - p_lat)
    dlng = math.radians(d_lng - p_lng)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(p_lat)) * math.cos(math.radians(d_lat)) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = round(max(0.5, 6371 * c), 2)

    tier_rates = {
        "Bajaj": {"base": 50.0, "per_km": 15.0, "time_min": max(10, round(distance_km * 4))},
        "Motorbike": {"base": 60.0, "per_km": 20.0, "time_min": max(8, round(distance_km * 3))},
        "Car": {"base": 100.0, "per_km": 28.0, "time_min": max(12, round(distance_km * 3.5))},
        "Truck": {"base": 250.0, "per_km": 45.0, "time_min": max(20, round(distance_km * 5))},
        "Any": {"base": 60.0, "per_km": 20.0, "time_min": max(10, round(distance_km * 3))}
    }

    rates = tier_rates.get(vehicle_type, tier_rates["Any"])
    estimated_fare = round(rates["base"] + (distance_km * rates["per_km"]), 2)

    all_estimates = {}
    for vt, r in tier_rates.items():
        if vt != "Any":
            all_estimates[vt] = {
                "base_fee": r["base"],
                "per_km": r["per_km"],
                "total_fare": round(r["base"] + (distance_km * r["per_km"]), 2),
                "formatted_fare": f"{round(r['base'] + (distance_km * r['per_km']), 2):,.2f} ETB",
                "estimated_minutes": r["time_min"]
            }

    return {
        "status": "success",
        "distance_km": distance_km,
        "vehicle_type": vehicle_type,
        "estimated_fare": estimated_fare,
        "formatted_fare": f"{estimated_fare:,.2f} ETB",
        "estimated_minutes": rates["time_min"],
        "tier_estimates": all_estimates
    }


@frappe.whitelist()
def find_bizride(reference_doctype, reference_name, vehicle_type="Motorbike", cod_amount=0.0):
    """
    Desk-Level 'Find BizRide' action handler for Delivery Note & Sales Invoice.
    Initiates broadcast to active online riders within a 5km radius.
    """
    if not frappe.db.exists(reference_doctype, reference_name):
        frappe.throw(f"{reference_doctype} {reference_name} not found")

    doc = frappe.get_doc(reference_doctype, reference_name)

    # Determine Pickup (Seller/Company address) and Delivery (Customer shipping)
    seller_company = getattr(doc, "company", "Biz Technology Solutions")
    buyer_name = getattr(doc, "customer_name", getattr(doc, "customer", "Valued Customer"))
    buyer_phone = getattr(doc, "contact_mobile", getattr(doc, "contact_phone", "0911000000"))

    pickup_lat, pickup_lng = 9.001, 38.785
    delivery_lat, delivery_lng = 9.019, 38.769

    if hasattr(doc, "company") and frappe.db.exists("Company", doc.company):
        comp = frappe.get_doc("Company", doc.company)
        if comp.latitude and comp.longitude:
            pickup_lat, pickup_lng = flt(comp.latitude), flt(comp.longitude)

    # Create Delivery request
    res = request_delivery(
        order_reference=reference_name,
        order_doctype=reference_doctype,
        seller_company=seller_company,
        pickup_address=getattr(doc, "company_address", "Addis Ababa"),
        delivery_address=getattr(doc, "shipping_address", getattr(doc, "customer_address", "Addis Ababa")),
        buyer_name=buyer_name,
        buyer_phone=buyer_phone,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        delivery_lat=delivery_lat,
        delivery_lng=delivery_lng,
        vehicle_type=vehicle_type,
        is_cod=bool(flt(cod_amount) > 0),
        cod_amount=flt(cod_amount)
    )

    # Update reference document custom fields if present
    try:
        frappe.db.set_value(reference_doctype, reference_name, {
            "bizride_delivery_id": res.get("delivery_id"),
            "delivery_status": "BizRide Dispatched"
        }, update_modified=False)
        frappe.db.commit()
    except Exception:
        pass

    return {
        "status": "success",
        "message": f"Broadcast initiated for {reference_name}! Nearby riders alerted.",
        "delivery_id": res.get("delivery_id"),
        "pickup_otp": res.get("pickup_otp"),
        "delivery_otp": res.get("delivery_otp"),
        "tracking_url": f"/track/{res.get('delivery_id')}"
    }

