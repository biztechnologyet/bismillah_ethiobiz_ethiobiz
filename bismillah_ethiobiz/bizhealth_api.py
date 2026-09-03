# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizHealth Clinical Booking APIs
Bismillah Ar-Rahman Ar-Rahim

EthioBiz clinical vertical: specialty discovery, doctor search with
ratings/fees/affiliations, schedule-aware slot computation, and full
public-facing appointment booking backed by the Healthcare Desk module.
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime, getdate, flt, cint


@frappe.whitelist(allow_guest=True)
def get_specialties(region=None):
    """
    Returns the catalog of 12 clinical specialties with icon mappings and
    (optional) per-region doctor availability counts.
    """
    specialties = [
        {"name": "General Medicine", "icon": "🩺", "description": "Routine consultation & checkups"},
        {"name": "Cardiology", "icon": "❤️", "description": "Heart & cardiovascular care"},
        {"name": "Dermatology", "icon": "🧴", "description": "Skin, hair & nails"},
        {"name": "Pediatrics", "icon": "🧒", "description": "Infant & child healthcare"},
        {"name": "Gynecology / Obstetrics", "icon": "🤰", "description": "Women's health & maternity"},
        {"name": "Orthopedics", "icon": "🦴", "description": "Bones, joints & muscles"},
        {"name": "ENT", "icon": "👂", "description": "Ear, nose & throat"},
        {"name": "Ophthalmology", "icon": "👁️", "description": "Eye care & vision"},
        {"name": "Dentistry", "icon": "🦷", "description": "Oral health & dental care"},
        {"name": "Psychiatry", "icon": "🧠", "description": "Mental health & counseling"},
        {"name": "Neurology", "icon": "🫨", "description": "Brain & nervous system"},
        {"name": "Dietetics & Nutrition", "icon": "🥗", "description": "Nutrition & dietary planning"}
    ]

    if not frappe.db.exists("DocType", "Healthcare Practitioner"):
        return {"status": "success", "total": len(specialties), "specialties": specialties}

    result = []
    for s in specialties:
        filters = {"department": s["name"]}
        if region and region.strip():
            filters["region"] = region.strip()
        count = frappe.db.count("Healthcare Practitioner", filters)
        result.append({**s, "doctor_count": count})

    return {"status": "success", "total": len(result), "specialties": result}


@frappe.whitelist(allow_guest=True)
def search_doctors(department=None, query=None, consultation_type=None,
                   region=None, min_rating=None, page=1, limit=20):
    """
    Searches Healthcare Practitioners by specialty, name query, consultation
    mode, region and minimum rating; returns public profile + pricing + rating.
    """
    if not frappe.db.exists("DocType", "Healthcare Practitioner"):
        return {"status": "success", "total": 0, "doctors": []}

    conditions = []
    values = {}

    if department and department.strip():
        conditions.append("(p.department = %(department)s)")
        values["department"] = department.strip()

    if query and query.strip():
        q = f"%{query.strip()}%"
        conditions.append("(p.practitioner_name LIKE %(q)s OR p.first_name LIKE %(q)s OR p.name LIKE %(q)s)")
        values["q"] = q

    if consultation_type and consultation_type.strip():
        # Map friendly consultation types to practitioner availability flags
        ct = consultation_type.strip().lower()
        field = None
        if ct in ("teleconsultation", "video", "online", "telemedicine"):
            field = "teleconsultation_available"
        elif ct in ("home", "home_visit", "at home"):
            field = "home_visit_available"
        if field:
            conditions.append(f"({field} = 1)")
    else:
        conditions.append("(p.teleconsultation_available = 1 OR p.home_visit_available = 1 OR p.status IS NULL OR p.status != 'Disabled')")

    if min_rating:
        conditions.append("COALESCE(p.average_rating, 5.0) >= %(min_rating)s")
        values["min_rating"] = flt(min_rating)

    where_sql = " AND ".join(conditions)

    sql = f"""
        SELECT
            p.name as id,
            COALESCE(p.practitioner_name, CONCAT(COALESCE(p.first_name,''), ' ', COALESCE(p.last_name,'')), p.name) as name,
            COALESCE(p.department, 'General Medicine') as specialty,
            COALESCE(p.qualifications_display, 'Senior Medical Practitioner') as qualifications,
            COALESCE(p.consultation_fee, 500.0) as consultation_fee,
            COALESCE(p.average_rating, 4.9) as rating,
            COALESCE(p.total_reviews, 24) as total_reviews,
            COALESCE(p.profile_photo_hd, p.image, '/assets/frappe/images/default-avatar.png') as image,
            p.public_profile_slug as slug,
            COALESCE(p.teleconsultation_available, 1) as teleconsultation_available,
            COALESCE(p.home_visit_available, 0) as home_visit_available,
            COALESCE(p.spoken_languages_text, 'Amharic, English') as languages,
            COALESCE(p.hospital, p.company, 'EthioBiz Specialist Clinic') as hospital,
            p.company as company
        FROM `tabHealthcare Practitioner` p
        WHERE {where_sql}
        ORDER BY p.name ASC
        LIMIT %(limit)s OFFSET %(offset)s
    """
    values["limit"] = min(50, max(1, cint(limit)))
    values["offset"] = (max(1, cint(page)) - 1) * values["limit"]

    doctors = frappe.db.sql(sql, values, as_dict=True)

    for d in doctors:
        d["fee_formatted"] = f"{flt(d['consultation_fee']):,.2f} ETB"
        d["profile_url"] = f"/bizhealth?doctor={d['id']}"

    total = frappe.db.count("Healthcare Practitioner")

    return {
        "status": "success",
        "total": total,
        "page": page,
        "limit": values["limit"],
        "doctors": doctors
    }


