// EthioBiz Company DocType Map & Geolocation Desk Controller
frappe.provide('frappe.ui.form');

frappe.ui.form.on('Company', {
    onload: function(frm) {
        inject_leaflet_desk_styles();
    },

    refresh: function(frm) {
        inject_leaflet_desk_styles();

        if (!frm.is_new()) {
            frm.add_custom_button(__('📍 Capture My GPS'), function() {
                capture_device_gps(frm);
            }, __('Map Location'));

            frm.add_custom_button(__('🔍 Fullscreen Map Dialog'), function() {
                open_fullscreen_map(frm);
            }, __('Map Location'));

            frm.add_custom_button(__('🇪🇹 Center Addis Ababa'), function() {
                frm.set_value('latitude', 9.0108);
                frm.set_value('longitude', 38.7617);
                sync_coords_to_map_field(frm);
            }, __('Map Location'));
        }

        // Attach listener to Leaflet Map field
        setup_map_listeners(frm);
    },

    latitude: function(frm) {
        sync_coords_to_map_field(frm);
    },

    longitude: function(frm) {
        sync_coords_to_map_field(frm);
    },

    map_location: function(frm) {
        extract_coords_from_map(frm);
    },

    before_save: function(frm) {
        if (frm.doc.map_location) {
            extract_coords_from_map(frm);
        } else if (frm.doc.latitude && frm.doc.longitude) {
            sync_coords_to_map_field(frm);
        }
    }
});

function inject_leaflet_desk_styles() {
    if (document.getElementById('leaflet-desk-icon-fix-styles')) return;

    const style = document.createElement('style');
    style.id = 'leaflet-desk-icon-fix-styles';
    style.innerHTML = `
        /* Leaflet Draw & Zoom Controls Desk Fix */
        .leaflet-draw-toolbar, .leaflet-bar {
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            overflow: hidden !important;
        }
        .leaflet-control-zoom-in, .leaflet-control-zoom-out {
            font-size: 18px !important;
            font-weight: 700 !important;
            line-height: 28px !important;
            color: #0f172a !important;
            background: #ffffff !important;
            text-align: center !important;
        }
        .leaflet-draw-toolbar a {
            background-color: #ffffff !important;
            background-image: none !important;
            color: #0f172a !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 15px !important;
            line-height: 28px !important;
            width: 30px !important;
            height: 30px !important;
            text-decoration: none !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        .leaflet-draw-toolbar a:hover {
            background-color: #f1f5f9 !important;
            color: #008080 !important;
        }
        /* Icon representation for blank draw buttons */
        .leaflet-draw-draw-marker::after { content: "📍" !important; font-size: 14px; }
        .leaflet-draw-draw-polygon::after { content: "⬡" !important; font-size: 14px; font-weight: bold; }
        .leaflet-draw-draw-rectangle::after { content: "▭" !important; font-size: 14px; font-weight: bold; }
        .leaflet-draw-draw-circle::after { content: "○" !important; font-size: 14px; font-weight: bold; }
        .leaflet-draw-draw-polyline::after { content: "〰" !important; font-size: 12px; }
        .leaflet-draw-edit-edit::after { content: "✏️" !important; font-size: 13px; }
        .leaflet-draw-edit-remove::after { content: "🗑️" !important; font-size: 13px; }
    `;
    document.head.appendChild(style);
}

function setup_map_listeners(frm) {
    setTimeout(() => {
        const field = frm.fields_dict['map_location'];
        if (!field || !field.map) return;

        const map = field.map;

        // If coordinates are 0 or empty, center on Addis Ababa
        if (!frm.doc.latitude && !frm.doc.longitude) {
            map.setView([9.0108, 38.7617], 12);
        }

        map.on('draw:created', function(e) {
            if (e.layer && e.layer.getLatLng) {
                const latlng = e.layer.getLatLng();
                frm.set_value('latitude', latlng.lat);
                frm.set_value('longitude', latlng.lng);
                frm.set_value('show_on_map', 1);
            }
        });

        map.on('draw:edited', function(e) {
            extract_coords_from_map(frm);
        });

        map.on('click', function(e) {
            if (e.latlng) {
                frm.set_value('latitude', e.latlng.lat);
                frm.set_value('longitude', e.latlng.lng);
                frm.set_value('show_on_map', 1);
                sync_coords_to_map_field(frm);
            }
        });
    }, 600);
}

