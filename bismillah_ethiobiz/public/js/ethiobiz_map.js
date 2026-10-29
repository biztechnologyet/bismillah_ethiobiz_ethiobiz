// BISMALLAH ETHIOBIZ FULL-SCREEN GOOGLE MAPS-STYLE PORTAL JAVASCRIPT
// Handles Leaflet mapping, multi-layer tile switcher, marker clustering,
// branch badges, GPS FAB, bounds-fit, Google Maps directions & sidebar pin/collapse

(function() {
    function initEthiobizMapPortal() {
        console.log("[EthioBiz Map] Portal Initializing...");

        let map = null;
        let markers = null;
        let currentCategory = "all";
        let userLocation = null;
        let allCompanies = [];
        let userGpsMarker = null;
        let userGpsCircle = null;

        // 1. Initialize UI Controls FIRST so sidebar collapse, pin, search work immediately
        initControls();

        // 2. Wait for Leaflet & Leaflet.markercluster to be ready, then init map and load data
        startMapEngine(20);

        function startMapEngine(retriesRemaining) {
            if (typeof L !== "undefined") {
                console.log("[EthioBiz Map] Leaflet detected, initializing canvas...");
                initMap();
                loadCompanies();
            } else if (retriesRemaining > 0) {
                console.log("[EthioBiz Map] Waiting for Leaflet... retries left: " + retriesRemaining);
                setTimeout(function() { startMapEngine(retriesRemaining - 1); }, 150);
            } else {
                console.warn("[EthioBiz Map] Leaflet timed out. Loading companies to sidebar directly.");
                loadCompanies();
            }
        }

        function initMap() {
            try {
                const mapEl = document.getElementById("ethiobiz-fullscreen-map");
                if (!mapEl) {
                    console.error("[EthioBiz Map] Element #ethiobiz-fullscreen-map not found");
                    return false;
                }

                // Base tile layers (Free, reliable, no API key required)
                const streetLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                    attribution: "&copy; OpenStreetMap contributors | EthioBiz.ET",
                    maxZoom: 19
                });

                const satelliteLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
                    attribution: "Tiles &copy; Esri &mdash; EthioBiz.ET",
                    maxZoom: 19
                });

                // Pristine Clean Light basemap (Esri Light Gray Canvas - 100% free, no API key required)
                const cleanLightLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
                    attribution: "Tiles &copy; Esri &mdash; EthioBiz.ET",
                    maxZoom: 19
                });

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

                // Safe Marker Clustering with fallback
                if (typeof L.markerClusterGroup === "function") {
                    try {
                        markers = L.markerClusterGroup({
                            showCoverageOnHover: false,
                            spiderfyOnMaxZoom: true,
                            maxClusterRadius: 45
                        });
                        console.log("[EthioBiz Map] MarkerClusterGroup active.");
                    } catch(err) {
                        console.warn("[EthioBiz Map] MarkerClusterGroup failed, falling back to featureGroup", err);
                        markers = L.featureGroup();
                    }
                } else {
                    console.warn("[EthioBiz Map] L.markerClusterGroup not defined. Using L.featureGroup fallback.");
                    markers = L.featureGroup();
                }

                map.addLayer(markers);
                return true;
            } catch(e) {
                console.error("[EthioBiz Map] Exception in initMap:", e);
                return false;
            }
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
            function setPinned(pinned, save) {
                if (save === undefined) save = true;
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
                setTimeout(function() { if (map) map.invalidateSize(); }, 360);
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
                if (sidebar) sidebar.classList.add("is-collapsed");
                if (btnFloatingExpand) btnFloatingExpand.style.display = "flex";
                setTimeout(function() { if (map) map.invalidateSize(); }, 360);
            }

            function expandSidebar() {
                if (wrapper) wrapper.classList.remove("sidebar-collapsed");
                if (sidebar) sidebar.classList.remove("is-collapsed");
                if (btnFloatingExpand) btnFloatingExpand.style.display = "none";
                setTimeout(function() { if (map) map.invalidateSize(); }, 360);
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
            document.querySelectorAll(".map-cat-chip").forEach(function(chip) {
                chip.addEventListener("click", function(e) {
                    e.preventDefault();
                    document.querySelectorAll(".map-cat-chip").forEach(function(c) { c.classList.remove("active"); });
                    this.classList.add("active");
                    currentCategory = this.dataset.cat;
                    filterCompanies();
                });
            });

            // 6. Search Input
            const searchInput = document.getElementById("map-search-input");
            if (searchInput) {
                let debounceTimer;
                searchInput.addEventListener("input", function(e) {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(function() {
                        filterCompanies(e.target.value.trim());
                    }, 250);
                });
            }

            // Search Icon Button
            const btnSearch = document.getElementById("btn-sidebar-search");
            if (btnSearch && searchInput) {
                btnSearch.addEventListener("click", function(e) {
                    e.preventDefault();
                    filterCompanies(searchInput.value.trim());
                });
            }

            // Radius Slider
            const radiusSlider = document.getElementById("radius-slider");
            const radiusVal = document.getElementById("radius-val");
            if (radiusSlider && radiusVal) {
                radiusSlider.addEventListener("input", function(e) {
                    radiusVal.innerText = e.target.value;
                });
                radiusSlider.addEventListener("change", function(e) {
                    if (userLocation) {
                        loadCompanies(userLocation.lat, userLocation.lng, e.target.value);
                    }
                });
            }

            // Back button in Dossier
            const btnCloseDossier = document.getElementById("btn-close-dossier");
            if (btnCloseDossier) {
                btnCloseDossier.addEventListener("click", function(e) {
                    e.preventDefault();
                    const dossier = document.getElementById("map-dossier-panel");
                    if (dossier) dossier.style.display = "none";
                });
            }

            console.log("[EthioBiz Map] Controls & Event Listeners Bound Successfully.");
        }

        function fitAllMarkers() {
            if (!map || !markers) return;
            try {
                const layers = markers.getLayers ? markers.getLayers() : [];
                if (layers.length > 0 && typeof markers.getBounds === "function") {
                    const bounds = markers.getBounds();
                    if (bounds.isValid && bounds.isValid()) {
                        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
                    }
                } else {
                    map.setView([9.010, 38.761], 13);
                }
            } catch(e) {
                console.warn("[EthioBiz Map] Error fitting bounds:", e);
                map.setView([9.010, 38.761], 13);
            }
        }

        function locateUser(animate) {
            if (animate === undefined) animate = true;
            if (!navigator.geolocation) {
                alert("Geolocation is not supported by your browser.");
                return;
            }

            const btnLocateFab = document.getElementById("btn-map-locate-fab");
            if (btnLocateFab) btnLocateFab.classList.add("locating");

            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    if (btnLocateFab) btnLocateFab.classList.remove("locating");
                    const lat = pos.coords.latitude;
                    const lng = pos.coords.longitude;
                    const accuracy = pos.coords.accuracy;
                    userLocation = { lat: lat, lng: lng };

                    if (map && typeof L !== "undefined") {
                        if (userGpsMarker) map.removeLayer(userGpsMarker);
                        if (userGpsCircle) map.removeLayer(userGpsCircle);

                        userGpsMarker = L.circleMarker([lat, lng], {
                            radius: 8,
                            fillColor: "#2563eb",
                            color: "#ffffff",
                            weight: 3,
                            opacity: 1,
                            fillOpacity: 1
                        }).addTo(map);
                        userGpsMarker.bindPopup("<strong>You are here</strong>");

                        userGpsCircle = L.circle([lat, lng], {
                            radius: accuracy,
                            fillColor: "#3b82f6",
                            fillOpacity: 0.15,
                            color: "#2563eb",
                            weight: 1
                        }).addTo(map);

                        if (animate) {
                            map.flyTo([lat, lng], 14, { duration: 1.5 });
                        }
                    }

                    const radiusSlider = document.getElementById("radius-slider");
                    const radius = radiusSlider ? radiusSlider.value : 5;
                    loadCompanies(lat, lng, radius);
                },
                function(err) {
                    if (btnLocateFab) btnLocateFab.classList.remove("locating");
                    console.warn("[EthioBiz Map] Geolocation failed:", err.message);
                    alert("Could not retrieve your current location. Please ensure location services are enabled.");
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
            );
        }

        function loadCompanies(userLat, userLng, radius) {
            const countEl = document.getElementById("map-feed-count");
            if (countEl) countEl.innerText = "Discovering verified businesses...";

            const params = new URLSearchParams();
            if (currentCategory && currentCategory !== "all") params.append("category", currentCategory);
            if (userLat && userLng) {
                params.append("user_lat", userLat);
                params.append("user_lng", userLng);
            }
            if (radius) params.append("radius_km", radius);

            fetch("/api/method/bismillah_ethiobiz.magala_shop_api.get_companies_map?" + params.toString())
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.message && data.message.status === "success") {
                        allCompanies = data.message.companies || [];
                    } else if (data.message && Array.isArray(data.message.companies)) {
                        allCompanies = data.message.companies;
                    } else if (data.message && Array.isArray(data.message)) {
                        allCompanies = data.message;
                    } else {
                        allCompanies = [];
                    }
                    console.log("[EthioBiz Map] Loaded " + allCompanies.length + " companies from API.");
                    filterCompanies();
                })
                .catch(function(err) {
                    console.error("[EthioBiz Map] Error loading map companies:", err);
                    if (countEl) countEl.innerText = "Error loading businesses. Retrying...";
                });
        }

        function filterCompanies(query) {
            if (query === undefined) query = "";
            if (markers && typeof markers.clearLayers === "function") {
                markers.clearLayers();
            }

            const listContainer = document.getElementById("map-company-list");
            if (!listContainer) return;
            listContainer.innerHTML = "";

            const filtered = allCompanies.filter(function(comp) {
                const catStr = (comp.category || "").toLowerCase();
                const matchCat = (currentCategory === "all" || catStr.includes(currentCategory.toLowerCase()));
                const nameStr = (comp.company_name || comp.name || "").toLowerCase();
                const addrStr = (comp.address || "").toLowerCase();
                const matchQuery = !query || nameStr.includes(query.toLowerCase()) || addrStr.includes(query.toLowerCase());
                return matchCat && matchQuery;
            });

            const countEl = document.getElementById("map-feed-count");
            if (countEl) {
                countEl.innerText = "Found " + filtered.length + " verified companies";
            }

            if (filtered.length === 0) {
                listContainer.innerHTML = '<div style="padding:28px 16px;text-align:center;color:#64748b;font-size:0.88rem;line-height:1.5;">' +
                    '<div style="font-size:2rem; margin-bottom:8px;">🗺️</div>' +
                    '<strong>No businesses found in this selection.</strong><br>' +
                    'Try choosing "All" or widening the search radius.' +
                '</div>';
                return;
            }

            filtered.forEach(function(comp) {
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
                    ? '<span class="branch-badge primary">⭐ Head Office</span>' 
                    : (branchName ? '<span class="branch-badge branch">🏢 ' + branchName + '</span>' : '');

                const directionsUrl = "https://www.google.com/maps/dir/?api=1&destination=" + comp.lat + "," + comp.lng;

                // Render Card in Sidebar
                const card = document.createElement("div");
                card.className = "company-map-card";
                card.innerHTML = 
                    '<img src="' + (comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png') + '" alt="' + displayName + '" class="comp-card-thumb" onerror="this.src=\'/assets/bismillah_ethiobiz/img/walta_real_logo.png\'" />' +
                    '<div class="comp-card-info">' +
                        '<div class="comp-card-name-row">' +
                            '<h4 class="comp-card-title">' + displayName + '</h4>' +
                            branchBadgeHtml +
                        '</div>' +
                        '<div class="comp-card-meta">' +
                            '<span class="badge-cat">' + (comp.category || 'Business') + '</span>' +
                            '<span class="rating">⭐ ' + (comp.rating || '5.0') + '</span>' +
                        '</div>' +
                        '<p class="comp-card-address">📍 ' + (comp.address || 'Ethiopia') + '</p>' +
                        '<div class="comp-card-actions">' +
                            '<a href="/shop?company=' + encodeURIComponent(comp.company || comp.id) + '" class="btn-card-action primary">Visit Shop</a>' +
                            '<a href="' + directionsUrl + '" target="_blank" rel="noopener" class="btn-card-action secondary">Directions</a>' +
                        '</div>' +
                    '</div>';

                card.addEventListener("click", function(e) {
                    if (e.target.tagName === 'A' || e.target.closest('a')) return;
                    if (map) {
                        map.setView([comp.lat, comp.lng], 16);
                        if (marker && marker.openPopup) marker.openPopup();
                    }
                    openCompanyDossier(comp);
                });

                listContainer.appendChild(card);

                // Add Leaflet Pin if map & Leaflet are loaded
                let marker = null;
                if (typeof L !== "undefined" && markers && map) {
                    const customIcon = L.divIcon({
                        className: "ethiobiz-custom-pin",
                        html: 
                            '<div style="position:relative; width:34px; height:34px;">' +
                                '<div style="position:absolute; width:34px; height:34px; background:#0d9488; border-radius:50% 50% 50% 0; transform:rotate(-45deg); border:2px solid #ffffff; box-shadow:0 3px 8px rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center;">' +
                                    '<span style="transform:rotate(45deg); font-size:14px;">📍</span>' +
                                '</div>' +
                            '</div>',
                        iconSize: [34, 34],
                        iconAnchor: [17, 34],
                        popupAnchor: [0, -32]
                    });

                    marker = L.marker([comp.lat, comp.lng], { icon: customIcon });

                    const popupHtml = 
                        '<div class="map-rich-popup" style="min-width: 260px; font-family: \'Inter\', -apple-system, sans-serif;">' +
                            '<div style="width:100%; height:110px; overflow:hidden; border-radius:8px; margin-bottom:8px; background:#f1f5f9;">' +
                                '<img src="' + (comp.banner || comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png') + '" alt="' + displayName + '" style="width:100%; height:100%; object-fit:cover;" onerror="this.src=\'/assets/bismillah_ethiobiz/img/walta_real_logo.png\'" />' +
                            '</div>' +
                            '<div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">' +
                                '<img src="' + (comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png') + '" alt="' + displayName + '" style="width:36px; height:36px; border-radius:6px; object-fit:cover; border:1px solid #e2e8f0;" onerror="this.src=\'/assets/bismillah_ethiobiz/img/walta_real_logo.png\'" />' +
                                '<div>' +
                                    '<h4 style="margin:0; font-size:0.95rem; font-weight:700; color:#0f172a;">' + displayName + '</h4>' +
                                    '<div style="font-size:0.75rem; color:#0d9488; font-weight:700; margin-top:2px;">' +
                                        (comp.category || 'Business').toUpperCase() + ' • ⭐ ' + (comp.rating || '5.0') +
                                        branchBadgeHtml +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<p style="margin:0 0 10px 0; font-size:0.8rem; color:#64748b; line-height:1.35;">📍 ' + (comp.address || 'Ethiopia') + '</p>' +
                            '<div style="display:flex; gap:6px; flex-wrap:wrap;">' +
                                '<a href="/shop?company=' + encodeURIComponent(comp.company || comp.id) + '" style="flex:1; min-width:85px; text-align:center; background:#0d9488; color:#ffffff !important; padding:6px 10px; border-radius:8px; font-weight:700; font-size:0.78rem; text-decoration:none; display:inline-block;">Store ➔</a>' +
                                '<a href="' + directionsUrl + '" target="_blank" rel="noopener" style="flex:1; min-width:85px; text-align:center; background:#0284c7; color:#ffffff !important; padding:6px 10px; border-radius:8px; font-weight:700; font-size:0.78rem; text-decoration:none; display:inline-block;">🧭 Directions</a>' +
                                '<button onclick="window.viewDossier(\'' + comp.id + '\')" style="background:#f1f5f9; color:#1e293b; border:1px solid #cbd5e1; padding:6px 10px; border-radius:8px; font-weight:700; font-size:0.78rem; cursor:pointer;">Dossier</button>' +
                            '</div>' +
                        '</div>';
                    marker.bindPopup(popupHtml, { maxWidth: 300 });
                    markers.addLayer(marker);
                }
            });

            // Fit view to visible markers if not user locating
            if (filtered.length && !userLocation && map && markers) {
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
                ? '<span class="branch-badge primary">⭐ Head Office</span>' 
                : (branchName ? '<span class="branch-badge branch">🏢 ' + branchName + '</span>' : '');

            const directionsUrl = "https://www.google.com/maps/dir/?api=1&destination=" + comp.lat + "," + comp.lng;

            body.innerHTML = 
                '<div style="position:relative; margin-bottom:16px; border-radius:12px; overflow:hidden;">' +
                    '<img src="' + (comp.banner || comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png') + '" alt="' + displayName + '" style="width:100%; height:160px; object-fit:cover;" onerror="this.src=\'/assets/bismillah_ethiobiz/img/walta_real_logo.png\'" />' +
                '</div>' +
                '<div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">' +
                    '<img src="' + (comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png') + '" alt="' + displayName + '" style="width:56px; height:56px; border-radius:12px; object-fit:cover; border:2px solid #e2e8f0;" onerror="this.src=\'/assets/bismillah_ethiobiz/img/walta_real_logo.png\'" />' +
                    '<div>' +
                        '<h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#0f172a;">' + displayName + '</h3>' +
                        '<div style="font-size:0.82rem; color:#0d9488; font-weight:700; margin-top:3px;">' +
                            (comp.category || 'Business') + ' ' + branchBadgeHtml +
                        '</div>' +
                    '</div>' +
                '</div>' +
                '<p style="font-size:0.88rem; color:#475569; line-height:1.5; margin-bottom:16px;">' +
                    (comp.description || 'Verified enterprise operating on the EthioBiz Cloud Network in Ethiopia.') +
                '</p>' +
                '<div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:16px;">' +
                    '<a href="/shop?company=' + encodeURIComponent(comp.company || comp.id) + '" class="btn-card-action primary" style="text-align:center; padding:10px; font-size:0.9rem;">' +
                        '🏪 Open Shop' +
                    '</a>' +
                    '<a href="' + directionsUrl + '" target="_blank" rel="noopener" class="btn-card-action secondary" style="text-align:center; padding:10px; font-size:0.9rem;">' +
                        '🧭 Directions' +
                    '</a>' +
                '</div>' +
                '<div style="background:#f8fafc; padding:14px; border-radius:12px; font-size:0.88rem; border:1px solid #e2e8f0;">' +
                    '<div style="margin-bottom:8px;"><strong>📍 Location:</strong> ' + (comp.address || 'Ethiopia') + '</div>' +
                    '<div style="margin-bottom:8px;"><strong>🕒 Hours:</strong> ' + (comp.working_hours || 'Mon - Sat: 8:30 AM - 6:30 PM') + '</div>' +
                    '<div><strong>🚚 Express Fulfillment:</strong> Available across regional hub</div>' +
                '</div>';

            dossier.style.display = "flex";
            if (map) map.setView([comp.lat, comp.lng], 16);
        }

        window.viewDossier = function(compId) {
            const comp = allCompanies.find(function(c) { return c.id === compId; });
            if (comp) openCompanyDossier(comp);
        };
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initEthiobizMapPortal);
    } else {
        initEthiobizMapPortal();
    }
})();