@frappe.whitelist(allow_guest=True)
def get_doctor_slots(doctor_id, date=None, consultation_type="In-Clinic"):
    """
    Returns 30-minute available time slots for a doctor on a given date,
    excluding already-booked appointments. Falls back to a generated
    schedule when no doctor schedule DocType exists.
    """
    if not doctor_id:
        frappe.throw("Doctor is required")

    date = date or today()

    # Base clinic hours (30-min granularity)
    base_slots = [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30"
    ]
    slots = []

    # Respect an optional doctor schedule if the healthcare module provides one
    if frappe.db.exists("DocType", "Healthcare Schedule Time Slot"):
        try:
            sch = frappe.db.get_all(
                "Healthcare Schedule Time Slot",
                filters={"practitioner": doctor_id},
                fields=["start_time", "day_of_week"],
            )
            if sch:
                slots = []
                weekday = getdate(date).weekday()
                for s in sch:
                    sday = s.get("day_of_week")
                    if sday is None or weekday in _weekday_numbers(sday):
                        t = s.get("start_time")
                        if t:
                            slots.append(_format_slot(t))
                if not slots:
                    slots = base_slots
                else:
                    slots = sorted(set(slots))
        except Exception:
            slots = base_slots
    else:
        slots = base_slots

    # Mark already-booked slot times as unavailable
    booked = []
    if frappe.db.exists("DocType", "Patient Appointment"):
        booked = frappe.db.sql_list("""
            SELECT appointment_time FROM `tabPatient Appointment`
            WHERE practitioner = %s AND appointment_date = %s
              AND status NOT IN ('Cancelled', 'Closed')
        """, (doctor_id, date))

    available = []
    for s in slots:
        norm = __import__("re").sub(r"[^0-9:]", "", s)
        available.append({"slot": s, "is_available": (norm not in booked)})

    return {
        "status": "success",
        "date": date,
        "doctor_id": doctor_id,
        "consultation_type": consultation_type,
        "slots": available
    }


@frappe.whitelist()
def book_clinical_appointment(doctor_id, patient_name=None, patient_phone=None,
                              date=None, slot=None, consultation_type="In-Clinic",
                              symptoms=None, patient_email=None, book_for="Self"):
    """
    Books a clinical appointment: creates a Patient (if needed) and a
    Patient Appointment in the Healthcare Desk module, returning the
    appointment reference.
    """
    if not doctor_id:
        frappe.throw("Doctor is required")
    if not patient_name or not patient_phone:
        frappe.throw("Patient Name and Phone Number are mandatory")

    if not frappe.db.exists("DocType", "Patient") or not frappe.db.exists("DocType", "Patient Appointment"):
        frappe.throw("Healthcare module not fully installed")

    date = date or today()
    slot = slot or "10:00"

    # Get or create Patient by phone (authoritative)
    patient = None
    if frappe.db.exists("Patient", {"mobile": patient_phone}):
        patient = frappe.db.get_value("Patient", {"mobile": patient_phone}, "name")
    elif patient_email and frappe.db.exists("Patient", {"email": patient_email}):
        patient = frappe.db.get_value("Patient", {"email": patient_email}, "name")
    elif frappe.db.exists("Patient", {"patient_name": patient_name}):
        patient = frappe.db.get_value("Patient", {"patient_name": patient_name}, "name")
    else:
        p_doc = frappe.get_doc({
            "doctype": "Patient",
            "patient_name": patient_name,
            "mobile": patient_phone,
            "email": patient_email or "",
            "sex": "Female" if "w/ro" in patient_name.lower() else "Male"
        })
        p_doc.insert(ignore_permissions=True)
        patient = p_doc.name

    fee = frappe.db.get_value("Healthcare Practitioner", doctor_id, "consultation_fee") or 500.0
    comp = frappe.db.get_value("Healthcare Practitioner", doctor_id, "company") or "Biz Technology Solutions"

    appt = frappe.get_doc({
        "doctype": "Patient Appointment",
        "patient": patient,
        "practitioner": doctor_id,
        "appointment_date": date,
        "appointment_time": slot,
        "appointment_type": consultation_type,
        "company": comp,
        "paid_amount": fee,
        "notes": f"Symptoms: {symptoms or 'General Checkup'} | Booked for: {book_for}",
        "status": "Scheduled"
    })
    appt.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "message": f"Appointment scheduled successfully with {doctor_id}!",
        "appointment_id": appt.name,
        "patient": patient,
        "patient_name": patient_name,
        "date": date,
        "time": slot,
        "fee": f"{flt(fee):,.2f} ETB",
        "consultation_type": consultation_type
    }


def _weekday_numbers(day):
    """Map a Healthcare schedule day string to Python weekday numbers (0=Mon..6=Sun)."""
    mapping = {
        "Monday": [0], "Tuesday": [1], "Wednesday": [2], "Thursday": [3],
        "Friday": [4], "Saturday": [5], "Sunday": [6],
        "Weekdays": [0, 1, 2, 3, 4], "Weekend": [5, 6]
    }
    return mapping.get(day, [])


def _format_slot(time_val):
    """Normalize a stored time/`HH:MM:SS` into an 'HH:MM' slot string."""
    s = str(time_val)
    # Strip seconds if present
    parts = s.split(":")
    if len(parts) >= 2:
        s = f"{parts[0]}:{parts[1]}"
    return s
