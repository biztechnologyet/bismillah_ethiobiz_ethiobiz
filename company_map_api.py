import json
import os
import frappe
from frappe.utils import flt, cstr
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_company_map_fields():
    """Adds GPS and location fields to Company DocType for WebShop Map View."""
    custom_fields = {
        "Company": [
            {
                "fieldname": "location_section",
                "fieldtype": "Section Break",
                "label": "WebShop Map & Location",
                "insert_after": "domain",
                "collapsible": 1
            },
            {
                "fieldname": "show_on_map",
                "fieldtype": "Check",
                "label": "Show on WebShop Map",
                "default": "1",
                "insert_after": "location_section",
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            {
                "fieldname": "business_category",
                "fieldtype": "Select",
                "label": "Business Category",
                "options": "\nHotel & Lodging\nRestaurant & Cafe\nRetail & Supermarket\nSalon & Beauty\nClinic & Healthcare\nReal Estate & Property\nIT & Professional Services\nOther",
                "insert_after": "show_on_map",
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            {
                "fieldname": "col_break_loc1",
                "fieldtype": "Column Break",
                "insert_after": "business_category"
            },
            {
                "fieldname": "latitude",
                "fieldtype": "Float",
                "label": "Latitude",
                "precision": "7",
                "insert_after": "col_break_loc1"
            },
            {
                "fieldname": "longitude",
                "fieldtype": "Float",
                "label": "Longitude",
                "precision": "7",
                "insert_after": "latitude"
            },
            {
                "fieldname": "gps_accuracy",
                "fieldtype": "Float",
                "label": "GPS Accuracy (Meters)",
                "read_only": 1,
                "insert_after": "longitude"
            },
            {
                "fieldname": "sec_break_loc2",
                "fieldtype": "Section Break",
                "insert_after": "gps_accuracy"
            },
            {
                "fieldname": "location_address",
                "fieldtype": "Small Text",
                "label": "Location Description / Landmark",
                "insert_after": "sec_break_loc2"
            },
            {
                "fieldname": "map_location",
                "fieldtype": "Geolocation",
                "label": "Map Pin Location",
                "insert_after": "location_address"
            },
            {
                "fieldname": "sec_break_multi_pin",
                "fieldtype": "Section Break",
                "label": "Multiple Branch Map Pins (Showroom / Factory / Branches)",
                "insert_after": "map_location",
                "collapsible": 1
            },
            {
                "fieldname": "company_locations",
                "fieldtype": "Table",
                "label": "Company Locations (Multiple Map Pins)",
                "options": "BizCompany Location",
                "insert_after": "sec_break_multi_pin",
                "description": "Add one row per map pin: Addis Ababa Branch, Hawasa Branch, Main Showroom, Factory, Warehouse, etc. Each row is a separate pin on the map."
            }
        ]
    }
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
    print("Company GPS and location custom fields created successfully!")


def ensure_bizcompany_location_installed():
    """Programmatically create the `BizCompany Location` child DocType on a
    production server (no developer_mode), reading the versioned JSON def.

    The map needs one row per physical company location (Addis Ababa Branch,
    Hawasa Branch, Main Showroom, Factory, Warehouse, ...). Idempotent.
    """
    if frappe.db.exists("DocType", "BizCompany Location"):
        return
    import os as _os
    json_path = _os.path.join(
        _os.path.dirname(__file__), "map_locations", "bizcompany_location",
        "bizcompany_location.json")
    if not _os.path.exists(json_path):
        return
    with open(json_path) as f:
        dt_def = json.load(f)
    dt = frappe.get_doc({
        "doctype": "DocType",
        "name": dt_def["name"],
        "module": "EthioBiz Theme",
        "custom": 1,
        "istable": 1,
        "editable_grid": 1,
        "engine": "InnoDB",
        "fields": dt_def["fields"],
        "permissions": [],
    })
    dt.insert(ignore_permissions=True)
    frappe.db.commit()


def ensure_company_map_locations_installed():
    """Ensure the multi-pin infrastructure exists: the `BizCompany Location`
    child DocType AND the `company_locations` Table field on Company. Idempotent."""
    ensure_bizcompany_location_installed()
    if not frappe.db.has_column("Company", "company_locations"):
        try:
            setup_company_map_fields()
        except Exception as e:
            frappe.log_error(f"ensure_company_map_locations_installed: {e}", "MapPins")


def _get_company_location_rows(company_name, as_dicts=True):
    """Return the `company_locations` child rows for a Company, defensively.

    The child table field (`company_locations` → `BizCompany Location`) is a
    runtime/versioned table that may not exist yet on a given server, so every
    access is guarded. Returns an empty list when absent.
    """
    if not frappe.db.exists("DocType", "BizCompany Location"):
        return []
    if not frappe.db.has_column("Company", "company_locations"):
        return []
    try:
        doc = frappe.get_doc("Company", company_name)
        rows = doc.get("company_locations") or []
    except Exception:
        return []
    if as_dicts:
        out = []
        for r in rows:
            try:
                out.append(r.as_dict() if hasattr(r, "as_dict") else frappe._dict(r))
            except Exception:
                pass
        return out
    return rows


def _sound_pin(lat, lng):
    """True when lat/lng are non-zero and within Ethiopia bounds."""
    lat = flt(lat); lng = flt(lng)
    return bool(lat) and bool(lng) and (3.0 <= lat <= 15.0) and (33.0 <= lng <= 48.0)


def _company_pin_rows(comp):
    """Yield one pin per `company_locations` child row for a Company.

    - When the company has branch rows, emit one pin per active row.
    - Otherwise fall back to the legacy single lat/lng point (or region/fallback)
      resolved by `_resolve_company_coords`, so existing single-pin companies
      keep rendering AND remain upgradeable to multi-point.
    """
    rows = _get_company_location_rows(comp.get("name"))
    active = [r for r in rows if int(r.get("is_active") or 1)]
    if active:
        # Ensure at least one is primary when none marked
        if not any(int(r.get("is_primary") or 0) for r in active):
            active[0]["is_primary"] = 1
        return active

    lat, lng = _resolve_company_coords(frappe._dict(comp))
    if not _sound_pin(lat, lng):
        return []
    return [frappe._dict({
        "location_name": "Head Office",
        "branch_type": "Head Office",
        "is_primary": 1,
        "is_active": 1,
        "latitude": lat,
        "longitude": lng,
        "gps_accuracy": comp.get("gps_accuracy") or 0,
        "location_address": comp.get("location_address") or "",
        "ethiopian_region": comp.get("ethiopian_region") or "",
        "serving_cities": comp.get("serving_cities") or "",
    })]


def seed_company_location_rows(dry_run=0):
    """Backfill a default primary `BizCompany Location` row for every mapable
    Company that has no explicit multi-point rows yet.

    This lets each Company carry its own branch table going forward, while today's
    single-coordinate companies render a pin immediately. Idempotent, DB-first.
    Returns an audit dict.
    """
    dry_run = int(dry_run)
    # Ensure the multi-pin child DocType + Company table field exist before seeding
    try:
        ensure_company_map_locations_installed()
    except Exception:
        pass
    if not frappe.db.exists("DocType", "BizCompany Location") \
            or not frappe.db.has_column("Company", "company_locations"):
        return {"status": "success", "note": "BizCompany Location table not present", "seeded": 0}

    companies = frappe.get_all(
        "Company",
        fields=["name", "company_name", "latitude", "longitude", "ethiopian_region",
                "map_location", "show_on_map", "map_enabled"]
    )
    seeded = 0
    logged = []
    for c in companies:
        want_map = (int(c.get("show_on_map") or 0) or int(c.get("map_enabled") or 0))
        if not want_map:
            continue
        if _get_company_location_rows(c["name"]):
            continue  # already has explicit branch rows
        lat, lng = _resolve_company_coords(frappe._dict(c))
        if not _sound_pin(lat, lng):
            continue
        if dry_run:
            seeded += 1
            logged.append({"company": c["name"], "pin": [lat, lng]})
            continue
        try:
            doc = frappe.get_doc("Company", c["name"])
            doc.append("company_locations", {
                "location_name": "Head Office",
                "branch_type": "Head Office",
                "is_primary": 1,
                "is_active": 1,
                "latitude": lat,
                "longitude": lng,
                "location_address": c.get("location_address") or "",
                "ethiopian_region": c.get("ethiopian_region") or "",
            })
            doc.flags.ignore_validate = True
            doc.flags.ignore_mandatory = True
            doc.save(ignore_permissions=True)
            seeded += 1
            logged.append({"company": c["name"], "pin": [lat, lng]})
        except Exception as e:
            frappe.log_error(f"seed_company_location_rows {c['name']}: {e}", "MapPins")
    frappe.db.commit()
    return {"status": "success", "dry_run": bool(dry_run), "seeded": seeded, "updated": logged}


@frappe.whitelist(allow_guest=True)
def get_company_locations(category=None, user_lat=None, user_lng=None, radius_km=None):
    """Whitelisted API endpoint to return one pin per Company map location
    (multi-point: Addis Ababa Branch, Hawasa Branch, Showroom, Factory, ...).

    A Company with N `company_locations` rows returns N pins; a Company with no
    rows falls back to its single legacy coordinate.
    """
    filters = {}

    # BISMALLAH — honor BOTH the legacy `show_on_map` flag and the `map_enabled`
    # flag added by magala_setup, defensively guarding missing columns. A company is
    # mapable if either flag is set, or unconditionally when neither column exists.
    or_filters = []
    if frappe.db.has_column("Company", "show_on_map"):
        or_filters.append(["show_on_map", "=", 1])
    if frappe.db.has_column("Company", "map_enabled"):
        or_filters.append(["map_enabled", "=", 1])

    if category and category.strip():
        filters["business_category"] = category.strip()

    companies = frappe.get_all(
        "Company",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        fields=[
            "name", "company_name", "company_description", "business_category",
            "latitude", "longitude", "gps_accuracy", "location_address",
            "phone_no", "email", "website", "company_logo", "ethiopian_region"
        ]
    )

    valid_locations = []
    for comp in companies:
        for row in _company_pin_rows(comp):
            lat = flt(row.get("latitude"))
            lng = flt(row.get("longitude"))
            if not _sound_pin(lat, lng):
                continue
            valid_locations.append({
                "id": f"{comp.name}:{row.get('location_name') or 'loc'}",
                "company": comp.name,
                "name": row.get("location_name") or comp.company_name or comp.name,
                "company_name": comp.company_name or comp.name,
                "branch_type": row.get("branch_type") or "Branch",
                "is_primary": int(row.get("is_primary") or 0),
                "category": comp.business_category or "Other",
                "lat": float(lat),
                "lng": float(lng),
                "accuracy": row.get("gps_accuracy") or comp.gps_accuracy or 0,
                "address": row.get("location_address") or comp.location_address or "",
                "region": row.get("ethiopian_region") or comp.ethiopian_region or "",
                "serving_cities": row.get("serving_cities") or "",
                "phone": comp.phone_no or "",
                "email": comp.email or "",
                "website": comp.website or "",
                "logo": comp.company_logo or "/assets/frappe/images/default-avatar.png",
                "shop_url": f"/shop?company={comp.name}"
            })

    return {
        "status": "success",
        "total": len(valid_locations),
        "companies": valid_locations
    }


# ==============================================================================
# BISMALLAH — MAP PIN HEALTH: reconciliation + region-based GPS backfill
# Fixes the "no pins on /map, /shop, /all-products" defect by guaranteeing every
# mapable company has usable coordinates. Idempotent, DB-first, defensive.
# ==============================================================================

# Deterministic Addis-Ababa fallback + per-region coords (mirrors magala_setup)
_REGION_COORDS = {
    "Addis Ababa": (9.010, 38.761),
    "Oromia": (8.54, 39.27),
    "Amhara": (11.60, 37.38),
    "Tigray": (13.49, 39.47),
    "Sidama": (6.80, 38.50),
    "Somali": (6.34, 43.79),
    "Afar": (11.75, 40.95),
    "Benishangul-Gumuz": (10.06, 34.54),
    "Gambela": (8.25, 34.58),
    "South West Ethiopia": (7.00, 36.00),
    "Dire Dawa": (9.59, 41.86),
    "Harari": (9.31, 42.12),
}
_FALLBACK_COORDS = (9.010, 38.761)  # Addis Ababa


def _parse_map_location(raw):
    """Extract (lng, lat) from the Company `map_location` Geolocation map tool.

    The Geolocation widget stores either a JSON array [lng, lat], a GeoJSON
    Point/Feature/FeatureCollection, or a dict with "coordinates"/"features".
    Returns (lng, lat) floats, or (None, None) when unparseable/absent.
    """
    if not raw:
        return None, None
    data = raw
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return None, None
        if raw.startswith("["):
            try:
                data = json.loads(raw)
            except Exception:
                return None, None
        elif raw.startswith("{") and '"coordinates"' in raw:
            try:
                data = json.loads(raw)
            except Exception:
                data = None
    if not data:
        return None, None

    try:
        if isinstance(data, dict):
            gtype = data.get("type")
            if gtype == "FeatureCollection" and data.get("features"):
                coords = data["features"][0].get("geometry", {}).get("coordinates")
            elif gtype == "Feature":
                coords = data.get("geometry", {}).get("coordinates")
            elif gtype == "Point":
                coords = data.get("coordinates")
            else:
                coords = data.get("coordinates")
            if not coords and "lng" in data and "lat" in data:
                return flt(data["lng"]), flt(data["lat"])
            if not coords and "longitude" in data and "latitude" in data:
                return flt(data["longitude"]), flt(data["latitude"])
        elif isinstance(data, (list, tuple)) and len(data) >= 2:
            coords = data
        else:
            return None, None

        if coords and len(coords) >= 2:
            return flt(coords[0]), flt(coords[1])
    except Exception:
        return None, None
    return None, None


def _resolve_company_coords(doc):
    """Return (lat, lng) for a Company using the Company's own map tools first.

    Precedence (highest to lowest authority, each is a Company map tool/field):
      1. `map_location` Geolocation map-pin widget → (lng, lat)
      2. explicit `latitude` / `longitude`
      3. linked `ethiopian_region` region coords
      4. deterministic Addis Ababa fallback
    """
    ml_lng, ml_lat = _parse_map_location(getattr(doc, "map_location", None))
    if ml_lng and ml_lat:
        return ml_lat, ml_lng

    lat = flt(getattr(doc, "latitude", 0) or 0)
    lng = flt(getattr(doc, "longitude", 0) or 0)
    if lat and lng:
        return lat, lng

    region = cstr(getattr(doc, "ethiopian_region", "") or "")
    if region:
        region_doc = frappe.db.get_value(
            "Ethiopian Region", region, ["latitude", "longitude"], as_dict=True
        )
        if region_doc and flt(region_doc.get("latitude")) and flt(region_doc.get("longitude")):
            return flt(region_doc["latitude"]), flt(region_doc["longitude"])
        for _name, (_lat, _lng) in _REGION_COORDS.items():
            if _name.lower() in region.lower():
                return _lat, _lng

    return _FALLBACK_COORDS[0], _FALLBACK_COORDS[1]


def _ensure_map_flag_columns():
    """Ensure both on-map flag columns exist so reconciliation has a home."""
    for fname, label in (("show_on_map", "Show on WebShop Map"), ("map_enabled", "Show on Public Map")):
        if not frappe.db.has_column("Company", fname):
            try:
                create_custom_fields({
                    "Company": [{
                        "fieldname": fname,
                        "fieldtype": "Check",
                        "label": label,
                        "default": "1",
                    }]
                }, update=True)
            except Exception:
                pass
    frappe.db.commit()


@frappe.whitelist()
def sync_company_map_pins(dry_run=0):
    """Reconcile Company map flags + backfill coordinates so pins render.

    - Ensures `show_on_map` and `map_enabled` columns exist.
    - Normalizes both flags to 1 when either is 1 (keeps schema consistent).
    - Backfills empty latitude/longitude from the linked region (or fallback).
    Returns an audit dict (before/after counts). dry_run=1 reports without writing.
    """
    _ensure_map_flag_columns()
    dry_run = int(dry_run)

    companies = frappe.get_all(
        "Company",
        fields=["name", "company_name", "latitude", "longitude", "ethiopian_region",
                "map_location", "show_on_map", "map_enabled"]
    )

    updated_flags = 0
    backfilled = 0
    mapped_after = 0
    logged = []

    for c in companies:
        lat = flt(c.get("latitude") or 0)
        lng = flt(c.get("longitude") or 0)
        show = int(c.get("show_on_map") or 0)
        enabled = int(c.get("map_enabled") or 0)
        want_map = (show or enabled)

        patch = {}
        # Reconcile flags: if either is set, both should be set (consistency)
        if want_map and (not show or not enabled):
            if not show:
                patch["show_on_map"] = 1
            if not enabled:
                patch["map_enabled"] = 1
        # Backfill coordinates when absent and the company is mapable.
        # Prefer the Company's own map tools: the `map_location` Geolocation
        # widget first, then explicit lat/lng, then region, then fallback.
        needs_gps = (not lat or not lng) and want_map
        if needs_gps:
            rlat, rlng = _resolve_company_coords(frappe._dict(c))
            patch["latitude"] = rlat
            patch["longitude"] = rlng
        # Even if lat/lng are present, when the GeoJSON map tool has newer coords
        # that differ materially, bring them in so the pin reflects the owner's pin.
        elif c.get("map_location"):
            ml_lng, ml_lat = _parse_map_location(c.get("map_location"))
            if ml_lng and ml_lat and (
                abs(flt(ml_lat) - lat) > 0.0001 or abs(flt(ml_lng) - lng) > 0.0001
            ):
                patch["latitude"] = flt(ml_lat)
                patch["longitude"] = flt(ml_lng)

        if patch and not dry_run:
            try:
                frappe.db.set_value("Company", c["name"], patch)
                if "latitude" in patch:
                    backfilled += 1
                elif "show_on_map" in patch or "map_enabled" in patch:
                    updated_flags += 1
                logged.append({"company": c["name"], "patched": patch})
            except Exception as e:
                frappe.log_error(f"sync_company_map_pins {c['name']}: {e}", "MapPins")
        elif patch:
            if "latitude" in patch:
                backfilled += 1
            elif "show_on_map" in patch or "map_enabled" in patch:
                updated_flags += 1
            logged.append({"company": c["name"], "patched": patch})
        elif want_map:
            mapped_after += 1

    frappe.db.commit()

    # BISMALLAH (Phase 6.5 multi-pin): backfill a primary `company_locations` row
    # for every mapable company so each becomes an editable multi-point location
    # (Addis Ababa Branch, Hawasa Branch, Showroom, Factory, ...) while still
    # rendering immediately.
    seed_res = seed_company_location_rows(dry_run=dry_run)

    # Count how many companies now have mapable pins
    pin_count = 0
    for c in frappe.get_all(
        "Company",
        fields=["name", "latitude", "longitude", "show_on_map", "map_enabled"]
    ):
        if (int(c.get("show_on_map") or 0) or int(c.get("map_enabled") or 0)) \
                and flt(c.get("latitude") or 0) and flt(c.get("longitude") or 0):
            pin_count += 1

    # Count actual multi-point pins that would render (one per location row)
    multi_point_pins = 0
    try:
        if frappe.db.exists("DocType", "BizCompany Location") \
                and frappe.db.has_column("Company", "company_locations"):
            for c in frappe.get_all(
                "Company",
                fields=["name", "company_name", "show_on_map", "map_enabled"]
            ):
                if not (int(c.get("show_on_map") or 0) or int(c.get("map_enabled") or 0)):
                    continue
                multi_point_pins += len(_company_pin_rows(c))
    except Exception:
        pass

    return {
        "status": "success",
        "dry_run": bool(dry_run),
        "total_companies": len(companies),
        "flag_reconciled": updated_flags,
        "coords_backfilled": backfilled,
        "branch_locations_seeded": int((seed_res or {}).get("seeded") or 0),
        "companies_with_pins_after": pin_count,
        "multi_point_pins_after": multi_point_pins,
        "updated": logged,
    }


@frappe.whitelist(allow_guest=True)
def get_map_pin_status():
    """Lightweight audit used by the map UI + test suites: how many pins WOULD render."""
    return sync_company_map_pins(dry_run=1)


# ==============================================================================
# BISMALLAH — LIVE GPS CAPTURE (Phase 6.5): register a physical location pin on a
# Company from the browser's live geolocation (navigator.geolocation). Creates or
# updates a `BizCompany Location` child row with source/metadata stamped.
# ==============================================================================

@frappe.whitelist()
def register_live_gps(company=None, location_name=None, lat=0, lng=0,
                      branch_type=None, accuracy=0, address=None, serving_cities=None,
                      ethiopian_region=None, update_primary=0):
    """Create (or update the primary) `BizCompany Location` for a Company using a
    live GPS reading captured from the device/browser.

    - `company` (Link→Company) is required.
    - `latitude`/`longitude` are required floats (the live GPS fix).
    - Creates a new branch row; or, when `update_primary=1`, updates the primary
      (or first) location row with the live coordinates.
    Stamps `gps_source=Live GPS`, `captured_at`, `gps_captured_by`.
    """
    if not frappe.db.exists("DocType", "BizCompany Location") \
            or not frappe.db.has_column("Company", "company_locations"):
        try:
            ensure_company_map_locations_installed()
        except Exception:
            pass
    if not frappe.db.exists("DocType", "BizCompany Location") \
            or not frappe.db.has_column("Company", "company_locations"):
        frappe.throw("Multi-location map pins are not installed on this server")

    if not company or not frappe.db.exists("Company", company):
        frappe.throw("A valid Company is required to register a live GPS pin")

    lat = flt(lat); lng = flt(lng)
    if not lat or not lng or not _sound_pin(lat, lng):
        frappe.throw("A valid Ethiopia in-bounds Latitude & Longitude is required (live GPS fix)")

    now_ts = frappe.utils.now_datetime()
    by_user = frappe.session.user or "Administrator"
    location_name = cstr(location_name or "").strip() or "Live GPS Location"

    doc = frappe.get_doc("Company", company)

    if int(update_primary or 0):
        rows = _get_company_location_rows(company, as_dicts=False)
        target = None
        for r in rows:
            if int(r.get("is_primary") or 0):
                target = r
                break
        if target is None and rows:
            target = rows[0]
        if target is not None:
            target.latitude = lat
            target.longitude = lng
            target.gps_accuracy = flt(accuracy)
            target.location_address = address or target.get("location_address") or ""
            target.ethiopian_region = ethiopian_region or target.get("ethiopian_region") or ""
            target.gps_source = "Live GPS"
            target.captured_at = now_ts
            target.gps_captured_by = by_user
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "mode": "updated", "company": company,
                    "location_name": target.get("location_name"), "lat": lat, "lng": lng}

    doc.append("company_locations", {
        "location_name": location_name,
        "branch_type": branch_type or "Branch",
        "is_primary": 0,
        "is_active": 1,
        "latitude": lat,
        "longitude": lng,
        "gps_accuracy": flt(accuracy),
        "location_address": address or "",
        "ethiopian_region": ethiopian_region or "",
        "serving_cities": serving_cities or "",
        "gps_source": "Live GPS",
        "captured_at": now_ts,
        "gps_captured_by": by_user,
    })
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "mode": "created", "company": company,
            "location_name": location_name, "lat": lat, "lng": lng}

