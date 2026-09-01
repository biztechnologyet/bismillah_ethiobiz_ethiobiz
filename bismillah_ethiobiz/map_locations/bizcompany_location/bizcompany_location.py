# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz — BizCompany Location (child table).

Gives a Company MULTIPLE map pins (Addis Ababa Branch, Hawasa Branch, Main
Showroom, Factory, Warehouse, ...). Each row is a single point with required
lat/lng + location name. Stored on the Company under `company_locations` and
consumed by the /map, /shop and /all-products map APIs (Phase 6.5 multi-pin).

DB-first + defensive: every access guards against a missing table/field.
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cstr


class BizCompanyLocation(Document):
    """Child-table controller: coerce + validate a single company map pin."""

    def validate(self):
        # 1) Parse the Geolocation `map_location` map tool (drop/drag the live GPS
        # pin) into numeric latitude/longitude when the user pinned on the map.
        map_raw = self.get("map_location")
        if map_raw:
            parsed = _parse_location_pin(map_raw)
            if parsed:
                lng, lat = parsed
                if lat and lng:
                    self.latitude = flt(lat)
                    self.longitude = flt(lng)
                    if not self.get("gps_source"):
                        self.gps_source = "Map Pin"
                    if not self.get("captured_at"):
                        self.captured_at = frappe.utils.now_datetime()

        lat = flt(self.get("latitude"))
        lng = flt(self.get("longitude"))

        # 2) Reject clearly-bad / out-of-Ethiopia values to avoid garbled pins.
        if lat and not (-15 <= lat <= 15):
            self.latitude = 0
        if lng and not (25 <= lng <= 50):
            self.longitude = 0
        if not self.get("latitude") or not self.get("longitude"):
            # 3) Seed coordinates from the linked region when GPS is missing.
            region = cstr(self.get("ethiopian_region") or "").strip()
            if region and frappe.db.exists("DocType", "Ethiopian Region") \
                    and frappe.db.exists("Ethiopian Region", region):
                g = frappe.db.get_value(
                    "Ethiopian Region", region,
                    ["latitude", "longitude"], as_dict=True)
                if g and flt(g.get("latitude")) and flt(g.get("longitude")):
                    self.latitude = flt(g["latitude"])
                    self.longitude = flt(g["longitude"])
                    self.gps_source = self.gps_source or "Region Default"
                    # fall through to the final check below
            if not self.get("latitude") or not self.get("longitude"):
                frappe.msgprint(
                    _("Location '{0}' needs valid Latitude and Longitude (or a "
                      "linked Ethiopian Region).").format(
                        self.get("location_name") or ""),
                    alert=True)

        if not self.get("location_name"):
            self.location_name = "Branch"


def _parse_location_pin(raw):
    """Parse the Geolocation map tool into (lng, lat) floats for a branch pin."""
    import json as _json
    if not raw:
        return None
    data = raw
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return None
        try:
            data = _json.loads(raw)
        except Exception:
            data = raw
    if isinstance(data, str):
        # bare "[lng, lat]" string
        try:
            data = _json.loads(data)
        except Exception:
            return None
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
            return None
        if coords and len(coords) >= 2:
            return flt(coords[0]), flt(coords[1])
    except Exception:
        return None
    return None

