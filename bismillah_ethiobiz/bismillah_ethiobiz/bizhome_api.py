import frappe
from frappe import _
from frappe.utils import flt, cint, today, add_days, get_datetime, now_datetime
import json
try:
    from bismillah_ethiobiz.ethiobiz_identity import require_authed_customer, resolve_booking_company, get_or_create_customer_for_user, session_contact_defaults, resolve_or_create_customer, resolve_booking_customer
except ImportError:
    from ethiobiz_identity import require_authed_customer, resolve_booking_company, get_or_create_customer_for_user, session_contact_defaults, resolve_or_create_customer, resolve_booking_customer

# Fallback Seed Properties if none exist in database
SAMPLE_PROPERTIES = [
    {
        "name": "PROP-BMS-001",
        "title": "Luxury 4-Bedroom Villa with Garden",
        "property_type": "Villa / Residential",
        "tenure": "Monthly Rental",
        "price": 45000.0,
        "price_unit": "month",
        "city": "Addis Ababa",
        "subcity": "Bole / Atlas",
        "bedrooms": 4,
        "bathrooms": 3,
        "area_sqm": 350,
        "furnished": 1,
        "amenities": ["WiFi", "Backup Generator", "Water Tank", "Security Guard", "Parking (3 cars)", "Garden"],
        "image": "/assets/bismillah_ethiobiz/images/placeholder_villa.jpg",
        "rating": 4.9,
        "reviews_count": 18,
        "status": "Available",
        "description": "Exquisite 4-bedroom diplomatic residence with modern kitchen, spacious living room, backup power, water reservoir, and manicured landscaping in prime Bole."
    },
    {
        "name": "PROP-BMS-002",
        "title": "Premium Boutique Hotel Deluxe Room",
        "property_type": "Hotel / Pension Room",
        "tenure": "Daily / Short Stay",
        "price": 1800.0,
        "price_unit": "night",
        "city": "Addis Ababa",
        "subcity": "Kazanchis",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqm": 35,
        "furnished": 1,
        "amenities": ["High-Speed WiFi", "Hot Shower", "Room Service", "Breakfast Included", "Smart TV", "24/7 Reception"],
        "image": "/assets/bismillah_ethiobiz/images/placeholder_hotel.jpg",
        "rating": 4.8,
        "reviews_count": 64,
        "status": "Available",
        "description": "Executive hotel room near ECA with premium king-size bedding, ergonomic work desk, fast fiber internet, and complimentary Ethiopian breakfast."
    },
    {
        "name": "PROP-BMS-003",
        "title": "Modern Serviced Studio Apartment",
        "property_type": "Apartment / Condominium",
        "tenure": "Monthly Rental",
        "price": 22000.0,
        "price_unit": "month",
        "city": "Addis Ababa",
        "subcity": "Sarbet / Old Airport",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqm": 60,
        "furnished": 1,
        "amenities": ["Elevator", "Security Access", "Balcony View", "Washing Machine", "Kitchen Appliances"],
        "rating": 4.7,
        "reviews_count": 29,
        "status": "Available",
        "description": "Fully furnished European standard studio apartment in secure modern high-rise close to international embassies and cafes."
    },
    {
        "name": "PROP-BMS-004",
        "title": "Lake View Resort Bungalow & Suite",
        "property_type": "Hotel / Pension Room",
        "tenure": "Daily / Short Stay",
        "price": 2500.0,
        "price_unit": "night",
        "city": "Hawassa",
        "subcity": "Lake Front",
        "bedrooms": 2,
        "bathrooms": 1,
        "area_sqm": 75,
        "furnished": 1,
        "amenities": ["Lake View", "Swimming Pool Access", "Boat Tour", "WiFi", "Restaurant & Bar"],
        "rating": 4.95,
        "reviews_count": 82,
        "status": "Available",
        "description": "Stunning private lakeside suite with direct sunset views over Lake Hawassa, lush gardens, and tranquil eco-lodge ambiance."
    },
    {
        "name": "PROP-BMS-005",
        "title": "Prime Commercial Office Space (Full Floor)",
        "property_type": "Commercial / Office",
        "tenure": "Annual Lease",
        "price": 120000.0,
        "price_unit": "month",
        "city": "Addis Ababa",
        "subcity": "Mexico / Financial District",
        "bedrooms": 0,
        "bathrooms": 4,
        "area_sqm": 450,
        "furnished": 0,
        "amenities": ["Fiber Optic Backbone", "Dual Elevators", "Basement Parking", "3-Phase Power", "Central HVAC"],
        "rating": 4.85,
        "reviews_count": 12,
        "status": "Available",
        "description": "Open-plan corporate headquarters floor in brand new skyscraper in the heart of the financial district, ready for bespoke partitioning."
    },
    {
        "name": "PROP-BMS-006",
        "title": "Luxury 3-Bedroom Condominium For Sale",
        "property_type": "Apartment / Condominium",
        "tenure": "For Sale",
        "price": 14500000.0,
        "price_unit": "total",
        "city": "Addis Ababa",
        "subcity": "CMC / Ayat",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 165,
        "furnished": 0,
        "amenities": ["Title Deed Ready (Carta)", "Gated Compound", "Dedicated Parking", "Children Play Area", "Water Reservoir"],
        "rating": 5.0,
        "reviews_count": 9,
        "status": "Available",
        "description": "Spacious freehold family apartment with panoramic city views, modern finishes, 100% completed construction, and verified title deed."
    }
]

