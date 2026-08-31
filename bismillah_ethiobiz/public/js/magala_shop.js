// BISMALLAH ETHIOBIZ MAGALA SHOP ENGINE JAVASCRIPT
// Handles 3-way view switcher (Grid, List, Map), search autocomplete, dynamic filtering & cart

document.addEventListener("DOMContentLoaded", function() {
    let currentView = localStorage.getItem("magala_view_mode") || "grid";
    let currentCategory = "all";
    let currentPage = 1;
    let mapInstance = null;
    let markerCluster = null;

    initViewSwitcher();
    initSearch();
    initFilters();
    initCart();
    loadProducts();

    // VIEW SWITCHER
    function initViewSwitcher() {
        const viewBtns = document.querySelectorAll(".view-btn");
        viewBtns.forEach(btn => {
            if (btn.dataset.view === currentView) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }

            btn.addEventListener("click", function() {
                viewBtns.forEach(b => b.classList.remove("active"));
                this.classList.add("active");
                currentView = this.dataset.view;
                localStorage.setItem("magala_view_mode", currentView);
                applyViewLayout();
            });
        });
    }

    function applyViewLayout() {
        const container = document.getElementById("magala-items-container");
        const mapContainer = document.getElementById("magala-embedded-map-container");

        if (currentView === "grid") {
            container.style.display = "grid";
            container.className = "magala-grid-view";
            mapContainer.style.display = "none";
        } else if (currentView === "list") {
            container.style.display = "flex";
            container.className = "magala-list-view";
            mapContainer.style.display = "none";
        } else if (currentView === "map") {
            container.style.display = "none";
            mapContainer.style.display = "block";
            initEmbeddedMap();
        }
    }

    // SEARCH & TYPEAHEAD
    function initSearch() {
        const searchInput = document.getElementById("magala-search-input");
        let debounceTimer;

        searchInput.addEventListener("input", function() {
            clearTimeout(debounceTimer);
            const q = this.value.trim();
            debounceTimer = setTimeout(() => {
                currentPage = 1;
                loadProducts(q);
            }, 300);
        });

        // Near Me Button
        document.getElementById("btn-near-me").addEventListener("click", function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    loadProducts(searchInput.value.trim(), pos.coords.latitude, pos.coords.longitude);
                });
            }
        });
    }

    // CATEGORY PILLS & FILTERS
    function initFilters() {
        const pills = document.querySelectorAll(".cat-pill");
        pills.forEach(pill => {
            pill.addEventListener("click", function() {
                pills.forEach(p => p.classList.remove("active"));
                this.classList.add("active");
                currentCategory = this.dataset.category;
                currentPage = 1;
                loadProducts();
            });
        });

        document.getElementById("filter-sort-by").addEventListener("change", () => loadProducts());
    }

    // DATA LOADER
    function loadProducts(query="", lat=null, lng=null) {
        const countText = document.getElementById("results-count-text");
        const container = document.getElementById("magala-items-container");
        countText.innerText = "Loading products...";

        const params = new URLSearchParams({
            query: query || document.getElementById("magala-search-input").value.trim(),
            category: currentCategory === "all" ? "" : currentCategory,
            min_price: document.getElementById("filter-min-price").value || "",
            max_price: document.getElementById("filter-max-price").value || "",
            sort_by: document.getElementById("filter-sort-by").value,
            page: currentPage,
            limit: 20
        });

        fetch(`/api/method/bismillah_ethiobiz.magala_shop_api.search_products?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.status === "success") {
                    renderItems(data.message.items);
                    countText.innerText = `Showing ${data.message.items.length} of ${data.message.total} products`;
                }
            })
            .catch(err => {
                countText.innerText = "Failed to load products";
            });
    }

    function renderItems(items) {
        const container = document.getElementById("magala-items-container");
        container.innerHTML = "";

        if (!items.length) {
            container.innerHTML = '<p class="text-center p-4">No matching products found.</p>';
            return;
        }

        items.forEach(it => {
            if (currentView === "list") {
                container.innerHTML += `
                    <div class="product-list-row">
                        <img src="${it.image}" alt="${it.item_name}" style="width:100%; height:160px; object-fit:cover; border-radius:10px;" />
                        <div>
                            <div class="product-seller-badge">${it.company_name || it.company} • ${it.seller_address || 'Addis Ababa'}</div>
                            <h4 class="product-title">${it.item_name}</h4>
                            <div class="product-rating">⭐ ${it.rating} (${it.total_reviews} reviews)</div>
                            <p class="text-muted" style="font-size:0.9rem;">${(it.description || '').replace(/<[^>]*>?/gm, '').substring(0, 120)}...</p>
                        </div>
                        <div class="d-flex flex-column justify-content-between align-items-end">
                            <span class="price-tag">${it.formatted_price}</span>
                            <button class="btn-add-cart" onclick="addToCart('${it.item_code}')">Add to Cart 🛒</button>
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML += `
                    <div class="product-card">
                        <div class="product-img-wrapper">
                            <img src="${it.image}" alt="${it.item_name}" loading="lazy" />
                        </div>
                        <div class="product-info-box">
                            <span class="product-seller-badge">${it.company_name || it.company}</span>
                            <h4 class="product-title">${it.item_name}</h4>
                            <div class="product-rating">⭐ ${it.rating} (${it.total_reviews})</div>
                            <div class="product-price-row">
                                <span class="price-tag">${it.formatted_price}</span>
                                <button class="btn-add-cart" onclick="addToCart('${it.item_code}')">Add</button>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        applyViewLayout();
    }

    // EMBEDDED MAP VIEW INITIALIZER
    function initEmbeddedMap() {
        if (!mapInstance) {
            mapInstance = L.map("magala-split-map").setView([9.010, 38.761], 12);
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "© OpenStreetMap contributors"
            }).addTo(mapInstance);
            markerCluster = L.markerClusterGroup();
            mapInstance.addLayer(markerCluster);
        }

        fetch("/api/method/bismillah_ethiobiz.magala_shop_api.get_companies_map")
            .then(r => r.json())
            .then(res => {
                if (res.message && res.message.companies) {
                    markerCluster.clearLayers();
                    res.message.companies.forEach(c => {
                        const marker = L.marker([c.lat, c.lng]).bindPopup(`
                            <div style="min-width:180px;">
                                <strong>${c.name}</strong><br>
                                <span class="text-muted">${c.category} • ⭐ ${c.rating}</span><br>
                                <p style="margin:4px 0; font-size:0.85rem;">${c.address}</p>
                                <a href="/shop?company=${encodeURIComponent(c.id)}" style="color:#1FB6AE; font-weight:600;">View Storefront →</a>
                            </div>
                        `);
                        markerCluster.addLayer(marker);
                    });
                }
            });
    }

    // CART DRAWER HANDLER
    window.addToCart = function(itemCode) {
        let cart = JSON.parse(localStorage.getItem("magala_cart") || "[]");
        cart.push(itemCode);
        localStorage.setItem("magala_cart", JSON.stringify(cart));
        updateCartCount();
        document.getElementById("magala-cart-drawer").classList.add("open");
    };

    function initCart() {
        updateCartCount();
        document.getElementById("close-cart-drawer").addEventListener("click", () => {
            document.getElementById("magala-cart-drawer").classList.remove("open");
        });
    }

    function updateCartCount() {
        let cart = JSON.parse(localStorage.getItem("magala_cart") || "[]");
        document.getElementById("cart-drawer-count").innerText = cart.length;
    }
});
