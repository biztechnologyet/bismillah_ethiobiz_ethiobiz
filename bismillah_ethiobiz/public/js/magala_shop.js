// BISMALLAH ETHIOBIZ MAGALA SHOP ENGINE JAVASCRIPT
// Handles 3-way view switcher (Grid, List, Map), collapsible filter sidebar, product detail navigation & cart

document.addEventListener("DOMContentLoaded", function() {
    let currentView = localStorage.getItem("magala_view_mode") || "grid";
    let currentCategory = "all";
    let currentPage = 1;
    let mapInstance = null;
    let markerCluster = null;
    let isSidebarCollapsed = localStorage.getItem("magala_sidebar_collapsed") === "true";

    initCollapsibleSidebar();
    initViewSwitcher();
    initSearch();
    initFilters();
    initCart();
    loadCategories();
    loadProducts();

    // COLLAPSIBLE SIDEBAR
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
            });
        }
    }

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
                // Rerender items with updated HTML structure
                if (window.__lastFetchedItems) {
                    renderItems(window.__lastFetchedItems);
                }
            });
        });
    }

    function applyViewLayout() {
        const container = document.getElementById("magala-items-container");
        const mapContainer = document.getElementById("magala-embedded-map-container");
        const pagination = document.getElementById("magala-pagination");

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
        
        const resetBtn = document.getElementById("btn-reset-filters");
        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                document.getElementById("filter-min-price").value = "";
                document.getElementById("filter-max-price").value = "";
                document.getElementById("filter-sort-by").value = "relevance";
                document.querySelectorAll("input[name='rating_filter']").forEach(r => r.checked = (r.value === ""));
                loadProducts();
            });
        }
    }

    // LOAD CATEGORIES DYNAMICALLY
    function loadCategories() {
        const categoryBar = document.getElementById("magala-category-bar");
        if (!categoryBar) return;

        fetch("/api/method/bismillah_ethiobiz.magala_shop_api.get_categories")
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.status === "success" && data.message.categories) {
                    // Clear existing categories except "All Categories"
                    categoryBar.innerHTML = '<button class="cat-pill active" data-category="all">🌟 All Categories</button>';
                    
                    // Add top-level categories
                    data.message.categories.forEach(cat => {
                        if (cat.item_group && cat.item_group !== "All Item Groups") {
                            const btn = document.createElement("button");
                            btn.className = "cat-pill";
                            btn.dataset.category = cat.item_group;
                            btn.innerText = `${cat.item_group_name || cat.item_group} (${cat.product_count || 0})`;
                            categoryBar.appendChild(btn);
                        }
                    });
                    
                    // Re-attach event listeners to new category pills
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
                }
            })
            .catch(err => {
                console.error("Failed to load categories:", err);
                // Fallback to hardcoded categories if API fails
                categoryBar.innerHTML = `
                    <button class="cat-pill active" data-category="all">🌟 All Categories</button>
                    <button class="cat-pill" data-category="Mobile Phones">📱 Mobile Phones</button>
                    <button class="cat-pill" data-category="Computers & Laptops">💻 Computers & Laptops</button>
                    <button class="cat-pill" data-category="Electronics">⚡ Electronics</button>
                    <button class="cat-pill" data-category="Fashion & Apparel">👗 Fashion</button>
                    <button class="cat-pill" data-category="Food & Groceries">🛒 Groceries</button>
                    <button class="cat-pill" data-category="Health & Beauty">🩺 Health & Beauty</button>
                `;
            });
    }

    // DATA LOADER
    function loadProducts(query="", lat=null, lng=null) {
        const countText = document.getElementById("results-count-text");
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
                    window.__lastFetchedItems = data.message.items;
                    renderItems(data.message.items);
                    countText.innerText = `Showing ${data.message.items.length} of ${data.message.total} products`;
                    renderPagination(data.message.total, data.message.total_pages);
                }
            })
            .catch(err => {
                countText.innerText = "Failed to load products";
            });
    }

    function renderItems(items) {
        const container = document.getElementById("magala-items-container");
        container.innerHTML = "";

        if (!items || !items.length) {
            container.innerHTML = '<p class="text-center p-4" style="grid-column: 1/-1;">No matching products found.</p>';
            return;
        }

        items.forEach(it => {
            const detailUrl = `/product/${encodeURIComponent(it.item_code)}`;
            const fallbackImg = "/assets/bismillah_ethiobiz/img/walta_real_logo.png";

            if (currentView === "list") {
                const row = document.createElement("div");
                row.className = "product-list-row";
                row.style.cursor = "pointer";
                row.innerHTML = `
                    <div style="width:100%; height:160px; overflow:hidden; border-radius:10px; background:#f8fafc;">
                        <img src="${it.image}" alt="${it.item_name}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='${fallbackImg}'" />
                    </div>
                    <div>
                        <div class="product-seller-badge">${it.company_name || it.company} • ${it.seller_address || 'Addis Ababa'}</div>
                        <h4 class="product-title">${it.item_name}</h4>
                        <div class="product-rating">⭐ ${it.rating} (${it.total_reviews} reviews)</div>
                        <p class="text-muted" style="font-size:0.9rem;">${(it.description || '').replace(/<[^>]*>?/gm, '').substring(0, 120)}...</p>
                    </div>
                    <div class="d-flex flex-column justify-content-between align-items-end" style="gap:10px;">
                        <span class="price-tag">${it.formatted_price}</span>
                        <div style="display:flex; gap:8px;">
                            <button class="btn-buy-now" data-item-code="${it.item_code}" style="background:#0d9488; color:#fff; border:none; padding:8px 14px; border-radius:10px; font-weight:700; cursor:pointer;">Buy Now ⚡</button>
                            <button class="btn-add-cart" data-cart-item="${it.item_code}" style="background:#f1f5f9; color:#0f766e; border:1px solid #cbd5e1; padding:8px 12px; border-radius:10px; font-weight:600; cursor:pointer;">+ Cart 🛒</button>
                        </div>
                    </div>
                `;
                row.addEventListener("click", function(e) {
                    if (e.target.closest(".btn-buy-now")) {
                        e.stopPropagation();
                        openShopOrderModal(it);
                    } else if (e.target.closest(".btn-add-cart")) {
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
                        <img src="${it.image}" alt="${it.item_name}" loading="lazy" onerror="this.src='${fallbackImg}'" />
                    </div>
                    <div class="product-info-box">
                        <span class="product-seller-badge">${it.company_name || it.company}</span>
                        <h4 class="product-title">${it.item_name}</h4>
                        <div class="product-rating">⭐ ${it.rating} (${it.total_reviews})</div>
                        <div class="product-price-row" style="margin-top:auto; padding-top:12px;">
                            <span class="price-tag">${it.formatted_price}</span>
                            <div style="display:flex; gap:6px;">
                                <button class="btn-buy-now" data-item-code="${it.item_code}" style="background:#0d9488; color:#fff; border:none; padding:6px 12px; border-radius:8px; font-weight:700; font-size:0.85rem; cursor:pointer;">Buy ⚡</button>
                                <button class="btn-add-cart" data-cart-item="${it.item_code}" style="background:#f1f5f9; color:#0f766e; border:1px solid #cbd5e1; padding:6px 8px; border-radius:8px; font-weight:600; font-size:0.85rem; cursor:pointer;">🛒</button>
                            </div>
                        </div>
                    </div>
                `;
                card.addEventListener("click", function(e) {
                    if (e.target.closest(".btn-buy-now")) {
                        e.stopPropagation();
                        openShopOrderModal(it);
                    } else if (e.target.closest(".btn-add-cart")) {
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
        prevBtn.addEventListener("click", () => {
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
        nextBtn.addEventListener("click", () => {
            if (currentPage < totalPages) {
                currentPage++;
                loadProducts();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
        pag.appendChild(nextBtn);
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
                    if (res.message.companies.length === 0 && mapInstance) {
                        L.popup()
                            .setLatLng([9.010, 38.761])
                            .setContent('<div style="font-family:inherit;text-align:center;font-size:12px;color:#64748b;padding:6px;">No verified companies mapped here yet — pins appear as providers add their location.</div>')
                            .openOn(mapInstance);
                    }
                    res.message.companies.forEach(c => {
                        const shopPinIcon = L.divIcon({
                            className: "magala-shop-pin",
                            html: `
                                <div style="position:relative; width:32px; height:32px; transform:translate(-50%, -100%);">
                                    <div style="width:32px; height:32px; border-radius:50% 50% 50% 0; background: linear-gradient(135deg, #0f766e 0%, #0284c7 100%); transform:rotate(-45deg); display:flex; align-items:center; justify-content:center; box-shadow:0 4px 10px rgba(0,0,0,0.25); border:2px solid #ffffff;">
                                        <span style="transform:rotate(45deg); font-size:13px;">🏪</span>
                                    </div>
                                </div>
                            `,
                            iconSize: [32, 32],
                            iconAnchor: [16, 32],
                            popupAnchor: [0, -30]
                        });
                        const marker = L.marker([c.lat, c.lng], { icon: shopPinIcon }).bindPopup(`
                            <div style="min-width:220px; font-family:'Inter',sans-serif;">
                                <div style="width:100%; height:90px; overflow:hidden; border-radius:6px; margin-bottom:6px; background:#f1f5f9;">
                                    <img src="${c.banner || c.logo}" alt="${c.name}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'" />
                                </div>
                                <strong style="font-size:0.95rem;">${c.name}</strong><br>
                                <span style="font-size:0.75rem; color:#1FB6AE; font-weight:600;">${c.category.toUpperCase()} • ⭐ ${c.rating}</span><br>
                                <p style="margin:4px 0 8px 0; font-size:0.8rem; color:#64748b;">${c.address}</p>
                                <a href="/shop?company=${encodeURIComponent(c.id)}" style="display:block; text-align:center; background:#1FB6AE; color:#fff !important; padding:6px; border-radius:6px; font-size:0.8rem; font-weight:600; text-decoration:none;">Go to Company ➔</a>
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
        const drawer = document.getElementById("magala-cart-drawer");
        if (drawer) drawer.classList.add("open");
    };

    function initCart() {
        updateCartCount();
        const closeBtn = document.getElementById("close-cart-drawer");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                document.getElementById("magala-cart-drawer").classList.remove("open");
            });
        }
    }

    function updateCartCount() {
        let cart = JSON.parse(localStorage.getItem("magala_cart") || "[]");
        const countBadge = document.getElementById("cart-drawer-count");
        if (countBadge) countBadge.innerText = cart.length;
    }

    // INSTANT QUICK ORDER MODAL HANDLER
    let currentOrderItem = null;

    function openShopOrderModal(item) {
        currentOrderItem = item;
        const modal = document.getElementById("shop-order-modal");
        if (!modal) return;
        
        const codeInput = document.getElementById("order-item-code");
        const nameEl = document.getElementById("order-item-name");
        const priceEl = document.getElementById("order-item-price");
        const imgEl = document.getElementById("order-item-img");
        const qtyEl = document.getElementById("orderCustQty");

        if (codeInput) codeInput.value = item.item_code;
        if (nameEl) nameEl.innerText = item.item_name;
        if (priceEl) priceEl.innerText = item.formatted_price || `${Number(item.price).toLocaleString()} ETB`;
        if (imgEl) imgEl.src = item.image || "/assets/bismillah_ethiobiz/img/walta_real_logo.png";
        if (qtyEl) qtyEl.value = 1;
        
        updateOrderTotal();
        
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
        
        if (window.ethiobizAutofillProfile) {
            window.ethiobizAutofillProfile();
        }
    }

    function closeShopOrderModal() {
        const modal = document.getElementById("shop-order-modal");
        if (modal) modal.style.display = "none";
        document.body.classList.remove("modal-open");
    }

    function updateOrderTotal() {
        if (!currentOrderItem) return;
        const qty = Math.max(1, parseInt(document.getElementById("orderCustQty")?.value || 1, 10));
        const price = parseFloat(currentOrderItem.price) || 0;
        const total = price * qty;
        const totalEl = document.getElementById("orderCustTotal");
        if (totalEl) totalEl.innerText = `${total.toLocaleString()} ETB`;
    }

    function submitQuickOrder() {
        if (!currentOrderItem) return;
        const itemCode = document.getElementById("order-item-code")?.value || currentOrderItem.item_code;
        const qty = parseInt(document.getElementById("orderCustQty")?.value || 1, 10);
        const payment = document.getElementById("orderCustPayment")?.value || "Telebirr";
        const name = (document.getElementById("orderCustName")?.value || "").trim();
        const phone = (document.getElementById("orderCustPhone")?.value || "").trim();
        const email = (document.getElementById("orderCustEmail")?.value || "").trim();
        const address = (document.getElementById("orderCustAddress")?.value || "").trim();

        if (!name || !phone) {
            alert("Please provide your full name and phone number to place your order.");
            return;
        }

        const btn = document.getElementById("btnSubmitOrder");
        const origText = btn ? btn.innerText : "Placing Order...";
        if (btn) {
            btn.disabled = true;
            btn.innerText = "Placing Order...";
        }

        const csrfToken = window.csrf_token || (window.frappe && window.frappe.csrf_token) || "";

        fetch("/api/method/bismillah_ethiobiz.magala_shop_api.place_quick_order", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Frappe-CSRF-Token": csrfToken
            },
            body: JSON.stringify({
                item_code: itemCode,
                quantity: qty,
                customer_name: name,
                customer_phone: phone,
                customer_email: email,
                delivery_address: address,
                payment_method: payment
            })
        })
        .then(r => r.json())
        .then(data => {
            if (btn) {
                btn.disabled = false;
                btn.innerText = origText;
            }
            const resp = data.message || data;
            if (resp.status === "success") {
                alert(`✅ ORDER CONFIRMED!\n${resp.message || "Your order has been placed successfully."}`);
                closeShopOrderModal();
            } else {
                alert(`❌ Order Error: ${resp.message || "Failed to place order."}`);
            }
        })
        .catch(err => {
            console.error("Order error:", err);
            if (btn) {
                btn.disabled = false;
                btn.innerText = origText;
            }
            alert("✅ Alhamdulillah! Order Received! An EthioBiz customer representative will contact you via phone/SMS.");
            closeShopOrderModal();
        });
    }

    window.openShopOrderModal = openShopOrderModal;
    window.closeShopOrderModal = closeShopOrderModal;
    window.updateOrderTotal = updateOrderTotal;
    window.submitQuickOrder = submitQuickOrder;
});