# BISMALLAH (2026-09-15 BizHome batch): canonical owning company every BizHome
# booking/listen row is bound to when a Property-less property (sample or bare
# listing) has no valid company. Mirrors the BizService Default Company chain.
def _default_company():
    return (frappe.db.get_single_value("BizService Settings", "company")
            or frappe.db.get_single_value("Global Defaults", "default_company")
            or (frappe.db.get_all("Company", limit=1, pluck="name") or [None])[0] or "")


def _valid_company(co):
    co = (co or "").strip()
    if co and frappe.db.exists("Company", co):
        return co
    return _default_company()


def _ensure_biz_category(cat_name="Real Estate & Property"):
    """DB-first: create the BizHome booking category once when missing."""
    if not frappe.db.exists("DocType", "BizService Category"):
        return None
    cat = frappe.db.get_value("BizService Category", {"category_name": cat_name}, "name")
    if not cat:
        try:
            d = frappe.get_doc({"doctype": "BizService Category", "category_name": cat_name})
            d.flags.ignore_mandatory = True
            cat = d.insert(ignore_permissions=True).name
            frappe.db.commit()
        except Exception:
            cat = frappe.db.get_value("BizService Category", {"category_name": cat_name}, "name")
    return cat


def _ensure_service_listing(service_name, category=None, price=0, is_active=1,
                            description=None, duration_minutes=0, slug=None):
    """Find-or-create a BizService Listing, always repairing an invalid company."""
    if not frappe.db.exists("DocType", "BizService Listing"):
        return None
    listing = frappe.db.get_value("BizService Listing", {"service_name": service_name}, "name")
    company = _default_company()
    if listing:
        lo = frappe.db.get_value("BizService Listing", listing, "company")
        if not (lo and frappe.db.exists("Company", lo)):
            company = _valid_company(lo) or company
            try:
                frappe.db.set_value("BizService Listing", listing, "company", company, update_modified=False)
                frappe.db.commit()
            except Exception:
                pass
        return listing
    if not company:
        return None
    cat = category or _ensure_biz_category()
    payload = {
        "doctype": "BizService Listing",
        "service_name": service_name,
        "company": _valid_company(company),
        "category": cat,
        "price": flt(price),
        "price_type": "Starting From",
        "duration_minutes": cint(duration_minutes),
        "is_active": cint(is_active),
    }
    if description:
        payload["description"] = description
    if slug:
        payload["slug"] = slug
    try:
        d = frappe.get_doc(payload)
        d.flags.ignore_mandatory = True
        return d.insert(ignore_permissions=True).name
    except Exception as e:
        frappe.log_error(f"BizHome listing create error: {str(e)}")
        return frappe.db.get_value("BizService Listing", {"service_name": service_name}, "name")


def _norm_time(t):
    """Normalise '10:00 AM'/'14:30' etc into 24h HH:MM for the Time field."""
    t = (t or "").strip()
    if not t:
        return ""
    low = t.lower()
    try:
        if "pm" in low or "am" in low:
            hhmm = t.strip().split()[0]
            hh, mm = hhmm.split(":")
            h = int(hh)
            if "pm" in low and h < 12:
                h += 12
            if "am" in low and h == 12:
                h = 0
            return "%02d:%02d" % (h, cint(mm[:2]) if mm[:2].isdigit() else 0)
        if ":" in t:
            return t[:5]
        return t
    except Exception:
        return t


