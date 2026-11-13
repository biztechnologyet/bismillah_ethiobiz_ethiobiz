// BISMALLAH ETHIOBIZ FULL-SCREEN GOOGLE MAPS-STYLE PORTAL JAVASCRIPT
// Handles Leaflet mapping, multi-layer tile switcher, marker clustering,
// branch badges, GPS FAB, bounds-fit, Google Maps directions & sidebar pin/collapse

(function() {
    function initEthiobizMapPortal() {
        let map = null;
        let markers = null;
        let currentCategory = "all";
        let userLocation = null;
        let allCompanies = [];
        let userGpsMarker = null;
        let userGpsCircle = null;

        initMap();
        initControls();
        loadCompanies();

        function initMap() {
            // Base tile layers (Free, reliable, no API key required)
            const streetLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "&copy; OpenStreetMap contributors | EthioBiz.ET",
                maxZoom: 19
            });

            const satelliteLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
                attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP | EthioBiz.ET",
                maxZoom: 19
            });

            // Pristine Clean Light basemap (Esri Light Gray Canvas - 100% free, no API key required)
            const cleanLightLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
                attribution: "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | EthioBiz.ET",
                maxZoom: 19
            });

            const mapEl = document.getElementById("ethiobiz-fullscreen-map");
            if (!mapEl) return;

            map = L.map("ethiobiz-fullscreen-map", {
                zoomControl: false,
                layers: [streetLayer]
            }).setView([9.010, 38.761], 13);

            // Zoom control at bottom-right
            L.control.zoom({ position: "bottomright" }).addTo(map);

            // Multi-layer Switcher
            const baseMaps = {
                "🗺️ Streets": streetLayer,
                "🛰️ Satellite": satelliteLayer,
                "⚪ Clean Light": cleanLightLayer
            };
            L.control.layers(baseMaps, null, { position: "topright" }).addTo(map);

            markers = L.markerClusterGroup({
                showCoverageOnHover: false,
                spiderfyOnMaxZoom: true,
                maxClusterRadius: 45
            });
            map.addLayer(markers);
        }

        function initControls() {
            const wrapper = document.getElementById("map-portal-wrapper") || document.querySelector(".map-portal-wrapper");
            const sidebar = document.getElementById("map-sidebar");
            const btnToggle = document.getElementById("btn-toggle-map-sidebar");
            const btnPin = document.getElementById("btn-pin-map-sidebar");
            const btnFloatingExpand = document.getElementById("btn-floating-expand-sidebar");
            const btnFit = document.getElementById("btn-map-fit-bounds");
            const btnLocateFab = document.getElementById("btn-map-locate-fab");

            // 1. PIN / DOCK SIDEBAR TOGGLE WITH LOCALSTORAGE
            function setPinned(pinned, save=true) {
                if (!wrapper || !btnPin) return;
                if (pinned) {
                    wrapper.classList.add("is-pinned");
                    btnPin.classList.add("active");
                    btnPin.title = "Unpin / Float Sidebar";
                    btnPin.innerHTML = "📌";
                } else {
                    wrapper.classList.remove("is-pinned");
                    btnPin.classList.remove("active");
                    btnPin.title = "Pin / Dock Sidebar";
                    btnPin.innerHTML = "📍";
                }
                if (save) {
                    try {
                        localStorage.setItem("ethiobiz_map_sidebar_pinned", pinned ? "1" : "0");
                    } catch(e) {}
                }
                setTimeout(() => { if (map) map.invalidateSize(); }, 360);
            }

            // Restore pinned state from localStorage
            try {
                if (localStorage.getItem("ethiobiz_map_sidebar_pinned") === "1") {
                    setPinned(true, false);
                }
            } catch(e) {}

            if (btnPin) {
                btnPin.addEventListener("click", function(e) {
                    e.preventDefault();
                    const isNowPinned = !wrapper.classList.contains("is-pinned");
                    setPinned(isNowPinned, true);
                });
            }

            // 2. COLLAPSIBLE / EXPAND SIDEBAR TOGGLE
            function collapseSidebar() {
                if (wrapper) wrapper.classList.add("sidebar-collapsed");
                if (btnFloatingExpand) btnFloatingExpand.style.display = "flex";
                setTimeout(() => { if (map) map.invalidateSize(); }, 360);
            }

            function expandSidebar() {
                if (wrapper) wrapper.classList.remove("sidebar-collapsed");
                if (btnFloatingExpand) btnFloatingExpand.style.display = "none";
                setTimeout(() => { if (map) map.invalidateSize(); }, 360);
            }

            if (btnToggle) {
                btnToggle.addEventListener("click", function(e) {
                    e.preventDefault();
                    collapseSidebar();
                });
            }

            if (btnFloatingExpand) {
                btnFloatingExpand.addEventListener("click", function(e) {
                    e.preventDefault();
                    expandSidebar();
                });
            }

            // 3. FIT ALL MARKERS BOUNDS TOOL
            if (btnFit) {
                btnFit.addEventListener("click", function(e) {
                    e.preventDefault();
                    fitAllMarkers();
                });
            }

            // 4. GPS FAB / LOCATE ME TOOL
            if (btnLocateFab) {
                btnLocateFab.addEventListener("click", function(e) {
                    e.preventDefault();
                    locateUser(true);
                });
            }

            // Near Me Sidebar Button
            const btnNearMe = document.getElementById("btn-map-near-me");
            if (btnNearMe) {
                btnNearMe.addEventListener("click", function(e) {
                    e.preventDefault();
                    locateUser(true);
                });
            }

            // 5. Category Chips
            document.querySelectorAll(".map-cat-chip").forEach(chip => {
                chip.addEventListener("click", function(e) {
                    e.preventDefault();
                    document.querySelectorAll(".map-cat-chip").forEach(c => c.classList.remove("active"));
                    this.classList.add("active");
                    currentCategory = this.dataset.cat;
                    filterCompanies();
                });
            });

            // 6. Search Input
            const searchInput = document.getElementById("map-search-input");
            if (searchInput) {
                searchInput.addEventListener("input", function() {
                    filterCompanies(this.value.trim());
                });
            }

            // 7. Radius Slider
            const slider = document.getElementById("radius-slider");
            if (slider) {
                slider.addEventListener("input", function() {
                    const radiusVal = document.getElementById("radius-val");
                    if (radiusVal) radiusVal.innerText = this.value;
                    if (userLocation) {
                        loadCompanies(userLocation.lat, userLocation.lng, this.value);
                    }
                });
            }

            // 8. Close Dossier
            const btnCloseDossier = document.getElementById("btn-close-dossier");
            if (btnCloseDossier) {
                btnCloseDossier.addEventListener("click", function(e) {
                    e.preventDefault();
                    const p = document.getElementById("map-dossier-panel");
                    if (p) p.style.display = "none";
                });
            }
        }

        function fitAllMarkers() {
            if (!map || !markers) return;
            const layers = markers.getLayers();
            if (layers && layers.length > 0) {
                const bounds = markers.getBounds();
                if (bounds && bounds.isValid()) {
                    map.fitBounds(bounds, { padding: [60, 60], maxZoom: 14 });
                    return;
                }
            }
            map.setView([9.010, 38.761], 12);
        }

        function locateUser(zoomTo=true) {
            if (!navigator.geolocation) {
                alert("Geolocation is not supported by your browser");
                return;
            }

            const fab = document.getElementById("btn-map-locate-fab");
            if (fab) fab.classList.add("locating");

            navigator.geolocation.getCurrentPosition(
                pos => {
                    if (fab) fab.classList.remove("locating");
                    userLocation = {
                        lat: pos.coords.latitude,
                        lng: pos.coords.longitude
                    };

                    if (userGpsMarker && map) map.removeLayer(userGpsMarker);
                    if (userGpsCircle && map) map.removeLayer(userGpsCircle);

                    userGpsCircle = L.circle([userLocation.lat, userLocation.lng], {
                        radius: Math.max(pos.coords.accuracy || 50, 100),
                        fillColor: "#0d9488",
                        color: "#0d9488",
                        weight: 1,
                        opacity: 0.4,
                        fillOpacity: 0.15
                    }).addTo(map);

                    const gpsIcon = L.divIcon({
                        className: "user-gps-pulse-pin",
                        html: `<div class="pulse-ring"></div><div class="pulse-core"></div>`,
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                    });

                    userGpsMarker = L.marker([userLocation.lat, userLocation.lng], { icon: gpsIcon })
                        .addTo(map)
                        .bindPopup("<strong>📍 Your Current Location</strong><br><span style='font-size:0.8rem;color:#64748b;'>Accuracy: ~" + Math.round(pos.coords.accuracy || 0) + "m</span>");

                    if (zoomTo) {
                        map.flyTo([userLocation.lat, userLocation.lng], 14, { duration: 1.2 });
                        userGpsMarker.openPopup();
                    }

                    const radius = document.getElementById("radius-slider") ? document.getElementById("radius-slider").value : 5;
                    loadCompanies(userLocation.lat, userLocation.lng, radius);
                },
                err => {
                    if (fab) fab.classList.remove("locating");
                    console.warn("Geolocation failed:", err);
                    alert("Could not retrieve your location. Please check your location permissions.");
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
            );
        }

        function loadCompanies(userLat=null, userLng=null, radius=null) {
            const countEl = document.getElementById("map-feed-count");
            if (countEl) countEl.innerText = "Discovering verified businesses...";

            const params = new URLSearchParams();
            if (currentCategory && currentCategory !== "all") params.append("category", currentCategory);
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
                    } else if (data.message && Array.isArray(data.message.companies)) {
                        allCompanies = data.message.companies;
                    } else if (data.message && Array.isArray(data.message)) {
                        allCompanies = data.message;
                    } else {
                        allCompanies = [];
                    }
                    filterCompanies();
                })
                .catch(err => {
                    console.error("Error loading map companies:", err);
                    if (countEl) countEl.innerText = "Error loading businesses. Retrying...";
                });
        }

        function filterCompanies(query="") {
            if (!markers) return;
            markers.clearLayers();
            const listContainer = document.getElementById("map-company-list");
            if (!listContainer) return;
            listContainer.innerHTML = "";

            const filtered = allCompanies.filter(comp => {
                const catStr = (comp.category || "").toLowerCase();
                const matchCat = (currentCategory === "all" || catStr.includes(currentCategory.toLowerCase()));
                const nameStr = (comp.company_name || comp.name || "").toLowerCase();
                const addrStr = (comp.address || "").toLowerCase();
                const matchQuery = !query || nameStr.includes(query.toLowerCase()) || addrStr.includes(query.toLowerCase());
                return matchCat && matchQuery;
            });

            const countEl = document.getElementById("map-feed-count");
            if (countEl) {
                countEl.innerText = `Found ${filtered.length} verified companies`;
            }

            if (filtered.length === 0) {
                listContainer.innerHTML = `<div style="padding:28px 16px;text-align:center;color:#64748b;font-size:0.88rem;line-height:1.5;">
                    <div style="font-size:2rem; margin-bottom:8px;">🗺️</div>
                    <strong>No businesses found in this selection.</strong><br>
                    Try choosing "All" or widening the search radius.
                </div>`;
                return;
            }

            filtered.forEach(comp => {
                // Ensure valid coordinates
                let lat = parseFloat(comp.lat);
                let lng = parseFloat(comp.lng);
                if (isNaN(lat) || isNaN(lng) || lat === 0) {
                    lat = 9.010;
                    lng = 38.761;
                }
                comp.lat = lat;
                comp.lng = lng;

                const displayName = comp.company_name || comp.name || "Business";
                const branchName = comp.name !== comp.company_name && comp.name ? comp.name : (comp.branch_type || "");
                const isPrimary = Boolean(comp.is_primary);
                const branchBadgeHtml = isPrimary 
                    ? `<span class="branch-badge primary">⭐ Head Office</span>` 
                    : (branchName ? `<span class="branch-badge branch">🏢 ${branchName}</span>` : '');

                const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${comp.lat},${comp.lng}`;

                // Render Card in Sidebar
                const card = document.createElement("div");
                card.className = "company-map-card";
                card.innerHTML = `
                    <img src="${comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${displayName}" class="comp-card-thumb" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                    <div class="comp-card-info">
                        <h4 class="comp-card-title">${displayName} ${branchBadgeHtml}</h4>
                        <div class="comp-card-meta">${comp.category || 'Business'} • ⭐ ${comp.rating || '5.0'}</div>
                        <p class="comp-card-meta">📍 ${comp.address || 'Ethiopia'}</p>
                        <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-top:4px;">
                            <span class="comp-card-badge">🟢 Open</span>
                            ${comp.distance_km ? `<span style="font-size:0.75rem; color:#64748b;">• ${comp.distance_km} km away</span>` : ''}
                        </div>
                    </div>
                `;
                card.addEventListener("click", () => openCompanyDossier(comp));
                listContainer.appendChild(card);

                // Add Pin to Map with rich SVG Pin Icon
                const pinColor = comp.pin_color || (isPrimary ? "#0d9488" : "#0284c7");
                const customIcon = L.divIcon({
                    className: "ethiobiz-map-pin",
                    html: `
                        <div style="position:relative; width:34px; height:34px; transform:translate(-50%, -100%);">
                            <div style="width:34px; height:34px; border-radius:50% 50% 50% 0; background: linear-gradient(135deg, ${pinColor} 0%, #0369a1 100%); transform:rotate(-45deg); display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(0,0,0,0.35); border:2px solid #ffffff;">
                                <span style="transform:rotate(45deg); font-size:14px;">📍</span>
                            </div>
                        </div>
                    `,
                    iconSize: [34, 34],
                    iconAnchor: [17, 34],
                    popupAnchor: [0, -32]
                });

                const marker = L.marker([comp.lat, comp.lng], { icon: customIcon });

                const popupHtml = `
                    <div class="map-rich-popup" style="min-width: 260px; font-family: 'Inter', -apple-system, sans-serif;">
                        <div style="width:100%; height:110px; overflow:hidden; border-radius:8px; margin-bottom:8px; background:#f1f5f9;">
                            <img src="${comp.banner || comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${displayName}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                        </div>
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                            <img src="${comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${displayName}" style="width:36px; height:36px; border-radius:6px; object-fit:cover; border:1px solid #e2e8f0;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                            <div>
                                <h4 style="margin:0; font-size:0.95rem; font-weight:700; color:#0f172a;">${displayName}</h4>
                                <div style="font-size:0.75rem; color:#0d9488; font-weight:700; margin-top:2px;">
                                    ${(comp.category || 'Business').toUpperCase()} • ⭐ ${comp.rating || '5.0'}
                                    ${branchBadgeHtml}
                                </div>
                            </div>
                        </div>
                        <p style="margin:0 0 10px 0; font-size:0.8rem; color:#64748b; line-height:1.35;">📍 ${comp.address || 'Ethiopia'}</p>
                        <div style="display:flex; gap:6px; flex-wrap:wrap;">
                            <a href="/shop?company=${encodeURIComponent(comp.company || comp.id)}" style="flex:1; min-width:85px; text-align:center; background:#0d9488; color:#ffffff !important; padding:6px 10px; border-radius:8px; font-weight:700; font-size:0.78rem; text-decoration:none; display:inline-block;">Store ➔</a>
                            <a href="${directionsUrl}" target="_blank" rel="noopener" style="flex:1; min-width:85px; text-align:center; background:#0284c7; color:#ffffff !important; padding:6px 10px; border-radius:8px; font-weight:700; font-size:0.78rem; text-decoration:none; display:inline-block;">🧭 Directions</a>
                            <button onclick="window.viewDossier('${comp.id}')" style="background:#f1f5f9; color:#1e293b; border:1px solid #cbd5e1; padding:6px 10px; border-radius:8px; font-weight:700; font-size:0.78rem; cursor:pointer;">Dossier</button>
                        </div>
                    </div>
                `;
                marker.bindPopup(popupHtml, { maxWidth: 300 });
                markers.addLayer(marker);
            });

            // Fit view to visible markers if not user locating
            if (filtered.length && !userLocation) {
                fitAllMarkers();
            }
        }

        function openCompanyDossier(comp) {
            const dossier = document.getElementById("map-dossier-panel");
            const body = document.getElementById("dossier-content");
            if (!dossier || !body) return;

            const displayName = comp.company_name || comp.name || "Business";
            const branchName = comp.name !== comp.company_name && comp.name ? comp.name : (comp.branch_type || "");
            const isPrimary = Boolean(comp.is_primary);
            const branchBadgeHtml = isPrimary 
                ? `<span class="branch-badge primary">⭐ Head Office</span>` 
                : (branchName ? `<span class="branch-badge branch">🏢 ${branchName}</span>` : '');

            const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${comp.lat},${comp.lng}`;

            body.innerHTML = `
                <img src="${comp.banner || comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${displayName}" style="width:100%; height:140px; object-fit:cover; border-radius:12px; margin-bottom:12px;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                    <img src="${comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${displayName}" style="width:50px; height:50px; border-radius:10px; object-fit:cover; border:1px solid #e2e8f0;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                    <div>
                        <h3 style="margin:0; font-size:1.2rem; font-weight:800; color:#0f172a;">${displayName}</h3>
                        <div style="margin-top:2px;">
                            <span style="font-size:0.85rem; color:#0d9488; font-weight:700;">✓ Verified EthioBiz Merchant</span>
                            ${branchBadgeHtml}
                        </div>
                    </div>
                </div>
                <p style="color:#64748b; font-size:0.9rem; line-height:1.5;">${comp.description || 'Welcome to our verified storefront on EthioBiz. Explore our catalog, book appointments, and request express delivery.'}</p>
                <hr style="border:none; border-top:1px solid #e2e8f0; margin:16px 0;" />
                
                <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:8px; margin-bottom:16px;">
                    <a href="${directionsUrl}" target="_blank" rel="noopener" style="text-align:center; background:#0284c7; color:#fff !important; padding:10px; border-radius:10px; font-weight:700; text-decoration:none; display:flex; align-items:center; justify-content:center; gap:6px;">🧭 Directions</a>
                    <a href="tel:${comp.phone || '+251911000000'}" style="text-align:center; background:#0d9488; color:#fff !important; padding:10px; border-radius:10px; font-weight:700; text-decoration:none; display:flex; align-items:center; justify-content:center; gap:6px;">📞 Call Direct</a>
                    <a href="/shop?company=${encodeURIComponent(comp.company || comp.id)}" style="text-align:center; background:#f1f5f9; color:#1e293b; padding:10px; border-radius:10px; font-weight:700; text-decoration:none;">🛒 Shop Store</a>
                    <a href="/bizservice?provider=${encodeURIComponent(comp.company || comp.id)}" style="text-align:center; background:#f1f5f9; color:#1e293b; padding:10px; border-radius:10px; font-weight:700; text-decoration:none;">📅 Book Service</a>
                </div>

                <div style="background:#f8fafc; padding:14px; border-radius:12px; font-size:0.88rem; border:1px solid #e2e8f0;">
                    <div style="margin-bottom:8px;"><strong>📍 Location:</strong> ${comp.address || 'Ethiopia'}</div>
                    <div style="margin-bottom:8px;"><strong>🕒 Hours:</strong> ${comp.working_hours || 'Mon - Sat: 8:30 AM - 6:30 PM'}</div>
                    <div><strong>🚚 Express Fulfillment:</strong> Available across regional hub</div>
                </div>
            `;

            dossier.style.display = "flex";
            map.setView([comp.lat, comp.lng], 16);
        }

        window.viewDossier = function(compId) {
            const comp = allCompanies.find(c => c.id === compId);
            if (comp) openCompanyDossier(comp);
        };
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initEthiobizMapPortal);
    } else {
        initEthiobizMapPortal();
    }
})();
