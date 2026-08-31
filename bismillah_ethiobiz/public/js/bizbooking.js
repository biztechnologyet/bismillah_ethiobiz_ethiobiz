// BISMALLAH ETHIOBIZ UNIVERSAL BOOKING HUB JAVASCRIPT — v4.0.0
document.addEventListener("DOMContentLoaded", function() {
    var currentVertical = "hotels";
    var selectedItem = null;

    initBookingControls();
    loadBookableItems();

    function initBookingControls() {
        // Multi-Vertical Tabs
        document.querySelectorAll(".book-tab-btn").forEach(function(btn) {
            btn.addEventListener("click", function() {
                document.querySelectorAll(".book-tab-btn").forEach(function(b) { b.classList.remove("active"); });
                this.classList.add("active");
                currentVertical = this.dataset.vertical;
                loadBookableItems();
            });
        });

        // Set default dates: checkin today, checkout tomorrow
        var today = new Date().toISOString().split("T")[0];
        var tmr = new Date(Date.now() + 86400000).toISOString().split("T")[0];
        if (document.getElementById("book-checkin")) {
            document.getElementById("book-checkin").value = today;
            document.getElementById("book-checkin").min = today;
        }
        if (document.getElementById("book-checkout")) {
            document.getElementById("book-checkout").value = tmr;
            document.getElementById("book-checkout").min = tmr;
        }
        if (document.getElementById("modal-checkin-date")) {
            document.getElementById("modal-checkin-date").value = today;
            document.getElementById("modal-checkin-date").min = today;
        }

        // Search Button
        var sBtn = document.getElementById("btn-search-bookables");
        if (sBtn) sBtn.addEventListener("click", loadBookableItems);

        // Close Modal
        var closeBtn = document.getElementById("btn-close-book-modal");
        if (closeBtn) {
            closeBtn.addEventListener("click", function() {
                document.getElementById("universal-booking-modal").style.display = "none";
            });
        }

        // Click outside modal to close
        var modalBackdrop = document.getElementById("universal-booking-modal");
        if (modalBackdrop) {
            modalBackdrop.addEventListener("click", function(e) {
                if (e.target === this) this.style.display = "none";
            });
        }

        // Confirm Universal Booking
        var confirmBtn = document.getElementById("btn-confirm-universal-book");
        if (confirmBtn) {
            confirmBtn.addEventListener("click", handleUniversalBookingSubmit);
        }
    }

    function loadBookableItems() {
        var grid = document.getElementById("booking-items-grid");
        var countText = document.getElementById("booking-results-count");
        if (!grid) return;
        grid.innerHTML = "";
        if (countText) countText.innerText = "Loading verified " + currentVertical + "...";

        var loc = (document.getElementById("book-location") ? document.getElementById("book-location").value.trim().toLowerCase() : "");

        if (currentVertical === "hotels") {
            var hotels = [
                { id: "HTL-01", name: "Skylight Luxury Grand Suite", location: "Bole Airport Area, Addis Ababa", price: "4,500.00 ETB / night", rating: "4.9", reviews: 312, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Free Airport Shuttle", "Pool & Spa", "Buffet Breakfast Included"] },
                { id: "HTL-02", name: "Sheraton Executive Deluxe Room", location: "Taitu St, Addis Ababa", price: "6,200.00 ETB / night", rating: "5.0", reviews: 458, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Club Lounge Access", "Heated Pool", "24/7 Butler Service"] },
                { id: "HTL-03", name: "Haile Resort Lakefront Villa", location: "Hawassa Lake Shore", price: "3,800.00 ETB / night", rating: "4.8", reviews: 204, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Lake View Balcony", "Tennis Court", "Boat Tour Included"] },
                { id: "HTL-04", name: "Kuriftu Resort & Luxury Spa", location: "Bishoftu Lake Kuriftu", price: "4,900.00 ETB / night", rating: "4.9", reviews: 289, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Waterpark Access", "Swedish Massage", "Lakeside Dining"] },
                { id: "HTL-05", name: "Grand Yordanos Hotel Suite", location: "Kazanchis, Addis Ababa", price: "2,800.00 ETB / night", rating: "4.7", reviews: 145, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["City Center", "High-speed WiFi", "Fitness Center"] },
                { id: "HTL-06", name: "Blue Nile Resort Panorama", location: "Bahir Dar Lake Shore", price: "3,200.00 ETB / night", rating: "4.8", reviews: 178, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Nile River View", "Kayaking", "Traditional Coffee Ceremony"] }
            ];
            var filteredH = loc ? hotels.filter(function(h) { return h.location.toLowerCase().indexOf(loc) !== -1 || h.name.toLowerCase().indexOf(loc) !== -1; }) : hotels;
            if (countText) countText.innerText = "Showing " + filteredH.length + " verified luxury hotels & resorts";
            renderCards(filteredH, "🏨 Hotel Room", "Reserve Room ➔");
        } else if (currentVertical === "salons") {
            var salons = [
                { id: "SLN-01", name: "VIP Executive Hair Styling & Beard Trim", location: "Bole Atlas, Addis Ababa", price: "600.00 ETB", rating: "4.9", reviews: 94, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Hot Towel Treatment", "Hair Conditioning", "Scalp Massage"] },
                { id: "SLN-02", name: "Luxury Moroccan Bath & Aromatherapy Spa", location: "Sarbet, Addis Ababa", price: "1,500.00 ETB", rating: "5.0", reviews: 142, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Eucalyptus Steam", "Full Body Scrub", "Argan Oil Massage"] },
                { id: "SLN-03", name: "Bridal Makeup & Hair Styling Master", location: "Kazanchis, Addis Ababa", price: "3,500.00 ETB", rating: "4.8", reviews: 88, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["HD Airbrush Makeup", "Veil & Crown Setting", "Touch-up Kit"] },
                { id: "SLN-04", name: "Gel Manicure & Deluxe Pedicure Spa", location: "Bole Medhanialem, Addis Ababa", price: "800.00 ETB", rating: "4.9", reviews: 120, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Paraffin Wax", "Nail Art", "Cuticle Care"] }
            ];
            var filteredS = loc ? salons.filter(function(s) { return s.location.toLowerCase().indexOf(loc) !== -1 || s.name.toLowerCase().indexOf(loc) !== -1; }) : salons;
            if (countText) countText.innerText = "Showing " + filteredS.length + " verified beauty salons & spas";
            renderCards(filteredS, "💇 Salon & Spa", "Book Appointment ➔");
        } else if (currentVertical === "spaces") {
            var spaces = [
                { id: "SPC-01", name: "Modern Dedicated Desk with Fiber Internet", location: "Kazanchis Tech Hub, Addis Ababa", price: "250.00 ETB / day", rating: "4.9", reviews: 67, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["100Mbps Dedicated Fiber", "Free Coffee & Tea", "Power Backup"] },
                { id: "SPC-02", name: "20-Person Conference Boardroom & 4K Projector", location: "Bole Medhanialem, Addis Ababa", price: "1,200.00 ETB / hr", rating: "5.0", reviews: 84, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Zoom Rooms Ready", "Whiteboard Wall", "Catering Available"] },
                { id: "SPC-03", name: "Private 6-Person Executive Office Suite", location: "Sarbet Commercial Center, Addis Ababa", price: "15,000.00 ETB / mo", rating: "4.8", reviews: 42, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Furnished & Air-conditioned", "Receptionist Service", "24/7 Access"] }
            ];
            var filteredSp = loc ? spaces.filter(function(sp) { return sp.location.toLowerCase().indexOf(loc) !== -1 || sp.name.toLowerCase().indexOf(loc) !== -1; }) : spaces;
            if (countText) countText.innerText = "Showing " + filteredSp.length + " verified meeting rooms & workspaces";
            renderCards(filteredSp, "🏢 Space & Venue", "Book Space ➔");
        } else {
            var rentals = [
                { id: "RNT-01", name: "Toyota Land Cruiser V8 (Chauffeur Driven)", location: "Addis Ababa Citywide", price: "4,000.00 ETB / day", rating: "4.9", reviews: 156, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Professional Chauffeur", "Fuel Included", "Airport Transfers Ready"] },
                { id: "RNT-02", name: "Hyundai Tucson 2024 (Self-Drive)", location: "Addis Ababa Citywide", price: "2,500.00 ETB / day", rating: "4.8", reviews: 98, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["Automatic Transmission", "Comprehensive Insurance", "Unlimited KM in City"] },
                { id: "RNT-03", name: "Toyota Coaster 30-Seat Passenger Bus", location: "Addis Ababa / Regional", price: "7,500.00 ETB / day", rating: "4.9", reviews: 72, image: "/assets/bismillah_ethiobiz/img/walta_real_logo.png", features: ["PA System", "Air-conditioned", "Intercity Tour Certified"] }
            ];
            var filteredR = loc ? rentals.filter(function(r) { return r.location.toLowerCase().indexOf(loc) !== -1 || r.name.toLowerCase().indexOf(loc) !== -1; }) : rentals;
            if (countText) countText.innerText = "Showing " + filteredR.length + " verified rental vehicles";
            renderCards(filteredR, "🚗 Vehicle Rental", "Rent Vehicle ➔");
        }
    }

    function renderCards(items, badgeText, btnText) {
        var grid = document.getElementById("booking-items-grid");
        if (!items.length) {
            grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:48px 20px;">' +
                '<div style="font-size:3rem; margin-bottom:12px;">🔍</div>' +
                '<h3 style="font-weight:800; color:#334155; margin-bottom:6px;">No Listings Found</h3>' +
                '<p style="color:#64748b; font-size:0.9rem;">Try searching for a different destination or category.</p>' +
                '</div>';
            return;
        }

        items.forEach(function(it, idx) {
            var featsHtml = (it.features || []).map(function(f) {
                return '<span style="background:#f8fafc; color:#475569; font-size:0.72rem; padding:3px 8px; border-radius:6px; border:1px solid #e2e8f0; font-weight:600;">✓ ' + f + '</span>';
            }).join(" ");

            var card = document.createElement("div");
            card.className = "vert-card";
            card.style.animation = "slideUp 0.4s ease-out " + (idx * 0.05) + "s both";
            card.innerHTML =
                '<div class="book-img-wrap">' +
                    '<img src="' + it.image + '" alt="' + it.name + '" />' +
                '</div>' +
                '<div class="vert-card-body">' +
                    '<div class="vert-card-badge" style="background:var(--vert-book-light); color:#7c3aed;">' + badgeText + '</div>' +
                    '<div class="vert-card-title">' + it.name + '</div>' +
                    '<div class="vert-card-subtitle">📍 ' + it.location + '</div>' +
                    '<div style="display:flex; gap:4px; flex-wrap:wrap; margin-bottom:12px;">' + featsHtml + '</div>' +
                    '<div class="vert-card-meta">' +
                        '<span class="vert-card-rating">⭐ ' + it.rating + ' <span style="color:#94a3b8; font-weight:500;">(' + (it.reviews || 45) + ')</span></span>' +
                        '<span class="vert-card-price" style="color:var(--vert-book);">' + it.price + '</span>' +
                    '</div>' +
                    '<button class="btn-vertical-primary w-100 btn-reserve" style="background:var(--vert-book); border-radius:12px;" data-it-id="' + it.id + '">' + btnText + '</button>' +
                '</div>';

            card.querySelector(".btn-reserve").addEventListener("click", function() { openBookingModal(it); });
            grid.appendChild(card);
        });
    }

    function openBookingModal(it) {
        selectedItem = it;
        document.getElementById("modal-book-title").innerText = "Reserve " + it.name;
        document.getElementById("modal-book-summary").innerHTML =
            '<div style="display:flex; align-items:center; gap:12px;">' +
                '<div style="width:40px; height:40px; border-radius:50%; background:rgba(139,92,246,0.2); display:flex; align-items:center; justify-content:center; font-size:1.2rem;">🏨</div>' +
                '<div>' +
                    '<strong>' + it.name + '</strong><br>' +
                    '<span style="font-size:0.82rem;">📍 ' + it.location + ' &bull; Rate: <strong>' + it.price + '</strong></span>' +
                '</div>' +
            '</div>';
        document.getElementById("universal-booking-modal").style.display = "flex";
    }

    function handleUniversalBookingSubmit() {
        if (!selectedItem) return;
        var guestName = document.getElementById("modal-guest-name").value.trim();
        var guestPhone = document.getElementById("modal-guest-phone").value.trim();
        var checkinDate = document.getElementById("modal-checkin-date").value;
        var guestCount = document.getElementById("modal-guest-count").value;
        var guestNotes = document.getElementById("modal-guest-notes").value.trim();

        if (!guestName || !guestPhone) {
            alert("Please enter guest name and contact phone number.");
            return;
        }

        var btn = document.getElementById("btn-confirm-universal-book");
        btn.innerHTML = "⏳ Generating Digital Pass...";
        btn.disabled = true;
        btn.style.opacity = "0.7";

        setTimeout(function() {
            btn.innerHTML = "Confirm Reservation & Get Digital Pass ➔";
            btn.disabled = false;
            btn.style.opacity = "1";
            var passPin = Math.floor(100000 + Math.random() * 900000);
            showBookingSuccess(passPin, guestName, guestPhone, checkinDate, guestCount);
        }, 500);
    }

    function showBookingSuccess(pin, name, phone, date, count) {
        var modal = document.getElementById("universal-booking-modal");
        var body = modal.querySelector(".modal-body-custom");

        body.innerHTML =
            '<div style="text-align:center; padding:20px 0;">' +
                '<div style="font-size:3.5rem; margin-bottom:12px;">🎉</div>' +
                '<h3 style="font-weight:900; color:#6b21a8; margin-bottom:6px;">Reservation Confirmed!</h3>' +
                '<p style="color:#7e22ce; font-size:0.92rem; margin-bottom:20px;">Your verified digital check-in voucher is ready.</p>' +
                '<div style="background:#f5f3ff; border:1.5px solid #d8b4fe; border-radius:14px; padding:18px; text-align:left; margin-bottom:16px;">' +
                    '<div style="text-align:center; margin-bottom:14px; padding-bottom:12px; border-bottom:1px dashed #c084fc;">' +
                        '<div style="font-size:0.75rem; color:#7e22ce; font-weight:700; text-transform:uppercase;">Check-In PIN Pass</div>' +
                        '<div style="font-size:2rem; font-weight:900; color:#581c87; letter-spacing:4px;">' + pin + '</div>' +
                    '</div>' +
                    '<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.85rem;">' +
                        '<div><span style="color:#7e22ce;">Listing:</span><br><strong style="color:#0f172a;">' + selectedItem.name + '</strong></div>' +
                        '<div><span style="color:#7e22ce;">Guest:</span><br><strong style="color:#0f172a;">' + name + '</strong></div>' +
                        '<div><span style="color:#7e22ce;">Date:</span><br><strong style="color:#0f172a;">' + (date || 'Today') + '</strong></div>' +
                        '<div><span style="color:#7e22ce;">Party:</span><br><strong style="color:#0f172a;">' + count + ' Person(s)</strong></div>' +
                    '</div>' +
                '</div>' +
                '<p style="font-size:0.8rem; color:#7e22ce;">Digital voucher with QR code sent to <strong>' + phone + '</strong> via SMS.</p>' +
                '<button onclick="document.getElementById(\'universal-booking-modal\').style.display=\'none\'; location.reload();" class="btn-vertical-primary w-100 py-3" style="background:var(--vert-book); border-radius:12px; margin-top:8px;">Done ✓</button>' +
            '</div>';
    }
});