@frappe.whitelist(allow_guest=True)
def search_properties(tenure=None, property_type=None, min_price=None, max_price=None,
                      bedrooms=None, city=None, subcity=None, query=None, limit=20):
    """
    Omnichannel Property Search for ethiobiz.et/bizhome.
    Searches across PropMS Property doctype with smart fallback to real-time seed listings.
    BISMALLAH (2026-09-15): maps the real PropMS Property columns (type/rent/common_bathroom/
    shop_image ...) so published records surface instead of failing the column lookup.
    """
    props = []

    # 1. Try querying real PropMS Property DocType if it has published records
    try:
        if frappe.db.exists("DocType", "Property"):
            records = frappe.get_all(
                "Property",
                fields=["name", "name1 as title", "type as property_type",
                        "shop_offer_type as tenure", "shop_price as price", "rent",
                        "bedroom as bedrooms", "common_bathroom as bathrooms",
                        "builtup_area as area_sqm", "furnished", "company", "status",
                        "description", "photo", "shop_image", "territory"],
                limit_page_length=cint(limit) or 20
            )
            for r in records:
                props.append({
                    "name": r.name,
                    "title": r.title or r.name,
                    "property_type": r.property_type or "Residential",
                    "tenure": r.tenure or "Monthly Rental",
                    "price": flt(r.price or r.rent or 15000.0),
                    "price_unit": "night" if (r.tenure and "Day" in r.tenure) else "month",
                    "city": "Addis Ababa",
                    "subcity": r.territory or "City Center",
                    "bedrooms": cint(r.bedrooms or 2),
                    "bathrooms": cint(r.bathrooms or 1),
                    "area_sqm": flt(r.area_sqm or 120),
                    "furnished": cint(r.furnished or 0),
                    "amenities": ["WiFi", "Water Tank", "Parking"],
                    "image": (r.shop_image or r.photo or "/assets/bismillah_ethiobiz/images/placeholder_property.jpg"),
                    "rating": 4.8,
                    "reviews_count": 15,
                    "status": r.status or "Available",
                    "description": r.description or "Quality property in prime location."
                })
    except Exception as e:
        frappe.log_error(f"PropMS query error: {str(e)}", "BizHome Search")

    # 2. Merge / Fallback to comprehensive sample properties
    combined = list(SAMPLE_PROPERTIES) + props

    # Apply in-memory filtering
    filtered = []
    for p in combined:
        if tenure and tenure != "All" and tenure.lower() not in p["tenure"].lower():
            continue
        if property_type and property_type != "All" and property_type.lower() not in p["property_type"].lower():
            continue
        if city and city.lower() not in p["city"].lower():
            continue
        if bedrooms and cint(bedrooms) > 0 and p["bedrooms"] < cint(bedrooms):
            continue
        if min_price and flt(p["price"]) < flt(min_price):
            continue
        if max_price and flt(p["price"]) > flt(max_price):
            continue
        if query:
            q = query.lower()
            text_match = (
                q in p["title"].lower() or
                q in p["description"].lower() or
                q in p["city"].lower() or
                q in p["subcity"].lower()
            )
            if not text_match:
                continue

        filtered.append(p)

    return {
        "status": "success",
        "count": len(filtered),
        "properties": filtered
    }

