# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizBooking Aggregator APIs
Bismillah Ar-Rahman Ar-Rahim

Unified multi-vertical booking aggregator. Combines hotels, healthcare,
salons, services, workspaces and real-estate into a single `search_all_bookables`
command and provides a universal `create_universal_booking` dispatch that
generates a digital QR/PIN booking pass.

Backward-compatible with `bizbooking_api.create_universal_booking` (thin re-export).
"""

import json
import frappe
from frappe import _
from frappe.utils import today, add_days, flt, cint, now_datetime


@frappe.whitelist(allow_guest=True)
def search_all_bookables(vertical=None, location=None, check_in=None,
                         check_out=None, guests=1, query=None, page=1, limit=20):
    """
    Aggregates every bookable vertical into one response:
      - healthcare  : Healthcare Practitioners
      - hotels      : Rooms (PropMS)
      - services    : BizService Listings (salon, repair, home, legal)
      - resources   : BizBooking Resources (workspaces, venues, rentals)
      - all         : everything above combined
    Optionally filters by location text, guest count, and free-text query.
    """
    page = max(1, cint(page))
    limit = min(50, max(1, cint(limit)))
    verticals = (vertical or "all").lower().strip()
    results = []

    # ---- Healthcare ----
    if verticals in ("all", "healthcare", "health", "doctors"):
        if frappe.db.exists("DocType", "Healthcare Practitioner"):
            filt = {}
            if query and query.strip():
                q = f"%{query.strip()}%"
                filt["practitioner_name"] = ["like", q]
            docs = frappe.get_all(
                "Healthcare Practitioner",
                filters=filt,
                fields=["name", "practitioner_name", "department", "consultation_fee",
                        "average_rating", "profile_photo_hd", "image", "company"],
                limit=limit
            )
            for d in docs:
                results.append({
                    "id": d["name"],
                    "vertical": "healthcare",
                    "category": d.get("department") or "Healthcare",
                    "title": d.get("practitioner_name") or d["name"],
                    "subtitle": d.get("company") or "EthioBiz Specialist Clinic",
                    "image": d.get("profile_photo_hd") or d.get("image"),
                    "rating": flt(d.get("average_rating") or 4.9),
                    "price": flt(d.get("consultation_fee") or 500.0),
                    "price_text": f"{flt(d.get('consultation_fee') or 500.0):,.2f} ETB",
                    "action_url": f"/bizhealth?doctor={d['name']}",
                    "action_label": "Book Doctor"
                })

    # ---- Hotels / Rooms ----
    if verticals in ("all", "hotels", "hotel", "rooms", "lodging", "hospitality"):
        if frappe.db.exists("DocType", "Room"):
            rooms = frappe.db.sql("""
                SELECT r.name as id, r.room_type, r.room_number, r.company,
                       COALESCE(c.company_name, r.company) as hotel_name,
                       COALESCE(c.company_banner, '/assets/bismillah_ethiobiz/images/hotel_suite.jpg') as image,
                       c.location_address as address
                FROM `tabRoom` r
                LEFT JOIN `tabCompany` c ON c.name = r.company
                WHERE r.status != 'OutOfOrder'
                LIMIT %(limit)s
            """, {"limit": limit}, as_dict=True)
            for rm in rooms:
                results.append({
                    "id": rm["id"],
                    "vertical": "hotel",
                    "category": rm.get("room_type") or "Standard Suite",
                    "title": f"{rm['hotel_name']} — {rm.get('room_type') or 'Standard Suite'}",
                    "subtitle": rm.get("address") or "Addis Ababa, Ethiopia",
                    "image": rm.get("image"),
                    "hotel_company": rm.get("company"),
                    "room_number": rm.get("room_number"),
                    "rating": 4.9,
                    "price": 2500.0,
                    "price_text": "2,500.00 ETB / night",
                    "action_url": "/booking?type=hotel",
                    "action_label": "Reserve Room"
                })

    # ---- BizService Listings (salon, repair, legal, home) ----
    if verticals in ("all", "services", "salon", "service", "repair", "maintenance"):
        if frappe.db.exists("DocType", "BizService Listing"):
            s_filt = {"is_active": 1}
            if query and query.strip():
                s_filt["service_name"] = ["like", f"%{query.strip()}%"]
            srvs = frappe.get_all(
                "BizService Listing",
                filters=s_filt,
                fields=["name", "service_name", "category", "price", "duration_minutes", "company", "average_rating"],
                limit=limit
            )
            for s in srvs:
                results.append({
                    "id": s["name"],
                    "vertical": "service",
                    "category": s.get("category") or "Service",
                    "title": s.get("service_name") or s["name"],
                    "subtitle": f"{s.get('company') or 'EthioBiz Certified'} • {s.get('duration_minutes') or 30} Mins",
                    "image": "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "rating": flt(s.get("average_rating") or 4.9),
                    "price": flt(s.get("price") or 0.0),
                    "price_text": f"{flt(s.get('price') or 0.0):,.2f} ETB",
                    "action_url": f"/bizfix?service={s['name']}",
                    "action_label": "Book Service"
                })

    # ---- BizBooking Resources (workspaces, venues, rentals) ----
    if verticals in ("all", "resources", "workspaces", "venues", "rentals"):
        if frappe.db.exists("DocType", "BizBooking Resource"):
            r_filt = {"is_active": 1}
            if query and query.strip():
                r_filt["resource_name"] = ["like", f"%{query.strip()}%"]
            res = frappe.get_all(
                "BizBooking Resource",
                filters=r_filt,
                fields=["name", "resource_name", "category", "base_rate", "company"],
                limit=limit
            )
            for r in res:
                rate = flt(r.get("base_rate") or 0.0)
                results.append({
                    "id": r["name"],
                    "vertical": "resource",
                    "category": r.get("category") or "Service Booking",
                    "title": r.get("resource_name") or r["name"],
                    "subtitle": f"{r.get('company') or 'EthioBiz Hospitality'} • Instant Voucher Pass",
                    "image": "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
                    "rating": 4.9,
                    "price": rate,
                    "price_text": f"{rate:,.2f} ETB" if rate > 0 else "Free Appointment",
                    "action_url": "/booking",
                    "action_label": "Reserve Now"
                })

    # Location filter (best-effort text match on subtitle)
    if location and location.strip():
        loc_l = location.strip().lower()
        results = [r for r in results if loc_l in str(r.get("subtitle", "")).lower()]

    total = len(results)
    paged = results[(page - 1) * limit: page * limit]

    return {
        "status": "success",
        "vertical": vertical,
        "location": location,
        "check_in": check_in or today(),
        "check_out": check_out or add_days(check_in or today(), 1),
        "guests": cint(guests) or 1,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": __import__("math").ceil(total / limit) if limit else 1,
        "bookables": paged
    }


@frappe.whitelist(allow_guest=True)
def create_universal_booking(booking_data=None, **kwargs):
    """
    Universal booking dispatch across every vertical. Accepts either a JSON
    string/object `booking_data` or the flat keyword arguments, validates
    availability, creates the underlying Desk booking, and returns a
    digital QR/PIN booking pass.

    Expected booking_data keys:
      vertical       : 'healthcare' | 'hotel' | 'service' | 'resource' | 'salon'
      target_id      : doctor / room / service / resource name
      company        : merchant company (hotels/services)
      date / time_slot
      customer_name / customer_phone / customer_email
      check_out      : for hotel stays
      room_type / guests : for hotel
      symptoms/notes : optional
    """
    if isinstance(booking_data, str):
        try:
            booking_data = json.loads(booking_data)
        except Exception:
            booking_data = {}
    booking_data = booking_data or {}

    # Merge flat kwargs (backward-compat) into the payload
    for key, val in (kwargs or {}).items():
        if key not in booking_data or booking_data[key] in (None, ""):
            booking_data[key] = val

    vertical = (booking_data.get("vertical") or booking_data.get("booking_type") or "service").lower().strip()
    b_date = booking_data.get("date") or booking_data.get("booking_date") or str(now_datetime().date())
    customer_name = booking_data.get("customer_name") or frappe.session.user
    customer_phone = booking_data.get("customer_phone") or "0911000000"

    booking_ref = None
    message = ""

    # --- Healthcare ---
    if vertical in ("healthcare", "health", "doctor", "clinical"):
        from .bizbooking_api import create_appointment
        if not booking_data.get("practitioner") and booking_data.get("target_id"):
            booking_data["practitioner"] = booking_data["target_id"]
        res = create_appointment(
            practitioner=booking_data.get("practitioner"),
            date=b_date,
            time_slot=booking_data.get("time_slot") or booking_data.get("slot") or "10:00",
            patient_name=customer_name,
            patient_phone=customer_phone,
            symptoms=booking_data.get("symptoms"),
            service_type=booking_data.get("consultation_type") or booking_data.get("service_type") or "In-Clinic"
        )
        booking_ref = res.get("appointment_id")
        message = res.get("message", "Appointment booked")

    # --- Hotel ---
    elif vertical in ("hotel", "hotels", "lodging", "hospitality"):
        from .bizbooking_api import book_room
        company = booking_data.get("company") or booking_data.get("hotel_company")
        res = book_room(
            company=company,
            room_type=booking_data.get("room_type", "Standard Suite"),
            check_in=b_date,
            check_out=booking_data.get("check_out") or add_days(b_date, 1),
            guest_name=customer_name,
            guest_phone=customer_phone,
            guest_email=booking_data.get("customer_email"),
            guests=cint(booking_data.get("guests") or 1),
            rooms=cint(booking_data.get("rooms") or 1),
            special_requests=booking_data.get("notes")
        )
        booking_ref = res.get("booking_id")
        message = res.get("message", "Hotel reservation confirmed")

    # --- Salon ---
    elif vertical in ("salon", "spa", "beauty"):
        if not frappe.db.exists("DocType", "Salon Appointment"):
            frappe.throw("Salon Appointment module not installed")
        sa = frappe.get_doc({
            "doctype": "Salon Appointment",
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "appointment_date": b_date,
            "appointment_time": booking_data.get("time_slot") or "10:00",
            "status": "Confirmed"
        })
        sa.flags.ignore_mandatory = True
        sa.insert(ignore_permissions=True)
        frappe.db.commit()
        booking_ref = sa.name
        message = "Salon appointment booked!"

    # --- Resource (workspace/venue/rental) ---
    elif vertical in ("resource", "workspace", "venue", "rental", "booking"):
        if not frappe.db.exists("DocType", "BizBooking Resource"):
            frappe.throw("BizBooking Resource module not installed")
        res_id = booking_data.get("target_id") or booking_data.get("resource_id")
        if not res_id:
            frappe.throw("Resource is required")
        b_res = frappe.get_doc("BizBooking Resource", res_id)
        ent = frappe.get_doc({
            "doctype": "BizResource Booking",
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "resource": res_id,
            "company": b_res.get("company"),
            "booking_date": b_date,
            "booking_time": booking_data.get("time_slot") or "10:00",
            "status": "Confirmed"
        })
        ent.flags.ignore_mandatory = True
        ent.insert(ignore_permissions=True)
        frappe.db.commit()
        booking_ref = ent.name
        message = "Resource reserved!"

    # --- Default: BizService / maintenance ---
    else:
        from .bizbooking_api import book_service
        s_id = booking_data.get("target_id") or booking_data.get("service_id")
        res = book_service(
            service_id=s_id,
            booking_date=b_date,
            booking_time=booking_data.get("time_slot") or booking_data.get("slot") or "14:00",
            customer_name=customer_name,
            customer_phone=customer_phone,
            address=booking_data.get("address"),
            notes=booking_data.get("notes")
        )
        booking_ref = res.get("booking_id")
        message = res.get("message", "Service booked")

    # Digital booking pass (QR-encodable PIN)
    pass_pin = frappe.generate_hash(length=6).upper()

    return {
        "status": "success",
        "message": message,
        "booking_id": booking_ref,
        "vertical": vertical,
        "date": b_date,
        "time": booking_data.get("time_slot") or booking_data.get("slot") or "10:00",
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "booking_pass_pin": pass_pin,
        "qr_payload": json.dumps({
            "booking_id": booking_ref,
            "pin": pass_pin,
            "vertical": vertical,
            "date": b_date
        })
    }


# Keep a thin re-export for backward compatibility with code that imports
# create_universal_booking from bizbooking_api (that module delegates here).
def universal_booking(*args, **kwargs):
    return create_universal_booking(*args, **kwargs)
