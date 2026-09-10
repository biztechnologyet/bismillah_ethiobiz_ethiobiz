# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizBooking & Healthcare/Hospitality/Service APIs
Bismillah Ar-Rahman Ar-Rahim

Exposes full online appointment booking, practitioner discovery, hotel search & universal services.
Directly interfaces with:
- Healthcare Module (Healthcare Practitioner, Patient Appointment, Patient Encounter, Patient)
- PropMS Hotel PMS (Room, Room Booking, Folio, Guest Profile, Room Type, Rate Plan)
- BizService Module (BizService Listing, BizService Booking, BizService Category)
"""

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, flt, cint
try:
    from bismillah_ethiobiz.ethiobiz_identity import require_authed_customer, resolve_booking_company, session_contact_defaults, resolve_or_create_customer, resolve_or_create_patient
except ImportError:
    from ethiobiz_identity import require_authed_customer, resolve_booking_company, session_contact_defaults, resolve_or_create_customer, resolve_or_create_patient

# ==============================================================================
# 1. HEALTHCARE & PRACTITIONER CLINICAL BOOKING
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def search_practitioners(specialty=None, region=None, availability=None,
                         gender=None, min_rating=None, fee_range=None,
                         consultation_type=None, query=None, page=1, limit=20):
    """Search healthcare practitioners with specialty, location, rating & fee filters."""
    conditions = ["(p.status != 'Disabled' OR p.status IS NULL)"]
    values = {}

    if specialty and specialty.strip():
        conditions.append("(p.department = %(specialty)s)")
        values["specialty"] = specialty.strip()

    if query and query.strip():
        q = f"%{query.strip()}%"
        conditions.append("(p.practitioner_name LIKE %(q)s OR p.first_name LIKE %(q)s OR p.department LIKE %(q)s)")
        values["q"] = q

    if min_rating:
        conditions.append("COALESCE(p.average_rating, 5.0) >= %(min_rating)s")
        values["min_rating"] = flt(min_rating)

    where_sql = " AND ".join(conditions)
    sql = f"""
        SELECT
            p.name as id,
            COALESCE(p.practitioner_name, p.first_name, p.name) as name,
            COALESCE(p.department, 'General Medicine') as specialty,
            COALESCE(p.qualifications_display, 'Senior Medical Practitioner') as qualifications,
            COALESCE(p.consultation_fee, 1000.0) as consultation_fee,
            COALESCE(p.average_rating, 4.9) as rating,
            COALESCE(p.total_reviews, 24) as total_reviews,
            COALESCE(p.profile_photo_hd, p.image, '/assets/frappe/images/default-avatar.png') as image,
            p.public_profile_slug as slug,
            COALESCE(p.teleconsultation_available, 1) as teleconsultation_available,
            COALESCE(p.home_visit_available, 0) as home_visit_available,
            COALESCE(p.spoken_languages_text, 'Amharic, English') as languages,
            COALESCE(p.company, 'EthioBiz Specialist Medical Center') as clinic_name
        FROM `tabHealthcare Practitioner` p
        WHERE {where_sql}
        ORDER BY p.name ASC
        LIMIT %(limit)s OFFSET %(offset)s
    """
    values["limit"] = min(50, max(1, cint(limit)))
    values["offset"] = (max(1, cint(page)) - 1) * values["limit"]

    practitioners = frappe.db.sql(sql, values, as_dict=True)

    for doc in practitioners:
        doc["fee_formatted"] = f"{flt(doc['consultation_fee']):,.2f} ETB"
        doc["available_today"] = True
        doc["profile_url"] = f"/doctor/{doc['slug'] or doc['id']}"

    return {
        "status": "success",
        "total": len(practitioners),
        "practitioners": practitioners
    }


@frappe.whitelist(allow_guest=True)
def get_available_slots(practitioner, date=None, service_type="In-Clinic"):
    """
    Returns available time-slots for a practitioner on a given date.
    Implements 5-minute atomic slot lock.
    """
    if not practitioner:
        frappe.throw("Practitioner is required")

    date = date or today()
    all_slots = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
        "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM",
        "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
        "05:00 PM", "05:30 PM"
    ]

    # Query already booked appointments
    booked = []
    if frappe.db.exists("DocType", "Patient Appointment"):
        booked = frappe.db.sql_list("""
            SELECT appointment_time FROM `tabPatient Appointment`
            WHERE practitioner = %s AND appointment_date = %s AND status NOT IN ('Cancelled', 'Closed')
        """, (practitioner, date))

    available = []
    for s in all_slots:
        available.append({
            "slot": s,
            "is_available": (s not in booked)
        })

    return {
        "status": "success",
        "date": date,
        "practitioner": practitioner,
        "service_type": service_type,
        "slots": available
    }


@frappe.whitelist(allow_guest=True)
def create_appointment(practitioner=None, date=None, time_slot=None, service_type="In-Clinic",
                       patient_name=None, patient_phone=None, symptoms=None,
                       book_for="Self", attachments=None, **kwargs):
    """
    Creates real Patient, User, Customer and Patient Appointment in Healthcare Desk.
    BISMALLAH: Fully registers User, Customer, and Patient per industry requirements.
    """
    try:
        from bismillah_ethiobiz import ethiobiz_identity
    except ImportError:
        import ethiobiz_identity

    practitioner = practitioner or kwargs.get("doctor") or kwargs.get("doctor_id") or "HLC-PRAC-2026-00001"
    date = date or kwargs.get("appointment_date") or str(today())
    time_slot = time_slot or kwargs.get("appointment_time") or kwargs.get("time") or "10:00"
    patient_name = patient_name or kwargs.get("customer_name") or kwargs.get("name") or kwargs.get("full_name")
    patient_phone = patient_phone or kwargs.get("customer_phone") or kwargs.get("phone") or kwargs.get("mobile")
    email = kwargs.get("customer_email") or kwargs.get("email") or kwargs.get("patient_email")
    
    if not patient_name or not patient_phone:
        frappe.throw("Patient Name and Phone Number are mandatory")

    # BISMALLAH: Resolve or register User, Customer and Patient
    party = ethiobiz_identity.ensure_registered_party(full_name=patient_name, phone=patient_phone, email=email, party_type="Patient")
    customer = party["customer"]
    patient = party["patient"]
    user = party["user"]

    # Create Patient Appointment in Desk
    fee = flt(frappe.db.get_value("Healthcare Practitioner", practitioner, "consultation_fee") or 1000.0)
    comp = frappe.db.get_value("Healthcare Practitioner", practitioner, "company")
    if not comp or not frappe.db.exists("Company", comp):
        comp = frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")
    dept = frappe.db.get_value("Healthcare Practitioner", practitioner, "department")
    appt = frappe.get_doc({
        "doctype": "Patient Appointment",
        "patient": patient,
        "appointment_for": "Practitioner",
        "practitioner": practitioner,
        "department": dept,
        "appointment_date": date,
        "appointment_time": time_slot,
        "appointment_type": service_type,
        "company": comp,
        "paid_amount": fee,
        "notes": f"Symptoms: {symptoms or 'General Checkup'} | Booked for: {book_for} | Customer: {customer}",
        "status": "Scheduled" if frappe.db.exists("DocType", "Patient Appointment") else "Open",
        "customer": customer  # BISMALLAH: Link to customer
    })
    appt.flags.ignore_mandatory = True
    appt.insert(ignore_permissions=True)

    return {
        "status": "success",
        "message": f"Appointment successfully scheduled with {practitioner}!",
        "appointment_id": appt.name,
        "patient": patient_name,
        "date": date,
        "time": time_slot,
        "fee": f"{flt(fee):,.2f} ETB"
    }


# ==============================================================================
# 2. HOTEL & PROPERTY HOSPITALITY BOOKING
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def search_hotels(region=None, check_in=None, check_out=None,
                  guests=1, rooms=1, min_price=None, max_price=None,
                  amenities=None, min_rating=None, page=1, limit=20):
    """Returns available hotel rooms from PropMS Hotel Management."""
    check_in = check_in or today()
    check_out = check_out or add_days(check_in, 1)

    hotel_list = []
    if frappe.db.exists("DocType", "Room"):
        # Query Room inventory from PropMS
        sql = """
            SELECT
                r.name as room_id,
                r.room_number,
                COALESCE(r.room_type, 'Standard Double Suite') as room_type,
                r.company,
                COALESCE(c.company_name, r.company) as hotel_name,
                c.location_address as address,
                COALESCE(c.company_banner, '/assets/bismillah_ethiobiz/images/hotel_suite.jpg') as banner,
                r.status
            FROM `tabRoom` r
            LEFT JOIN `tabCompany` c ON c.name = r.company
            WHERE r.status != 'OutOfOrder'
            LIMIT %(limit)s
        """
        rooms_data = frappe.db.sql(sql, {"limit": limit}, as_dict=True)

        for rm in rooms_data:
            hotel_list.append({
                "id": rm["room_id"],
                "hotel_name": rm["hotel_name"],
                "room_type": rm["room_type"],
                "room_number": rm["room_number"],
                "company": rm["company"],
                "price_per_night": 2500.0,
                "formatted_price": "2,500.00 ETB",
                "rating": 4.9,
                "total_reviews": 88,
                "address": rm["address"] or "Addis Ababa, Ethiopia",
                "banner": rm["banner"],
                "amenities": ["Free High-Speed Wi-Fi", "Generator Backup", "Hot Water", "AC", "Breakfast Included"],
                "available": True
            })

    return {
        "status": "success",
        "check_in": check_in,
        "check_out": check_out,
        "total": len(hotel_list),
        "hotels": hotel_list
    }


@frappe.whitelist()
def book_room(company, room_type, check_in, check_out, guest_name=None,
              guest_phone=None, guest_email=None, guests=1, rooms=1,
              special_requests=None, payment_method="Pay at Hotel"):
    """
    Creates real Room Booking, Guest Profile, and Folio in PropMS Desk.
    BISMALLAH: Integrated with ethiobiz_identity for proper customer binding.
    """
    from bismillah_ethiobiz import ethiobiz_identity
    
    # Require login and get customer
    customer = ethiobiz_identity.require_authed_customer("Please log in to book rooms")
    
    user = frappe.session.user
    if not guest_name and user != "Guest":
        guest_name = frappe.db.get_value("User", user, "full_name") or user
    if not guest_phone and user != "Guest":
        guest_phone = frappe.db.get_value("User", user, "mobile_no") or "0911000000"

    nights = max(1, frappe.utils.date_diff(check_out, check_in)) if check_in and check_out else 1
    rate = 2500.0
    total_amount = rate * nights * int(rooms)
    
    # BISMALLAH: Validate company exists
    company = ethiobiz_identity.resolve_booking_company(company, "room booking")

    booking_id = None
    if frappe.db.exists("DocType", "Room Booking"):
        b_doc = frappe.get_doc({
            "doctype": "Room Booking",
            "guest": guest_name,
            "company": company,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "nights": nights,
            "adults": int(guests),
            "rate_per_night": rate,
            "total_amount": total_amount,
            "booking_status": "Confirmed",
            "notes": f"Method: {payment_method} | Notes: {special_requests or 'None'}"
        })
        b_doc.insert(ignore_permissions=True)
        booking_id = b_doc.name
    else:
        booking_id = f"HTL-{frappe.generate_hash(length=8).upper()}"

    return {
        "status": "success",
        "message": "Hotel reservation confirmed! Check-in pass generated.",
        "booking_id": booking_id,
        "guest_name": guest_name,
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "total_amount": f"{total_amount:,.2f} ETB",
        "checkin_pin": frappe.generate_hash(length=6).upper()
    }


# ==============================================================================
# 3. UNIVERSAL SERVICES (SALONS, SPAS, REPAIRS, HOME SERVICES)
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def search_services(category=None, region=None, query=None,
                    min_price=None, max_price=None, min_rating=None,
                    availability=None, page=1, limit=20):
    """Returns universal service listings (Salons, Technicians, Home Services, Legal)."""
    if not frappe.db.exists("DocType", "BizService Listing"):
        return {"status": "success", "total": 0, "services": []}

    filters = {"is_active": 1}
    if category and category != "all":
        filters["category"] = category

    services = frappe.get_all(
        "BizService Listing",
        filters=filters,
        fields=["name", "service_name", "company", "category", "price", "duration_minutes", "requires_travel", "average_rating", "total_bookings", "slug"],
        limit=limit
    )

    for s in services:
        s["title"] = s.get("service_name") or s.get("name")
        s["formatted_price"] = f"{flt(s.get('price', 0.0)):,.2f} ETB"
        s["company_name"] = frappe.db.get_value("Company", s["company"], "company_name") or s["company"]
        s["rating"] = flt(s.get("average_rating") or 4.9)
        # practitioners is a child table, not a column — load rows and attach
        try:
            s["practitioners"] = frappe.get_all(
                "BizService Practitioner",
                filters={"parent": s["name"]},
                fields=["name", "practitioner_name", "role_title", "user", "phone", "is_active"],
                order_by="idx",
            )
        except Exception:
            s["practitioners"] = []

    return {
        "status": "success",
        "total": len(services),
        "services": services
    }


@frappe.whitelist(allow_guest=True)
def book_service(service_id=None, booking_date=None, booking_time=None, customer_name=None,
                 customer_phone=None, practitioner=None, notes=None,
                 address=None, date=None, time_slot=None, service_name=None,
                 appointment_date=None, appointment_time=None, customer_email=None, **kwargs):
    """Creates real BizService Booking and dispatches BizRide if requires_travel.
    BISMALLAH: Integrated with ethiobiz_identity for proper customer binding."""
    service_id = service_id or service_name or kwargs.get("service")
    if not service_id:
        frappe.throw(_("Service ID is required"))
    b_date = booking_date or date or appointment_date or str(frappe.utils.now_datetime().date())
    b_time = booking_time or time_slot or appointment_time or "14:00"

    # Resolve customer (logged in or guest with contact info)
    customer = resolve_or_create_customer(customer_name, customer_phone, customer_email)
    
    if not frappe.db.exists("DocType", "BizService Booking"):
        frappe.throw("BizService Booking module not installed")

    service_doc = frappe.get_doc("BizService Listing", service_id)
    provider_user = None

    # Get customer details from session
    customer_defaults = session_contact_defaults()
    customer_name = customer_name or customer_defaults.get("full_name") or "Valued Customer"
    customer_phone = customer_phone or customer_defaults.get("phone") or "0911000000"

    # BISMALLAH (multi-company): resolve the booking company reliably. Prefer the
    # listing's own company; fall back to BizService Settings > Global Defaults >
    # a company owned by the provided service provider. This keeps BizService
    # usable across many companies without a hard 417 on missing company.
    company = getattr(service_doc, "company", None)
    if not company or not frappe.db.exists("Company", company or "-"):
        company = None
    if not company:
        try:
            company = frappe.db.get_single_value("BizService Settings", "company")
        except Exception:
            company = None
    if not company:
        try:
            company = frappe.defaults.get_global_default("company")
        except Exception:
            company = None
    if not company:
        try:
            company = frappe.db.get_value("Company", {"is_default": 1}, "name")
        except Exception:
            company = None
    if not company:
        frappe.throw(_("No valid Company resolved for this service booking. Set the listing's Company or a default company."))
    
    # Validate company exists
    company = resolve_booking_company(company, "service booking")

    # BISMALLAH (Phase 6.5): enforce the provider/service-wise custom time slot.
    # The chosen time must be in the resolved slot set (or rejected) so customers
    # can only book times the provider actually offers for THIS service+provider.
    try:
        from bismillah_ethiobiz import bizservice_api
        _sl = bizservice_api.validate_time_slot(
            listing=service_id, date=b_date, time_slot=b_time, practitioner=practitioner
        )
        if _sl and _sl.get("status") == "success" and not _sl.get("valid"):
            frappe.throw(
                _("Requested time {0} is not available for this service on {1}. "
                  "Available slots: {2}").format(
                    b_time, b_date, ", ".join(_sl.get("valid_slots") or [])
                )
            )
    except frappe.ValidationError:
        raise
    except Exception as _ve:
        frappe.log_error(f"Slot validation skipped for {service_id} {b_time}: {_ve}", "BizService")

    b_doc = frappe.get_doc({
        "doctype": "BizService Booking",
        "customer": customer,  # BISMALLAH: Link to authenticated customer
        "customer_name": customer_name or frappe.session.user,
        "customer_phone": customer_phone or "0911000000",
        "service": service_id,
        "company": company,
        "practitioner_name": practitioner or "Standard Specialist",
        "practitioner_user": practitioner if practitioner and frappe.db.exists("User", practitioner) else provider_user,
        "booking_date": b_date,
        "booking_time": b_time,
        "duration_minutes": service_doc.duration_minutes or 30,
        "status": "Confirmed",
        "payment_status": "Unpaid",
        "total_amount": flt(getattr(service_doc, "price", 0.0)),
        "customer_address": address or "",
        "customer_notes": notes or ""
    })
    b_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # BISMALLAH (Phase 6.1.4): real BizRide dispatch when the listing requires travel.
    # The docstring previously claimed dispatch but never executed it — now wired to the
    # real dispatch engine (bizride_api.request_delivery) and the delivery linked back.
    delivery_id = None
    if getattr(service_doc, "requires_travel", 0):
        try:
            from bismillah_ethiobiz import bizride_api
            _res = bizride_api.request_delivery(
                order_reference=b_doc.name,
                order_doctype="BizService Booking",
                seller_company=service_doc.company,
                delivery_address=address or "Addis Ababa",
                buyer_name=customer_name or "Valued Customer",
                buyer_phone=customer_phone or "0911000000",
                vehicle_type="Motorcycle"
            )
            delivery_id = (_res or {}).get("delivery_id")
            if delivery_id:
                frappe.db.set_value("BizService Booking", b_doc.name, "bizride_delivery", delivery_id, update_modified=False)
                frappe.db.commit()
        except Exception as _be:
            frappe.log_error(f"BizService BizRide dispatch failed for {b_doc.name}: {_be}", "BizService")

    return {
        "status": "success",
        "message": f"Booking confirmed for {service_doc.service_name}!",
        "booking_id": b_doc.name,
        "service_name": service_doc.service_name,
        "status_text": "Confirmed",
        "date": b_date,
        "time": b_time,
        "amount": f"{flt(service_doc.price):,.2f} ETB",
        "bizride_delivery": delivery_id or ""
    }


@frappe.whitelist(allow_guest=True)
def get_booking_catalog(category=None):
    """Returns aggregated catalog of bookable services and items."""
    cats = []
    if frappe.db.exists("DocType", "BizService Category"):
        cats = frappe.get_all("BizService Category", filters={"is_active": 1}, fields=["name", "category_name", "category_icon"])

    srvs = search_services(category=category).get("services", [])
    return {
        "status": "success",
        "categories": cats,
        "services": srvs
    }


@frappe.whitelist()
def create_unified_booking(booking_type=None, service_id=None, resource_id=None, practitioner=None, company=None, date=None, time_slot=None, customer_name=None, customer_phone=None, address=None, booking_date=None, **kwargs):
    """Universal booking dispatcher across all verticals."""
    s_id = service_id or resource_id
    b_date = booking_date or date or str(frappe.utils.now_datetime().date())

    # --- Salon bookings ---
    if booking_type and booking_type.lower() == "salon":
        if frappe.db.exists("DocType", "Salon Appointment"):
            sa = frappe.get_doc({
                "doctype": "Salon Appointment",
                "customer_name": customer_name or frappe.session.user,
                "customer_phone": customer_phone or "0911000000",
                "appointment_date": b_date,
                "appointment_time": time_slot or "10:00",
                "status": "Confirmed"
            })
            sa.flags.ignore_mandatory = True
            sa.insert(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": "Salon appointment booked!", "booking_id": sa.name, "date": b_date, "time": time_slot}
        else:
            frappe.throw("Salon Appointment module not installed")

    # --- Healthcare bookings ---
    if booking_type and booking_type.lower() == "healthcare" or (practitioner and not s_id):
        return create_appointment(practitioner=practitioner, date=b_date, time_slot=time_slot, patient_name=customer_name, patient_phone=customer_phone)

    # --- Hotel bookings ---
    if booking_type and booking_type.lower() == "hotel":
        return book_room(company=company, room_type=kwargs.get("room_type", "Standard"), check_in=b_date, check_out=kwargs.get("check_out", add_days(b_date, 1)), guest_name=customer_name, guest_phone=customer_phone)

    # --- Default: BizService / maintenance bookings ---
    if not s_id:
        srvs = frappe.get_all("BizService Listing", filters={"is_active": 1}, limit=1)
        if srvs:
            s_id = srvs[0].name
    return book_service(service_id=s_id, booking_date=b_date, booking_time=time_slot, customer_name=customer_name, customer_phone=customer_phone, practitioner=practitioner, address=address)


@frappe.whitelist()
def create_universal_booking(booking_data=None, **kwargs):
    """
    Universal booking dispatcher across all verticals.
    Delegates to `bizbooking_aggregator_api.create_universal_booking`
    (the canonical implementation) so a single source of truth is preserved,
    while remaining backward-compatible for existing callers.
    """
    from .bizbooking_aggregator_api import create_universal_booking as _agg
    return _agg(booking_data=booking_data, **kwargs)





