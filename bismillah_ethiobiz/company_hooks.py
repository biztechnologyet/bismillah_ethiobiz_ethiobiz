import json
import frappe

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
