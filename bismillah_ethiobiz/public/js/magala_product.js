/* ==========================================================================
   BISMALLAH ETHIOBIZ — DIKKA SHOP PRODUCT DETAIL JS (V1)
   Progressive enhancement for /product/<item_code>. Reuses window.MagalaCart
   from magala_checkout.js so cart state stays identical to /shop and /cart.
   ========================================================================== */
(function () {
    "use strict";

    var PRODUCT = window.MGS_PRODUCT || {};
    var root = document.getElementById("page-product");
    if (!root) return;

    var API = {
        add: "/api/method/bismillah_ethiobiz.magala_checkout.add_to_cart",
        qty: "/api/method/bismillah_ethiobiz.magala_checkout.update_cart_qty",
        cart: "/api/method/bismillah_ethiobiz.magala_checkout.get_cart",
    };

    var PLACEHOLDER_RE = /(walta_real_logo|placeholder|default[-_]?avatar|no[-_]?image)/i;

    function $(sel, scope) {
        return (scope || document).querySelector(sel);
    }

    function $all(sel, scope) {
        return Array.prototype.slice.call((scope || document).querySelectorAll(sel));
    }

    function escapeHtml(value) {
        if (value === null || value === undefined) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function formatMoney(value, currency) {
        var n = Number(value || 0);
        try {
            return new Intl.NumberFormat("en-ET", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }).format(n) + " " + (currency || "ETB");
        } catch (e) {
            return n.toFixed(2) + " " + (currency || "ETB");
        }
    }

    function csrf() {
        if (window.frappe && frappe.csrf_token) return frappe.csrf_token;
        var m = document.cookie.match(/csrf_token=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : "";
    }

    function showToast(html) {
        var el = document.getElementById("mgs-toast");
        if (!el) return;
        el.innerHTML = html;
        el.classList.add("is-visible");
        clearTimeout(showToast._t);
        showToast._t = setTimeout(function () {
            el.classList.remove("is-visible");
        }, 4200);
    }

    function cleanError(error) {
        var raw = error && error.message ? String(error.message) : t("Something went wrong.", "Something went wrong.");
        return raw.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 240);
    }

    /* Bilingual helpers: static copy is translated by ethiobiz_i18n.js, while
       dynamic labels are rebuilt here so a language switch re-renders cleanly. */
    function currentLang() {
        try {
            if (window.EthioBizI18n && typeof window.EthioBizI18n.getLanguage === "function") {
                return window.EthioBizI18n.getLanguage() || "en";
            }
            return localStorage.getItem("ethiobiz_lang") || "en";
        } catch (e) {
            return "en";
        }
    }

    function t(key, fallback) {
        try {
            if (window.EthioBizI18n && typeof window.EthioBizI18n.t === "function") {
                var out = window.EthioBizI18n.t(key);
                if (out && out !== key) return out;
            }
        } catch (e) { /* ignore */ }
        return fallback === undefined ? key : fallback;
    }

    function tpl(key, vars, fallback) {
        var out = t(key, fallback === undefined ? key : fallback);
        Object.keys(vars || {}).forEach(function (name) {
            out = out.split("{" + name + "}").join(String(vars[name]));
        });
        return out;
    }

    function categoryIcon(group) {
        var g = String(group || "").toLowerCase();
        if (/food|restaurant|cafe|dining/.test(g)) return "🍽";
        if (/health|clinic|pharma|medical/.test(g)) return "⚕";
        if (/electron|phone|computer|tech/.test(g)) return "💻";
        if (/fashion|cloth|shoe|apparel/.test(g)) return "👕";
        if (/home|furniture|decor/.test(g)) return "🛋";
        if (/beauty|cosmetic|care/.test(g)) return "✨";
        if (/hotel|travel|tour/.test(g)) return "🏨";
        if (/educat|school|book/.test(g)) return "📚";
        if (/service|repair|maintenance/.test(g)) return "🛠";
        return "◈";
    }

    /* ----------------------------------------------------------------------
       Quantity
       ---------------------------------------------------------------------- */
    var qtyInput = document.getElementById("mp-qty");
    var MAX_QTY = 99;

    function getQty() {
        var n = parseInt((qtyInput && qtyInput.value) || "1", 10);
        if (!isFinite(n) || n < 1) n = 1;
        if (n > MAX_QTY) n = MAX_QTY;
        if (qtyInput) qtyInput.value = String(n);
        return n;
    }

    function setQty(n) {
        if (!qtyInput) return;
        n = Math.max(1, Math.min(MAX_QTY, parseInt(n, 10) || 1));
        qtyInput.value = String(n);
    }

    var dec = document.getElementById("mp-qty-dec");
    var inc = document.getElementById("mp-qty-inc");
    if (dec) dec.addEventListener("click", function () { setQty(getQty() - 1); });
    if (inc) inc.addEventListener("click", function () { setQty(getQty() + 1); });
    if (qtyInput) {
        qtyInput.addEventListener("change", function () { setQty(qtyInput.value); });
        qtyInput.addEventListener("blur", function () { setQty(qtyInput.value); });
    }

    /* ----------------------------------------------------------------------
       Gallery + lightbox
       ---------------------------------------------------------------------- */
    var mainImage = document.getElementById("mp-main-image");
    var mainWrap = document.getElementById("mp-main-image-wrap");
    var lightbox = document.getElementById("mp-lightbox");
    var lightboxImg = document.getElementById("mp-lightbox-img");

    function setMainImage(src, alt) {
        if (!src) return;
        if (mainImage) {
            mainImage.src = src;
            if (alt) mainImage.alt = alt;
            return;
        }
        // No <img> existed (fallback tile): replace it with a real image.
        if (mainWrap) {
            var fallback = $(".mp-image-fallback", mainWrap);
            if (fallback) {
                var img = document.createElement("img");
                img.id = "mp-main-image";
                img.src = src;
                img.alt = alt || PRODUCT.item_name || "";
                fallback.replaceWith(img);
                mainImage = img;
                var zoom = document.getElementById("mp-zoom-btn");
                if (zoom) zoom.hidden = false;
            }
        }
    }

    $all(".mp-thumb").forEach(function (thumb) {
        thumb.addEventListener("click", function () {
            $all(".mp-thumb").forEach(function (t) {
                t.classList.remove("is-active");
                t.setAttribute("aria-pressed", "false");
            });
            thumb.classList.add("is-active");
            thumb.setAttribute("aria-pressed", "true");
            var img = $("img", thumb);
            setMainImage(thumb.getAttribute("data-image"), img ? img.alt : "");
        });
    });

    function openLightbox() {
        if (!lightbox || !lightboxImg || !mainImage) return;
        lightboxImg.src = mainImage.src;
        lightbox.hidden = false;
        document.body.style.overflow = "hidden";
        var close = document.getElementById("mp-lightbox-close");
        if (close) close.focus();
    }

    function closeLightbox() {
        if (!lightbox) return;
        lightbox.hidden = true;
        document.body.style.overflow = "";
    }

    var zoomBtn = document.getElementById("mp-zoom-btn");
    if (zoomBtn) zoomBtn.addEventListener("click", openLightbox);
    if (mainImage) {
        mainImage.style.cursor = "zoom-in";
        mainImage.addEventListener("click", openLightbox);
    }
    var lightboxClose = document.getElementById("mp-lightbox-close");
    if (lightboxClose) lightboxClose.addEventListener("click", closeLightbox);
    if (lightbox) {
        lightbox.addEventListener("click", function (event) {
            if (event.target === lightbox) closeLightbox();
        });
    }
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") closeLightbox();
    });

    // Graceful image fallback for broken remote assets.
    $all("#page-product img").forEach(function (img) {
        img.addEventListener("error", function () {
            if (img.dataset.mpFailed) return;
            img.dataset.mpFailed = "1";
            img.style.display = "none";
            var holder = img.parentElement;
            if (holder && holder.classList.contains("mp-main-image") && !$(".mp-image-fallback", holder)) {
                var fb = document.createElement("div");
                fb.className = "mp-image-fallback";
                fb.setAttribute("role", "img");
                fb.setAttribute("aria-label", PRODUCT.item_name || t("Product image unavailable", "Product image unavailable"));
                fb.innerHTML = '<span class="mp-fallback-glyph" aria-hidden="true">◈</span><span class="mp-fallback-text">' +
                    escapeHtml(t("Dikka Shop", "Dikka Shop")) + '</span>';
                holder.appendChild(fb);
            }
        });
    });

    /* ----------------------------------------------------------------------
       Tabs
       ---------------------------------------------------------------------- */
    $all(".mp-tab").forEach(function (tab) {
        tab.addEventListener("click", function () {
            var name = tab.getAttribute("data-tab");
            $all(".mp-tab").forEach(function (t) {
                t.classList.remove("is-active");
                t.setAttribute("aria-selected", "false");
            });
            tab.classList.add("is-active");
            tab.setAttribute("aria-selected", "true");
            $all(".mp-panel").forEach(function (panel) {
                var active = panel.id === "mp-panel-" + name;
                panel.classList.toggle("is-active", active);
                panel.hidden = !active;
            });
        });
    });

    /* ----------------------------------------------------------------------
       Cart drawer
       ---------------------------------------------------------------------- */
    function renderShopCartDrawer(cart) {
        cart = cart || { items: [], count: 0, total: 0 };
        var items = Array.isArray(cart.items) ? cart.items : [];
        var count = Number(cart.count || items.reduce(function (sum, item) {
            return sum + Number(item.qty || 0);
        }, 0));
        var currency = cart.currency || "ETB";
        var total = Number(cart.total || 0);

        var drawerCount = document.getElementById("cart-drawer-count");
        var drawerTotal = document.getElementById("cart-drawer-total");
        var drawerItems = document.getElementById("cart-drawer-items");
        if (drawerCount) drawerCount.textContent = String(count);
        if (drawerTotal) drawerTotal.textContent = formatMoney(total, currency);
        if (!drawerItems) return;

        if (!items.length) {
            drawerItems.innerHTML = '<p class="empty-cart-msg">' + escapeHtml(t("Your cart is empty. Explore items to add!", "Your cart is empty. Explore items to add!")) + '</p>';
            return;
        }

        drawerItems.innerHTML = items.map(function (item) {
            var code = escapeHtml(item.item_code || "");
            var name = escapeHtml(item.item_name || item.item_code || t("Item", "Item"));
            var qty = Number(item.qty || 1);
            var amount = Number(item.amount || (Number(item.rate || 0) * qty) || 0);
            var image = item.image && !PLACEHOLDER_RE.test(item.image)
                ? '<img src="' + escapeHtml(item.image) + '" alt="' + name + '" loading="lazy" />'
                : '<span class="mgs-cart-thumb-fallback" aria-hidden="true">' + categoryIcon(item.item_group) + '</span>';
            return '<div class="cart-drawer-card" data-cart-code="' + code + '">' +
                image +
                '<div class="mp-cart-item-main">' +
                '<div class="mp-cart-item-name">' + name + '</div>' +
                '<div class="mp-cart-item-price">' + formatMoney(amount, currency) + '</div>' +
                '<div class="mp-qty-row">' +
                '<button type="button" class="mp-cart-qty-btn" data-cart-action="dec" data-cart-item="' + code + '" aria-label="' + escapeHtml(t("Decrease quantity", "Decrease quantity")) + '">−</button>' +
                '<span class="mgs-qty-value" data-cart-qty>' + qty + '</span>' +
                '<button type="button" class="mp-cart-qty-btn" data-cart-action="inc" data-cart-item="' + code + '" aria-label="' + escapeHtml(t("Increase quantity", "Increase quantity")) + '">+</button>' +
                '<button type="button" class="mp-remove-btn" data-cart-action="remove" data-cart-item="' + code + '">' + escapeHtml(t("Remove", "Remove")) + '</button>' +
                '</div></div></div>';
        }).join("");
    }

    window.renderShopCartDrawer = renderShopCartDrawer;

    function openDrawer() {
        var drawer = document.getElementById("magala-cart-drawer");
        if (!drawer) return;
        drawer.classList.add("open");
        drawer.setAttribute("aria-hidden", "false");
        document.body.classList.add("magala-cart-open");
        var backdrop = document.getElementById("cart-drawer-backdrop");
        if (backdrop) {
            backdrop.classList.add("open");
            backdrop.setAttribute("aria-hidden", "false");
        }
    }

    function closeDrawer() {
        var drawer = document.getElementById("magala-cart-drawer");
        if (!drawer) return;
        drawer.classList.remove("open");
        drawer.setAttribute("aria-hidden", "true");
        document.body.classList.remove("magala-cart-open");
        var backdrop = document.getElementById("cart-drawer-backdrop");
        if (backdrop) {
            backdrop.classList.remove("open");
            backdrop.setAttribute("aria-hidden", "true");
        }
    }

    var closeCartBtn = document.getElementById("close-cart-drawer");
    if (closeCartBtn) closeCartBtn.addEventListener("click", closeDrawer);
    var cartBackdrop = document.getElementById("cart-drawer-backdrop");
    if (cartBackdrop) cartBackdrop.addEventListener("click", closeDrawer);

    var drawerItemsEl = document.getElementById("cart-drawer-items");
    if (drawerItemsEl) {
        drawerItemsEl.addEventListener("click", function (event) {
            var btn = event.target.closest("[data-cart-action]");
            if (!btn) return;
            event.preventDefault();
            var code = btn.getAttribute("data-cart-item");
            var action = btn.getAttribute("data-cart-action");
            if (!code) return;
            if (!window.MagalaCart) return;
            if (action === "remove") {
                window.MagalaCart.remove(code);
                return;
            }
            var qtyEl = btn.parentElement.querySelector("[data-cart-qty]");
            var current = parseInt(qtyEl ? qtyEl.textContent : "1", 10) || 1;
            window.MagalaCart.updateQty(code, action === "inc" ? current + 1 : current - 1);
        });
    }

    /* ----------------------------------------------------------------------
       Add to cart / buy now
       ---------------------------------------------------------------------- */
    function fallbackPost(url, data) {
        return fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Frappe-CSRF-Token": csrf(),
            },
            body: new URLSearchParams(data || {}),
        }).then(function (r) { return r.json(); }).then(function (j) {
            if (j.exc) throw new Error(j.exc);
            return j.message !== undefined ? j.message : j;
        });
    }

    function addToCart(button, redirect) {
        var code = (button && button.getAttribute("data-item-code")) || PRODUCT.item_code;
        if (!code) return;
        var qty = getQty();
        if (button) {
            button.disabled = true;
            button.dataset.mpOriginal = button.innerHTML;
            button.innerHTML = escapeHtml(t("Adding…", "Adding…"));
        }

        var promise;
        if (window.MagalaCart && typeof window.MagalaCart.add === "function") {
            promise = window.MagalaCart.add(code, qty);
        } else {
            promise = fallbackPost(API.add, { item_code: code, qty: qty }).then(function (cart) {
                renderShopCartDrawer(cart);
                openDrawer();
                showToast(t('Added to cart. <a href="/cart">Checkout →</a>', 'Added to cart. <a href="/cart">Checkout →</a>'));
                return cart;
            });
        }

        return Promise.resolve(promise).then(function () {
            if (redirect) {
                window.location.href = "/cart";
            }
        }).catch(function (error) {
            var msg = cleanError(error);
            if (/log in|login required|not permitted/i.test(msg)) {
                window.location.href = "/login?redirect-to=" + encodeURIComponent(window.location.pathname + window.location.search);
                return;
            }
            showToast(escapeHtml(msg || t("Could not add to cart.", "Could not add to cart.")));
        }).finally(function () {
            if (button) {
                button.disabled = false;
                if (button.dataset.mpOriginal) button.innerHTML = button.dataset.mpOriginal;
            }
        });
    }

    var addBtn = document.getElementById("mp-add-to-cart");
    var buyBtn = document.getElementById("mp-buy-now");
    var stickyAdd = document.getElementById("mp-sticky-add");
    if (addBtn) addBtn.addEventListener("click", function () { addToCart(addBtn, false); });
    if (buyBtn) buyBtn.addEventListener("click", function () { addToCart(buyBtn, true); });
    if (stickyAdd) stickyAdd.addEventListener("click", function () { addToCart(stickyAdd, false); });

    /* ----------------------------------------------------------------------
       Share
       ---------------------------------------------------------------------- */
    var shareBtn = document.getElementById("mp-share-btn");
    if (shareBtn) {
        shareBtn.addEventListener("click", function () {
            var url = window.location.href;
            var data = { title: PRODUCT.share_title || document.title, text: PRODUCT.item_name || "", url: url };
            if (navigator.share) {
                navigator.share(data).catch(function () {});
                return;
            }
            var copy = function () {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(url).then(function () {
                        showToast(t("Link copied to clipboard.", "Link copied to clipboard."));
                    }).catch(function () { showToast(escapeHtml(url)); });
                } else {
                    showToast(escapeHtml(url));
                }
            };
            copy();
        });
    }

    /* ----------------------------------------------------------------------
       Tab links (rating summary, offer ribbon, review hash)
       ---------------------------------------------------------------------- */
    function activateTab(name) {
        var tab = document.querySelector('.mp-tab[data-tab="' + name + '"]');
        if (tab) tab.click();
        var panel = document.getElementById("mp-panel-" + name);
        if (panel) {
            setTimeout(function () {
                panel.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 60);
        }
    }

    $all("[data-mp-tab-link]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            activateTab(btn.getAttribute("data-mp-tab-link"));
        });
    });
    $all("[data-mp-reviews-link]").forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            activateTab("reviews");
        });
    });
    if (location.hash === "#mp-reviews" || location.hash === "#reviews") {
        setTimeout(function () { activateTab("reviews"); }, 120);
    }

    /* ----------------------------------------------------------------------
       Reviews: filter, sort, submit, helpful, load more
       ---------------------------------------------------------------------- */
    API.review = "/api/method/bismillah_ethiobiz.magala_shop_api.submit_review";
    API.reviews = "/api/method/bismillah_ethiobiz.magala_shop_api.get_product_reviews";
    API.helpful = "/api/method/bismillah_ethiobiz.magala_shop_api.mark_review_helpful";

    var reviewList = document.getElementById("mp-review-list");
    var reviewForm = document.getElementById("mp-review-form");
    var ratingInput = document.getElementById("mp-review-rating");
    var starButtons = $all(".mp-star-btn");
    var reviewFilter = "all";
    var reviewSort = "newest";
    var reviewPage = 1;
    var canReview = !!window.MGS_CAN_REVIEW;
    var loginUrl = window.MGS_LOGIN_URL || ("/login?redirect-to=" + encodeURIComponent(window.location.pathname + window.location.search));

    function reviewCardHtml(rev) {
        rev = rev || {};
        var rating = Number(rev.rating || 0);
        var initial = (rev.user_name || "C").trim().charAt(0).toUpperCase();
        var avatar = rev.user_image
            ? '<img class="mp-review-avatar-img" src="' + escapeHtml(rev.user_image) + '" alt="" loading="lazy" />'
            : '<span class="mp-review-avatar" aria-hidden="true">' + escapeHtml(initial) + '</span>';
        var verified = Number(rev.verified_purchase || 0)
            ? ' · <em>' + escapeHtml(t("Verified purchase", "Verified purchase")) + '</em>'
            : "";
        var region = rev.reviewer_region ? " · " + escapeHtml(rev.reviewer_region) : "";
        var title = rev.review_title ? "<h4>" + escapeHtml(rev.review_title) + "</h4>" : "";
        var seller = rev.seller_response
            ? '<div class="mp-seller-response"><strong>' + escapeHtml(t("Seller response", "Seller response")) +
                '</strong><p>' + escapeHtml(rev.seller_response) + "</p></div>"
            : "";
        var helpfulDisabled = canReview ? "" : ' disabled title="' + escapeHtml(t("Log in to mark helpful", "Log in to mark helpful")) + '"';
        return '<article class="mp-review" data-rating="' + escapeHtml(rating) +
            '" data-helpful="' + escapeHtml(rev.helpful_count || 0) +
            '" data-creation="' + escapeHtml(rev.creation_iso || rev.creation || "") + '">' +
            '<div class="mp-review-head">' + avatar +
            '<div class="mp-review-person"><strong>' + escapeHtml(rev.user_name || t("Verified customer", "Verified customer")) + "</strong>" +
            '<span class="mp-review-meta">' + escapeHtml(rev.date_label || "") + verified + region + "</span></div>" +
            '<span class="mp-review-stars">★ ' + rating.toFixed(1) + "</span></div>" +
            title +
            '<p class="mp-review-comment">' + escapeHtml(rev.comment || "") + "</p>" +
            seller +
            '<div class="mp-review-foot"><button type="button" class="mp-helpful-btn" data-helpful-review="' +
            escapeHtml(rev.name || "") + '"' + helpfulDisabled + '><span aria-hidden="true">♡</span> ' +
            escapeHtml(t("Helpful", "Helpful")) + ' <span class="mp-helpful-count">' +
            escapeHtml(rev.helpful_count || 0) + "</span></button></div></article>";
    }

    var loadedReviews = (window.MGS_REVIEWS || []).slice();

    function renderReviewList() {
        if (!reviewList || !loadedReviews.length) return;
        reviewList.innerHTML = loadedReviews.map(reviewCardHtml).join("");
        applyReviewView();
    }

    function applyReviewView() {
        if (!reviewList) return;
        var cards = $all(".mp-review", reviewList);
        var visible = cards.filter(function (card) {
            if (reviewFilter === "all") return true;
            return Math.round(Number(card.getAttribute("data-rating") || 0)) === Number(reviewFilter);
        });
        visible.sort(function (a, b) {
            if (reviewSort === "highest" || reviewSort === "lowest") {
                var ar = Number(a.getAttribute("data-rating") || 0);
                var br = Number(b.getAttribute("data-rating") || 0);
                return reviewSort === "highest" ? br - ar : ar - br;
            }
            if (reviewSort === "helpful") {
                return Number(b.getAttribute("data-helpful") || 0) - Number(a.getAttribute("data-helpful") || 0);
            }
            var ac = a.getAttribute("data-creation") || "";
            var bc = b.getAttribute("data-creation") || "";
            return bc.localeCompare(ac);
        });
        cards.forEach(function (card) { card.hidden = true; });
        visible.forEach(function (card) {
            card.hidden = false;
            reviewList.appendChild(card);
        });
        var empty = document.getElementById("mp-review-filter-empty");
        if (empty) empty.hidden = visible.length > 0 || !cards.length;
    }

    $all("[data-review-filter]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            $all("[data-review-filter]").forEach(function (b) { b.classList.remove("is-active"); });
            btn.classList.add("is-active");
            reviewFilter = btn.getAttribute("data-review-filter") || "all";
            applyReviewView();
        });
    });

    var reviewSortSelect = document.getElementById("mp-review-sort");
    if (reviewSortSelect) {
        reviewSortSelect.addEventListener("change", function () {
            reviewSort = reviewSortSelect.value || "newest";
            applyReviewView();
        });
    }

    function setReviewRating(value) {
        if (ratingInput) ratingInput.value = String(value);
        starButtons.forEach(function (btn) {
            var active = Number(btn.getAttribute("data-star") || 0) <= Number(value);
            btn.classList.toggle("is-active", active);
            btn.setAttribute("aria-checked", Number(btn.getAttribute("data-star")) === Number(value) ? "true" : "false");
        });
    }

    starButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            setReviewRating(Number(btn.getAttribute("data-star") || 0));
        });
    });

    function showReviewForm() {
        if (!canReview) {
            window.location.href = loginUrl;
            return;
        }
        if (!reviewForm) return;
        reviewForm.hidden = false;
        reviewForm.scrollIntoView({ behavior: "smooth", block: "center" });
        var firstStar = reviewForm.querySelector(".mp-star-btn");
        if (firstStar) firstStar.focus();
    }

    function hideReviewForm() {
        if (reviewForm) reviewForm.hidden = true;
    }

    ["mp-write-review", "mp-empty-write-review"].forEach(function (id) {
        var btn = document.getElementById(id);
        if (btn && btn.tagName === "BUTTON") {
            btn.addEventListener("click", showReviewForm);
        }
    });
    var reviewCancel = document.getElementById("mp-review-cancel");
    if (reviewCancel) reviewCancel.addEventListener("click", hideReviewForm);

    if (reviewForm) {
        reviewForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (!canReview) {
                window.location.href = loginUrl;
                return;
            }
            var rating = parseInt((ratingInput && ratingInput.value) || "0", 10) || 0;
            if (rating < 1 || rating > 5) {
                showToast(escapeHtml(t("Please choose a rating from 1 to 5 stars.", "Please choose a rating from 1 to 5 stars.")));
                return;
            }
            var titleEl = document.getElementById("mp-review-title");
            var textEl = document.getElementById("mp-review-text");
            var text = textEl ? textEl.value.trim() : "";
            if (text.length < 3) {
                showToast(escapeHtml(t("Please write a short review before publishing.", "Please write a short review before publishing.")));
                if (textEl) textEl.focus();
                return;
            }
            var submit = document.getElementById("mp-review-submit");
            if (submit) {
                submit.disabled = true;
                submit.dataset.mpOriginal = submit.innerHTML;
                submit.innerHTML = escapeHtml(t("Publishing…", "Publishing…"));
            }
            fallbackPost(API.review, {
                item_code: PRODUCT.item_code || "",
                website_item: PRODUCT.website_item || window.MGS_WEBSITE_ITEM || "",
                rating: String(rating),
                review_title: titleEl ? titleEl.value.trim() : "",
                review_text: text,
            }).then(function () {
                showToast(escapeHtml(t("Thank you! Your review has been published.", "Thank you! Your review has been published.")));
                setTimeout(function () {
                    window.location.hash = "mp-reviews";
                    window.location.reload();
                }, 900);
            }).catch(function (error) {
                showToast(escapeHtml(cleanError(error) || t("Could not publish your review.", "Could not publish your review.")));
                if (submit) {
                    submit.disabled = false;
                    if (submit.dataset.mpOriginal) submit.innerHTML = submit.dataset.mpOriginal;
                }
            });
        });
    }

    if (reviewList) {
        reviewList.addEventListener("click", function (event) {
            var btn = event.target.closest("[data-helpful-review]");
            if (!btn || btn.disabled) return;
            var reviewName = btn.getAttribute("data-helpful-review");
            if (!reviewName) return;
            btn.disabled = true;
            fallbackPost(API.helpful, { review_name: reviewName }).then(function (result) {
                var count = result && result.helpful_count !== undefined ? result.helpful_count : null;
                var countEl = btn.querySelector(".mp-helpful-count");
                if (countEl && count !== null) countEl.textContent = String(count);
                btn.classList.add("is-marked");
                showToast(escapeHtml(t("Marked as helpful. Thank you!", "Marked as helpful. Thank you!")));
            }).catch(function (error) {
                btn.disabled = false;
                var msg = cleanError(error);
                if (/log in|login|permission/i.test(msg)) {
                    window.location.href = loginUrl;
                    return;
                }
                showToast(escapeHtml(msg || t("Could not mark this review.", "Could not mark this review.")));
            });
        });
    }

    var reviewMore = document.getElementById("mp-review-more");
    if (reviewMore) {
        reviewMore.addEventListener("click", function () {
            reviewMore.disabled = true;
            reviewMore.textContent = t("Loading…", "Loading…");
            var params = new URLSearchParams({
                item_code: PRODUCT.item_code || "",
                website_item: PRODUCT.website_item || window.MGS_WEBSITE_ITEM || "",
                page: String(reviewPage + 1),
                limit: "12",
                sort_by: reviewSort,
            });
            fetch(API.reviews + "?" + params.toString(), { credentials: "same-origin" })
                .then(function (response) { return response.json(); })
                .then(function (json) {
                    var data = json.message || {};
                    var reviews = data.reviews || [];
                    if (reviewList && reviews.length) {
                        loadedReviews = loadedReviews.concat(reviews);
                        reviewList.insertAdjacentHTML("beforeend", reviews.map(reviewCardHtml).join(""));
                    }
                    reviewPage += 1;
                    applyReviewView();
                    if (data.has_more) {
                        reviewMore.disabled = false;
                        reviewMore.textContent = t("Load more reviews", "Load more reviews");
                    } else {
                        reviewMore.remove();
                    }
                })
                .catch(function (error) {
                    reviewMore.disabled = false;
                    reviewMore.textContent = t("Load more reviews", "Load more reviews");
                    showToast(escapeHtml(cleanError(error) || t("Could not load more reviews.", "Could not load more reviews.")));
                });
        });
    }

    /* ----------------------------------------------------------------------
       Sticky mobile buy bar
       ---------------------------------------------------------------------- */
    var sticky = document.getElementById("mp-sticky-buy");
    var buyBox = $(".mp-buy-box");
    if (sticky && buyBox) {
        // A scroll handler (not IntersectionObserver) is used here because the
        // buy box can be skipped past in a single jump — anchor links, keyboard
        // End/PageDown, or a restored scroll position — in which case the
        // intersection state never changes and the bar would stay hidden.
        var stickyTicking = false;
        var updateSticky = function () {
            stickyTicking = false;
            var rect = buyBox.getBoundingClientRect();
            var visible = rect.bottom < 0;
            sticky.classList.toggle("is-visible", visible);
            sticky.setAttribute("aria-hidden", visible ? "false" : "true");
        };
        var requestSticky = function () {
            if (stickyTicking) return;
            stickyTicking = true;
            if (window.requestAnimationFrame) window.requestAnimationFrame(updateSticky);
            else window.setTimeout(updateSticky, 16);
        };
        window.addEventListener("scroll", requestSticky, { passive: true });
        window.addEventListener("resize", requestSticky);
        updateSticky();
    }

    /* ----------------------------------------------------------------------
       Hydrate cart badge/drawer
       ---------------------------------------------------------------------- */
    if (window.MagalaCart && typeof window.MagalaCart.refresh === "function") {
        window.MagalaCart.refresh();
    }

    /* ----------------------------------------------------------------------
       Language switch: rebuild dynamic labels and review cards
       ---------------------------------------------------------------------- */
    window.addEventListener("ethiobiz-lang-changed", function () {
        renderReviewList();
        var moreBtn = document.getElementById("mp-review-more");
        if (moreBtn) moreBtn.textContent = t("Load more reviews", "Load more reviews");
        if (window.MagalaCart && typeof window.MagalaCart.refresh === "function") {
            window.MagalaCart.refresh();
        }
    });
})();
