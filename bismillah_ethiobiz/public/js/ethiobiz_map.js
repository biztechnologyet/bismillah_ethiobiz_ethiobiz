// BISMALLAH ETHIOBIZ FULL-SCREEN GOOGLE MAPS-STYLE PORTAL JAVASCRIPT
// Handles Leaflet mapping, marker clustering, company dossier drawer, search & GPS near me

document.addEventListener("DOMContentLoaded", function() {
    let map = null;
    let markers = null;
    let currentCategory = "all";
    let userLocation = null;
    let allCompanies = [];

    initMap();
    initControls();
    loadCompanies();

    function initMap() {
        map = L.map("ethiobiz-fullscreen-map", {
            zoomControl: false
        }).setView([9.010, 38.761], 13);

        L.control.zoom({ position: "bottomright" }).addTo(map);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors | EthioBiz.ET",
            maxZoom: 19
        }).addTo(map);

        markers = L.markerClusterGroup({
            showCoverageOnHover: false,
            spiderfyOnMaxZoom: true
        });
        map.addLayer(markers);
    }

    function initControls() {
        // Category Chips
        document.querySelectorAll(".map-cat-chip").forEach(chip => {
            chip.addEventListener("click", function() {
                document.querySelectorAll(".map-cat-chip").forEach(c => c.classList.remove("active"));
                this.classList.add("active");
                currentCategory = this.dataset.cat;
                filterCompanies();
            });
        });

        // Search Input
        const searchInput = document.getElementById("map-search-input");
        searchInput.addEventListener("input", function() {
            filterCompanies(this.value.trim());
        });

        // Near Me Button
        document.getElementById("btn-map-near-me").addEventListener("click", function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    userLocation = {
                        lat: pos.coords.latitude,
                        lng: pos.coords.longitude
                    };
                    map.setView([userLocation.lat, userLocation.lng], 14);
                    L.circleMarker([userLocation.lat, userLocation.lng], {
                        radius: 8,
                        fillColor: "#3b82f6",
                        color: "#fff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.9
                    }).addTo(map).bindPopup("📍 Your Current Location").openPopup();
                    loadCompanies(userLocation.lat, userLocation.lng);
                });
            }
        });

        // Radius Slider
        const slider = document.getElementById("radius-slider");
        slider.addEventListener("input", function() {
            document.getElementById("radius-val").innerText = this.value;
            if (userLocation) {
                loadCompanies(userLocation.lat, userLocation.lng, this.value);
            }
        });

        // Close Dossier
        document.getElementById("btn-close-dossier").addEventListener("click", function() {
            document.getElementById("map-dossier-panel").style.display = "none";
        });
    }

    function loadCompanies(userLat=null, userLng=null, radius=null) {
        const params = new URLSearchParams();
        if (currentCategory !== "all") params.append("category", currentCategory);
        if (userLat && userLng) {
            params.append("user_lat", userLat);
            params.append("user_lng", userLng);
        }
        if (radius) params.append("radius_km", radius);

        fetch(`/api/method/bismillah_ethiobiz.magala_shop_api.get_companies_map?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.status === "success") {
                    allCompanies = data.message.companies || [];
                    filterCompanies();
                }
            });
    }

    function filterCompanies(query="") {
        markers.clearLayers();
        const listContainer = document.getElementById("map-company-list");
        listContainer.innerHTML = "";

        const filtered = allCompanies.filter(comp => {
            const matchCat = (currentCategory === "all" || comp.category.toLowerCase().includes(currentCategory.toLowerCase()));
            const matchQuery = !query || comp.name.toLowerCase().includes(query.toLowerCase()) || comp.address.toLowerCase().includes(query.toLowerCase());
            return matchCat && matchQuery;
        });

        document.getElementById("map-feed-count").innerText = `Found ${filtered.length} verified companies`;

        filtered.forEach(comp => {
            // Render Card in Sidebar
            const card = document.createElement("div");
            card.className = "company-map-card";
            card.innerHTML = `
                <img src="${comp.logo}" alt="${comp.name}" class="comp-card-thumb" />
                <div class="comp-card-info">
                    <h4 class="comp-card-title">${comp.name}</h4>
                    <div class="comp-card-meta">${comp.category} • ⭐ ${comp.rating}</div>
                    <p class="comp-card-meta">${comp.address}</p>
                    <span class="comp-card-badge">🟢 Open Now</span>
                    ${comp.distance_km ? `<span style="font-size:0.75rem; color:#64748b; margin-left:8px;">📍 ${comp.distance_km} km away</span>` : ''}
                </div>
            `;
            card.addEventListener("click", () => openCompanyDossier(comp));
            listContainer.appendChild(card);

            // Add Pin to Map with rich Image & Go to Company action
            const marker = L.marker([comp.lat, comp.lng]);
            const popupHtml = `
                <div class="map-rich-popup" style="min-width: 240px; font-family: 'Inter', sans-serif;">
                    <div style="width:100%; height:110px; overflow:hidden; border-radius:8px; margin-bottom:8px; background:#f1f5f9;">
                        <img src="${comp.banner || comp.logo}" alt="${comp.name}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                        <img src="${comp.logo}" alt="${comp.name}" style="width:36px; height:36px; border-radius:6px; object-fit:cover; border:1px solid #e2e8f0;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                        <div>
                            <h4 style="margin:0; font-size:0.95rem; font-weight:700; color:#0f172a;">${comp.name}</h4>
                            <span style="font-size:0.75rem; color:#1FB6AE; font-weight:600;">${comp.category.toUpperCase()} • ⭐ ${comp.rating}</span>
                        </div>
                    </div>
                    <p style="margin:0 0 8px 0; font-size:0.8rem; color:#64748b; line-height:1.3;">📍 ${comp.address}</p>
                    <div style="display:flex; gap:6px;">
                        <a href="/shop?company=${encodeURIComponent(comp.id)}" style="flex:1; text-align:center; background:#1FB6AE; color:#ffffff !important; padding:6px 10px; border-radius:6px; font-weight:600; font-size:0.8rem; text-decoration:none; display:inline-block;">Go to Company ➔</a>
                        <button onclick="window.viewDossier('${comp.id}')" style="background:#f1f5f9; color:#1e293b; border:1px solid #cbd5e1; padding:6px 10px; border-radius:6px; font-weight:600; font-size:0.8rem; cursor:pointer;">Dossier</button>
                    </div>
                </div>
            `;
            marker.bindPopup(popupHtml, { maxWidth: 280 });
            markers.addLayer(marker);
        });

        if (filtered.length && !userLocation) {
            map.setView([filtered[0].lat, filtered[0].lng], 13);
        }
    }

    function openCompanyDossier(comp) {
        const dossier = document.getElementById("map-dossier-panel");
        const body = document.getElementById("dossier-content");

        body.innerHTML = `
            <img src="${comp.banner}" alt="${comp.name}" style="width:100%; height:140px; object-fit:cover; border-radius:12px; margin-bottom:12px;" />
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                <img src="${comp.logo}" alt="${comp.name}" style="width:50px; height:50px; border-radius:10px;" />
                <div>
                    <h3 style="margin:0; font-size:1.2rem;">${comp.name}</h3>
                    <span style="font-size:0.85rem; color:#1FB6AE; font-weight:600;">✓ Verified EthioBiz Merchant</span>
                </div>
            </div>
            <p style="color:#64748b; font-size:0.9rem;">${comp.description || 'Welcome to our verified storefront on EthioBiz. Explore our catalog, book appointments, and request express delivery.'}</p>
            <hr style="border-top:1px solid #e2e8f0; margin:16px 0;" />
            <div style="display:flex; gap:8px; margin-bottom:16px;">
                <a href="tel:${comp.phone}" style="flex:1; text-align:center; background:#1FB6AE; color:#fff; padding:10px; border-radius:10px; font-weight:600; text-decoration:none;">📞 Call</a>
                <a href="/shop?company=${encodeURIComponent(comp.id)}" style="flex:1; text-align:center; background:#f1f5f9; color:#1e293b; padding:10px; border-radius:10px; font-weight:600; text-decoration:none;">🛒 Shop</a>
                <a href="/book?company=${encodeURIComponent(comp.id)}" style="flex:1; text-align:center; background:#f1f5f9; color:#1e293b; padding:10px; border-radius:10px; font-weight:600; text-decoration:none;">📅 Book</a>
            </div>
            <div style="background:#f8fafc; padding:12px; border-radius:10px; font-size:0.88rem;">
                <div style="margin-bottom:6px;"><strong>📍 Location:</strong> ${comp.address}</div>
                <div style="margin-bottom:6px;"><strong>🕒 Hours:</strong> ${comp.working_hours}</div>
                <div><strong>🚚 BizRide Express:</strong> 45 min delivery available</div>
            </div>
        `;

        dossier.style.display = "flex";
        map.setView([comp.lat, comp.lng], 15);
    }

    window.viewDossier = function(compId) {
        const comp = allCompanies.find(c => c.id === compId);
        if (comp) openCompanyDossier(comp);
    };
});