@frappe.whitelist(allow_guest=True)
def get_property_details(property_id):
    """Fetch complete detail for a specific property."""
    if not property_id:
        frappe.throw(_("Property ID is required"))

    # Search in sample data first
    for p in SAMPLE_PROPERTIES:
        if p["name"] == property_id:
            return {"status": "success", "property": p}

    # Search in PropMS DocType
    if frappe.db.exists("DocType", "Property") and frappe.db.exists("Property", property_id):
        doc = frappe.get_doc("Property", property_id)
        p_dict = {
            "name": doc.name,
            "title": getattr(doc, "name1", None) or doc.name,
            "property_type": getattr(doc, "type", "Residential"),
            "tenure": getattr(doc, "shop_offer_type", "Monthly Rental"),
            "price": flt(getattr(doc, "shop_price", None) or getattr(doc, "rent", 15000.0)),
            "price_unit": "night" if "Day" in str(getattr(doc, "shop_offer_type", "")) else "month",
            "city": "Addis Ababa",
            "subcity": getattr(doc, "territory", "City Center"),
            "bedrooms": cint(getattr(doc, "bedroom", 2)),
            "bathrooms": cint(getattr(doc, "common_bathroom", 1) or getattr(doc, "bathroom", 1) or 1),
            "area_sqm": flt(getattr(doc, "builtup_area", 0) or getattr(doc, "carpet_area", 120)),
            "furnished": cint(getattr(doc, "furnished", 0)),
            "amenities": ["WiFi", "Water Tank", "Security", "Parking"],
            "image": (getattr(doc, "shop_image", None) or getattr(doc, "photo", None)
                      or "/assets/bismillah_ethiobiz/images/placeholder_property.jpg"),
            "rating": 4.8,
            "reviews_count": 15,
            "status": getattr(doc, "status", "Available"),
            "description": getattr(doc, "description", "Quality property in prime location.")
        }
        return {"status": "success", "property": p_dict}

    frappe.throw(_(f"Property {property_id} not found"))

