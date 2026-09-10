// BISMALLAH ETHIOBIZ UNIVERSAL BOOKING HUB JAVASCRIPT
document.addEventListener("DOMContentLoaded", function() {
    let currentVertical = "hotels";
    let selectedItem = null;

    initBookingControls();
    loadBookableItems();

    function initBookingControls() {
        // Multi-Vertical Tabs
        document.querySelectorAll(".book-tab-btn").forEach(btn => {
            btn.addEventListener("click", function() {
                document.querySelectorAll(".book-tab-btn").forEach(b => b.classList.remove("active"));
                this.classList.add("active");
                currentVertical = this.dataset.vertical;
                loadBookableItems();
            });
        });

        // Set default dates: checkin today, checkout tomorrow
        const today = new Date().toISOString().split("T")[0];
        const tmr = new Date(Date.now() + 86400000).toISOString().split("T")[0];
        if (document.getElementById("book-checkin")) document.getElementById("book-checkin").value = today;
        if (document.getElementById("book-checkout")) document.getElementById("book-checkout").value = tmr;

        // Search Button
        document.getElementById("btn-search-bookables").addEventListener("click", loadBookableItems);

        // Close Modal
        const closeBtn = document.getElementById("btn-close-book-modal");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                document.getElementById("universal-booking-modal").style.display = "none";
            });
        }

        // Confirm Universal Booking
        const confirmBtn = document.getElementById("btn-confirm-universal-book");
        if (confirmBtn) {
            confirmBtn.addEventListener("click", handleUniversalBookingSubmit);
        }
    }

    function loadBookableItems() {
        const grid = document.getElementById("booking-items-grid");
        const countText = document.getElementById("booking-results-count");
        if (!grid) return;
        grid.innerHTML = "";
        if (countText) countText.innerText = `Loading verified ${currentVertical}...`;

        if (currentVertical === "hotels") {
            const sampleHotels = [
                { id: "HTL-01", name: "Skylight Luxury Grand Suite", location: "Bole Airport Area, Addis Ababa", price: "4,500.00 ETB / night", rating: "4.9", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" },
                { id: "HTL-02", name: "Sheraton Addis Executive Room", location: "Taitu St, Addis Ababa", price: "6,200.00 ETB / night", rating: "5.0", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" },
                { id: "HTL-03", name: "Haile Resort Lakefront Villa", location: "Hawassa Lake Shore", price: "3,800.00 ETB / night", rating: "4.8", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" },
                { id: "HTL-04", name: "Kuriftu Resort & Luxury Spa", location: "Bishoftu Lake Kuriftu", price: "4,900.00 ETB / night", rating: "4.9", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" }
            ];
            if (countText) countText.innerText = `Showing ${sampleHotels.length} verified luxury hotels & resorts`;
            renderCards(sampleHotels, "🏨 Hotel Room", "Reserve Room ➔");
        } else if (currentVertical === "salons") {
            const sampleSalons = [
                { id: "SLN-01", name: "VIP Executive Hair Styling & Beard Trim", location: "Bole Atlas, Addis Ababa", price: "600.00 ETB", rating: "4.9", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" },
                { id: "SLN-02", name: "Luxury Moroccan Bath & Aromatherapy Spa", location: "Sarbet, Addis Ababa", price: "1,500.00 ETB", rating: "5.0", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" },
                { id: "SLN-03", name: "Bridal Makeup & Hair Styling Master", location: "Kazanchis, Addis Ababa", price: "3,500.00 ETB", rating: "4.8", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" }
            ];
            if (countText) countText.innerText = `Showing ${sampleSalons.length} verified beauty salons & spas`;
            renderCards(sampleSalons, "💇 Salon & Spa", "Book Appointment ➔");
        } else if (currentVertical === "spaces") {
            const sampleSpaces = [
                { id: "SPC-01", name: "Modern Dedicated Desk with Fiber Internet", location: "Kazanchis Tech Hub", price: "250.00 ETB / day", rating: "4.9", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" },
                { id: "SPC-02", name: "20-Person Conference Boardroom & Projector", location: "Bole Medhanialem", price: "1,200.00 ETB / hr", rating: "5.0", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" }
            ];
            if (countText) countText.innerText = `Showing ${sampleSpaces.length} verified meeting rooms & workspaces`;
            renderCards(sampleSpaces, "🏢 Space & Venue", "Book Space ➔");
        } else {
            const sampleRentals = [
                { id: "RNT-01", name: "Toyota Land Cruiser V8 (Chauffeur Driven)", location: "Addis Ababa Citywide", price: "4,000.00 ETB / day", rating: "4.9", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" },
                { id: "RNT-02", name: "Hyundai Tucson 2024 (Self-Drive)", location: "Addis Ababa Citywide", price: "2,500.00 ETB / day", rating: "4.8", image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png" }
            ];
            if (countText) countText.innerText = `Showing ${sampleRentals.length} verified rental vehicles`;
            renderCards(sampleRentals, "🚗 Vehicle Rental", "Rent Vehicle ➔");
        }
    }

    function renderCards(items, badgeText, btnText) {
        const grid = document.getElementById("booking-items-grid");
        items.forEach(it => {
            const card = document.createElement("div");
            card.className = "vert-card";
            card.innerHTML = `
                <div style="height:150px; background:#f1f5f9; display:flex; align-items:center; justify-content:center;">
                    <img src="${it.image}" alt="${it.name}" style="max-height:80px; object-fit:contain;" />
                </div>
                <div class="vert-card-body">
                    <span class="hero-badge" style="background:rgba(139,92,246,0.15); color:#7c3aed; margin-bottom:6px; align-self:flex-start;">${badgeText}</span>
                    <h4 style="font-size:1.1rem; font-weight:800; margin-bottom:4px;">${it.name}</h4>
                    <p style="font-size:0.82rem; color:#64748b; margin-bottom:8px;">📍 ${it.location}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="color:#f59e0b; font-weight:700; font-size:0.88rem;">⭐ ${it.rating}</span>
                        <strong style="color:#8b5cf6; font-size:1.05rem;">${it.price}</strong>
                    </div>
                    <div style="margin-top:auto;">
                        <button class="btn-vertical-primary w-100 btn-reserve" style="background:#8b5cf6;" data-it-id="${it.id}">${btnText}</button>
                    </div>
                </div>
            `;
            card.querySelector(".btn-reserve").addEventListener("click", () => openBookingModal(it));
            grid.appendChild(card);
        });
    }

    function openBookingModal(it) {
        selectedItem = it;
        document.getElementById("modal-book-title").innerText = `Reserve ${it.name}`;
        document.getElementById("modal-book-summary").innerHTML = `
            <strong>${it.name}</strong> • Rate: <strong>${it.price}</strong>
        `;
        document.getElementById("universal-booking-modal").style.display = "flex";
    }

    function handleUniversalBookingSubmit() {
        if (!selectedItem) return;
        const guestName = document.getElementById("modal-guest-name").value.trim();
        const guestPhone = document.getElementById("modal-guest-phone").value.trim();
        const guestNotes = document.getElementById("modal-guest-notes").value.trim();

        if (!guestName || !guestPhone) {
            alert("Please enter guest name and contact phone number.");
            return;
        }

        const btn = document.getElementById("btn-confirm-universal-book");
        btn.innerText = "Generating Pass...";
        btn.disabled = true;

        setTimeout(() => {
            btn.innerText = "Confirm Reservation & Get Digital Pass ➔";
            btn.disabled = false;
            const passPin = Math.floor(100000 + Math.random() * 900000);
            alert(`🎉 Reservation Confirmed!\nBooking Ref: ${selectedItem.id}\nCheck-in PIN: ${passPin}\nDigital voucher sent to ${guestPhone}`);
            document.getElementById("universal-booking-modal").style.display = "none";
        }, 600);
    }
});
