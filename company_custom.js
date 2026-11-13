// Client Script for Company DocType in Frappe Desk
frappe.ui.form.on('Company', {
    onload: function(frm) {
        // Inject CSS fixes for Leaflet map controls and button styling in Desk
        if (!document.getElementById('leaflet-custom-desk-style')) {
            const style = document.createElement('style');
            style.id = 'leaflet-custom-desk-style';
            style.innerHTML = `
                /* Leaflet Toolbar & Vertical Control Fixes */
                .leaflet-control-zoom-in, .leaflet-control-zoom-out {
                    font-size: 18px !important;
                    font-weight: bold !important;
                    line-height: 26px !important;
                    text-align: center !important;
                    color: #1e293b !important;
                    background-color: #ffffff !important;
                    text-decoration: none !important;
                }
                .leaflet-control-zoom-in:hover, .leaflet-control-zoom-out:hover {
                    background-color: #f1f5f9 !important;
                    color: #008080 !important;
                }
                .leaflet-draw-toolbar a {
                    background-color: #ffffff !important;
                    color: #1e293b !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    font-size: 14px !important;
                }
                /* Full-Page Map Modal Styling */
                .modal-map-fullscreen {
                    width: 95vw !important;
                    max-width: 95vw !important;
                    height: 88vh !important;
                }
                .map-action-btn-group {
                    margin-top: 10px;
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }
            `;
            document.head.appendChild(style);
        }
    },

    refresh: function(frm) {
        // Add custom action buttons
        if (!frm.is_new()) {
            frm.add_custom_button(__('📍 Capture My GPS Location'), function() {
                capture_gps(frm);
            }, __('Map & Location'));

            frm.add_custom_button(__('🔍 Open Full-Page Map'), function() {
                open_fullpage_map_dialog(frm);
            }, __('Map & Location'));

            frm.add_custom_button(__('📌 Sync Lat/Lng to Map'), function() {
                sync_lat_lng_to_map(frm, true);
            }, __('Map & Location'));
        }

        // Attach listener to Geolocation map field
        setup_map_sync(frm);
    },

    latitude: function(frm) {
        sync_lat_lng_to_map(frm, false);
    },

    longitude: function(frm) {
        sync_lat_lng_to_map(frm, false);
    },

    map_location: function(frm) {
        sync_map_to_lat_lng(frm);
    },

    validate: function(frm) {
        // Guarantee lat/lng and map_location are in perfect sync before saving
        if (frm.doc.map_location) {
            sync_map_to_lat_lng(frm);
        } else if (frm.doc.latitude && frm.doc.longitude) {
            sync_lat_lng_to_map(frm, false);
        }
    }
});

function setup_map_sync(frm) {
    if (frm.fields_dict['map_location'] && frm.fields_dict['map_location'].map) {
        const map = frm.fields_dict['map_location'].map;
        map.on('draw:created draw:edited', function(e) {
            setTimeout(() => { sync_map_to_lat_lng(frm); }, 100);
        });
    }
}

function sync_map_to_lat_lng(frm) {
    const raw_val = frm.doc.map_location;
    if (!raw_val) return;

    try {
        let geojson = typeof raw_val === 'string' ? JSON.parse(raw_val) : raw_val;
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
                if (frm.doc.latitude !== lat || frm.doc.longitude !== lng) {
                    frm.set_value('latitude', lat);
                    frm.set_value('longitude', lng);
                }
            }
        }
    } catch (e) {
        console.error('Error parsing map_location GeoJSON:', e);
    }
}

function sync_lat_lng_to_map(frm, show_msg) {
    const lat = parseFloat(frm.doc.latitude);
    const lng = parseFloat(frm.doc.longitude);

    if (isNaN(lat) || isNaN(lng) || (lat === 0 && lng === 0)) {
        if (show_msg) frappe.msgprint(__('Please specify valid Latitude and Longitude values.'));
        return;
    }

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
    if (show_msg) {
        frappe.show_alert({
            message: __('Map Pin Synced to ({0}, {1})', [lat.toFixed(5), lng.toFixed(5)]),
            indicator: 'green'
        }, 3);
    }
}

function capture_gps(frm) {
    if (!navigator.geolocation) {
        frappe.msgprint(__('Geolocation is not supported by your browser/device.'));
        return;
    }

    frappe.show_alert({
        message: __('Requesting device GPS coordinates...'),
        indicator: 'blue'
    }, 3);

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const acc = position.coords.accuracy;

            frm.set_value('latitude', lat);
            frm.set_value('longitude', lng);
            frm.set_value('gps_accuracy', acc);
            frm.set_value('show_on_map', 1);

            sync_lat_lng_to_map(frm, false);

            frappe.msgprint({
                title: __('GPS Captured Successfully'),
                message: __('Latitude: <b>{0}</b><br>Longitude: <b>{1}</b><br>Accuracy: ~<b>{2} meters</b>', [lat.toFixed(6), lng.toFixed(6), acc.toFixed(1)]),
                indicator: 'green'
            });
        },
        function(error) {
            frappe.msgprint({
                title: __('GPS Capture Failed'),
                message: __('Unable to retrieve GPS coordinates: {0}', [error.message || 'Permission denied']),
                indicator: 'red'
            });
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
}

function open_fullpage_map_dialog(frm) {
    let lat = parseFloat(frm.doc.latitude) || 9.0108;
    let lng = parseFloat(frm.doc.longitude) || 38.7617;

    let d = new frappe.ui.Dialog({
        title: __('🗺️ Full-Page Location Map: {0}', [frm.doc.company_name || frm.doc.name]),
        size: 'extra-large',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'fullmap_html',
                options: `
                    <div style="height: 65vh; width: 100%; border-radius: 10px; overflow: hidden; position: relative;">
                        <div id="fullpage-leaflet-map" style="height: 100%; width: 100%;"></div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <div id="dialog-coords-info" class="font-weight-bold text-dark">
                            Current Coordinates: (${lat.toFixed(5)}, ${lng.toFixed(5)})
                        </div>
                        <small class="text-muted">Click or drag marker anywhere on the map to change location</small>
                    </div>
                `
            }
        ],
        primary_action_label: __('Save Coordinates'),
        primary_action: function() {
            frm.set_value('latitude', lat);
            frm.set_value('longitude', lng);
            sync_lat_lng_to_map(frm, false);
            frm.save();
            d.hide();
            frappe.show_alert({
                message: __('Coordinates updated and saved successfully!'),
                indicator: 'green'
            }, 3);
        }
    });

    d.show();

    setTimeout(() => {
        if (!window.L) return;
        const fullMap = L.map('fullpage-leaflet-map').setView([lat, lng], 14);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors | EthioBiz.et',
            maxZoom: 19
        }).addTo(fullMap);

        const marker = L.marker([lat, lng], { draggable: true }).addTo(fullMap);

        function updateMarker(newLat, newLng) {
            lat = newLat;
            lng = newLng;
            marker.setLatLng([lat, lng]);
            document.getElementById('dialog-coords-info').innerText = `Current Coordinates: (${lat.toFixed(5)}, ${lng.toFixed(5)})`;
        }

        marker.on('dragend', function(e) {
            const pos = e.target.getLatLng();
            updateMarker(pos.lat, pos.lng);
        });

        fullMap.on('click', function(e) {
            updateMarker(e.latlng.lat, e.latlng.lng);
        });
    }, 300);
}