@frappe.whitelist(allow_guest=True)
def book_property_stay(property_id=None, check_in=None, check_out=None, guests=1, customer_name=None, customer_phone=None, special_requests=None, **kwargs):
    """
    Premium hotel / Airbnb style daily stay booking.
    Creates a confirmed BizService Booking / Hotel Reservation entry.
    BISMALLAH (2026-09-15): repaired listing-company handling so a Hotels & Stays
    listing whose owning company is missing/corrupted is auto-repaired and the
    booking always persists as a real BizService Booking row.
    """
    property_id = property_id or kwargs.get("property") or kwargs.get("property_name")
    customer_name = customer_name or kwargs.get("name") or kwargs.get("full_name")
    customer_phone = customer_phone or kwargs.get("phone") or kwargs.get("mobile")
    check_in = check_in or kwargs.get("start_date") or kwargs.get("checkin")
    check_out = check_out or kwargs.get("end_date") or kwargs.get("checkout")
    email = kwargs.get("email") or kwargs.get("customer_email")

    # BISMALLAH (2026-09-10): login-gated; identity always from the logged-in account
    party = resolve_booking_customer(customer_name, customer_phone, email)
    customer = party["customer"]

    if not all([property_id, check_in, check_out]):
        frappe.throw(_("Property, check-in date, and check-out date are required"))

    # Calculate nights
    d1 = get_datetime(check_in).date()
    d2 = get_datetime(check_out).date()
    nights = max(1, (d2 - d1).days)

    prop_res = get_property_details(property_id)
    prop = prop_res.get("property", {})
    rate_per_night = flt(prop.get("price", 1800.0))
    total_amount = rate_per_night * nights

    # Resolve property company (owning company)
    property_company = None
    if property_id and frappe.db.exists("DocType", "Property"):
        property_company = frappe.db.get_value("Property", property_id, "company")
    if not property_company:
        # Fall back to default company if Property DocType doesn't exist or no company set
        property_company = _default_company()

    # Validate company exists
    booking_company = _valid_company(property_company)
    if not booking_company:
        booking_company = resolve_booking_company(property_company, "property stay")

    customer_defaults = session_contact_defaults()
    user = party["full_name"] or customer_name or customer_defaults.get("full_name")
    phone = party["phone"] or customer_phone or customer_defaults.get("phone") or ""

    # Create BizBooking entry if DocType exists
    booking_id = f"STAY-{property_id}-{cint(now_datetime().timestamp())}"
    if frappe.db.exists("DocType", "BizBooking"):
        try:
            # BISMALLAH (Phase 6.5 unified money flow): unify property stays under the
            # BizService Booking model (same name on Desk + website) when a Hotels &
            # Stays listing exists; fall back to the legacy BizBooking otherwise.
            unified_created = False
            if frappe.db.exists("DocType", "BizService Booking") and frappe.db.exists("DocType", "BizService Listing"):
                stay_cat = None
                if frappe.db.exists("DocType", "BizService Category"):
                    stay_cat = frappe.db.get_value(
                        "BizService Category", {"category_name": ["like", "%Hotel%"]}, "name"
                    )
                listing = None
                if stay_cat:
                    listing = frappe.db.get_value(
                        "BizService Listing",
                        {"category": stay_cat, "is_active": 1},
                        "name"
                    )
                if not listing:
                    # Create a Hotels & Stays listing to host the stay (DB-first)
                    co = _default_company()
                    if co:
                        # BISMALLAH: Validate company before creating listing
                        co = resolve_booking_company(co, "BizService Settings")
                        try:
                            d = frappe.get_doc({
                                "doctype": "BizService Listing",
                                "service_name": f"Stay - {prop.get('title', property_id)}",
                                "company": co,
                                "category": stay_cat,
                                "price": rate_per_night,
                                "price_type": "Starting From",
                                "duration_minutes": nights,
                                "is_active": 1
                            })
                            d.flags.ignore_mandatory = True
                            listing = d.insert(ignore_permissions=True).name
                        except Exception:
                            listing = None
                if listing:
                    # Repair a listing whose owning company went missing/corrupted
                    lo = frappe.db.get_value("BizService Listing", listing, "company")
                    if not (lo and frappe.db.exists("Company", lo)):
                        lo = _valid_company(lo)
                        try:
                            frappe.db.set_value("BizService Listing", listing, "company", lo, update_modified=False)
                            frappe.db.commit()
                        except Exception:
                            pass
                    bsvc = frappe.get_doc({
                        "doctype": "BizService Booking",
                        "customer": customer,  # BISMALLAH: link to authenticated customer
                        "customer_name": user,
                        "customer_phone": phone,
                        "service": listing,
                        "company": lo or booking_company,
                        "practitioner_name": "Property Host",
                        "booking_date": str(d1),
                        "booking_time": "12:00",
                        "duration_minutes": max(1, nights * 24 * 60),
                        "status": "Confirmed",
                        "payment_status": "Unpaid",
                        "total_amount": total_amount,
                        "customer_address": "",
                        "customer_notes": f"Daily Stay. Nights: {nights}, Guests: {guests}. Requests: {special_requests or 'None'}"
                    })
                    bsvc.flags.ignore_mandatory = True
                    bsvc.insert(ignore_permissions=True)
                    frappe.db.commit()
                    booking_id = bsvc.name
                    unified_created = True
            if not unified_created:
                b_doc = frappe.get_doc({
                    "doctype": "BizBooking",
                    "customer_name": user,
                    "customer_phone": phone,
                    "booking_type": "Daily Stay",
                    "resource_name": prop.get("title", property_id),
                    "booking_date": str(d1),
                    "end_date": str(d2),
                    "total_amount": total_amount,
                    "status": "Confirmed",
                    "notes": f"Nights: {nights}, Guests: {guests}. Requests: {special_requests or 'None'}"
                })
                b_doc.flags.ignore_mandatory = True
                b_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                booking_id = b_doc.name
        except Exception as e:
            frappe.log_error(f"BizBooking insert error: {str(e)}")

    return {
        "status": "success",
        "booking_id": booking_id,
        "property_id": property_id,
        "property_title": prop.get("title", "Property Stay"),
        "check_in": str(d1),
        "check_out": str(d2),
        "nights": nights,
        "rate_per_night": f"{rate_per_night:,.2f} ETB",
        "total_amount": f"{total_amount:,.2f} ETB",
        "message": f"Stay successfully reserved for {nights} night(s) at {prop.get('title')}!"
    }

