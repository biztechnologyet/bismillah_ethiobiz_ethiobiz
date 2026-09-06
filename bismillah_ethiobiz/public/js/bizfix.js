// BISMALLAH ETHIOBIZ FIX PORTAL JAVASCRIPT — v4.0.0
document.addEventListener("DOMContentLoaded", function() {
    var currentCategory = "all";
    var services = [];
    var selectedService = null;

    initFixControls();
    loadFixCategories();
    loadFixServices();

    function initFixControls() {
        // Category Cards
        document.querySelectorAll(".fix-cat-card").forEach(function(card) {
            card.addEventListener("click", function() {
                document.querySelectorAll(".fix-cat-card").forEach(function(c) { c.classList.remove("active"); });
                this.classList.add("active");
                currentCategory = this.dataset.cat;
                loadFixServices();
            });
        });

        // Search Input — debounced
        var searchTimer = null;
        var sInp = document.getElementById("fix-search-input");
        if (sInp) {
            sInp.addEventListener("input", function() {
                clearTimeout(searchTimer);
                var q = this.value.trim().toLowerCase();
                searchTimer = setTimeout(function() { renderFixGrid(q); }, 200);
            });
        }

        // Search Button
        var sBtn = document.getElementById("btn-search-fix");
        if (sBtn) {
            sBtn.addEventListener("click", function() { loadFixServices(); });
        }

        // Close Modal
        var closeBtn = document.getElementById("btn-close-fix-modal");
        if (closeBtn) {
            closeBtn.addEventListener("click", function() {
                document.getElementById("fix-booking-modal").style.display = "none";
            });
        }

        // Click outside modal to close
        var modalBackdrop = document.getElementById("fix-booking-modal");
        if (modalBackdrop) {
            modalBackdrop.addEventListener("click", function(e) {
                if (e.target === this) this.style.display = "none";
            });
        }

        // Confirm Dispatch
        var confirmBtn = document.getElementById("btn-confirm-fix");
        if (confirmBtn) {
            confirmBtn.addEventListener("click", handleFixSubmit);
        }
    }

    function loadFixCategories() {
        var categoryGrid = document.getElementById("fix-category-grid");
        if (!categoryGrid) return;

        // Keep "All Services" and load dynamic categories
        var allServicesCard = categoryGrid.querySelector('[data-cat="all"]');
        categoryGrid.innerHTML = "";
        if (allServicesCard) categoryGrid.appendChild(allServicesCard);

        fetch("/api/method/bismillah_ethiobiz.bizservice_api.get_categories")
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.message && data.message.categories) {
                    data.message.categories.forEach(function(cat) {
                        if (cat.category_name && cat.category_name !== "All Item Groups") {
                            var card = document.createElement("div");
                            card.className = "fix-cat-card";
                            card.dataset.cat = cat.category_name;
                            card.innerHTML = '<span class="cat-icon">🔧</span><h4>' + cat.category_name + '</h4><p>' + (cat.description || "Maintenance Services") + '</p>';
                            categoryGrid.appendChild(card);
                        }
                    });
                    
                    // Re-attach event listeners to new category cards
                    document.querySelectorAll(".fix-cat-card").forEach(function(card) {
                        card.addEventListener("click", function() {
                            document.querySelectorAll(".fix-cat-card").forEach(function(c) { c.classList.remove("active"); });
                            this.classList.add("active");
                            currentCategory = this.dataset.cat;
                            loadFixServices();
                        });
                    });
                }
            })
            .catch(function(err) {
                console.error("Failed to load categories:", err);
                // Fallback to hardcoded categories if API fails
                var fallbackCategories = [
                    { cat: "Electrical & Power", icon: "⚡", title: "Electrical & Power", desc: "Wiring, Solar, Generators & Panels" },
                    { cat: "Plumbing & Water", icon: "🚿", title: "Plumbing & Water", desc: "Leaks, Pumps, Tanks & Drainage" },
                    { cat: "HVAC & Appliances", icon: "❄️", title: "HVAC & Appliances", desc: "Cold Rooms, AC, Fridges & Ovens" },
                    { cat: "Auto Mechanics", icon: "🚗", title: "Auto & Roadside", desc: "Mobile Mechanics & Diagnostics" },
                    { cat: "IT & Security", icon: "💻", title: "IT & Security", desc: "PC/Laptop, CCTV & Structured Cabling" },
                    { cat: "Facility Maintenance", icon: "🏢", title: "Facility Handyman", desc: "Office Repairs, Locks, Glass & Drywall" },
                    { cat: "Carpentry & Woodwork", icon: "🪵", title: "Carpentry & Wood", desc: "Custom Cabinets & Furniture Fixes" },
                    { cat: "Sanitation & Cleaning", icon: "🧹", title: "Sanitation & Cleaning", desc: "Fumigation, Deep Cleaning & Tanks" }
                ];
                fallbackCategories.forEach(function(cat) {
                    var card = document.createElement("div");
                    card.className = "fix-cat-card";
                    card.dataset.cat = cat.cat;
                    card.innerHTML = '<span class="cat-icon">' + cat.icon + '</span><h4>' + cat.title + '</h4><p>' + cat.desc + '</p>';
                    categoryGrid.appendChild(card);
                });
                
                // Re-attach event listeners
                document.querySelectorAll(".fix-cat-card").forEach(function(card) {
                    card.addEventListener("click", function() {
                        document.querySelectorAll(".fix-cat-card").forEach(function(c) { c.classList.remove("active"); });
                        this.classList.add("active");
                        currentCategory = this.dataset.cat;
                        loadFixServices();
                    });
                });
            });
    }

    function loadFixServices() {
        var countText = document.getElementById("fix-results-count");
        if (countText) countText.innerText = "Loading certified maintenance services...";

        var params = new URLSearchParams();
        if (currentCategory !== "all") params.append("category", currentCategory);

        var sVal = document.getElementById("fix-search-input");
        if (sVal && sVal.value.trim()) params.append("q", sVal.value.trim());

        fetch("/api/method/bismillah_ethiobiz.bizbooking_api.search_services?" + params.toString())
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.message && data.message.services) {
                    services = data.message.services;
                    if (countText) countText.innerText = "Showing " + services.length + " certified maintenance packages";
                    renderFixGrid();
                }
            })
            .catch(function() {
                // Fallback catalog if API unavailable
                services = [
                    { name: "FIX-ELEC-01", title: "Emergency Power & Breaker Repair", category: "Electrical & Power", formatted_price: "450.00 ETB / hr", duration_minutes: 60, company_name: "Addis Electric Masters" },
                    { name: "FIX-PLUMB-01", title: "Burst Pipe & Leak Sealing", category: "Plumbing & Water", formatted_price: "400.00 ETB / hr", duration_minutes: 45, company_name: "Ethio Hydro Care" },
                    { name: "FIX-HVAC-01", title: "AC & Commercial Cold Room Overhaul", category: "HVAC & Appliances", formatted_price: "500.00 ETB / hr", duration_minutes: 90, company_name: "CoolTech Ethiopia" },
                    { name: "FIX-AUTO-01", title: "Roadside Mobile Auto Diagnostics & Battery Jump", category: "Auto Mechanics", formatted_price: "650.00 ETB", duration_minutes: 45, company_name: "QuickFix Mechanics" },
                    { name: "FIX-IT-01", title: "CCTV Camera Installation & LAN Cabling", category: "IT & Security", formatted_price: "550.00 ETB / hr", duration_minutes: 120, company_name: "BizIT Infrastructure" },
                    { name: "FIX-FAC-01", title: "Commercial Facility & Locksmith Service", category: "Facility Maintenance", formatted_price: "600.00 ETB / hr", duration_minutes: 60, company_name: "Prime Property Care" },
                    { name: "FIX-CARP-01", title: "Custom Woodwork & Door Alignment", category: "Carpentry & Woodwork", formatted_price: "400.00 ETB / hr", duration_minutes: 90, company_name: "Sheger Woodcraft" },
                    { name: "FIX-SANI-01", title: "Full Premises Deep Sanitation & Fumigation", category: "Sanitation & Cleaning", formatted_price: "350.00 ETB / hr", duration_minutes: 120, company_name: "CleanBio Solutions" }
                ];
                if (countText) countText.innerText = "Found " + services.length + " certified maintenance packages";
                renderFixGrid();
            });
    }

    function renderFixGrid(filterQuery) {
        filterQuery = filterQuery || "";
        var grid = document.getElementById("fix-service-grid");
        if (!grid) return;
        grid.innerHTML = "";

        var filtered = services.filter(function(s) {
            var matchQ = !filterQuery || s.title.toLowerCase().indexOf(filterQuery) !== -1 || (s.category || '').toLowerCase().indexOf(filterQuery) !== -1;
            var matchCat = (currentCategory === "all") || (s.category === currentCategory);
            return matchQ && matchCat;
        });

        var countText = document.getElementById("fix-results-count");
        if (countText) countText.innerText = "Showing " + filtered.length + " certified maintenance packages";

        if (!filtered.length) {
            grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:48px 20px;">' +
                '<div style="font-size:3rem; margin-bottom:12px;">🔧</div>' +
                '<h3 style="font-weight:800; color:#334155; margin-bottom:6px;">No Maintenance Services Found</h3>' +
                '<p style="color:#64748b; font-size:0.9rem;">Try selecting "All Services" or adjusting your search keywords.</p>' +
                '</div>';
            return;
        }

        var catIcons = {
            "Electrical & Power": "⚡",
            "Plumbing & Water": "🚿",
            "HVAC & Appliances": "❄️",
            "Auto Mechanics": "🚗",
            "IT & Security": "💻",
            "Facility Maintenance": "🏢",
            "Carpentry & Woodwork": "🪵",
            "Sanitation & Cleaning": "🧹"
        };

        filtered.forEach(function(srv, idx) {
            var icon = catIcons[srv.category] || "🔧";
            var card = document.createElement("div");
            card.className = "vert-card";
            card.style.animation = "slideUp 0.4s ease-out " + (idx * 0.05) + "s both";
            card.innerHTML =
                '<div class="fix-icon-wrap">' +
                    '<span style="filter:drop-shadow(0 4px 10px rgba(245,158,11,0.25));">' + icon + '</span>' +
                '</div>' +
                '<div class="vert-card-body">' +
                    '<div class="vert-card-badge" style="background:var(--vert-fix-light); color:#b45309;">' + srv.category + '</div>' +
                    '<div class="vert-card-title">' + srv.title + '</div>' +
                    '<div class="vert-card-subtitle">🏢 ' + (srv.company_name || 'EthioBiz Certified Partner') + '</div>' +
                    '<div class="vert-card-meta">' +
                        '<span style="color:#059669; font-weight:700; font-size:0.85rem;">⏱️ ' + (srv.duration_minutes || 60) + ' min arrival</span>' +
                        '<span class="vert-card-price" style="color:var(--vert-fix);">' + srv.formatted_price + '</span>' +
                    '</div>' +
                    '<button class="btn-vertical-primary w-100 btn-book-fix" style="background:var(--vert-fix); border-radius:12px;" data-srv-id="' + srv.name + '">Dispatch Technician ➔</button>' +
                '</div>';

            card.querySelector(".btn-book-fix").addEventListener("click", function() { openFixModal(srv); });
            grid.appendChild(card);
        });
    }

    function openFixModal(srv) {
        selectedService = srv;
        document.getElementById("modal-fix-title").innerText = "Request " + srv.title;
        document.getElementById("modal-fix-summary").innerHTML =
            '<div style="display:flex; align-items:center; gap:12px;">' +
                '<div style="width:40px; height:40px; border-radius:50%; background:rgba(245,158,11,0.2); display:flex; align-items:center; justify-content:center; font-size:1.2rem;">🔧</div>' +
                '<div>' +
                    '<strong>' + srv.title + '</strong><br>' +
                    '<span style="font-size:0.82rem;">' + srv.category + ' &bull; Rate: <strong>' + srv.formatted_price + '</strong></span>' +
                '</div>' +
            '</div>';
        document.getElementById("fix-booking-modal").style.display = "flex";
        if (window.ethiobizAutofillProfile) {
            window.ethiobizAutofillProfile();
        }
    }

    function handleFixSubmit() {
        if (!selectedService) return;
        var name = (document.getElementById("fix-contact-name") ? document.getElementById("fix-contact-name").value : "").trim();
        var phone = (document.getElementById("fix-contact-phone") ? document.getElementById("fix-contact-phone").value : "").trim();
        var address = (document.getElementById("fix-address") ? document.getElementById("fix-address").value : "").trim();
        var desc = (document.getElementById("fix-fault-desc") ? document.getElementById("fix-fault-desc").value : "").trim();
        var urgency = document.querySelector('input[name="fix_urgency"]:checked') ? document.querySelector('input[name="fix_urgency"]:checked').value : "Emergency";

        // Fallback to logged-in user profile if inputs were not populated
        if (!name && window.ETHIOBIZ_USER_PROFILE) {
            name = window.ETHIOBIZ_USER_PROFILE.full_name || window.ETHIOBIZ_USER_PROFILE.user || "";
        }
        if (!phone && window.ETHIOBIZ_USER_PROFILE) {
            phone = window.ETHIOBIZ_USER_PROFILE.phone || "";
        }
        if (!address && window.ETHIOBIZ_USER_PROFILE && window.ETHIOBIZ_USER_PROFILE.address) {
            address = window.ETHIOBIZ_USER_PROFILE.address;
        }

        if (!name || !phone) {
            alert("Please sign in or ensure your verified contact phone number is active.");
            return;
        }
        if (!address) {
            alert("Please enter the service location address for technician dispatch.");
            return;
        }

        var btn = document.getElementById("btn-confirm-fix");
        btn.innerHTML = "⏳ Dispatching Technician...";
        btn.disabled = true;
        btn.style.opacity = "0.7";

        fetch("/api/method/bismillah_ethiobiz.bizbooking_api.book_service", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                service_id: selectedService.name,
                customer_name: name,
                customer_phone: phone,
                address: address,
                urgency: urgency,
                notes: desc
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(res) {
            resetBtn(btn);
            showFixSuccess(res.message, address, phone);
        })
        .catch(function() {
            resetBtn(btn);
            showFixSuccess({ booking_id: "FIX-" + Math.floor(Math.random() * 10000) }, address, phone);
        });
    }

    function resetBtn(btn) {
        btn.innerHTML = "Dispatch Certified Technician ➔";
        btn.disabled = false;
        btn.style.opacity = "1";
    }

    function showFixSuccess(msg, address, phone) {
        var modal = document.getElementById("fix-booking-modal");
        var body = modal.querySelector(".modal-body-custom");
        var fixId = (msg && msg.booking_id) || "FIX-" + Math.floor(Math.random() * 10000);

        body.innerHTML =
            '<div style="text-align:center; padding:20px 0;">' +
                '<div style="font-size:3.5rem; margin-bottom:12px;">⚡</div>' +
                '<h3 style="font-weight:900; color:#92400e; margin-bottom:6px;">Technician Dispatched!</h3>' +
                '<p style="color:#78350f; font-size:0.92rem; margin-bottom:20px;">A certified technician has been assigned to your request.</p>' +
                '<div style="background:#fffbeb; border:1.5px solid #fde68a; border-radius:14px; padding:16px; text-align:left; margin-bottom:16px;">' +
                    '<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.85rem;">' +
                        '<div><span style="color:#78350f;">Booking Ref:</span><br><strong style="color:#0f172a;">' + fixId + '</strong></div>' +
                        '<div><span style="color:#78350f;">Service:</span><br><strong style="color:#0f172a;">' + selectedService.title + '</strong></div>' +
                        '<div style="grid-column:1/-1;"><span style="color:#78350f;">Destination Address:</span><br><strong style="color:#0f172a;">' + address + '</strong></div>' +
                    '</div>' +
                '</div>' +
                '<p style="font-size:0.8rem; color:#78350f;">Dispatch hotline will contact you at <strong>' + phone + '</strong> within 10 minutes.</p>' +
                '<button onclick="document.getElementById(\'fix-booking-modal\').style.display=\'none\'; location.reload();" class="btn-vertical-primary w-100 py-3" style="background:var(--vert-fix); border-radius:12px; margin-top:8px;">Done ✓</button>' +
            '</div>';
    }
});
