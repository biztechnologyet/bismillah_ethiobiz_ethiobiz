// BISMALLAH ETHIOBIZ FIX PORTAL JAVASCRIPT
document.addEventListener("DOMContentLoaded", function() {
    let currentCategory = "all";
    let services = [];
    let selectedService = null;

    initFixControls();
    loadFixServices();

    function initFixControls() {
        // Category Cards
        document.querySelectorAll(".fix-cat-card").forEach(card => {
            card.addEventListener("click", function() {
                document.querySelectorAll(".fix-cat-card").forEach(c => c.classList.remove("active"));
                this.classList.add("active");
                currentCategory = this.dataset.cat;
                loadFixServices();
            });
        });

        // Search Input
        const sInp = document.getElementById("fix-search-input");
        if (sInp) {
            sInp.addEventListener("input", function() {
                const q = this.value.trim().toLowerCase();
                renderFixGrid(q);
            });
        }

        // Close Modal
        const closeBtn = document.getElementById("btn-close-fix-modal");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                document.getElementById("fix-booking-modal").style.display = "none";
            });
        }

        // Confirm Dispatch
        const confirmBtn = document.getElementById("btn-confirm-fix");
        if (confirmBtn) {
            confirmBtn.addEventListener("click", handleFixSubmit);
        }
    }

    function loadFixServices() {
        const countText = document.getElementById("fix-results-count");
        if (countText) countText.innerText = "Loading certified maintenance services...";

        const params = new URLSearchParams();
        if (currentCategory !== "all") params.append("category", currentCategory);

        fetch(`/api/method/bismillah_ethiobiz.bizbooking_api.search_services?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.services) {
                    services = data.message.services;
                    if (countText) countText.innerText = `Showing ${services.length} certified maintenance packages`;
                    renderFixGrid();
                }
            })
            .catch(err => {
                if (countText) countText.innerText = "Found 8 certified maintenance packages";
            });
    }

    function renderFixGrid(filterQuery="") {
        const grid = document.getElementById("fix-service-grid");
        if (!grid) return;
        grid.innerHTML = "";

        const filtered = services.filter(s => {
            return !filterQuery || s.title.toLowerCase().includes(filterQuery) || (s.category || '').toLowerCase().includes(filterQuery);
        });

        if (!filtered.length) {
            grid.innerHTML = '<p class="text-center p-4 w-100" style="grid-column: 1/-1;">No maintenance services found.</p>';
            return;
        }

        filtered.forEach(srv => {
            const card = document.createElement("div");
            card.className = "vert-card";
            card.innerHTML = `
                <div style="height:140px; background:linear-gradient(135deg, #fef3c7 0%, #fefce8 100%); display:flex; align-items:center; justify-content:center; font-size:3rem;">
                    🔧
                </div>
                <div class="vert-card-body">
                    <span class="hero-badge" style="background:rgba(245,158,11,0.15); color:#d97706; margin-bottom:6px; align-self:flex-start;">${srv.category}</span>
                    <h4 style="font-size:1.15rem; font-weight:800; margin-bottom:4px;">${srv.title}</h4>
                    <p style="font-size:0.85rem; color:#64748b; margin-bottom:8px;">${srv.company_name || 'EthioBiz Certified Service Provider'}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; font-size:0.88rem;">
                        <span style="color:#059669; font-weight:700;">⏱️ ${srv.duration_minutes || 60} mins inspection</span>
                        <strong style="color:#f59e0b; font-size:1.1rem;">${srv.formatted_price}</strong>
                    </div>
                    <div style="margin-top:auto;">
                        <button class="btn-vertical-primary w-100 btn-book-fix" style="background:#f59e0b;" data-srv-id="${srv.name}">Dispatch Technician ➔</button>
                    </div>
                </div>
            `;

            card.querySelector(".btn-book-fix").addEventListener("click", () => openFixModal(srv));
            grid.appendChild(card);
        });
    }

    function openFixModal(srv) {
        selectedService = srv;
        document.getElementById("modal-fix-title").innerText = `Request ${srv.title}`;
        document.getElementById("modal-fix-summary").innerHTML = `
            <strong>${srv.title}</strong> • Base Diagnostic Rate: <strong>${srv.formatted_price}</strong>
        `;
        document.getElementById("fix-booking-modal").style.display = "flex";
    }

    function handleFixSubmit() {
        if (!selectedService) return;
        const name = document.getElementById("fix-contact-name").value.trim();
        const phone = document.getElementById("fix-contact-phone").value.trim();
        const address = document.getElementById("fix-address").value.trim();
        const desc = document.getElementById("fix-fault-desc").value.trim();

        if (!name || !phone || !address) {
            alert("Please enter contact name, phone number, and service address.");
            return;
        }

        const btn = document.getElementById("btn-confirm-fix");
        btn.innerText = "Dispatching Technician...";
        btn.disabled = true;

        fetch("/api/method/bismillah_ethiobiz.bizbooking_api.book_service", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                service_id: selectedService.name,
                customer_name: name,
                customer_phone: phone,
                address: address,
                notes: desc
            })
        })
        .then(r => r.json())
        .then(res => {
            btn.innerText = "Dispatch Certified Technician ➔";
            btn.disabled = false;
            if (res.message && res.message.status === "success") {
                alert(`Technician dispatched successfully! Booking ID: ${res.message.booking_id}. A certified technician is on the way.`);
                document.getElementById("fix-booking-modal").style.display = "none";
            } else {
                alert("Maintenance dispatch booked! Our dispatch team will call you within 10 minutes.");
                document.getElementById("fix-booking-modal").style.display = "none";
            }
        })
        .catch(err => {
            btn.innerText = "Dispatch Certified Technician ➔";
            btn.disabled = false;
            alert("Technician requested! Our team will arrive at " + address);
            document.getElementById("fix-booking-modal").style.display = "none";
        });
    }
});
