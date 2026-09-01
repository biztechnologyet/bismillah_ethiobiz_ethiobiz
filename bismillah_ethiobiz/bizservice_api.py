# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizServices API — provider portfolio, availability, booking
status, and reviews for the BizServices module (Phase 6).

All endpoints are DB-first and defensive (DocTypes are runtime-created on this
server, so every access is guarded with frappe.db.exists / has_column).
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt, cstr, nowdate, getdate

_DOW = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def _has(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def _parse_slot_list(raw):
    """Parse a 'MON:09:00,10:00|09:30,14:00' string into {weekday_upper or '*': [hh:mm,...]}.

    A chunk is treated as per-day only when its leading token (before the colon) is
    one or more known weekdays (e.g. MON or MON,TUE) or '*'; otherwise the whole
    chunk is a plain time list (e.g. '09:00, 10:30').
    """
    out = {}
    raw = cstr(raw or "")
    for chunk in raw.split("|"):
        chunk = chunk.strip()
        if not chunk:
            continue
        head, _, tail = chunk.partition(":")
        head_clean = head.strip().upper()
        head_days = [d for d in (cstr(head_clean).split(",") if head_clean and head_clean != "*" else [head_clean]) if d]
        is_day_prefix = bool(head_days) and all(d == "*" or d in _DOW for d in head_days)
        if is_day_prefix and tail.strip():
            daykey = head_clean.replace(" ", "")
            times = tail
        else:
            daykey = "*"
            times = chunk
        parsed = []
        for t in cstr(times).split(","):
            t = t.strip()
            if len(t) == 4 and t.isdigit():        # 0930 -> 09:30
                t = f"{t[:2]}:{t[2:]}"
            if ":" in t:
                hh, mm = t.split(":", 1)
                if (hh.isdigit() and mm.isdigit()
                        and 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59):
                    parsed.append(f"{int(hh):02d}:{int(mm):02d}")
        if parsed:
            out.setdefault(daykey, set()).update(parsed)
    return {k: sorted(v) for k, v in out.items()}


def _resolve_time_slots(listing_name, date=None, practitioner=None):
    """Return the ordered list of bookable time slots for a service (and optionally a
    specific provider) on a date.

    Precedence (from most specific to fallback):
      1. provider custom_slots            (service + provider wise)
      2. listing custom_slots             (service wise)
      3. provider working_hours window    (provider wise window)
      4. listing practitioner windows
      5. default window 09:00-18:00
    Also respects slot_days (available weekdays) and days_off.
    """
    dt = getdate(date) if date else getdate(nowdate())
    if not hasattr(dt, "strftime"):
        dt = getdate(str(dt))
    dow = _DOW[dt.weekday()]  # MON..SUN from date.weekday() 0=Mon
    listing = None
    if listing_name and frappe.db.exists("BizService Listing", listing_name):
        listing = frappe.get_doc("BizService Listing", listing_name)

    providers = []
    if listing:
        providers = [p for p in (listing.get("practitioners") or []) if int(p.get("is_active") or 1)]
    if practitioner and providers:
        providers = [p for p in providers if cstr(p.get("practitioner_name")) == cstr(practitioner) or cstr(p.get("user")) == cstr(practitioner)]

    chosen_provider = providers[0] if providers else None

    def _slot_day_allowed(slot_days):
        if not slot_days:
            return True
        return dow in [d.strip().upper() for d in cstr(slot_days).split(",")]

    def _day_off(days_off):
        if not days_off:
            return False
        for raw in cstr(days_off).splitlines():
            raw = raw.strip()
            if not raw:
                continue
            raw = raw.upper()
            if raw in _DOW and raw == dow:
                return True
            if _is_iso(raw) and getdate(raw) == dt:
                return True
        return False

    slot_map = {}

    # 1) provider custom_slots (service + provider wise) — most specific
    if chosen_provider and chosen_provider.get("custom_slots"):
        if not _slot_day_allowed(chosen_provider.get("slot_days")) or _day_off(chosen_provider.get("days_off")):
            return {"slots": [], "source": "provider-off", "provider": practitioner}
        slot_map = _parse_slot_list(chosen_provider.get("custom_slots"))
        generated = slot_map.get(dow) or slot_map.get("*") or []
        return {"slots": sorted(set(generated)), "source": "provider-custom", "provider": practitioner}

    # 2) listing custom_slots (service wise)
    if listing and listing.get("custom_slots"):
        if not _slot_day_allowed(listing.get("slot_days")) or _day_off(listing.get("days_off")):
            return {"slots": [], "source": "service-off", "provider": practitioner}
        slot_map = _parse_slot_list(listing.get("custom_slots"))
        generated = slot_map.get(dow) or slot_map.get("*") or []
        return {"slots": sorted(set(generated)), "source": "service-custom", "provider": practitioner}

    # 3/4) working-hours windows from provider, then listing providers
    windows = []
    if chosen_provider and chosen_provider.get("working_hours"):
        windows.append(chosen_provider.get("working_hours"))
    elif listing and providers:
        for p in providers:
            if p.get("working_hours"):
                windows.append(p.get("working_hours"))
    if not windows:
        windows = ["09:00-18:00"]

    duration = int(listing.get("duration_minutes") or 30) if listing else 30
    generated = set()
    for wh in windows:
        for part in cstr(wh).split(","):
            part = part.strip()
            if "-" not in part:
                continue
            start, end = part.split("-", 1)
            try:
                sh, sm = [int(x) for x in start.strip().split(":")]
                eh, em = [int(x) for x in end.strip().split(":")]
            except Exception:
                continue
            cur = sh * 60 + sm
            endm = eh * 60 + em
            while cur < endm:
                generated.add(f"{cur // 60:02d}:{cur % 60:02d}")
                cur += max(15, duration)
    slots = sorted(generated)

    # Apply slot_days / days_off constraints — a specific chosen provider first,
    # then the service-level constraints, so both remain enforceable.
    if chosen_provider:
        if (not _slot_day_allowed(chosen_provider.get("slot_days"))
                or _day_off(chosen_provider.get("days_off"))):
            slots = []
    if listing:
        if (not _slot_day_allowed(listing.get("slot_days"))
                or _day_off(listing.get("days_off"))):
            slots = []

    return {"slots": slots, "source": "window", "provider": practitioner}


def _is_iso(day_str):
    s = cstr(day_str or "").strip()
    if len(s) != 10 or s.count("-") != 2:
        return False
    try:
        getdate(s)
        return True
    except Exception:
        return False


@frappe.whitelist(allow_guest=True)
def get_service_availability(listing=None, date=None, practitioner=None, service=None):
    """Return custom, per-service and per-service+provider bookable time slots.

    Slots are resolved in precedence order controlled by the provider from the
    Desk (service-wise custom slots on the listing, provider-wise custom slots on
    each assigned staff member), then filtered to the selected weekday/days-off and
    to times already booked (DB-first) for the same service and same provider.
    """
    listing = listing or service
    if not _has("BizService Listing"):
        return {"status": "success", "available": False, "slots": []}
    if not listing or not frappe.db.exists("BizService Listing", listing):
        return {"status": "error", "message": "Listing not found"}

    dt = date or nowdate()
    resolved = _resolve_time_slots(listing, date=dt, practitioner=practitioner)
    slots = resolved.get("slots", [])
    source = resolved.get("source", "window")

    # Knock out times already booked for this service/date
    if _has("BizService Booking"):
        booked = frappe.get_all(
            "BizService Booking",
            filters={"service": listing, "booking_date": dt,
                     "status": ["not in", ["Cancelled", "No-Show"]]},
            fields=["booking_time"]
        )
        booked_set = {str(b.get("booking_time") or "")[:5] for b in booked}
        slots = [s for s in slots if s not in booked_set]

    return {
        "status": "success",
        "listing": listing,
        "date": dt,
        "practitioner": practitioner,
        "source": source,
        "available": len(slots) > 0,
        "slots": slots,
    }


@frappe.whitelist(allow_guest=True)
def validate_time_slot(listing=None, date=None, time_slot=None, practitioner=None, service=None):
    """Validate that a requested time_slot is in the resolved custom slot set."""
    listing = listing or service
    if not _has("BizService Listing") or not listing or not frappe.db.exists("BizService Listing", listing):
        return {"status": "success", "valid": True, "reason": "listing-check-disabled"}
    resolved = _resolve_time_slots(listing, date=date, practitioner=practitioner)
    slots = resolved.get("slots", [])
    req = cstr(time_slot or "")[:5]
    if not req:
        return {"status": "success", "valid": True, "reason": "no-time-slot"}
    valid = req in slots
    if valid and _has("BizService Booking"):
        booked = frappe.get_all(
            "BizService Booking",
            filters={"service": listing, "booking_date": date,
                     "booking_time": req, "status": ["not in", ["Cancelled", "No-Show"]]},
            fields=["name"], limit=1
        )
        if booked:
            valid = False
    return {"status": "success", "valid": valid, "valid_slots": slots, "reason": "ok" if valid else "slot-closed-or-off"}



@frappe.whitelist(allow_guest=True)
def get_categories():
    """Return active BizService categories for the website portal."""
    if not _has("BizService Category"):
        return {"status": "success", "total": 0, "categories": []}
    cats = frappe.get_all(
        "BizService Category",
        filters={"is_active": 1},
        fields=["name", "category_name", "category_icon", "slug", "description"],
        order_by="category_name asc"
    )
    for c in cats:
        c["title"] = c.get("category_name") or c.get("name")
        c["listing_count"] = frappe.db.count(
            "BizService Listing",
            {"category": c["name"], "is_active": 1}
        ) if _has("BizService Listing") else 0
    return {"status": "success", "total": len(cats), "categories": cats}


@frappe.whitelist(allow_guest=True)
def get_provider_portfolio(company=None):
    """Return one provider's listings, bookings, and ratings for the portal/Desk."""
    if not _has("BizService Listing"):
        return {"status": "success", "company": company, "total": 0, "listings": [], "bookings": [], "rating_summary": {}}

    listing_filters = {"is_active": 1}
    if company:
        listing_filters["company"] = company

    listings = frappe.get_all(
        "BizService Listing",
        filters=listing_filters,
        fields=["name", "service_name", "category", "price", "price_type", "currency",
                "duration_minutes", "requires_travel", "serving_city", "serving_region",
                "featured", "average_rating", "total_bookings", "slug"],
        order_by="service_name asc"
    )
    for l in listings:
        l["title"] = l.get("service_name") or l.get("name")

    bookings = []
    if _has("BizService Booking") and company:
        bookings = frappe.get_all(
            "BizService Booking",
            filters={"company": company},
            fields=["name", "customer_name", "service", "status", "payment_status",
                    "booking_date", "booking_time", "total_amount", "rating"],
            order_by="booking_date desc"
        )

    ratings = frappe.db.sql("""
        SELECT COALESCE(AVG(rating),0) avg_rating, COUNT(*) cnt
        FROM `tabBizService Booking`
        WHERE rating IS NOT NULL AND rating > 0
    """, as_dict=True)
    summary = {}
    if ratings:
        summary = {"average_rating": flt(ratings[0].get("avg_rating")), "review_count": int(ratings[0].get("cnt") or 0)}

    return {
        "status": "success",
        "company": company,
        "total": len(listings),
        "listings": listings,
        "bookings": bookings,
        "rating_summary": summary,
    }


@frappe.whitelist()
def update_booking_status(booking=None, status=None):
    """Confirm / complete / cancel / no-show a BizService Booking (whitelisted)."""
    if not _has("BizService Booking"):
        frappe.throw("BizService Booking module not installed")
    if not booking or not frappe.db.exists("BizService Booking", booking):
        frappe.throw("Booking not found")
    valid = ["Pending", "Confirmed", "In-Progress", "Completed", "Cancelled", "No-Show"]
    if status not in valid:
        frappe.throw("Invalid status")

    doc = frappe.get_doc("BizService Booking", booking)
    doc.status = status
    doc.save(ignore_permissions=True)

    if status in ("Completed", "Cancelled", "No-Show") and doc.bizride_delivery:
        try:
            from bismillah_ethiobiz import bizride_api
            if status == "Cancelled":
                bizride_api.reject_delivery(doc.bizride_delivery, reason="Booking cancelled")
        except Exception as _e:
            frappe.log_error(f"BizRide sync on booking status {status}: {_e}", "BizService")

    return {"status": "success", "booking": booking, "booking_status": status}


@frappe.whitelist()
def submit_review(booking=None, rating=0, review=None):
    """Record a review; gated to Completed bookings when BizService Settings.enable.
    Recomputes the listing average_rating."""
    if not _has("BizService Booking"):
        frappe.throw("BizService Booking module not installed")
    if not booking or not frappe.db.exists("BizService Booking", booking):
        frappe.throw("Booking not found")

    doc = frappe.get_doc("BizService Booking", booking)
    try:
        gate = frappe.db.get_single_value("BizService Settings", "review_gating")
    except Exception:
        gate = 1
    if int(gate or 1) and doc.status != "Completed":
        frappe.throw("Reviews are only allowed after the booking is Completed")

    doc.rating = flt(rating or 0) / 5.0 if flt(rating or 0) > 5 else flt(rating or 0)
    doc.review = review or ""
    doc.save(ignore_permissions=True)

    # Recompute listing average_rating from all reviews (DB-first)
    if doc.service and _has("BizService Listing"):
        agg = frappe.db.sql("""
            SELECT COALESCE(AVG(rating),0) avg_r, COUNT(*) cnt
            FROM `tabBizService Booking`
            WHERE service=%s AND rating IS NOT NULL AND rating > 0
        """, (doc.service, ), as_dict=True)
        if agg:
            frappe.db.set_value(
                "BizService Listing", doc.service,
                {"average_rating": flt(agg[0].get("avg_r")),
                 "total_bookings": int(agg[0].get("cnt") or 0)},
                update_modified=False
            )

    return {"status": "success", "booking": booking, "rating": doc.rating, "review": doc.review}
