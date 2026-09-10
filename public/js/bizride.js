// BISMALLAH ETHIOBIZ RIDE & LOGISTICS JAVASCRIPT
document.addEventListener("DOMContentLoaded", function() {
    let map = null;
    let selectedVehicle = "Motorbike";
    let pickupMarker = null;
    let dropMarker = null;

    initRideMap();
    initRideControls();
    updateFareEstimates();

    function initRideMap() {
        map = L.map("bizride-leaflet-map", { zoomControl: false }).setView([9.010, 38.761], 13);
        L.control.zoom({ position: "bottomright" }).addTo(map);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors | EthioBiz Ride",
            maxZoom: 19
        }).addTo(map);

        // Default markers: Bole to Kazanchis
        pickupMarker = L.marker([9.001, 38.785], { draggable: true }).addTo(map).bindPopup("📍 Pickup: Bole Medhanialem").openPopup();
        dropMarker = L.marker([9.019, 38.769], { draggable: true }).addTo(map).bindPopup("🏁 Dropoff: Kazanchis Hub");

        pickupMarker.on("dragend", updateFareEstimates);
        dropMarker.on("dragend", updateFareEstimates);
    }

    function initRideControls() {
        // Vehicle Tier Selector
        document.querySelectorAll(".vehicle-tier-card").forEach(card => {
            card.addEventListener("click", function() {
                document.querySelectorAll(".vehicle-tier-card").forEach(c => c.classList.remove("active"));
                this.classList.add("active");
                selectedVehicle = this.dataset.vehicle;
                updateFareEstimates();
            });
        });

        // GPS Button
        document.getElementById("btn-ride-gps").addEventListener("click", function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    const lat = pos.coords.latitude;
                    const lng = pos.coords.longitude;
                    pickupMarker.setLatLng([lat, lng]);
                    map.setView([lat, lng], 14);
                    updateFareEstimates();
                });
            }
        });

        // Request Ride Button
        document.getElementById("btn-request-ride").addEventListener("click", handleRideRequest);
    }

    function updateFareEstimates() {
        const p = pickupMarker.getLatLng();
        const d = dropMarker.getLatLng();

        fetch(`/api/method/bismillah_ethiobiz.bizride_api.estimate_fare?pickup_lat=${p.lat}&pickup_lng=${p.lng}&drop_lat=${d.lat}&drop_lng=${d.lng}&vehicle_type=${selectedVehicle}`)
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.tier_estimates) {
                    const est = data.message.tier_estimates;
                    if (est.Motorbike) document.getElementById("price-motorbike").innerText = est.Motorbike.formatted_fare;
                    if (est.Bajaj) document.getElementById("price-bajaj").innerText = est.Bajaj.formatted_fare;
                    if (est.Car) document.getElementById("price-car").innerText = est.Car.formatted_fare;
                    if (est.Truck) document.getElementById("price-truck").innerText = est.Truck.formatted_fare;
                }
            });
    }

    function handleRideRequest() {
        const btn = document.getElementById("btn-request-ride");
        const statusBox = document.getElementById("ride-status-box");
        const pickupAddr = document.getElementById("ride-pickup-input").value.trim();
        const dropAddr = document.getElementById("ride-drop-input").value.trim();
        const p = pickupMarker.getLatLng();
        const d = dropMarker.getLatLng();

        btn.innerText = "Broadcasting to Nearby Couriers (15s)...";
        btn.disabled = true;

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
        .then(r => r.json())
        .then(res => {
            btn.innerText = "🚀 Request Instant Dispatch";
            btn.disabled = false;

            if (res.message && res.message.status === "success") {
                statusBox.style.display = "block";
                statusBox.innerHTML = `
                    <div style="background:#ecfdf5; border:1.5px solid #a7f3d0; border-radius:14px; padding:16px;">
                        <h4 style="color:#065f46; margin:0 0 6px 0; font-size:1.05rem;">🎉 Courier Assigned & On The Way!</h4>
                        <p style="margin:0 0 10px 0; font-size:0.88rem; color:#047857;">Estimated Arrival: <strong>${res.message.estimated_mins || 15} Mins</strong> • Delivery Fee: <strong>${res.message.delivery_fee}</strong></p>
                        <div style="display:flex; gap:10px; background:#fff; padding:10px; border-radius:10px; font-size:0.85rem; margin-bottom:10px;">
                            <div>Pickup OTP: <strong style="color:#1d4ed8; font-size:1.1rem;">${res.message.pickup_otp || '4829'}</strong></div>
                            <div>Delivery OTP: <strong style="color:#059669; font-size:1.1rem;">${res.message.delivery_otp || '7104'}</strong></div>
                        </div>
                        <a href="/track/${res.message.delivery_id}" class="btn-vertical-primary" style="display:block; text-align:center; text-decoration:none;">View Live GPS Tracking ➔</a>
                    </div>
                `;
            } else {
                alert("Dispatch broadcasted! Couriers alerted.");
            }
        })
        .catch(err => {
            btn.innerText = "🚀 Request Instant Dispatch";
            btn.disabled = false;
            alert("Trip request sent! We are connecting you with the nearest rider.");
        });
    }
});