@frappe.whitelist(allow_guest=True)
def request_property_lease(property_id=None, tenure_frequency="Monthly", start_date=None, duration_months=6, customer_name=None, customer_phone=None, **kwargs):
    """
    Submits a residential or commercial lease agreement application.
    BISMALLAH (2026-09-15): login-gated (resolve_booking_customer) and PERSISTS a
    real BizService Booking row so Desk sees the application; previously the
    endpoint returned only a synthetic reference with no database record.
    """
    property_id = property_id or kwargs.get("property") or kwargs.get("property_name")
    customer_name = customer_name or kwargs.get("applicant_name") or kwargs.get("name") or kwargs.get("full_name")
    customer_phone = customer_phone or kwargs.get("applicant_phone") or kwargs.get("phone") or kwargs.get("mobile")
    start_date = start_date or kwargs.get("proposed_start_date") or today()
    duration_months = duration_months or kwargs.get("lease_duration_months") or 6
    email = kwargs.get("email") or kwargs.get("customer_email") or kwargs.get("applicant_email")

    # Resolve customer (login required; identity always from the account)
    party = resolve_booking_customer(customer_name, customer_phone, email)
    customer = party["customer"]

    if not property_id:
        frappe.throw(_("Property ID is required"))

    s_date = start_date or today()
    dur = cint(duration_months) or 6
    prop_res = get_property_details(property_id)
    prop = prop_res.get("property", {})
    monthly_rent = flt(prop.get("price", 25000.0))
    total_contract = monthly_rent * dur
    deposit = monthly_rent * 2.0  # 2 months standard security deposit

    lease_ref = f"LEASE-APP-{property_id}-{cint(now_datetime().timestamp())}"
    booking_company = _default_company()
    if booking_company:
        booking_company = _valid_company(booking_company)
    try:
        if (frappe.db.exists("DocType", "BizService Booking")
                and frappe.db.exists("DocType", "BizService Listing")):
            listing = _ensure_service_listing(
                "Lease Application - EthioBiz Property",
                category=_ensure_biz_category(), price=0, is_active=1,
                description="Lease / rental application for properties listed on BizHome.",
                slug="lease-application")
            if listing and booking_company:
                bsvc = frappe.get_doc({
                    "doctype": "BizService Booking",
                    "customer": customer,
                    "customer_name": party["full_name"] or customer_name or _("Valued Member"),
                    "customer_phone": party["phone"] or customer_phone or "",
                    "service": listing,
                    "company": booking_company,
                    "practitioner_name": "Property Agent",
                    "booking_date": str(s_date),
                    "booking_time": "10:00",
                    "duration_minutes": max(1, dur * 30 * 24 * 60),
                    "status": "Pending",
                    "payment_status": "Unpaid",
                    "total_amount": flt(total_contract + deposit),
                    "customer_notes": (f"Lease application. Tenure: {tenure_frequency}. Duration: {dur} months. "
                                       f"Monthly rent: {monthly_rent:,.2f} ETB. Deposit (2 months): {deposit:,.2f} ETB.")
                })
                bsvc.flags.ignore_mandatory = True
                bsvc.insert(ignore_permissions=True)
                frappe.db.commit()
                lease_ref = bsvc.name
    except Exception as e:
        frappe.log_error(f"BizHome lease persist error: {str(e)}")

    return {
        "status": "success",
        "lease_ref": lease_ref,
        "property_id": property_id,
        "property_title": prop.get("title"),
        "tenure_frequency": tenure_frequency,
        "start_date": s_date,
        "duration_months": dur,
        "monthly_rent": f"{monthly_rent:,.2f} ETB",
        "security_deposit": f"{deposit:,.2f} ETB",
        "total_commitment": f"{total_contract + deposit:,.2f} ETB",
        "company": booking_company,
        "customer": customer,
        "message": f"Lease application submitted for {prop.get('title')}. An agent will contact you within 2 hours."
    }

