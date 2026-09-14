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
    const urlParams = new URLSearchParams(window.location.search);
    const deepProvider = urlParams.get("provider") || "";
    const detailSlug = window.BS_PROVIDER || urlParams.get("provider") || "";

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
        const detailUrl = s.detail_url || ("/bizservice/" + slug);
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
            <h3><a href="${detailUrl}" style="color:inherit; text-decoration:none;">${s.service_name}</a></h3>
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
            renderEmpty(grid);
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

        if (detailSlug) {
            loadDetail(detailSlug);
        } else {
            initBrowse();
        }

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

    // ---- Detail view (provider / single listing) ----
    function initBrowse() {
        getJSON("bizservice_api.get_categories").then(cats => {
            renderCats(cats.categories);
            window.__bsCats = {};
            (cats.categories || []).forEach(c => window.__bsCats[c.name] = c.category_name);
        });
        getJSON("bizbooking_api.search_services", { limit: 200 }).then(res => {
            const services = (res && res.services) || [];
            const catMap = window.__bsCats || {};
            allListings = services.map(s => Object.assign({}, s, {
                detail_url: "/bizservice/" + (s.slug || s.name),
                category_name: (catMap[s.category] || ""),
                images: s.images || []
            }));
            render();
            const stats = el("bs-total-services");
            if (stats) stats.textContent = allListings.length;
        }).then(() => {
            // Deep-link: ?provider=<listing name> auto-opens that listing's booking
            if (deepProvider) {
                const match = allListings.find(l => l.name === deepProvider || (l.slug && l.slug === deepProvider));
                if (match) { window.__openBizServiceBooking(match.name); return; }
                const providerMatch = allListings.find(l =>
                    (l.practitioners || []).some(p => (p.name || "") === deepProvider || (p.practitioner_name || "") === deepProvider)
                );
                if (providerMatch) window.__openBizServiceBooking(providerMatch.name);
            }
        });
    }

    function renderEmpty(grid) {
        grid.innerHTML =
            '<div class="bs-empty" style="padding:48px 20px; text-align:center;">' +
                '<div style="font-size:2.8rem; margin-bottom:10px;">🧰</div>' +
                '<h3 style="margin:0 0 6px; color:#0f172a; font-weight:800;">No services listed yet</h3>' +
                '<p style="margin:0 0 14px; color:#64748b; font-size:0.9rem;">Providers are joining every week. Check back soon — or join EthioBiz as a provider today.</p>' +
                '<a class="bs-btn" href="/bizservice" style="text-decoration:none; display:inline-block; margin-right:6px;">Browse all services</a>' +
                '<a class="bs-btn" href="/dobiz-signup" style="text-decoration:none; display:inline-block; background:#0d9488;">List your business</a>' +
            '</div>';
    }

    function renderProviderHeader(detail) {
        const wrap = el("bs-provider-header");
        if (!wrap) return;
        const provider = detail.provider || {};
        const rs = detail.rating_summary || {};
        const logo = provider.company_logo
            ? '<img src="' + provider.company_logo + '" style="width:72px;height:72px;border-radius:16px;object-fit:cover;" alt="">'
            : '<div class="bs-provider-initial">' + (provider.company_name || "P").trim().charAt(0) + "</div>";
        const loc = (provider.location_address || provider.city || "").trim();
        const ratingLine = rs.review_count
            ? "&#9733; " + Number(rs.average_rating || 0).toFixed(1) + " (" + rs.review_count + " reviews)"
            : "No reviews yet";
        const sub = el("bs-detail-subhead");
        if (sub) sub.textContent = "Services by " + (provider.company_name || "this provider");
        wrap.innerHTML =
            '<div class="bs-provider-hero">' +
                logo +
                '<div class="bs-provider-info">' +
                    '<h1>' + (provider.company_name || "Service Provider") + "</h1>" +
                    (loc ? '<div class="bs-card-meta">' + "&#128205; " + loc + "</div>" : "") +
                    '<div class="bs-card-meta">' + ratingLine + " &nbsp; &bull; &nbsp; " + detail.total + " services</div>" +
                '</div>' +
                '<a class="bs-btn" href="/bizservice" style="text-decoration:none; margin-left:auto; align-self:center;">&#8592; All Services</a>' +
            "</div>";
    }

    function renderProviderReviews(detail) {
        const listWrap = el("bs-reviews-list");
        const actionWrap = el("bs-review-action");
        if (!listWrap || !actionWrap) return;

        const reviews = detail.reviews || [];
        if (reviews.length) {
            listWrap.innerHTML = reviews.map(r =>
                '<div class="bs-review-item">' +
                    '<div class="bs-card-meta">&#9733; ' + Number(r.rating || 0).toFixed(1) +
                    ' &nbsp;&nbsp; <b>' + (r.customer_name || "Customer") + "</b>&nbsp;&nbsp; " + (r.booking_date || "") + "</div>" +
                    "<div>" + (r.review || "") + "</div>" +
                "</div>").join("");
        } else {
            listWrap.innerHTML = '<div class="bs-empty">No reviews yet — be the first to review this provider after a completed booking.</div>';
        }

        if (!detail.is_logged_in) {
            actionWrap.innerHTML =
                '<div class="bs-review-gate" style="margin-top:12px; padding:14px; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:12px; color:#475569; font-size:0.9rem;">' +
                    "Sign in to write a review after your booking is completed. " +
                    '<a href="/login?redirect-to=' + encodeURIComponent(window.location.pathname) + '" style="font-weight:700; color:#0d9488;">Log in here &#8594;</a>' +
                "</div>";
            return;
        }

        actionWrap.innerHTML =
            '<div style="margin-top:14px;">' +
                '<button type="button" class="bs-btn" id="bs-review-btn">&#9733; Review a completed booking</button>' +
                '<div id="bs-review-form" style="display:none; margin-top:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px;"></div>' +
            "</div>";

        const btn = el("bs-review-btn");
        const form = el("bs-review-form");
        if (!btn || !form) return;
        btn.addEventListener("click", function () {
            form.style.display = "block";
            if (form.dataset.loaded) return;
            form.dataset.loaded = "1";
            form.innerHTML = "Loading your completed bookings…";
            const providerName = (detail.provider && detail.provider.name) || "";
            getJSON("bizservice_api.get_my_provider_bookings", { company: providerName }).then(res => {
                const eligible = (res && res.review_eligible) || [];
                if (!eligible.length) {
                    form.innerHTML = '<div style="color:#64748b; font-size:0.9rem;">You have no completed bookings for this provider yet. Bookings can be reviewed only after they are Completed.</div>';
                    return;
                }
                form.innerHTML =
                    '<label style="font-weight:700; font-size:0.85rem;">Completed booking to review</label>' +
                    '<select id="bs-review-booking" style="width:100%; padding:8px; border-radius:8px; border:1px solid #cbd5e1; margin:6px 0 10px;">' +
                        eligible.map(b => '<option value="' + b.name + '">' + (b.booking_date || "") + " &bull; " + (b.service_name || b.service || "") + "</option>").join("") +
                    "</select>" +
                    '<label style="font-weight:700; font-size:0.85rem;">Rating (1–5)</label>' +
                    '<select id="bs-review-rating" style="width:100%; padding:8px; border-radius:8px; border:1px solid #cbd5e1; margin:6px 0 10px;">' +
                        "<option value='5'>&#9733;&#9733;&#9733;&#9733;&#9733; Excellent</option>" +
                        "<option value='4'>&#9733;&#9733;&#9733;&#9733; Good</option>" +
                        "<option value='3'>&#9733;&#9733;&#9733; Average</option>" +
                        "<option value='2'>&#9733;&#9733; Poor</option>" +
                        "<option value='1'>&#9733; Terrible</option>" +
                    "</select>" +
                    '<label style="font-weight:700; font-size:0.85rem;">Your review</label>' +
                    '<textarea id="bs-review-text" rows="3" style="width:100%; padding:8px; border-radius:8px; border:1px solid #cbd5e1; margin:6px 0 10px;" placeholder="How was your experience?"></textarea>' +
                    '<button type="button" class="bs-btn" id="bs-review-submit" style="width:100%;">Submit review</button>' +
                    '<div id="bs-review-msg" style="margin-top:8px; font-size:0.85rem; color:#0d9488; font-weight:700;"></div>';

                el("bs-review-submit").addEventListener("click", function () {
                    const payload = {
                        booking: el("bs-review-booking").value,
                        rating: el("bs-review-rating").value,
                        review: el("bs-review-text").value.trim()
                    };
                    fetch(API + "bizservice_api.submit_review", {
                        method: "POST",
                        headers: { "X-Frappe-CSRF-Token": window.csrf_token || "", "Content-Type": "application/x-www-form-urlencoded" },
                        body: new URLSearchParams(payload)
                    }).then(function (r) { return r.json(); }).then(function (res) {
                        const msg = (res && res.message) || {};
                        el("bs-review-msg").textContent = (msg.status === "success") ? "Review submitted. Thank you!" : ("Could not submit: " + (msg.message || "review is gated to Completed bookings"));
                        if (msg.status === "success") { form.dataset.loaded = ""; loadDetail(detailSlug || ""); }
                    }).catch(function () {
                        el("bs-review-msg").textContent = "Could not reach the review service.";
                    });
                });
            }).catch(function () {
                form.innerHTML = '<div style="color:#b91c1c; font-size:0.9rem;">Could not load your bookings.</div>';
            });
        });
    }

    let detailAutoOpened = false;

    function loadDetail(slug) {
        if (!slug) { initBrowse(); return; }
        getJSON("bizservice_api.get_categories").then(cats => {
            window.__bsCats = {};
            (cats.categories || []).forEach(c => window.__bsCats[c.name] = c.category_name);
        });
        getJSON("bizservice_api.get_provider_detail", { provider: slug, listing: slug }).then(detail => {
            if (!detail || !(detail.listings || detail.provider)) { initBrowse(); return; }
            window.__BS_DETAIL = detail;
            renderProviderHeader(detail);
            const catMap = window.__bsCats || {};
            allListings = (detail.listings || []).map(s => Object.assign({}, s, {
                detail_url: "/bizservice/" + (s.slug || s.name),
                category_name: catMap[s.category] || s.category || "",
                images: []
            }));
            render();
            const stats = el("bs-total-services");
            if (stats) stats.textContent = allListings.length;
            renderProviderReviews(detail);
            // Single-service deep link: auto-open its booking modal (once per load)
            if (allListings.length === 1 && !detailAutoOpened) {
                detailAutoOpened = true;
                window.__openBizServiceBooking(allListings[0].name);
            }
        }).catch(() => initBrowse());
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
})();
