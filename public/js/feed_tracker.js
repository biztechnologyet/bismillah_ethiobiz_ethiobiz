// BISMALLAH AR-RAHMAN AR-RAHIM
// EthioBiz Smart Feed interaction beacon (feed_tracker.js) v1.0.0
//
// IntersectionObserver-based user interaction beacon for the smart feed and
// vertical pages. Tracks views, dwell time, and clicks and fires them at
// bismillah_ethiobiz.smart_feed_api.log_interactions (POST) so that
// compute_user_preferences() can build per-user affinity vectors.
//
// Defensive: never blocks the UI and never throws. Guests are not tracked.

(function() {
    "use strict";

    var API_URL = "/api/method/bismillah_ethiobiz.smart_feed_api.log_interactions";
    var ENABLED = false;

    function currentUser() {
        try {
            if (window.frappe && frappe.session && frappe.session.user) {
                return frappe.session.user;
            }
        } catch (e) {
            return null;
        }
        return null;
    }

    function isGuest(user) {
        return !user || user === "Guest";
    }

    function beacon(payload) {
        if (!ENABLED) return;
        try {
            fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Frappe-CSRF-Token": (window.frappe && frappe.csrf_token) || ""
                },
                body: JSON.stringify({ events: [payload] }),
                credentials: "same-origin"
            }).catch(function() {
                // silently ignore network/availability errors
            });
        } catch (e) {
            // never let tracking break page behavior
        }
    }

    function trackCard(interaction_type, card, dwell_ms) {
        if (!card) return;
        var type = card.getAttribute("data-track-type") || card.getAttribute("data-type") || card.getAttribute("data-vertical") || "feed";
        var id = card.getAttribute("data-track-id") || card.getAttribute("data-id") || card.getAttribute("data-target") || "";
        var category = card.getAttribute("data-track-category") || card.getAttribute("data-category") || "";
        var company = card.getAttribute("data-track-company") || "";

        beacon({
            interaction_type: interaction_type,
            content_type: String(type).slice(0, 60),
            content_id: String(id).slice(0, 140),
            content_category: String(category).slice(0, 140),
            content_company: company || null,
            dwell_time_ms: Math.max(0, Math.min(Math.round(dwell_ms || 0), 600000)),
            source_page: window.location.pathname || "home"
        });
    }

    function cardFromElement(el) {
        if (!el) return null;
        var cur = el.closest ? el.closest("[data-track-type], [data-track-id], [data-type], [data-vertical], .stream-card, .vert-card, .bs-card, .shop-card") : el;
        return cur || null;
    }

    function initBeacon() {
        var user = currentUser();
        ENABLED = !isGuest(user);
        if (!ENABLED) return;

        // ---- View / dwell tracking via IntersectionObserver ----
        var dwellMap = {};
        var viewObserver = null;
        try {
            if ("IntersectionObserver" in window) {
                viewObserver = new IntersectionObserver(function(entries) {
                    entries.forEach(function(entry) {
                        var el = entry.target;
                        var key = el.getAttribute("data-track-id") || (el.getAttribute("data-track-type") || "") + "_" + (el.getAttribute("data-track-category") || "") + "_" + el.className;
                        if (entry.isIntersecting) {
                            trackCard("view", el);
                            dwellMap[key] = Date.now();
                        } else if (dwellMap[key]) {
                            var ms = Date.now() - dwellMap[key];
                            if (ms >= 3000) trackCard("dwell", el, ms);
                            delete dwellMap[key];
                        }
                    });
                }, { threshold: 0.4 });
            }
        } catch (e) {
            viewObserver = null;
        }

        function observeCards(root) {
            if (!viewObserver) return;
            var cards = (root || document).querySelectorAll("[data-track-type], [data-track-id], .stream-card, .vert-card, .bs-card, .shop-card");
            Array.prototype.forEach.call(cards, function(card) {
                if (!card.getAttribute("data-beacon-observed")) {
                    card.setAttribute("data-beacon-observed", "1");
                    viewObserver.observe(card);
                }
            });
        }

        observeCards(document);

        // Re-observe cards added later (infinite scroll / vertical filters)
        if (viewObserver && "MutationObserver" in window) {
            try {
                var mo = new MutationObserver(function(muts) {
                    muts.forEach(function(m) {
                        if (m.addedNodes && m.addedNodes.length) observeCards(m.target);
                    });
                });
                (document.getElementById("infinite-stream-container") || document.body) && mo.observe(
                    document.getElementById("infinite-stream-container") || document.body,
                    { childList: true, subtree: true }
                );
            } catch (e) {
                // ignore
            }
        }

        // ---- Click / engagement listeners (document-level delegation) ----
        document.addEventListener("click", function(ev) {
            var el = ev.target && ev.target.closest ? ev.target.closest('a, button, [data-track-action]') : ev.target;
            if (!el) return;
            var action = el.getAttribute("data-track-action") || "";
            var label = action;

            if (el.classList.contains("stream-card-link")
                    || el.classList.contains("btn-reserve")
                    || el.classList.contains("btn-book")
                    || el.classList.contains("bs-btn")
                    || /order|book|reserve|apply|enroll|dispatch|view/i.test(el.textContent || "")) {
                label = "click";
            }
            if (el.classList.contains("like-btn") || action === "like") label = "like";
            if (el.classList.contains("share-btn") || action === "share") label = "share";
            if ((el.classList.contains("cart-add") || action === "cart_add")) label = "cart_add";
            if (label && label !== "click") {
                var card = cardFromElement(el);
                var type = card ? (card.getAttribute("data-track-type") || "feed") : "feed";
                var id = card ? (card.getAttribute("data-track-id") || "") : "";
                beacon({
                    interaction_type: label,
                    content_type: String(type).slice(0, 60),
                    content_id: String(id).slice(0, 140),
                    content_category: card ? String(card.getAttribute("data-track-category") || "").slice(0, 140) : "",
                    content_company: card ? (card.getAttribute("data-track-company") || null) : null,
                    dwell_time_ms: 0,
                    source_page: window.location.pathname || "home"
                });
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initBeacon);
    } else {
        initBeacon();
    }
})();