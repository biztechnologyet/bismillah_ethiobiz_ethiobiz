// BISMALLAH ETHIOBIZ UNIVERSAL BOOKING HUB JAVASCRIPT — v4.1.0
// DB-first aggregator-backed rewrite: search_all_bookables + create_universal_booking
document.addEventListener("DOMContentLoaded", function() {
    var currentVertical = "hotels";
    var selectedItem = null;

    initBookingControls();
    loadBookableItems();

    function getJSON(url) {
        return fetch(url).then(function(r) { return r.json(); }).then(function(res) { return res.message || res; });
    }

    function api(method, data) {
        return fetch("/api/method/" + method, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": (window.frappe && frappe.csrf_token) || "" },
            body: JSON.stringify(data || {})
        }).then(function(r) { return r.json(); });
    }

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

    function verticalForTab(tab) {
        // Map booking.html hotel/salons/spaces/rentals tabs to aggregator verticals
        switch (tab) {
            case "hotels": return "hotels";
            case "salons": return "salon";
            case "spaces": return "workspaces";
            case "rentals": return "rentals";
            default: return tab;
        }
    }

    function itemToCard(it, idx, badgeText) {
        return {
            id: it.id,
            vertical: it.vertical || currentVertical,
            company: it.hotel_company || it.company || null,
            room_type: it.category || "Standard Suite",
            name: it.title || it.id,
            location: it.subtitle || "Addis Ababa, Ethiopia",
            price: it.price_text || "",
            price_num: it.price || 0,
            rating: (it.rating || 4.9).toString(),
            reviews: it.reviews || 45,
            image: it.image || "/assets/bismillah_ethiobiz/img/walta_real_logo.png",
            features: it.category ? [it.category] : [],
            category: it.category || "Service Booking"
        };
    }

    function loadBookableItems() {
        var grid = document.getElementById("booking-items-grid");
        var countText = document.getElementById("booking-results-count");
        if (!grid) return;
        grid.innerHTML = "";
        if (countText) countText.innerText = "Loading verified " + currentVertical + "...";

        var loc = (document.getElementById("book-location") ? document.getElementById("book-location").value.trim() : "") || undefined;
        var checkIn = document.getElementById("book-checkin") ? document.getElementById("book-checkin").value : undefined;
        var checkOut = document.getElementById("book-checkout") ? document.getElementById("book-checkout").value : undefined;

        var vertical = verticalForTab(currentVertical);
        var params = new URLSearchParams();
        if (vertical && vertical !== "all") params.set("vertical", vertical);
        if (loc) params.set("location", loc);
        if (checkIn) params.set("check_in", checkIn);
        if (checkOut) params.set("check_out", checkOut);
        params.set("guests", "1");

        var badgeText = currentVertical === "hotels" ? "🏨 Hotel Room"
            : currentVertical === "salons" ? "💇 Salon & Spa"
            : currentVertical === "spaces" ? "🏢 Space & Venue"
            : "🚗 Vehicle Rental";
        var btnText = currentVertical === "hotels" ? "Reserve Room ➔"
            : currentVertical === "salons" ? "Book Appointment ➔"
            : currentVertical === "spaces" ? "Book Space ➔"
            : "Rent Vehicle ➔";

        getJSON("bismillah_ethiobiz.bizbooking_aggregator_api.search_all_bookables?" + params.toString())
            .then(function(res) {
                var items = (res && res.bookables) || [];
                if (countText) countText.innerText = "Showing " + (res ? res.total : items.length) + " verified listings";
                if (Array.isArray(items)) {
                    renderCards(items.map(function(it, idx) { return itemToCard(it, idx); }), badgeText, btnText);
                } else {
                    renderCards([], badgeText, btnText);
                }
            })
            .catch(function() {
                if (countText) countText.innerText = "No verified listings available right now. Check back soon!";
                renderCards([], badgeText, btnText);
            });
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
                '<div style="width:40px; height:40px; border-radius:50%; background:rgba(139,92,246,0.2); display:flex; align-items:center; justify-content:center; font-size:1.2rem;">' + (it.vertical === "hotel" ? "🏨" : it.vertical === "service" || it.vertical === "salon" ? "💇" : it.vertical === "resource" ? "🏢" : "🚗") + '</div>' +
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
        btn.innerHTML = "⏳ Confirming Reservation...";
        btn.disabled = true;
        btn.style.opacity = "0.7";

        var bookingData = {
            vertical: selectedItem.vertical || currentVertical,
            target_id: selectedItem.id,
            company: selectedItem.company || undefined,
            customer_name: guestName,
            customer_phone: guestPhone,
            date: checkinDate,
            time_slot: "10:00",
            guests: parseInt(guestCount, 10) || 1,
            notes: guestNotes,
            room_type: selectedItem.room_type
        };
        if ((selectedItem.vertical || currentVertical) === "hotel" || currentVertical === "hotels") {
            bookingData.check_out = document.getElementById("book-checkout")
                ? document.getElementById("book-checkout").value
                : (new Date(new Date(checkinDate + "T00:00:00").getTime() + 86400000)).toISOString().split("T")[0];
        }

        api("bismillah_ethiobiz.bizbooking_aggregator_api.create_universal_booking", { booking_data: bookingData })
            .then(function(res) {
                var msg = res.message || res;
                if (msg && msg.status === "success") {
                    showBookingSuccess(
                        msg.booking_pass_pin || (msg.booking_id || "").toUpperCase(),
                        msg.booking_id || msg.message || "Confirmed",
                        guestName, guestPhone, checkinDate, guestCount
                    );
                } else {
                    resetBtn(btn);
                    alert("Booking could not be completed: " + ((msg && msg.message) || "unknown error"));
                }
            })
            .catch(function() {
                resetBtn(btn);
                alert("Booking could not be completed. Please try again or contact the company directly.");
            });
    }

    function resetBtn(btn) {
        btn.innerHTML = "Confirm Reservation & Get Digital Pass ➔";
        btn.disabled = false;
        btn.style.opacity = "1";
    }

    function showBookingSuccess(pin, ref, name, phone, date, count) {
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
                        '<div><span style="color:#7e22ce;">Reference:</span><br><strong style="color:#0f172a;">' + ref + '</strong></div>' +
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