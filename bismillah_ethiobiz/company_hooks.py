import json
import frappe
from frappe.utils import cstr

def before_save_company(doc, method=None):
    """Guarantees bidirectional synchronization between map_location GeoJSON and latitude/longitude fields."""
    if doc.map_location:
        try:
            raw = doc.map_location
            geojson = json.loads(raw) if isinstance(raw, str) else raw
            coords = None

            if isinstance(geojson, dict):
                if geojson.get("type") == "FeatureCollection" and geojson.get("features"):
                    coords = geojson["features"][0].get("geometry", {}).get("coordinates")
                elif geojson.get("type") == "Feature":
                    coords = geojson.get("geometry", {}).get("coordinates")
                elif geojson.get("type") == "Point":
                    coords = geojson.get("coordinates")

            if coords and len(coords) >= 2:
                lng = float(coords[0])
                lat = float(coords[1])
                doc.latitude = lat
                doc.longitude = lng
        except Exception as e:
            frappe.log_error(f"Error parsing Company map_location GeoJSON: {e}", "Company Geolocation Sync")

    elif doc.latitude and doc.longitude:
        try:
            lat = float(doc.latitude)
            lng = float(doc.longitude)
            geojson = {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    }
                }]
            }
            doc.map_location = json.dumps(geojson)
        except Exception as e:
            frappe.log_error(f"Error constructing Company map_location GeoJSON: {e}", "Company Geolocation Sync")

    # BISMALLAH — reconcile map-flag consistency + backfill GPS from region
    # (both map APIs honor either flag, so keeping them in sync prevents the
    # "no pins on /map, /shop, /all-products" defect going forward).
    try:
        show = int(getattr(doc, "show_on_map", 0) or 0)
        enabled = int(getattr(doc, "map_enabled", 0) or 0)
        if show or enabled:
            if not show:
                doc.show_on_map = 1
            if not enabled:
                doc.map_enabled = 1

            lat_f = getattr(doc, "latitude", 0) or 0
            lng_f = getattr(doc, "longitude", 0) or 0
            if not lat_f or not lng_f:
                region = cstr(getattr(doc, "ethiopian_region", "") or "")
                rlat, rlng = 9.010, 38.761  # Addis Ababa fallback
                if region:
                    rd = frappe.db.get_value(
                        "Ethiopian Region", region, ["latitude", "longitude"], as_dict=True
                    )
                    if rd and rd.get("latitude") and rd.get("longitude"):
                        rlat, rlng = float(rd["latitude"]), float(rd["longitude"])
                if not lat_f:
                    doc.latitude = rlat
                if not lng_f:
                    doc.longitude = rlng
    except Exception as e:
        frappe.log_error(f"Error reconciling Company map flags: {e}", "Company Map Flags")

    # BISMALLAH (Phase 6.5 multi-pin): keep the `company_locations` child rows
    # consistent — parse each branch row's live-GPS Geolocation `map_location` pin
    # into its Latitude/Longitude, and mirror the Company's primary point into the
    # primary row (and the primary row back into the single coords when no pins).
    try:
        rows = doc.get("company_locations")
        if rows is None:
            return
        rows = list(rows)
        if not rows:
            return

        _parse = None
        try:
            from bismillah_ethiobiz.company_map_api import _parse_map_location as _parse_loc
            _parse = lambda raw: _parse_loc(raw)
        except Exception:
            _parse = None

        primary = None
        for r in rows:
            # Parse a branch Geolocation pin (lng, lat) -> (lat, lng)
            raw_pin = getattr(r, "map_location", None)
            if raw_pin and _parse:
                try:
                    lng, lat = _parse(raw_pin)
                    if lat and lng:
                        r.latitude = float(lat)
                        r.longitude = float(lng)
                        if not getattr(r, "gps_source", None):
                            r.gps_source = "Map Pin"
                except Exception:
                    pass
            if int(getattr(r, "is_primary", 0) or 0) and primary is None:
                primary = r

        # Mirror company single coords into the primary row if the company point
        # was the one updated via the main ESLint widget (no explicit branch rows).
        if primary is not None:
            clat = getattr(doc, "latitude", 0) or 0
            clng = getattr(doc, "longitude", 0) or 0
            if clat and clng and (not getattr(primary, "latitude", 0) or not getattr(primary, "longitude", 0)):
                primary.latitude = clat
                primary.longitude = clng
    except Exception as e:
        frappe.log_error(f"Error syncing Company multi-location pins: {e}", "Company Map Pins")

