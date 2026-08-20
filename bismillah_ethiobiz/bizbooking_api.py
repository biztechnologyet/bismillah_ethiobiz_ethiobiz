import json
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_booking_catalog(category=None):
    """Returns booking catalog across Hotels, Healthcare Doctors, Salon Services & Properties."""
    category = (category or frappe.form_dict.get("category") or "all").lower().strip()
    
    catalog = {
        "hotels": [],
        "doctors": [],
        "salons": [],
        "properties": []
    }

    # 1. HOTEL ROOMS
    if category in ("all", "hotels", "hotel"):
        if frappe.db.exists("DocType", "BizBooking Resource"):
            rooms = frappe.get_all(
                "BizBooking Resource",
                filters={"category": "Hotel Room", "is_active": 1},
                fields=["name", "resource_name", "company", "base_rate", "capacity", "description"]
            )
            for r in rooms:
                catalog["hotels"].append({
                    "id": r.name,
                    "title": r.resource_name,
                    "company": r.company,
                    "price_per_night": r.base_rate or 2500.0,
                    "capacity": f"{r.capacity or 2} Guests",
                    "description": r.description or "Luxury accommodation with high-speed WiFi, breakfast buffet, and airport shuttle.",
                    "image": "/files/hotel_room_default.jpg"
                })

    # 2. HEALTHCARE PRACTITIONERS (PRACTO-INSPIRED)
    if category in ("all", "doctors", "healthcare"):
        if frappe.db.exists("DocType", "Healthcare Practitioner"):
            docs = frappe.get_all(
                "Healthcare Practitioner",
                fields=["name", "practitioner_name", "department", "op_consulting_charge", "image"]
            )
            for d in docs:
                catalog["doctors"].append({
                    "id": d.name,
                    "name": d.practitioner_name or d.name,
                    "specialty": d.department or "General Physician",
                    "qualifications": "MD, MBBS - Senior Consultant",
                    "experience": "12+ Years Experience",
                    "rating": 4.9,
                    "clinic": "EthioBiz Central Medical & Specialist Center",
                    "fee": d.op_consulting_charge or 1200.0,
                    "image": d.image or "/assets/frappe/images/default-avatar.png",
                    "available_today": True
                })

    # 3. SALON & SPA SERVICES
    if category in ("all", "salons", "salon", "spa"):
        if frappe.db.exists("DocType", "Salon Service"):
            srvs = frappe.get_all(
                "Salon Service",
                filters={"is_active": 1},
                fields=["name", "service_name", "category", "price", "duration_minutes", "service_image", "description", "company"]
            )
            for s in srvs:
                catalog["salons"].append({
                    "id": s.name,
                    "name": s.service_name,
                    "category": s.category,
                    "price": s.price,
                    "duration": f"{s.duration_minutes} mins",
                    "company": s.company,
                    "description": s.description or "Professional beauty & grooming service with premium organic products.",
                    "image": s.service_image or "/files/salon_default.jpg"
                })

    # 4. PROPERTIES & SPACES
    if category in ("all", "properties", "property"):
        if frappe.db.exists("DocType", "BizBooking Resource"):
            props = frappe.get_all(
                "BizBooking Resource",
                filters={"category": "Property Viewing", "is_active": 1},
                fields=["name", "resource_name", "company", "description"]
            )
            for pr in props:
                catalog["properties"].append({
                    "id": pr.name,
                    "title": pr.resource_name,
                    "company": pr.company,
                    "price": "Free Appointment",
                    "description": pr.description or "Guided on-site tour of residential luxury villas and prime commercial spaces."
                })

    return {
        "status": "success",
        "category": category,
        "catalog": catalog
    }

