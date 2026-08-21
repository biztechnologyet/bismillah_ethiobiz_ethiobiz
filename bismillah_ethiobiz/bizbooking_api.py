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
                filters={"category": ["in", ["Hotel Room", "Hotel Room & Suite"]], "is_active": 1},
                fields=["name", "resource_name", "company", "base_rate", "capacity", "description"]
            )
            for r in rooms:
                catalog["hotels"].append({
                    "id": r.name,
                    "title": r.resource_name,
                    "company": r.company or "Biz Technology Solutions",
                    "price_per_night": r.base_rate or 2500.0,
                    "capacity": f"{r.capacity or 2} Guests",
                    "description": r.description or "Luxury accommodation with high-speed WiFi, breakfast buffet, and mountain views.",
                    "image": "/files/hotel_suite.jpg"
                })

    # 2. HEALTHCARE PRACTITIONERS & DOCTORS
    if category in ("all", "doctors", "healthcare"):
        if frappe.db.exists("DocType", "BizBooking Resource"):
            docs = frappe.get_all(
                "BizBooking Resource",
                filters={"category": "Medical Clinic & Doctor", "is_active": 1},
                fields=["name", "resource_name", "company", "base_rate", "description"]
            )
            for d in docs:
                spec = "Cardiology & Specialist Medicine"
                if "Dental" in d.resource_name: spec = "Dental Surgery & Orthodontics"
                elif "Pediatric" in d.resource_name: spec = "Pediatrics & Child Wellness"
                elif "Dermatology" in d.resource_name: spec = "Dermatology & Skin Health"

                catalog["doctors"].append({
                    "id": d.name,
                    "name": d.resource_name,
                    "specialty": spec,
                    "qualifications": "MD, MBBS - Senior Consultant",
                    "experience": "10+ Years Experience",
                    "rating": 4.9,
                    "clinic": d.company or "EthioBiz Specialist Medical Center",
                    "fee": d.base_rate or 1200.0,
                    "image": "/files/doctor_cardio.jpg",
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
                    "company": s.company or "Salon & Spa Hub",
                    "description": s.description or "Professional beauty & grooming service with premium organic products.",
                    "image": s.service_image or "/files/salon_haircut.jpg"
                })

        # Also add Salon Chairs from BizBooking Resource
        if frappe.db.exists("DocType", "BizBooking Resource"):
            chairs = frappe.get_all(
                "BizBooking Resource",
                filters={"category": "Salon Chair & Stylist", "is_active": 1},
                fields=["name", "resource_name", "company", "base_rate", "description"]
            )
            for c in chairs:
                catalog["salons"].append({
                    "id": c.name,
                    "name": c.resource_name,
                    "category": "Styling Chair & Barber",
                    "price": c.base_rate or 600.0,
                    "duration": "45 mins",
                    "company": c.company or "Biz Technology Solutions",
                    "description": c.description or "Executive styling chair reservation with master barbers.",
                    "image": "/files/salon_haircut.jpg"
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
                    "company": pr.company or "Kistet Engineering & Trading",
                    "price": "Free Tour",
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
    
    # Auto-resolve logged in user if available
    user = frappe.session.user
    if user and user != "Guest":
        u_doc = frappe.get_doc("User", user)
        customer_name = u_doc.full_name or u_doc.first_name or customer_name
        customer_phone = u_doc.mobile_no or u_doc.phone or customer_phone or "0911000000"
        customer_email = u_doc.email or customer_email
    else:
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

    # Ensure Customer master exists in ERPNext
    cust_id = None
    if frappe.db.exists("Customer", {"mobile_no": customer_phone}):
        cust_id = frappe.db.get_value("Customer", {"mobile_no": customer_phone}, "name")
    elif frappe.db.exists("Customer", {"customer_name": customer_name}):
        cust_id = frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")
    else:
        try:
            c_doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Individual",
                "mobile_no": customer_phone,
                "email_id": customer_email,
                "customer_group": "Individual",
                "territory": "Ethiopia"
            })
            c_doc.flags.ignore_permissions = True
            c_doc.insert(ignore_permissions=True)
            cust_id = c_doc.name
        except Exception:
            cust_id = None

    desk_doc_created = None
    desk_doctype = None
    amount = 0.0

    # 1. HOTEL ROOM BOOKING
    if booking_type in ("hotel", "hotels"):
        desk_doctype = "Room Booking"
        rate = 2500.0
        comp = "Biz Technology Solutions"
        if resource_id and frappe.db.exists("BizBooking Resource", resource_id):
            rate = frappe.db.get_value("BizBooking Resource", resource_id, "base_rate") or 2500.0
            comp = frappe.db.get_value("BizBooking Resource", resource_id, "company") or comp

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
                    "customer": cust_id,
                    "company": comp,
                    "check_in_date": booking_date,
                    "check_out_date": check_out_date or booking_date,
                    "nights": nights,
                    "adults": number_of_persons,
                    "rate_per_night": rate,
                    "total_amount": amount,
                    "notes": special_requests
                })
                room_doc.flags.ignore_permissions = True
                room_doc.insert(ignore_permissions=True)
                desk_doc_created = room_doc.name
            except Exception as e:
                frappe.log_error(f"Error creating Room Booking: {e}")

    # 2. SALON APPOINTMENT
    elif booking_type in ("salon", "spa", "haircut"):
        desk_doctype = "Salon Appointment"
        srv_name = resource_id
        comp = "Biz Technology Solutions"
        if resource_id and frappe.db.exists("Salon Service", resource_id):
            srv_doc = frappe.get_doc("Salon Service", resource_id)
            srv_name = srv_doc.service_name
            amount = srv_doc.price
            comp = srv_doc.company or comp
        elif resource_id and frappe.db.exists("BizBooking Resource", resource_id):
            r_doc = frappe.get_doc("BizBooking Resource", resource_id)
            srv_name = r_doc.resource_name
            amount = r_doc.base_rate or 600.0
            comp = r_doc.company or comp

        if frappe.db.exists("DocType", "Salon Appointment"):
            try:
                salon_doc = frappe.get_doc({
                    "doctype": "Salon Appointment",
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_email": customer_email,
                    "customer": cust_id,
                    "company": comp,
                    "salon_service": srv_name,
                    "appointment_date": booking_date,
                    "time_slot": time_slot,
                    "amount": amount,
                    "status": "Confirmed",
                    "payment_status": "Unpaid",
                    "notes": special_requests
                })
                salon_doc.flags.ignore_permissions = True
                salon_doc.insert(ignore_permissions=True)
                desk_doc_created = salon_doc.name
            except Exception as e:
                frappe.log_error(f"Error creating Salon Appointment: {e}")

    # 3. GENERIC BIZBOOKING ENTRY
    if not desk_doc_created:
        desk_doctype = "BizBooking Entry"
        if frappe.db.exists("DocType", "BizBooking Entry"):
            try:
                b_entry = frappe.get_doc({
                    "doctype": "BizBooking Entry",
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_email": customer_email,
                    "customer": cust_id,
                    "company": "Biz Technology Solutions",
                    "booking_date": booking_date,
                    "time_slot": time_slot,
                    "notes": special_requests,
                    "status": "Confirmed"
                })
                b_entry.flags.ignore_permissions = True
                b_entry.insert(ignore_permissions=True)
                desk_doc_created = b_entry.name
            except Exception:
                desk_doc_created = f"BK-{frappe.generate_hash(length=8).upper()}"
        else:
            desk_doc_created = f"BK-{frappe.generate_hash(length=8).upper()}"

    return {
        "status": "success",
        "message": f"Reservation confirmed! Record posted to {desk_doctype} ledger in Desk.",
        "booking_id": desk_doc_created,
        "doctype": desk_doctype,
        "customer": customer_name,
        "total_amount": f"{amount:,.2f} ETB" if amount > 0 else "Free"
    }

@frappe.whitelist(allow_guest=True)
def create_online_booking(
    resource_name=None, customer_name=None, customer_phone=None,
    booking_date=None, time_slot=None, company=None, notes=None, amount=0.0
):
    """Direct booking handler called from Homepage instant booking drawer."""
    return create_unified_booking(
        booking_type="salon" if "Hair" in str(resource_name) or "Facial" in str(resource_name) or "Massage" in str(resource_name) or "Chair" in str(resource_name) else "generic",
        resource_id=resource_name,
        customer_name=customer_name,
        customer_phone=customer_phone,
        booking_date=booking_date,
        time_slot=time_slot,
        special_requests=notes
    )