function extract_coords_from_map(frm) {
    const raw = frm.doc.map_location;
    if (!raw) return;

    try {
        const geojson = typeof raw === 'string' ? JSON.parse(raw) : raw;
        let coords = null;

        if (geojson.type === 'FeatureCollection' && geojson.features && geojson.features.length) {
            coords = geojson.features[0].geometry.coordinates;
        } else if (geojson.type === 'Feature' && geojson.geometry) {
            coords = geojson.geometry.coordinates;
        } else if (geojson.type === 'Point') {
            coords = geojson.coordinates;
        }

        if (coords && coords.length >= 2) {
            const lng = parseFloat(coords[0]);
            const lat = parseFloat(coords[1]);
            if (!isNaN(lat) && !isNaN(lng)) {
                frm.set_value('latitude', lat);
                frm.set_value('longitude', lng);
                frm.set_value('show_on_map', 1);
            }
        }
    } catch (e) {
        console.error('Error parsing map_location GeoJSON:', e);
    }
}

function sync_coords_to_map_field(frm) {
    const lat = parseFloat(frm.doc.latitude);
    const lng = parseFloat(frm.doc.longitude);

    if (isNaN(lat) || isNaN(lng) || (lat === 0 && lng === 0)) return;

    const geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            }
        }]
    };

    frm.set_value('map_location', JSON.stringify(geojson));
}

function capture_device_gps(frm) {
    if (!navigator.geolocation) {
        frappe.msgprint(__('Geolocation is not supported by your browser.'));
        return;
    }

    frappe.show_alert({ message: __('Acquiring GPS location...'), indicator: 'blue' });

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            const acc = pos.coords.accuracy;

            frm.set_value('latitude', lat);
            frm.set_value('longitude', lng);
            frm.set_value('gps_accuracy', acc);
            frm.set_value('show_on_map', 1);

            sync_coords_to_map_field(frm);

            frappe.msgprint({
                title: __('📍 GPS Location Captured'),
                message: __('Latitude: <b>{0}</b><br>Longitude: <b>{1}</b><br>Accuracy: <b>~{2}m</b>', [lat.toFixed(6), lng.toFixed(6), Math.round(acc)]),
                indicator: 'green'
            });
        },
        function(err) {
            frappe.msgprint({
                title: __('GPS Failed'),
                message: __('Unable to get GPS coordinates: {0}', [err.message || 'Permission denied']),
                indicator: 'red'
            });
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
}

function open_fullscreen_map(frm) {
    let lat = parseFloat(frm.doc.latitude) || 9.0108;
    let lng = parseFloat(frm.doc.longitude) || 38.7617;

    const d = new frappe.ui.Dialog({
        title: __('🗺️ Full-Page Company Location Map: {0}', [frm.doc.company_name || frm.doc.name]),
        size: 'extra-large',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'fullmap_html',
                options: `
                    <div style="height: 62vh; width: 100%; border-radius: 12px; overflow: hidden; position: relative;">
                        <div id="fullpage-company-leaflet-map" style="height: 100%; width: 100%;"></div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <div id="dialog-coords-text" style="font-weight: 700; color: #0f172a; font-size: 14px;">
                            Coordinates: (${lat.toFixed(5)}, ${lng.toFixed(5)})
                        </div>
                        <small class="text-muted">Click anywhere on the map or drag the pin to update coordinates</small>
                    </div>
                `
            }
        ],
        primary_action_label: __('Save Coordinates'),
        primary_action: function() {
            frm.set_value('latitude', lat);
            frm.set_value('longitude', lng);
            frm.set_value('show_on_map', 1);
            sync_coords_to_map_field(frm);
            frm.save();
            d.hide();
            frappe.show_alert({ message: __('Coordinates saved successfully!'), indicator: 'green' });
        }
    });

    d.show();

    setTimeout(() => {
        if (!window.L) return;
        const dialogMap = L.map('fullpage-company-leaflet-map').setView([lat, lng], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors | EthioBiz.et',
            maxZoom: 19
        }).addTo(dialogMap);

        const marker = L.marker([lat, lng], { draggable: true }).addTo(dialogMap);

        function updateCoords(newLat, newLng) {
            lat = newLat;
            lng = newLng;
            marker.setLatLng([lat, lng]);
            const txt = document.getElementById('dialog-coords-text');
            if (txt) txt.innerText = `Coordinates: (${lat.toFixed(5)}, ${lng.toFixed(5)})`;
        }

        marker.on('dragend', function(e) {
            const p = e.target.getLatLng();
            updateCoords(p.lat, p.lng);
        });

        dialogMap.on('click', function(e) {
            updateCoords(e.latlng.lat, e.latlng.lng);
        });
    }, 300);
}
