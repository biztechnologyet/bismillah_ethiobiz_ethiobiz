// BISMALLAH ETHIOBIZ MAGALA SHOP ENGINE JAVASCRIPT
// Handles 3-way view switcher (Grid, List, Map), interactive map node filtering,
// collapsible filter sidebar, product detail navigation & shopping cart

document.addEventListener("DOMContentLoaded", function() {
    console.log("[Magala Shop] Engine Initializing...");

    let currentView = localStorage.getItem("magala_view_mode") || "grid";
    let currentCategory = "all";
    let currentPage = 1;
    let mapInstance = null;
    let markerCluster = null;
    let allMapCompanies = [];
    let isMapLoaded = false;
    let isSidebarCollapsed = localStorage.getItem("magala_sidebar_collapsed") === "true";
    let userLocation = null;

    const urlParams = new URLSearchParams(window.location.search);
    const selectedCompany = (urlParams.get("company") || "").trim();

    initCollapsibleSidebar();
    initViewSwitcher();
    initSearch();
    initFilters();
    initCart();
    loadProducts();

    // If map view was stored or URL directs to map
    if (currentView === "map") {
        applyViewLayout();
    }

    // 1. COLLAPSIBLE SIDEBAR
    function initCollapsibleSidebar() {
        const toggleBtn = document.getElementById("btn-toggle-filters");
        const sidebar = document.querySelector(".magala-sidebar");
        const layout = document.querySelector(".magala-layout");
        const toggleText = document.getElementById("toggle-filter-text");

        if (isSidebarCollapsed && sidebar && layout) {
            sidebar.classList.add("collapsed");
            layout.classList.add("sidebar-collapsed");
            if (toggleText) toggleText.innerText = "Show Filters";
        }

        if (toggleBtn && sidebar && layout) {
            toggleBtn.addEventListener("click", function() {
                const isMobile = window.innerWidth <= 992;
                if (isMobile) {
                    sidebar.classList.toggle("mobile-open");
                } else {
                    isSidebarCollapsed = !isSidebarCollapsed;
                    localStorage.setItem("magala_sidebar_collapsed", isSidebarCollapsed);
                    sidebar.classList.toggle("collapsed", isSidebarCollapsed);
                    layout.classList.toggle("sidebar-collapsed", isSidebarCollapsed);
                    if (toggleText) toggleText.innerText = isSidebarCollapsed ? "Show Filters" : "Hide Filters";
                }
                setTimeout(function() {
                    if (mapInstance) mapInstance.invalidateSize();
                }, 300);
            });
        }
    }

    // 2. VIEW SWITCHER (Grid | List | Map)
    function initViewSwitcher() {
        const viewBtns = document.querySelectorAll(".view-btn");
        viewBtns.forEach(function(btn) {
            if (btn.dataset.view === currentView) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }

            btn.addEventListener("click", function() {
                viewBtns.forEach(function(b) { b.classList.remove("active"); });
                this.classList.add("active");
                currentView = this.dataset.view;
                localStorage.setItem("magala_view_mode", currentView);
                applyViewLayout();
                if (currentView !== "map" && window.__lastFetchedItems) {
                    renderItems(window.__lastFetchedItems);
                }
            });
        });
    }

    function applyViewLayout() {
        const container = document.getElementById("magala-items-container");
        const mapContainer = document.getElementById("magala-embedded-map-container");
        const pagination = document.getElementById("magala-pagination");

        if (!container || !mapContainer) return;

        if (currentView === "grid") {
            container.style.display = "grid";
            container.className = "magala-grid-view";
            mapContainer.style.display = "none";
            if (pagination) pagination.style.display = "flex";
        } else if (currentView === "list") {
            container.style.display = "flex";
            container.className = "magala-list-view";
            mapContainer.style.display = "none";
            if (pagination) pagination.style.display = "flex";
        } else if (currentView === "map") {
            container.style.display = "none";
            mapContainer.style.display = "block";
            if (pagination) pagination.style.display = "none";
            initEmbeddedMap();
            setTimeout(function() {
                if (mapInstance) mapInstance.invalidateSize();
            }, 250);
        }
    }

    // 3. SEARCH & TYPEAHEAD
    function initSearch() {
        const searchInput = document.getElementById("magala-search-input");
        const clearBtn = document.getElementById("magala-clear-search");
        let debounceTimer;

        if (searchInput) {
            searchInput.addEventListener("input", function() {
                clearTimeout(debounceTimer);
                const q = this.value.trim();
                if (clearBtn) clearBtn.style.display = q ? "inline-block" : "none";

                debounceTimer = setTimeout(function() {
                    currentPage = 1;
                    loadProducts(q);
                    filterAndRenderMapMarkers();
                }, 250);
            });
        }

        if (clearBtn && searchInput) {
            clearBtn.addEventListener("click", function() {
                searchInput.value = "";
                clearBtn.style.display = "none";
                currentPage = 1;
                loadProducts("");
                filterAndRenderMapMarkers();
            });
        }

        // Near Me Button
        const btnNearMe = document.getElementById("btn-near-me");
        if (btnNearMe) {
            btnNearMe.addEventListener("click", function() {
                if (navigator.geolocation) {
                    btnNearMe.innerText = "Locating...";
                    navigator.geolocation.getCurrentPosition(
                        function(pos) {
                            btnNearMe.innerText = "📍 Near Me";
                            userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                            loadProducts(searchInput ? searchInput.value.trim() : "", pos.coords.latitude, pos.coords.longitude);
                            if (mapInstance) {
                                mapInstance.flyTo([pos.coords.latitude, pos.coords.longitude], 13);
                            }
                            filterAndRenderMapMarkers();
                        },
                        function(err) {
                            btnNearMe.innerText = "📍 Near Me";
                            console.warn("Geolocation denied or error:", err);
                        }
                    );
                }
            });
        }
    }

    // 4. CATEGORY PILLS & FILTERS
    function initFilters() {
        const pills = document.querySelectorAll(".cat-pill");
        pills.forEach(function(pill) {
            pill.addEventListener("click", function() {
                pills.forEach(function(p) { p.classList.remove("active"); });
                this.classList.add("active");
                currentCategory = this.dataset.category || "all";
                currentPage = 1;
                loadProducts();
                filterAndRenderMapMarkers();
            });
        });

        const sortSelect = document.getElementById("filter-sort-by");
        if (sortSelect) {
            sortSelect.addEventListener("change", function() {
                loadProducts();
            });
        }

        const minPriceInput = document.getElementById("filter-min-price");
        const maxPriceInput = document.getElementById("filter-max-price");
        [minPriceInput, maxPriceInput].forEach(function(input) {
            if (input) {
                input.addEventListener("change", function() {
                    currentPage = 1;
                    loadProducts();
                    filterAndRenderMapMarkers();
                });
            }
        });

        document.querySelectorAll("input[name='rating_filter']").forEach(function(radio) {
            radio.addEventListener("change", function() {
                currentPage = 1;
                loadProducts();
                filterAndRenderMapMarkers();
            });
        });

        const expressCheckbox = document.getElementById("filter-bizride-express");
        if (expressCheckbox) {
            expressCheckbox.addEventListener("change", function() {
                currentPage = 1;
                loadProducts();
                filterAndRenderMapMarkers();
            });
        }

        // Reset Filters Button
        const resetBtn = document.getElementById("btn-reset-filters");
        if (resetBtn) {
            resetBtn.addEventListener("click", function(e) {
                e.preventDefault();
                if (minPriceInput) minPriceInput.value = "";
                if (maxPriceInput) maxPriceInput.value = "";
                if (sortSelect) sortSelect.value = "relevance";
                document.querySelectorAll("input[name='rating_filter']").forEach(function(r) {
                    r.checked = (r.value === "");
                });
                if (expressCheckbox) expressCheckbox.checked = true;
                const searchInput = document.getElementById("magala-search-input");
                if (searchInput) searchInput.value = "";
                pills.forEach(function(p) { p.classList.remove("active"); });
                const allPill = document.querySelector(".cat-pill[data-category='all']");
                if (allPill) allPill.classList.add("active");
                currentCategory = "all";
                currentPage = 1;
                loadProducts();
                filterAndRenderMapMarkers();
            });
        }

        // Fit map bounds button
        const btnFitMap = document.getElementById("btn-magala-map-fit");
        if (btnFitMap) {
            btnFitMap.addEventListener("click", function(e) {
                e.preventDefault();
                fitMapToMarkers();
            });
        }
    }

    // 5. EMBEDDED MAP VIEW INITIALIZER (Interactive Leaflet Map with Filtered Nodes)
    function initEmbeddedMap() {
        if (typeof L === "undefined") {
            console.warn("[Magala Shop] Leaflet not loaded yet. Waiting...");
            setTimeout(initEmbeddedMap, 150);
            return;
        }

        const mapEl = document.getElementById("magala-split-map");
        if (!mapEl) return;

        if (!mapInstance) {
            const streetLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "&copy; OpenStreetMap contributors | EthioBiz.ET",
                maxZoom: 19
            });

            const satelliteLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
                attribution: "Tiles &copy; Esri &mdash; EthioBiz.ET",
                maxZoom: 19
            });

            const cleanLightLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
                attribution: "Tiles &copy; Esri &mdash; EthioBiz.ET",
                maxZoom: 19
            });

            mapInstance = L.map("magala-split-map", {
                zoomControl: false,
                layers: [streetLayer]
            }).setView([9.010, 38.761], 12);

            L.control.zoom({ position: "bottomright" }).addTo(mapInstance);

            const baseMaps = {
                "🗺️ Streets": streetLayer,
                "🛰️ Satellite": satelliteLayer,
                "⚪ Clean Light": cleanLightLayer
            };
            L.control.layers(baseMaps, null, { position: "topright" }).addTo(mapInstance);

            // Safe Marker Clustering
            if (typeof L.markerClusterGroup === "function") {
                try {
                    markerCluster = L.markerClusterGroup({
                        showCoverageOnHover: false,
                        spiderfyOnMaxZoom: true,
                        maxClusterRadius: 40
                    });
                } catch(e) {
                    markerCluster = L.featureGroup();
                }
            } else {
                markerCluster = L.featureGroup();
            }
            mapInstance.addLayer(markerCluster);
        }

        if (allMapCompanies.length === 0) {
            const statusEl = document.getElementById("magala-map-status");
            if (statusEl) statusEl.innerText = "🗺️ Discovering verified business locations...";

            fetch("/api/method/bismillah_ethiobiz.magala_shop_api.get_companies_map")
                .then(function(r) { return r.json(); })
                .then(function(res) {
                    if (res.message && res.message.companies) {
                        allMapCompanies = res.message.companies;
                    } else if (res.message && Array.isArray(res.message)) {
                        allMapCompanies = res.message;
                    } else {
                        allMapCompanies = [];
                    }
                    console.log("[Magala Shop Map] Fetched " + allMapCompanies.length + " company locations.");
                    filterAndRenderMapMarkers();
                })
                .catch(function(err) {
                    console.error("[Magala Shop Map] Error fetching locations:", err);
                    if (statusEl) statusEl.innerText = "🗺️ Error loading locations. Retrying...";
                });
        } else {
            filterAndRenderMapMarkers();
        }
    }

    // 6. REACTIVE MAP NODES FILTERING ENGINE
    function filterAndRenderMapMarkers() {
        if (!mapInstance || !markerCluster) return;
        markerCluster.clearLayers();

        const searchInput = document.getElementById("magala-search-input");
        const query = (searchInput ? searchInput.value.trim().toLowerCase() : "");

        const ratingRadio = document.querySelector("input[name='rating_filter']:checked");
        const minRating = ratingRadio && ratingRadio.value ? parseFloat(ratingRadio.value) : 0;

        const filtered = allMapCompanies.filter(function(comp) {
            const nameStr = (comp.company_name || comp.name || comp.company || "").toLowerCase();
            const addrStr = (comp.address || "").toLowerCase();
            const catStr = (comp.category || "").toLowerCase();
            const idStr = (comp.id || "").toLowerCase();

            // 1. Company filter from URL
            if (selectedCompany) {
                const sCompLower = selectedCompany.toLowerCase();
                const matchCompany = nameStr.includes(sCompLower) || idStr.includes(sCompLower) || (comp.company && comp.company.toLowerCase().includes(sCompLower));
                if (!matchCompany) return false;
            }

            // 2. Category pill filter
            if (currentCategory && currentCategory !== "all") {
                const curCatLower = currentCategory.toLowerCase();
                const matchCategory = catStr.includes(curCatLower) || nameStr.includes(curCatLower);
                if (!matchCategory && !selectedCompany) return false;
            }

            // 3. Search query filter
            if (query) {
                const matchQuery = nameStr.includes(query) || addrStr.includes(query) || catStr.includes(query);
                if (!matchQuery) return false;
            }

            // 4. Rating filter
            if (minRating > 0) {
                const r = parseFloat(comp.rating || 5.0);
                if (r < minRating) return false;
            }

            return true;
        });

        const statusEl = document.getElementById("magala-map-status");
        if (statusEl) {
            if (selectedCompany) {
                statusEl.innerHTML = `📍 Showing <strong>${filtered.length}</strong> branch locations for <em>${escapeHtml(selectedCompany)}</em>`;
            } else {
                statusEl.innerHTML = `🗺️ Showing <strong>${filtered.length}</strong> verified business locations`;
            }
        }

        let primaryMarker = null;

        filtered.forEach(function(comp) {
            let lat = parseFloat(comp.lat);
            let lng = parseFloat(comp.lng);
            if (isNaN(lat) || isNaN(lng) || lat === 0) {
                lat = 9.010;
                lng = 38.761;
            }
            comp.lat = lat;
            comp.lng = lng;

            const displayName = comp.company_name || comp.name || comp.company || "Enterprise";
            const branchName = comp.name && comp.name !== comp.company_name ? comp.name : (comp.branch_type || "");
            const isPrimary = Boolean(comp.is_primary);
            const branchBadge = isPrimary 
                ? '<span style="background:#fef08a; color:#854d0e; font-weight:700; padding:2px 7px; border-radius:10px; font-size:0.72rem;">⭐ Head Office</span>'
                : (branchName ? '<span style="background:#e0f2fe; color:#0369a1; font-weight:700; padding:2px 7px; border-radius:10px; font-size:0.72rem;">🏢 ' + branchName + '</span>' : '');

            const pinColor = isPrimary ? "#0d9488" : "#0284c7";

            // Rich Custom Pin Icon
            const customIcon = L.divIcon({
                className: "magala-custom-pin",
                html: `
                    <div style="position:relative; width:34px; height:34px;">
                        <div style="position:absolute; width:34px; height:34px; background:${pinColor}; border-radius:50% 50% 50% 0; transform:rotate(-45deg); border:2px solid #ffffff; box-shadow:0 3px 10px rgba(0,0,0,0.35); display:flex; align-items:center; justify-content:center;">
                            <span style="transform:rotate(45deg); font-size:14px;">${isPrimary ? '⭐' : '📍'}</span>
                        </div>
                    </div>
                `,
                iconSize: [34, 34],
                iconAnchor: [17, 34],
                popupAnchor: [0, -32]
            });

            const directionsUrl = "https://www.google.com/maps/dir/?api=1&destination=" + comp.lat + "," + comp.lng;
            const shopUrl = "/shop?company=" + encodeURIComponent(comp.company || comp.id || comp.name);

            const popupContent = `
                <div style="min-width:240px; max-width:280px; font-family:'Inter',sans-serif; padding:4px;">
                    <div style="width:100%; height:100px; overflow:hidden; border-radius:8px; margin-bottom:8px; background:#f1f5f9;">
                        <img src="${comp.banner || comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${displayName}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                        <img src="${comp.logo || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${displayName}" style="width:36px; height:36px; border-radius:6px; object-fit:cover; border:1px solid #e2e8f0;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                        <div>
                            <strong style="font-size:0.95rem; color:#0f172a; display:block; line-height:1.2;">${displayName}</strong>
                            <div style="margin-top:2px;">
                                <span style="font-size:0.75rem; color:#0d9488; font-weight:700;">${(comp.category || 'Business').toUpperCase()} • ⭐ ${comp.rating || '5.0'}</span>
                                ${branchBadge}
                            </div>
                        </div>
                    </div>
                    <p style="margin:4px 0 8px 0; font-size:0.8rem; color:#64748b; line-height:1.35;">📍 ${comp.address || 'Ethiopia'}</p>
                    <div style="display:flex; gap:6px; margin-top:8px;">
                        <a href="${shopUrl}" style="flex:1; text-align:center; background:#0d9488; color:#ffffff !important; padding:6px 10px; border-radius:6px; font-size:0.78rem; font-weight:700; text-decoration:none;">Store ➔</a>
                        <a href="${directionsUrl}" target="_blank" rel="noopener" style="flex:1; text-align:center; background:#0284c7; color:#ffffff !important; padding:6px 10px; border-radius:6px; font-size:0.78rem; font-weight:700; text-decoration:none;">🧭 Directions</a>
                    </div>
                </div>
            `;

            const marker = L.marker([comp.lat, comp.lng], { icon: customIcon }).bindPopup(popupContent, { maxWidth: 300 });
            markerCluster.addLayer(marker);

            if (isPrimary || !primaryMarker) {
                primaryMarker = marker;
            }
        });

        // Smart Zoom & Bounds fitting
        if (filtered.length > 0) {
            if (selectedCompany && primaryMarker) {
                mapInstance.setView(primaryMarker.getLatLng(), 15);
                setTimeout(function() { primaryMarker.openPopup(); }, 350);
            } else {
                fitMapToMarkers();
            }
        } else {
            mapInstance.setView([9.010, 38.761], 12);
        }
    }

    function fitMapToMarkers() {
        if (!mapInstance || !markerCluster) return;
        try {
            const layers = markerCluster.getLayers ? markerCluster.getLayers() : [];
            if (layers.length > 0 && typeof markerCluster.getBounds === "function") {
                const bounds = markerCluster.getBounds();
                if (bounds.isValid && bounds.isValid()) {
                    mapInstance.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
                }
            } else {
                mapInstance.setView([9.010, 38.761], 12);
            }
        } catch(e) {
            mapInstance.setView([9.010, 38.761], 12);
        }
    }

    // 7. PRODUCT DATA LOADER
    function loadProducts(query, lat, lng) {
        if (query === undefined) query = "";
        const countText = document.getElementById("results-count-text");
        if (countText) countText.innerText = "Loading products...";

        const searchInput = document.getElementById("magala-search-input");
        const minPriceInput = document.getElementById("filter-min-price");
        const maxPriceInput = document.getElementById("filter-max-price");
        const sortSelect = document.getElementById("filter-sort-by");
        const ratingRadio = document.querySelector("input[name='rating_filter']:checked");

        const params = new URLSearchParams({
            query: query || (searchInput ? searchInput.value.trim() : ""),
            category: currentCategory === "all" ? "" : currentCategory,
            company: selectedCompany || "",
            min_price: (minPriceInput ? minPriceInput.value : "") || "",
            max_price: (maxPriceInput ? maxPriceInput.value : "") || "",
            min_rating: (ratingRadio && ratingRadio.value ? ratingRadio.value : ""),
            sort_by: (sortSelect ? sortSelect.value : "relevance"),
            page: currentPage,
            limit: 20
        });

        if (lat && lng) {
            params.append("user_lat", lat);
            params.append("user_lng", lng);
        }

        fetch("/api/method/bismillah_ethiobiz.magala_shop_api.search_products?" + params.toString())
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.message && data.message.status === "success") {
                    const items = data.message.items || [];
                    window.__lastFetchedItems = items;
                    renderItems(items);

                    if (countText) {
                        if (items.length > 0) {
                            countText.innerText = "Showing " + items.length + " of " + data.message.total + " products";
                        } else if (selectedCompany) {
                            countText.innerHTML = "No products currently listed for <strong>" + escapeHtml(selectedCompany) + "</strong>. <a href='/shop' style='color:#0d9488; font-weight:700; text-decoration:underline;'>Browse All Marketplace Products</a>";
                        } else {
                            countText.innerText = "No matching products found";
                        }
                    }
                    renderPagination(data.message.total || 0, data.message.total_pages || 1);
                } else {
                    if (countText) countText.innerText = "No products found in this selection";
                    renderItems([]);
                }
            })
            .catch(function(err) {
                console.error("[Magala Shop] Error loading products:", err);
                if (countText) {
                    if (selectedCompany) {
                        countText.innerHTML = "Storefront for <strong>" + escapeHtml(selectedCompany) + "</strong>. <a href='/shop' style='color:#0d9488; font-weight:700;'>View All Marketplace Items</a>";
                    } else {
                        countText.innerText = "Explore Magala Marketplace Products";
                    }
                }
            });
    }

    function renderItems(items) {
        const container = document.getElementById("magala-items-container");
        if (!container) return;
        container.innerHTML = "";

        if (!items || !items.length) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; padding:40px 20px; text-align:center; color:#64748b;">
                    <div style="font-size:2.5rem; margin-bottom:12px;">🛍️</div>
                    <h3 style="color:#0f172a; margin-bottom:8px; font-weight:700;">No matching products found</h3>
                    <p style="margin:0 0 16px 0; font-size:0.92rem;">Try choosing "All Categories", clearing search terms, or exploring other verified stores.</p>
                    <a href="/shop" style="display:inline-block; background:#0d9488; color:#ffffff !important; padding:8px 18px; border-radius:8px; font-weight:700; text-decoration:none;">View All Products</a>
                </div>
            `;
            return;
        }

        items.forEach(function(it) {
            const detailUrl = "/product/" + encodeURIComponent(it.item_code);
            const fallbackImg = "/assets/bismillah_ethiobiz/img/walta_real_logo.png";

            if (currentView === "list") {
                const row = document.createElement("div");
                row.className = "product-list-row";
                row.style.cursor = "pointer";
                row.innerHTML = `
                    <div style="width:100%; height:160px; overflow:hidden; border-radius:10px; background:#f8fafc;">
                        <img src="${it.image || fallbackImg}" alt="${it.item_name}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='${fallbackImg}'" />
                    </div>
                    <div>
                        <div class="product-seller-badge">${it.company_name || it.company} • ${it.seller_address || 'Ethiopia'}</div>
                        <h4 class="product-title">${it.item_name}</h4>
                        <div class="product-rating">⭐ ${it.rating || '5.0'} (${it.total_reviews || 0} reviews)</div>
                        <p class="text-muted" style="font-size:0.9rem;">${(it.description || '').replace(/<[^>]*>?/gm, '').substring(0, 120)}...</p>
                    </div>
                    <div class="d-flex flex-column justify-content-between align-items-end">
                        <span class="price-tag">${it.formatted_price || it.price}</span>
                        <button class="btn-add-cart" data-cart-item="${it.item_code}">Add to Cart 🛒</button>
                    </div>
                `;
                row.addEventListener("click", function(e) {
                    if (e.target.closest(".btn-add-cart")) {
                        e.stopPropagation();
                        addToCart(it.item_code);
                    } else {
                        window.location.href = detailUrl;
                    }
                });
                container.appendChild(row);
            } else {
                const card = document.createElement("div");
                card.className = "product-card";
                card.style.cursor = "pointer";
                card.innerHTML = `
                    <div class="product-img-wrapper">
                        <img src="${it.image || fallbackImg}" alt="${it.item_name}" loading="lazy" onerror="this.src='${fallbackImg}'" />
                    </div>
                    <div class="product-info-box">
                        <span class="product-seller-badge">${it.company_name || it.company}</span>
                        <h4 class="product-title">${it.item_name}</h4>
                        <div class="product-rating">⭐ ${it.rating || '5.0'} (${it.total_reviews || 0})</div>
                        <div class="product-price-row">
                            <span class="price-tag">${it.formatted_price || it.price}</span>
                            <button class="btn-add-cart" data-cart-item="${it.item_code}">Add</button>
                        </div>
                    </div>
                `;
                card.addEventListener("click", function(e) {
                    if (e.target.closest(".btn-add-cart")) {
                        e.stopPropagation();
                        addToCart(it.item_code);
                    } else {
                        window.location.href = detailUrl;
                    }
                });
                container.appendChild(card);
            }
        });
        applyViewLayout();
    }

    function renderPagination(total, totalPages) {
        const pag = document.getElementById("magala-pagination");
        if (!pag) return;
        pag.innerHTML = "";
        if (totalPages <= 1) return;

        const prevBtn = document.createElement("button");
        prevBtn.className = "btn-prev";
        prevBtn.innerHTML = "← Prev";
        prevBtn.disabled = (currentPage === 1);
        prevBtn.addEventListener("click", function() {
            if (currentPage > 1) {
                currentPage--;
                loadProducts();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
        pag.appendChild(prevBtn);

        const pageIndicator = document.createElement("span");
        pageIndicator.style.fontWeight = "700";
        pageIndicator.style.color = "#0f172a";
        pageIndicator.innerText = `Page ${currentPage} of ${totalPages}`;
        pag.appendChild(pageIndicator);

        const nextBtn = document.createElement("button");
        nextBtn.className = "btn-next";
        nextBtn.innerHTML = "Next →";
        nextBtn.disabled = (currentPage >= totalPages);
        nextBtn.addEventListener("click", function() {
            if (currentPage < totalPages) {
                currentPage++;
                loadProducts();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
        pag.appendChild(nextBtn);
    }

    // 8. SHOPPING CART HANDLERS
    window.addToCart = function(itemCode) {
        let cart = JSON.parse(localStorage.getItem("magala_cart") || "[]");
        cart.push(itemCode);
        localStorage.setItem("magala_cart", JSON.stringify(cart));
        updateCartCount();
        const drawer = document.getElementById("magala-cart-drawer");
        if (drawer) drawer.classList.add("open");
    };

    function initCart() {
        updateCartCount();
        const closeBtn = document.getElementById("close-cart-drawer");
        if (closeBtn) {
            closeBtn.addEventListener("click", function() {
                const drawer = document.getElementById("magala-cart-drawer");
                if (drawer) drawer.classList.remove("open");
            });
        }
    }

    function updateCartCount() {
        let cart = JSON.parse(localStorage.getItem("magala_cart") || "[]");
        const countBadge = document.getElementById("cart-drawer-count");
        if (countBadge) countBadge.innerText = cart.length;
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }
});