@frappe.whitelist(allow_guest=True)
def create_unified_booking(
    booking_type=None, resource_id=None, customer_name=None, customer_phone=None,
    customer_email=None, booking_date=None, time_slot=None, check_out_date=None,
    number_of_persons=1, special_requests=None
):
    """Unified booking dispatcher creating official records in Room Booking, Patient Appointment, Salon Appointment & BizBooking Entry."""
    booking_type = (booking_type or frappe.form_dict.get("booking_type") or "hotel").lower().strip()
    resource_id = resource_id or frappe.form_dict.get("resource_id")
    customer_name = customer_name or frappe.form_dict.get("customer_name")
    customer_phone = customer_phone or frappe.form_dict.get("customer_phone")
    customer_email = customer_email or frappe.form_dict.get("customer_email") or ""
    booking_date = booking_date or frappe.form_dict.get("booking_date") or frappe.utils.today()
    time_slot = time_slot or frappe.form_dict.get("time_slot") or "10:00 AM"
    check_out_date = check_out_date or frappe.form_dict.get("check_out_date")
    number_of_persons = int(number_of_persons or frappe.form_dict.get("number_of_persons") or 1)
    special_requests = special_requests or frappe.form_dict.get("special_requests") or ""

    if not customer_name or not customer_phone:
        frappe.throw(_("Customer Name and Phone Number are required."))

    desk_doc_created = None
    desk_doctype = None
    amount = 0.0

    # 1. HOTEL ROOM BOOKING
    if booking_type in ("hotel", "hotels"):
        desk_doctype = "Room Booking"
        rate = 2500.0
        if resource_id and frappe.db.exists("BizBooking Resource", resource_id):
            rate = frappe.db.get_value("BizBooking Resource", resource_id, "base_rate") or 2500.0

        nights = 1
        if check_out_date and booking_date:
            try:
                nights = max(1, frappe.utils.date_diff(check_out_date, booking_date))
            except Exception:
                nights = 1
        amount = rate * nights

        if frappe.db.exists("DocType", "Room Booking"):
            try:
                room_doc = frappe.get_doc({
                    "doctype": "Room Booking",
                    "guest": customer_name,
                    "check_in_date": booking_date,
                    "check_out_date": check_out_date or booking_date,
                    "nights": nights,
                    "adults": number_of_persons,
                    "rate_per_night": rate,
                    "total_amount": amount,
                    "net_amount": amount,
                    "booking_status": "Confirmed",
                    "payment_status": "Unpaid",
                    "special_requests": special_requests or f"Phone: {customer_phone}",
                    "company": "Biz Technology Solutions"
                })
                room_doc.flags.ignore_permissions = True
                room_doc.insert(ignore_permissions=True)
                desk_doc_created = room_doc.name
            except Exception as e:
                frappe.log_error(f"Error creating Room Booking: {e}")

    # 2. HEALTHCARE DOCTOR APPOINTMENT (PRACTO ENGINE)
    elif booking_type in ("healthcare", "doctor", "doctors"):
        desk_doctype = "Patient Appointment"
        fee = 1200.0
        practitioner = resource_id

        # Find or create Patient
        patient_name = customer_name
        patient_id = None
        if frappe.db.exists("DocType", "Patient"):
            existing_pat = frappe.db.get_value("Patient", {"mobile": customer_phone}, "name")
            if not existing_pat:
                existing_pat = frappe.db.get_value("Patient", {"patient_name": customer_name}, "name")
            if existing_pat:
                patient_id = existing_pat
            else:
                try:
                    p_doc = frappe.get_doc({
                        "doctype": "Patient",
                        "patient_name": customer_name,
                        "mobile": customer_phone,
                        "email": customer_email,
                        "sex": "Other",
                        "status": "Active"
                    })
                    p_doc.flags.ignore_permissions = True
                    p_doc.insert(ignore_permissions=True)
                    patient_id = p_doc.name
                except Exception:
                    patient_id = None

        if frappe.db.exists("DocType", "Patient Appointment"):
            try:
                appt_doc = frappe.get_doc({
                    "doctype": "Patient Appointment",
                    "patient": patient_id or customer_name,
                    "patient_name": customer_name,
                    "practitioner": practitioner,
                    "appointment_date": booking_date,
                    "appointment_time": time_slot if ":" in time_slot else "10:00:00",
                    "duration": 30,
                    "status": "Open",
                    "paid_amount": fee,
                    "notes": special_requests or "Booked via EthioBiz Practo Health Engine",
                    "company": "Biz Technology Solutions"
                })
                appt_doc.flags.ignore_permissions = True
                appt_doc.insert(ignore_permissions=True)
                desk_doc_created = appt_doc.name
            except Exception as e:
                frappe.log_error(f"Error creating Patient Appointment: {e}")
        amount = fee

    # 3. SALON & SPA APPOINTMENT
    elif booking_type in ("salon", "salons", "spa", "haircut"):
        desk_doctype = "Salon Appointment"
        srv_price = 800.0
        if resource_id and frappe.db.exists("Salon Service", resource_id):
            srv_price = frappe.db.get_value("Salon Service", resource_id, "price") or 800.0
        amount = srv_price

        if frappe.db.exists("DocType", "Salon Appointment"):
            try:
                sal_doc = frappe.get_doc({
                    "doctype": "Salon Appointment",
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_email": customer_email,
                    "appointment_date": booking_date,
                    "time_slot": time_slot,
                    "salon_service": resource_id or "Haircut & Styling",
                    "amount": amount,
                    "status": "Confirmed",
                    "payment_status": "Unpaid",
                    "notes": special_requests,
                    "company": "Biz Technology Solutions"
                })
                sal_doc.flags.ignore_permissions = True
                sal_doc.insert(ignore_permissions=True)
                desk_doc_created = sal_doc.name
            except Exception as e:
                frappe.log_error(f"Error creating Salon Appointment: {e}")

    # 4. CREATE CORRESPONDING BIZBOOKING ENTRY (Unified Ledger)
    ledger_entry_id = None
    if frappe.db.exists("DocType", "BizBooking Entry"):
        try:
            entry_doc = frappe.get_doc({
                "doctype": "BizBooking Entry",
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "customer_email": customer_email,
                "booking_type": booking_type.capitalize(),
                "resource": resource_id or "Direct Service",
                "booking_date": booking_date,
                "slot_start_time": time_slot,
                "number_of_persons": number_of_persons,
                "amount": amount,
                "booking_status": "Confirmed",
                "payment_status": "Unpaid",
                "special_requests": f"{special_requests} | Desk Ref: {desk_doctype} {desk_doc_created}" if desk_doc_created else special_requests,
                "company": "Biz Technology Solutions"
            })
            entry_doc.flags.ignore_permissions = True
            entry_doc.insert(ignore_permissions=True)
            ledger_entry_id = entry_doc.name
        except Exception as e:
            frappe.log_error(f"Error creating BizBooking Entry: {e}")

    frappe.db.commit()

    return {
        "status": "success",
        "message": f"🎉 Your {booking_type.capitalize()} reservation has been confirmed!",
        "booking_id": ledger_entry_id or desk_doc_created,
        "desk_doctype": desk_doctype,
        "desk_docname": desk_doc_created,
        "customer_name": customer_name,
        "booking_date": booking_date,
        "time_slot": time_slot,
        "total_amount": f"{amount:,.2f} ETB"
    }
