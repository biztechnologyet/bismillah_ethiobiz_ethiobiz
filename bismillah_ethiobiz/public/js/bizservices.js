/* ============================================================
   Bismallah EthioBiz — BizServices Public Portal Controller (Phase 6)
   Loads categories + listings, search/filter, booking flow backed by
   real availability + book_service, and feed-interaction tracking.
   ============================================================ */
(function () {
    "use strict";

    const API = "/api/method/bismillah_ethiobiz.";
    let allListings = [];
    let currentCat = "all";
    let currentQuery = "";

    function getJSON(method, params) {
        const url = new URL(API + method, window.location.origin);
        if (params) Object.keys(params).forEach(k => params[k] != null && url.searchParams.append(k, params[k]));
        return fetch(url).then(r => r.json()).then(d => (d && d.message) || {});
    }

    function el(id) { return document.getElementById(id); }

    function track(interaction, itemType, itemId) {
        try {
            if (window.ethiobizTrack) window.ethiobizTrack(interaction, itemType, itemId);
            if (window.feedTracker) window.feedTracker.log(itemType, interaction, itemId);
        } catch (e) { /* non-fatal */ }
    }

    function renderCats(categories) {
        const wrap = el("bs-cats");
        if (!wrap) return;
        wrap.innerHTML = '<button class="bs-cat-chip active" data-cat="all">All Services</button>';
        (categories || []).forEach(c => {
            const b = document.createElement("button");
            b.className = "bs-cat-chip";
            b.dataset.cat = c.name;
            b.textContent = (c.category_icon ? c.category_icon + " " : "") + c.category_name;
            b.addEventListener("click", () => {
                currentCat = b.dataset.cat;
                wrap.querySelectorAll(".bs-cat-chip").forEach(x => x.classList.remove("active"));
                b.classList.add("active");
                render();
            });
            wrap.appendChild(b);
        });
    }

    function cardHtml(s) {
        const img = (s.images && s.images[0] && s.images[0].image) || "";
        const slug = s.slug || s.name;
        const imgStyle = img
            ? `background-image:url('${img}')`
            : "background:linear-gradient(135deg,#0d9488,#0284c7)";
        const rating = (s.average_rating != null && s.average_rating > 0)
            ? "&#9733; " + Number(s.average_rating).toFixed(1)
            : "";
        return `
        <div class="bs-card">
          <div class="bs-card-img" style="${imgStyle}"></div>
          <div class="bs-card-body">
            <div class="bs-card-cat">${s.category_name || s.category || ""}</div>
            <h3>${s.service_name}</h3>
            <div class="bs-card-price">${Number(s.price).toLocaleString()} ${s.currency || "ETB"}${s.price_type === "Starting From" ? " / from" : " " + (s.price_type || "")}</div>
            <div class="bs-card-meta">&#9200; ${s.duration_minutes || 30} min &nbsp; ${rating}</div>
            ${s.requires_travel ? '<div class="bs-card-meta" style="color:#ea580c;">&#128674; Home dispatch available</div>' : ""}
            <div class="bs-btn" data-service="${s.name}" data-slug="${slug}">Book Now</div>
          </div>
        </div>`;
    }

    function render() {
        const grid = el("bs-grid");
        if (!grid) return;
        let list = allListings;
        if (currentCat !== "all") list = list.filter(s => s.category === currentCat);
        if (currentQuery) {
            const q = currentQuery.toLowerCase();
            list = list.filter(s =>
                (s.service_name || "").toLowerCase().includes(q) ||
                (s.category_name || "").toLowerCase().includes(q) ||
                (s.category || "").toLowerCase().includes(q) ||
                (s.serving_city || "").toLowerCase().includes(q)
            );
        }
        if (!list.length) {
            grid.innerHTML = '<div class="bs-empty">No services found yet. Check back soon — providers are joining daily.</div>';
            return;
        }
        grid.innerHTML = list.map(cardHtml).join("");
        grid.querySelectorAll(".bs-btn").forEach(btn => {
            btn.addEventListener("click", () => openBooking(btn.dataset.service));
        });
    }

    // ---- Booking modal backed by real availability + book_service ----
    function loadAvailability(serviceId, provider) {
        getJSON("bizservice_api.get_service_availability", {
            listing: serviceId,
            date: el("bs-date").value || undefined,
            practitioner: provider || undefined
        }).then(res => {
            const slots = (res && res.slots) || [];
            const sel = el("bs-slot-select");
            sel.innerHTML = "<option value=''>Select a time…</option>";
            slots.forEach(s => {
                const o = document.createElement("option");
                o.value = s; o.textContent = s;
                sel.appendChild(o);
            });
            if (el("bs-avail-note")) {
                const src = (res && res.source) || "";
                const srcLabel = src === "provider-custom" ? " (provider custom)" :
                    src === "service-custom" ? " (service custom)" : "";
                el("bs-avail-note").textContent =
                    res && res.available ? `${slots.length} slots available${srcLabel}` :
                    "No slots available for this date";
            }
        });
    }

    function openBooking(serviceId) {
        track("view_booking", "BizService Listing", serviceId);
        const modal = el("bs-modal");
        if (!modal) return;
        el("bs-book-service").value = serviceId;
        el("bs-modal-title").textContent = "Book this service";
        el("bs-slot-select").innerHTML = "<option value=''>Select a time…</option>";

        // Populate the provider picker with the listing's assigned staff
        const prov = el("bs-provider");
        if (prov) {
            prov.innerHTML = "<option value=''>Any available provider</option>";
            const listing = allListings.find(l => l.name === serviceId) || {};
            (listing.practitioners || []).forEach(p => {
                const o = document.createElement("option");
                o.value = p.practitioner_name || p.name || "";
                o.textContent = p.practitioner_name || p.role_title || "Provider";
                prov.appendChild(o);
            });
        }

        modal.classList.add("open");
        loadAvailability(serviceId, prov ? prov.value : undefined);
    }

    function closeBooking() { el("bs-modal") && el("bs-modal").classList.remove("open"); }

    function submitBooking() {
        const serviceId = el("bs-book-service").value;
        const payload = {
            service_id: serviceId,
            booking_date: el("bs-date").value,
            booking_time: el("bs-slot-select").value,
            practitioner: el("bs-provider") ? el("bs-provider").value || undefined : undefined,
            customer_name: el("bs-name").value,
            customer_phone: el("bs-phone").value,
            address: el("bs-address").value,
            notes: el("bs-notes").value
        };
        fetch(API + "bizbooking_api.book_service", {
            method: "POST",
            headers: { "X-Frappe-CSRF-Token": window.csrf_token || "", "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams(payload)
        }).then(r => r.json()).then(res => {
            const msg = (res && res.message) || {};
            track("booked", "BizService Listing", serviceId);
            el("bs-modal-title").textContent = msg.message || "Booking confirmed!";
            if (msg.booking_id) {
                el("bs-book-result").innerHTML =
                    `<div style="background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0;border-radius:10px;padding:12px;">
                       Booking ID: <b>${msg.booking_id}</b><br>
                       ${msg.bizride_delivery ? "Home dispatch started: <b>" + msg.bizride_delivery + "</b><br>" : ""}
                       ${msg.amount || ""}
                     </div>`;
            } else {
                el("bs-book-result").innerHTML = `<div style="color:#b91c1c;">Something went wrong. Please try again.</div>`;
            }
        }).catch(() => {
            el("bs-book-result").innerHTML = `<div style="color:#b91c1c;">Could not reach the booking service.</div>`;
        });
    }

    function init() {
        const wrap = el("bizservices-app");
        if (!wrap) return;

        const search = el("bs-search");
        if (search) search.addEventListener("input", e => { currentQuery = e.target.value.trim(); render(); });

        const date = el("bs-date");
        if (date && !date.value) date.value = new Date().toISOString().slice(0, 10);

        getJSON("bizservice_api.get_categories").then(cats => renderCats(cats.categories));
        getJSON("bizbooking_api.search_services", { limit: 200 }).then(res => {
            const services = (res && res.services) || [];
            const catMap = {};
            if (window.__bsCats) catMap = window.__bsCats;
            allListings = services.map(s => Object.assign({}, s, {
                category_name: (catMap[s.category] || ""),
                images: s.images || []
            }));
            render();
            const stats = el("bs-total-services");
            if (stats) stats.textContent = allListings.length;
        });

        // category names for display
        getJSON("bizservice_api.get_categories").then(cats => {
            window.__bsCats = {};
            (cats.categories || []).forEach(c => window.__bsCats[c.name] = c.category_name);
            allListings = allListings.map(s => Object.assign({}, s, { category_name: window.__bsCats[s.category] || s.category }));
            render();
        });

        const modal = el("bs-modal");
        if (modal) {
            el("bs-close-modal").addEventListener("click", closeBooking);
            modal.addEventListener("click", e => { if (e.target === modal) closeBooking(); });
            el("bs-submit").addEventListener("click", submitBooking);

            const prov = el("bs-provider");
            const dateIn = el("bs-date");
            const refresh = () => {
                const sid = el("bs-book-service").value;
                if (sid) loadAvailability(sid, prov ? prov.value || undefined : undefined);
            };
            if (prov) prov.addEventListener("change", refresh);
            if (dateIn) dateIn.addEventListener("change", refresh);
        }

        window.__openBizServiceBooking = openBooking;
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
})();