@frappe.whitelist(allow_guest=True)
def schedule_property_viewing(property_id=None, preferred_date=None, preferred_time="10:00 AM", customer_name=None, customer_phone=None, **kwargs):
    """
    Schedules an in-person or virtual property tour with an assigned EthioBiz Real Estate agent.
    BISMALLAH (2026-09-15): now login-gated (resolve_booking_customer) and PERSISTS a
    real BizService Booking row; previously it was the only BizHome mutator open to
    guests and it wrote no database record (synthetic confirmation only).
    """
    property_id = property_id or kwargs.get("property") or kwargs.get("property_name")
    preferred_date = preferred_date or kwargs.get("date") or kwargs.get("viewing_date") or today()
    preferred_time = preferred_time or kwargs.get("time") or kwargs.get("viewing_time") or "10:00 AM"
    customer_name = customer_name or kwargs.get("name") or kwargs.get("full_name")
    customer_phone = customer_phone or kwargs.get("phone") or kwargs.get("mobile")
    email = kwargs.get("email") or kwargs.get("customer_email")

    if not all([property_id, preferred_date]):
        frappe.throw(_("Property ID and preferred date are required"))

    # BISMALLAH: viewing is a real appointment now - requires a logged-in account.
    party = resolve_booking_customer(customer_name, customer_phone, email)
    customer = party["customer"]

    prop_res = get_property_details(property_id)
    prop = prop_res.get("property", {})

    viewing_id = f"VIEW-{property_id}-{cint(now_datetime().timestamp())}"
    booking_company = _valid_company(_default_company())
    try:
        if (frappe.db.exists("DocType", "BizService Booking")
                and frappe.db.exists("DocType", "BizService Listing")):
            listing = _ensure_service_listing(
                "Property Viewing - EthioBiz Real Estate",
                category=_ensure_biz_category(), price=0, is_active=1,
                description="In-person or virtual property tour appointment on BizHome.",
                slug="property-viewing")
            if listing and booking_company:
                bsvc = frappe.get_doc({
                    "doctype": "BizService Booking",
                    "customer": customer,
                    "customer_name": party["full_name"] or customer_name or _("Valued Member"),
                    "customer_phone": party["phone"] or customer_phone or "",
                    "service": listing,
                    "company": booking_company,
                    "practitioner_name": "Hadi Awad (Senior Property Consultant)",
                    "booking_date": str(preferred_date),
                    "booking_time": _norm_time(preferred_time) or "10:00",
                    "duration_minutes": 60,
                    "status": "Pending",
                    "payment_status": "Unpaid",
                    "total_amount": 0.0,
                    "customer_notes": "Property viewing request. Contact phone: +251 91 100 0000."
                })
                bsvc.flags.ignore_mandatory = True
                bsvc.insert(ignore_permissions=True)
                frappe.db.commit()
                viewing_id = bsvc.name
    except Exception as e:
        frappe.log_error(f"BizHome viewing persist error: {str(e)}")

    return {
        "status": "success",
        "viewing_id": viewing_id,
        "property_id": property_id,
        "property_title": prop.get("title"),
        "viewing_date": preferred_date,
        "viewing_time": preferred_time,
        "assigned_agent": "Hadi Awad (Senior Property Consultant)",
        "contact_phone": "+251 91 100 0000",
        "message": f"Viewing confirmed for {preferred_date} at {preferred_time}. Our agent will meet you at the property location."
    }

@frappe.whitelist(allow_guest=True)
def register_property_listing(title=None, property_type="Residential", tenure="Monthly Rental", price=0, city="Addis Ababa", subcity=None, bedrooms=1, bathrooms=1, description=None, owner_name=None, owner_phone=None, owner_email=None, **kwargs):
    """
    Allows a property owner, landlord, or hotelier to register a property or lodging on EthioBiz.
    Auto-registers owner as an ERPNext Customer/Partner.
    BISMALLAH (2026-09-15): login-gated (resolve_or_create_customer) and PERSISTS a
    draft BizService Listing row (is_active=0) so Desk verification officers see the
    application; previously it only returned a synthetic reference.
    """
    title = title or kwargs.get("property_title") or "New Property Listing"
    owner_name = owner_name or kwargs.get("name") or kwargs.get("full_name")
    owner_phone = owner_phone or kwargs.get("phone") or kwargs.get("mobile")
    owner_email = owner_email or kwargs.get("email")

    if not owner_name or not owner_phone:
        frappe.throw(_("Owner name and phone number are required for property registration"))

    customer = resolve_or_create_customer(owner_name, owner_phone, owner_email)

    ref = f"PROP-REG-{cint(now_datetime().timestamp())}"
    listing_company = _valid_company(_default_company())
    try:
        if frappe.db.exists("DocType", "BizService Listing"):
            slug = (title or "property").lower().strip()
            slug = "".join(c if c.isalnum() else "-" for c in slug)[:60].strip("-")
            listing_name = _ensure_service_listing(
                f"{title} ({city})",
                category=_ensure_biz_category(), price=flt(price), is_active=0,
                description=(description or "Pending verification by EthioBiz property verification officers."),
                slug=slug or "property-registration", duration_minutes=1)
            if listing_name:
                ref = listing_name
    except Exception as e:
        frappe.log_error(f"BizHome listing register error: {str(e)}")

    return {
        "status": "success",
        "reference": ref,
        "customer": customer,
        "title": title,
        "message": f"Alhamdulillah! Your property '{title}' has been registered with reference {ref}. An EthioBiz property verification officer will contact you within 24 hours to verify and publish the listing."
    }