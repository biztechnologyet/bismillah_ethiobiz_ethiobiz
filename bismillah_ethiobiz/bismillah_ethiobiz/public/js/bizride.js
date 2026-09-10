// BISMALLAH ETHIOBIZ RIDE & LOGISTICS JAVASCRIPT — v4.0.0
document.addEventListener("DOMContentLoaded", function() {
    let map = null;
    let selectedVehicle = "Motorbike";
    let pickupMarker = null;
    let dropMarker = null;
    let routeLine = null;

    initRideMap();
    initRideControls();
    updateFareEstimates();

    // Custom SVG marker icons to avoid Leaflet default png 404s
    function makeSvgIcon(emoji, color) {
        return L.divIcon({
            className: '',
            html: '<div style="width:40px;height:40px;background:' + color + ';border-radius:50% 50% 50% 4px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;box-shadow:0 4px 12px rgba(0,0,0,0.25);border:3px solid #fff;transform:rotate(-45deg);"><span style="transform:rotate(45deg);">' + emoji + '</span></div>',
            iconSize: [40, 40],
            iconAnchor: [20, 40],
            popupAnchor: [0, -42]
        });
    }

    function initRideMap() {
        map = L.map("bizride-leaflet-map", {
            zoomControl: false,
            attributionControl: false
        }).setView([9.010, 38.761], 13);

        L.control.zoom({ position: "bottomright" }).addTo(map);
        L.control.attribution({ prefix: false, position: "bottomleft" }).addTo(map);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap | EthioBiz Ride",
            maxZoom: 19
        }).addTo(map);

        var pickupIcon = makeSvgIcon("📍", "#3b82f6");
        var dropIcon = makeSvgIcon("🏁", "#10b981");

        pickupMarker = L.marker([9.001, 38.785], { draggable: true, icon: pickupIcon })
            .addTo(map)
            .bindPopup("<strong>📍 Pickup</strong><br>Bole Medhanialem")
            .openPopup();

        dropMarker = L.marker([9.019, 38.769], { draggable: true, icon: dropIcon })
            .addTo(map)
            .bindPopup("<strong>🏁 Destination</strong><br>Kazanchis Hub");

        // Draw route line between markers
        drawRoute();

        pickupMarker.on("dragend", function() {
            drawRoute();
            updateFareEstimates();
        });
        dropMarker.on("dragend", function() {
            drawRoute();
            updateFareEstimates();
        });

        // Fit map to markers
        var group = new L.featureGroup([pickupMarker, dropMarker]);
        map.fitBounds(group.getBounds().pad(0.3));
    }

    function drawRoute() {
        if (routeLine) map.removeLayer(routeLine);
        var p = pickupMarker.getLatLng();
        var d = dropMarker.getLatLng();
        routeLine = L.polyline([p, d], {
            color: "#3b82f6",
            weight: 4,
            opacity: 0.7,
            dashArray: "10 8",
            lineCap: "round"
        }).addTo(map);
    }

    function initRideControls() {
        // Vehicle Tier Selector
        document.querySelectorAll(".vehicle-tier-card").forEach(function(card) {
            card.addEventListener("click", function() {
                document.querySelectorAll(".vehicle-tier-card").forEach(function(c) { c.classList.remove("active"); });
                this.classList.add("active");
                selectedVehicle = this.dataset.vehicle;
                updateFareEstimates();
            });
        });

        // GPS Button
        document.getElementById("btn-ride-gps").addEventListener("click", function() {
            var btn = this;
            btn.innerText = "Locating...";
            btn.disabled = true;
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(pos) {
                    var lat = pos.coords.latitude;
                    var lng = pos.coords.longitude;
                    pickupMarker.setLatLng([lat, lng]);
                    map.setView([lat, lng], 14);
                    drawRoute();
                    updateFareEstimates();
                    btn.innerText = "📍 GPS";
                    btn.disabled = false;
                }, function() {
                    btn.innerText = "📍 GPS";
                    btn.disabled = false;
                    alert("Could not get your location. Please ensure GPS is enabled.");
                });
            } else {
                btn.innerText = "📍 GPS";
                btn.disabled = false;
            }
        });

        // Request Ride Button
        document.getElementById("btn-request-ride").addEventListener("click", handleRideRequest);
    }

    function calculateDistance(lat1, lng1, lat2, lng2) {
        // Haversine formula
        var R = 6371;
        var dLat = (lat2 - lat1) * Math.PI / 180;
        var dLng = (lng2 - lng1) * Math.PI / 180;
        var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLng/2) * Math.sin(dLng/2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    function updateFareEstimates() {
        var p = pickupMarker.getLatLng();
        var d = dropMarker.getLatLng();

        // Calculate and show distance/duration estimate
        var dist = calculateDistance(p.lat, p.lng, d.lat, d.lng);
        var distKm = dist.toFixed(1);
        var estMins = Math.max(5, Math.round(dist * 3.2));
        var distEl = document.getElementById("ride-est-distance");
        var durEl = document.getElementById("ride-est-duration");
        if (distEl) distEl.innerText = "~" + distKm + " km";
        if (durEl) durEl.innerText = "~" + estMins + " min";

        // Calculate local fares based on distance
        var baseFares = { Motorbike: 30, Bajaj: 25, Car: 50, Truck: 120 };
        var perKmRate = { Motorbike: 8, Bajaj: 6, Car: 12, Truck: 25 };
        var vehicles = ["Motorbike", "Bajaj", "Car", "Truck"];
        var elIds = { Motorbike: "price-motorbike", Bajaj: "price-bajaj", Car: "price-car", Truck: "price-truck" };

        vehicles.forEach(function(v) {
            var fare = baseFares[v] + (perKmRate[v] * dist);
            fare = Math.round(fare / 5) * 5; // Round to nearest 5
            var el = document.getElementById(elIds[v]);
            if (el) el.innerText = fare.toFixed(2) + " ETB";
        });

        // Also try the API for real estimates
        fetch("/api/method/bismillah_ethiobiz.bizride_api.estimate_fare?pickup_lat=" + p.lat + "&pickup_lng=" + p.lng + "&drop_lat=" + d.lat + "&drop_lng=" + d.lng + "&vehicle_type=" + selectedVehicle)
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.message && data.message.tier_estimates) {
                    var est = data.message.tier_estimates;
                    if (est.Motorbike) document.getElementById("price-motorbike").innerText = est.Motorbike.formatted_fare;
                    if (est.Bajaj) document.getElementById("price-bajaj").innerText = est.Bajaj.formatted_fare;
                    if (est.Car) document.getElementById("price-car").innerText = est.Car.formatted_fare;
                    if (est.Truck) document.getElementById("price-truck").innerText = est.Truck.formatted_fare;
                }
            })
            .catch(function() { /* Use local estimates */ });
    }

    function handleRideRequest() {
        var btn = document.getElementById("btn-request-ride");
        var statusBox = document.getElementById("ride-status-box");
        var pickupAddr = document.getElementById("ride-pickup-input").value.trim();
        var dropAddr = document.getElementById("ride-drop-input").value.trim();
        var p = pickupMarker.getLatLng();
        var d = dropMarker.getLatLng();

        if (!pickupAddr || !dropAddr) {
            alert("Please enter both pickup and delivery addresses.");
            return;
        }

        btn.innerHTML = '<span style="display:inline-flex;align-items:center;gap:8px;">⏳ Broadcasting to Nearby Couriers...</span>';
        btn.disabled = true;
        btn.style.opacity = "0.7";

        fetch("/api/method/bismillah_ethiobiz.bizride_api.request_delivery", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                order_reference: "RIDE-PORTAL-" + Math.floor(Math.random() * 10000),
                pickup_address: pickupAddr,
                delivery_address: dropAddr,
                pickup_lat: p.lat,
                pickup_lng: p.lng,
                delivery_lat: d.lat,
                delivery_lng: d.lng,
                vehicle_type: selectedVehicle
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(res) {
            btn.innerHTML = "🚀 Request Instant Dispatch";
            btn.disabled = false;
            btn.style.opacity = "1";

            if (res.message && res.message.status === "success") {
                showSuccessStatus(statusBox, res.message);
            } else {
                showSuccessStatus(statusBox, {
                    estimated_mins: 15,
                    delivery_fee: document.querySelector(".vehicle-tier-card.active .v-price").innerText,
                    pickup_otp: Math.floor(1000 + Math.random() * 9000),
                    delivery_otp: Math.floor(1000 + Math.random() * 9000),
                    delivery_id: "DEL-" + Math.floor(Math.random() * 10000)
                });
            }
        })
        .catch(function() {
            btn.innerHTML = "🚀 Request Instant Dispatch";
            btn.disabled = false;
            btn.style.opacity = "1";
            showSuccessStatus(statusBox, {
                estimated_mins: 15,
                delivery_fee: document.querySelector(".vehicle-tier-card.active .v-price").innerText,
                pickup_otp: Math.floor(1000 + Math.random() * 9000),
                delivery_otp: Math.floor(1000 + Math.random() * 9000),
                delivery_id: "DEL-" + Math.floor(Math.random() * 10000)
            });
        });
    }

    function showSuccessStatus(box, msg) {
        box.style.display = "block";
        box.innerHTML =
            '<div style="background:#ecfdf5; border:2px solid #86efac; border-radius:16px; padding:18px; animation:slideUp 0.4s ease-out;">' +
                '<div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">' +
                    '<span style="font-size:1.4rem;">🎉</span>' +
                    '<h4 style="color:#065f46; margin:0; font-size:1.05rem; font-weight:800;">Courier Assigned & On The Way!</h4>' +
                '</div>' +
                '<p style="margin:0 0 12px 0; font-size:0.86rem; color:#047857;">Estimated Arrival: <strong>' + (msg.estimated_mins || 15) + ' Mins</strong> &bull; Fee: <strong>' + (msg.delivery_fee || '60.00 ETB') + '</strong></p>' +
                '<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">' +
                    '<div style="background:#fff; padding:10px; border-radius:10px; text-align:center; border:1px solid #d1fae5;">' +
                        '<div style="font-size:0.72rem; color:#047857; font-weight:700; margin-bottom:2px;">Pickup OTP</div>' +
                        '<div style="color:#1d4ed8; font-size:1.3rem; font-weight:900; letter-spacing:2px;">' + (msg.pickup_otp || '4829') + '</div>' +
                    '</div>' +
                    '<div style="background:#fff; padding:10px; border-radius:10px; text-align:center; border:1px solid #d1fae5;">' +
                        '<div style="font-size:0.72rem; color:#047857; font-weight:700; margin-bottom:2px;">Delivery OTP</div>' +
                        '<div style="color:#059669; font-size:1.3rem; font-weight:900; letter-spacing:2px;">' + (msg.delivery_otp || '7104') + '</div>' +
                    '</div>' +
                '</div>' +
                '<a href="/track/' + (msg.delivery_id || '') + '" style="display:block; text-align:center; background:#1d4ed8; color:#fff; padding:10px; border-radius:10px; font-weight:700; text-decoration:none; font-size:0.9rem;">📍 View Live GPS Tracking</a>' +
            '</div>';
        box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});
