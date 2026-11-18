/* ============================================================
   BISMALLAH ETHIOBIZ — MAGALA MARKETPLACE V3 ENGINE
   Search, dynamic categories, filters, grid/list/map views,
   cart drawer, mobile filter sheet and accessibility helpers.
   Scoped to #page-shop; does not touch ERPNext records.
   ============================================================ */
(function () {
    "use strict";

    const API = {
        search: "/api/method/bismillah_ethiobiz.magala_shop_api.search_products",
        categories: "/api/method/bismillah_ethiobiz.magala_shop_api.get_categories",
        map: "/api/method/bismillah_ethiobiz.magala_shop_api.get_companies_map",
        cart: "/api/method/bismillah_ethiobiz.magala_checkout.get_cart",
        add: "/api/method/bismillah_ethiobiz.magala_checkout.add_to_cart",
        qty: "/api/method/bismillah_ethiobiz.magala_checkout.update_cart_qty"
    };

    const FALLBACK_IMG = "/assets/bismillah_ethiobiz/img/walta_real_logo.png";
    const PLACEHOLDER_RE = /(default-avatar|placeholder|no[-_]?image|walta_real_logo|empty-image)/i;
    const TEST_CATEGORY_RE = /^(RM|FG|Packing)\s+\d+/i;
    const PAGE_SIZE = 24;

    const FALLBACK_CATEGORIES = [
        { name: "Products", label: "Products", count: null },
        { name: "Food & Dining", label: "Food & Dining", count: null },
        { name: "Healthcare & Medical", label: "Healthcare", count: null },
        { name: "Courses & Education", label: "Education", count: null },
        { name: "Salon & Beauty", label: "Salon & Beauty", count: null },
        { name: "Hotel & Hospitality", label: "Hotels", count: null },
        { name: "Consumables", label: "Consumables", count: null },
        { name: "Software & SaaS", label: "Software", count: null }
    ];

    const state = {
        view: "grid",
        category: "all",
        page: 1,
        query: "",
        sort: "relevance",
        minPrice: "",
        maxPrice: "",
        rating: "",
        company: "",
        items: [],
        total: 0,
        totalPages: 1,
        loading: false,
        requestSeq: 0,
        categories: [],
        categoriesReady: false,
        lastResponse: null,
        userLat: null,
        userLng: null,
        lastFocused: null,
        map: {
            instance: null,
            cluster: null,
            companies: [],
            loaded: false,
            loading: false,
            retry: 0,
            status: null
        }
    };

    const els = {};
    let searchTimer = null;
    let toastTimer = null;

    /* ---------------------------------------------------------
       Bilingual helpers
       Static copy is translated by ethiobiz_i18n.js (exact-match
       dictionary). Number-bearing labels are rebuilt here through
       the same dictionary so a language switch re-renders cleanly.
       --------------------------------------------------------- */
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
                const out = window.EthioBizI18n.t(key);
                if (out && out !== key) return out;
            }
        } catch (e) { /* ignore */ }
        return fallback === undefined ? key : fallback;
    }

    function tpl(key, vars, fallback) {
        let out = t(key, fallback === undefined ? key : fallback);
        Object.keys(vars || {}).forEach(function (name) {
            out = out.split("{" + name + "}").join(String(vars[name]));
        });
        return out;
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    function init() {
        cacheElements();
        if (!els.root) return;
        readUrlState();
        bindSearch();
        bindFilters();
        bindView();
        bindItems();
        bindPagination();
        bindCart();
        bindSticky();
        restoreSidebarState();
        applyView(false);
        loadCategories();
        loadProducts();
        refreshCart();
        if (state.view === "map") {
            setTimeout(function () { initMap(false); }, 260);
        }
        window.addEventListener("ethiobiz-lang-changed", onLanguageChange);
        console.log("[Magala Shop] V3 engine ready");
    }

    function onLanguageChange() {
        updateCategoryStatus();
        updateFilterToggleText();
        renderCategoryRail();
        renderCategoryFilters();
        renderResultsSummary();
        renderActiveFilters();
        renderItems();
        renderPagination();
        updateStoreBanner(state.company);
        refreshMapStatus();
        if (window.MagalaCart && typeof window.MagalaCart.refresh === "function") {
            window.MagalaCart.refresh().catch(function () { /* guest cart may be empty */ });
        }
    }

    /* ---------------------------------------------------------
       Boot / helpers
       --------------------------------------------------------- */
    function cacheElements() {
        els.root = document.getElementById("mgs-shop");
        if (!els.root) return;
        els.searchForm = document.getElementById("mgs-search-form");
        els.searchInput = document.getElementById("magala-search-input");
        els.clearSearch = document.getElementById("magala-clear-search");
        els.typeahead = document.getElementById("magala-typeahead-dropdown");
        els.nearMe = document.getElementById("btn-near-me");
        els.heroPanel = document.querySelector("#page-shop .mgs-hero-panel");
        els.categoryBar = document.getElementById("mgs-category-bar");
        els.categoryStatus = document.getElementById("mgs-category-status");
        els.categoryFilters = document.getElementById("mgs-category-filters");
        els.layout = document.getElementById("mgs-layout");
        els.sidebar = document.getElementById("mgs-filter-panel");
        els.filterTop = document.querySelector("#page-shop .mgs-filter-top");
        els.filterBackdrop = document.getElementById("mgs-filter-backdrop");
        els.filterToggle = document.getElementById("btn-toggle-filters");
        els.filterToggleText = document.getElementById("toggle-filter-text");
        els.closeFilters = document.getElementById("mgs-close-filters");
        els.applyFilters = document.getElementById("mgs-apply-filters");
        els.resetFilters = document.getElementById("btn-reset-filters");
        els.minPrice = document.getElementById("filter-min-price");
        els.maxPrice = document.getElementById("filter-max-price");
        els.sort = document.getElementById("filter-sort-by");
        els.items = document.getElementById("magala-items-container");
        els.results = document.getElementById("results-count-text");
        els.resultsSub = document.getElementById("mgs-results-sub");
        els.toolbar = document.getElementById("mgs-toolbar");
        els.pagination = document.getElementById("magala-pagination");
        els.activeFilters = document.getElementById("mgs-active-filters");
        els.storeBanner = document.getElementById("mgs-store-banner");
        els.storeName = document.getElementById("mgs-store-name");
        els.clearStore = document.getElementById("mgs-clear-store");
        els.mapWrap = document.getElementById("magala-embedded-map-container");
        els.mapContainer = document.getElementById("magala-split-map");
        els.mapStatus = document.getElementById("magala-map-status");
        els.mapFit = document.getElementById("btn-magala-map-fit");
        els.cartButton = document.getElementById("mgs-cart-button");
        els.cartCount = document.getElementById("mgs-cart-count");
        els.drawer = document.getElementById("magala-cart-drawer");
        els.drawerCount = document.getElementById("cart-drawer-count");
        els.drawerItems = document.getElementById("cart-drawer-items");
        els.drawerTotal = document.getElementById("cart-drawer-total");
        els.cartBackdrop = document.getElementById("cart-drawer-backdrop");
        els.closeCart = document.getElementById("close-cart-drawer");
        els.toast = document.getElementById("mgs-toast");
        els.openHadeeda = document.getElementById("mgs-open-hadeeda");
        els.ratingRadios = document.querySelectorAll('input[name="rating_filter"]');
        els.viewButtons = document.querySelectorAll("#page-shop .view-btn");
    }

    function readUrlState() {
        let params;
        try {
            params = new URLSearchParams(window.location.search);
        } catch (e) {
            params = new URLSearchParams("");
        }
        const storedView = localStorage.getItem("magala_view_mode");
        if (["grid", "list", "map"].indexOf(storedView) >= 0) state.view = storedView;
        const urlView = params.get("view");
        if (["grid", "list", "map"].indexOf(urlView) >= 0) state.view = urlView;

        state.query = params.get("q") || params.get("query") || "";
        state.category = params.get("category") || "all";
        state.sort = params.get("sort") || "relevance";
        state.minPrice = params.get("min") || "";
        state.maxPrice = params.get("max") || "";
        state.rating = params.get("rating") || "";
        state.company = params.get("company") || "";
        const page = parseInt(params.get("page") || "1", 10);
        state.page = isFinite(page) && page > 0 ? page : 1;

        if (els.searchInput) els.searchInput.value = state.query;
        if (els.clearSearch) els.clearSearch.hidden = !state.query;
        if (els.minPrice) els.minPrice.value = state.minPrice;
        if (els.maxPrice) els.maxPrice.value = state.maxPrice;
        if (els.sort) els.sort.value = state.sort;
        els.ratingRadios.forEach(function (radio) {
            radio.checked = String(radio.value) === String(state.rating || "");
        });
        if (state.company) updateStoreBanner(state.company);
    }

    function parseJson(res) {
        if (!res.ok) throw new Error("Request failed (" + res.status + ")");
        return res.json().then(function (payload) {
            if (payload && payload.exc) throw new Error(cleanError(payload._server_messages || payload.exc));
            return payload && payload.message !== undefined ? payload.message : payload;
        });
    }

    function cleanError(err) {
        const raw = err && err.message ? String(err.message) : String(err || t("Something went wrong.", "Something went wrong."));
        return raw.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 260);
    }

    function csrf() {
        if (window.frappe && window.frappe.csrf_token) return window.frappe.csrf_token;
        const match = document.cookie.match(/csrf_token=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
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

    function stripHtml(value) {
        return String(value || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    }

    function hashCode(value) {
        let hash = 0;
        const text = String(value || "");
        for (let i = 0; i < text.length; i += 1) {
            hash = ((hash << 5) - hash) + text.charCodeAt(i);
            hash |= 0;
        }
        return Math.abs(hash);
    }

    function formatMoney(amount, currency) {
        const number = Number(amount || 0);
        return number.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }) + " " + (currency || "ETB");
    }

    function categoryIcon(name) {
        const found = state.categories.find(function (item) { return item.name === name; });
        if (found && found.icon) return found.icon;
        const text = String(name || "").toLowerCase();
        if (text.indexOf("food") >= 0 || text.indexOf("restaurant") >= 0 || text.indexOf("dining") >= 0) return "🍽️";
        if (text.indexOf("health") >= 0 || text.indexOf("clinic") >= 0 || text.indexOf("medical") >= 0 || text.indexOf("dental") >= 0) return "🩺";
        if (text.indexOf("education") >= 0 || text.indexOf("course") >= 0 || text.indexOf("school") >= 0 || text.indexOf("learn") >= 0) return "🎓";
        if (text.indexOf("salon") >= 0 || text.indexOf("beauty") >= 0 || text.indexOf("spa") >= 0) return "💅";
        if (text.indexOf("hotel") >= 0 || text.indexOf("hospitality") >= 0 || text.indexOf("pension") >= 0) return "🏨";
        if (text.indexOf("software") >= 0 || text.indexOf("saas") >= 0 || text.indexOf("cloud") >= 0) return "☁️";
        if (text.indexOf("consumable") >= 0 || text.indexOf("supply") >= 0) return "📦";
        if (text.indexOf("product") >= 0 || text.indexOf("retail") >= 0 || text.indexOf("shop") >= 0) return "🛍️";
        return "🏷️";
    }

    function categoryLabel(name) {
        const found = state.categories.find(function (item) { return item.name === name; });
        if (!found) return name;
        if (currentLang() === "am" && found.label_am) return found.label_am;
        return found.label;
    }

    function categoryDisplayLabel(category) {
        if (!category) return "";
        if (currentLang() === "am" && category.label_am) return category.label_am;
        return category.label || category.name;
    }

    function priceHtml(item) {
        const price = Number(item.price || 0);
        if (price > 0) {
            return '<div class="mgs-price">' + escapeHtml(item.formatted_price || formatMoney(price, "ETB")) +
                '<small>' + escapeHtml(t("incl. VAT", "incl. VAT")) + '</small></div>';
        }
        return '<div class="mgs-price mgs-price--request">' + escapeHtml(t("Price on request", "Price on request")) +
            '<small>' + escapeHtml(t("Contact seller", "Contact seller")) + '</small></div>';
    }

    function ratingHtml(item) {
        const reviews = Number(item.total_reviews || 0);
        if (!reviews) {
            return '<span class="mgs-new-pill">' + escapeHtml(t("New arrival", "New arrival")) + '</span>';
        }
        const rating = Number(item.rating || 0);
        return '<span class="mgs-stars" title="' + escapeHtml(tpl("{n} out of 5", { n: rating.toFixed(1) }, rating.toFixed(1) + " out of 5")) + '">★ ' +
            escapeHtml(rating.toFixed(1)) + '</span><span>(' + reviews + ')</span>';
    }

    function thumbHtml(item, context) {
        const group = item.item_group || "Products";
        const icon = categoryIcon(group);
        const tone = "tone-" + (hashCode(group + (item.company || "") + (item.item_code || "")) % 6);
        const image = item.website_image || item.image || "";
        const alt = escapeHtml(item.web_item_name || item.item_name || t("Product image", "Product image"));
        if (!image || PLACEHOLDER_RE.test(image)) {
            return '<div class="mgs-thumb-fallback ' + tone + '">' +
                '<span class="mgs-fallback-icon" aria-hidden="true">' + icon + '</span>' +
                '<span class="mgs-fallback-label">' + escapeHtml(categoryLabel(group)) + '</span></div>';
        }
        const classes = context === "list" ? "mgs-card-img mgs-list-img" : "mgs-card-img";
        return '<img class="' + classes + '" src="' + escapeHtml(image) + '" alt="' + alt +
            '" loading="lazy" decoding="async" data-fallback-tone="' + tone +
            '" data-fallback-icon="' + escapeHtml(icon) +
            '" data-fallback-label="' + escapeHtml(categoryLabel(group)) + '" />';
    }

    function attachImageFallbacks(scope) {
        scope.querySelectorAll("img.mgs-card-img").forEach(function (img) {
            img.addEventListener("error", function () {
                const media = img.closest(".mgs-card-media, .mgs-list-media");
                if (!media) return;
                const fallback = document.createElement("div");
                fallback.className = "mgs-thumb-fallback " + (img.getAttribute("data-fallback-tone") || "tone-0");
                const icon = document.createElement("span");
                icon.className = "mgs-fallback-icon";
                icon.setAttribute("aria-hidden", "true");
                icon.textContent = img.getAttribute("data-fallback-icon") || "🏷️";
                const label = document.createElement("span");
                label.className = "mgs-fallback-label";
                label.textContent = img.getAttribute("data-fallback-label") || t("Product", "Product");
                fallback.appendChild(icon);
                fallback.appendChild(label);
                media.replaceChildren(fallback);
            }, { once: true });
        });
    }

    /* ---------------------------------------------------------
       Categories
       --------------------------------------------------------- */
    function loadCategories() {
        if (!els.categoryBar) return;
        fetch(API.categories, { credentials: "same-origin", headers: { Accept: "application/json" } })
            .then(parseJson)
            .then(function (data) {
                const raw = data && Array.isArray(data.categories) ? data.categories : [];
                state.categories = normalizeCategories(raw);
                state.categoriesReady = true;
                updateCategoryStatus();
                renderCategoryRail();
                renderCategoryFilters();
            })
            .catch(function () {
                state.categories = FALLBACK_CATEGORIES.map(function (category) {
                    return { name: category.name, label: category.label, count: category.count };
                });
                state.categoriesReady = true;
                updateCategoryStatus();
                renderCategoryRail();
                renderCategoryFilters();
            });
    }

    function updateCategoryStatus() {
        if (!els.categoryStatus) return;
        const count = state.categories.length;
        const english = count
            ? count + " categories · updated live"
            : "Browse all categories";
        // The global i18n engine caches each element's original English text in
        // data-i18n-orig and re-applies it on the next translation pass. Without
        // refreshing that cache the status would snap back to "Loading
        // categories." on the Amharic storefront, so always sync both.
        els.categoryStatus.setAttribute("data-i18n-orig", english);
        els.categoryStatus.textContent = count
            ? tpl("{n} categories · updated live", { n: count }, english)
            : t("Browse all categories", english);
    }

    function normalizeCategories(raw) {
        const seen = {};
        return (raw || [])
            .filter(function (category) {
                return category && category.item_group && !TEST_CATEGORY_RE.test(category.item_group) &&
                    !/(test|demo|sample)/i.test(category.item_group);
            })
            .map(function (category) {
                return {
                    name: category.item_group,
                    label: category.item_group_name || category.item_group,
                    label_am: category.label_am || "",
                    icon: category.icon || "",
                    count: Number(category.product_count || 0)
                };
            })
            .filter(function (category) {
                if (category.count <= 0 || seen[category.name]) return false;
                seen[category.name] = true;
                return true;
            })
            .sort(function (a, b) { return b.count - a.count; })
            .slice(0, 14);
    }

    function renderCategoryRail() {
        if (!els.categoryBar) return;
        const categories = state.categories.length ? state.categories : FALLBACK_CATEGORIES;
        const known = categories.some(function (category) { return category.name === state.category; });
        let html = chipHtml("all", t("All products", "All products"), "✨", state.total || null);
        if (state.category !== "all" && !known) {
            html += chipHtml(state.category, state.category, categoryIcon(state.category), null);
        }
        html += categories.map(function (category) {
            return chipHtml(category.name, categoryDisplayLabel(category), category.icon || categoryIcon(category.name), category.count);
        }).join("");
        els.categoryBar.innerHTML = html;
    }

    function chipHtml(value, label, icon, count) {
        const active = String(state.category) === String(value);
        return '<button type="button" class="cat-pill' + (active ? " active" : "") +
            '" data-category="' + escapeHtml(value) + '" role="listitem" aria-pressed="' +
            (active ? "true" : "false") + '">' +
            '<span class="mgs-chip-icon" aria-hidden="true">' + icon + '</span>' +
            '<span class="mgs-chip-label">' + escapeHtml(label) + '</span>' +
            (count ? '<span class="mgs-chip-count">' + escapeHtml(count) + '</span>' : "") +
            '</button>';
    }

    function renderCategoryFilters() {
        if (!els.categoryFilters) return;
        const categories = state.categories.length ? state.categories : FALLBACK_CATEGORIES;
        const known = categories.some(function (category) { return category.name === state.category; });
        let html = '<button type="button" class="mgs-cat-filter' +
            (state.category === "all" ? " active" : "") +
            '" data-category="all"><span>' + escapeHtml(t("All products", "All products")) + '</span><span>' +
            (state.total ? escapeHtml(state.total) : "") + '</span></button>';
        if (state.category !== "all" && !known) {
            html += '<button type="button" class="mgs-cat-filter active" data-category="' +
                escapeHtml(state.category) + '"><span>' + escapeHtml(state.category) +
                '</span><span></span></button>';
        }
        html += categories.map(function (category) {
            const active = String(state.category) === String(category.name);
            return '<button type="button" class="mgs-cat-filter' + (active ? " active" : "") +
                '" data-category="' + escapeHtml(category.name) + '"><span>' +
                escapeHtml(categoryDisplayLabel(category)) + '</span><span>' +
                (category.count ? escapeHtml(category.count) : "") + '</span></button>';
        }).join("");
        els.categoryFilters.innerHTML = html;
    }

    function updateAllCount() {
        if (els.categoryBar) {
            const chip = els.categoryBar.querySelector('.cat-pill[data-category="all"]');
            if (chip) {
                let countEl = chip.querySelector(".mgs-chip-count");
                if (!countEl && state.total) {
                    countEl = document.createElement("span");
                    countEl.className = "mgs-chip-count";
                    chip.appendChild(countEl);
                }
                if (countEl) countEl.textContent = state.total ? String(state.total) : "";
            }
        }
        if (els.categoryFilters) {
            const allFilter = els.categoryFilters.querySelector('.mgs-cat-filter[data-category="all"] span:last-child');
            if (allFilter) allFilter.textContent = state.total ? String(state.total) : "";
        }
    }

    /* ---------------------------------------------------------
       Search & typeahead
       --------------------------------------------------------- */
    function bindSearch() {
        if (els.searchForm) {
            els.searchForm.addEventListener("submit", function (event) {
                event.preventDefault();
                applySearch(true);
            });
        }
        if (els.searchInput) {
            els.searchInput.addEventListener("input", function () {
                if (els.clearSearch) els.clearSearch.hidden = !els.searchInput.value;
                clearTimeout(searchTimer);
                searchTimer = setTimeout(function () {
                    applySearch(false);
                }, 340);
            });
            els.searchInput.addEventListener("focus", function () {
                if (state.lastResponse && state.query) {
                    renderTypeahead(state.lastResponse, state.query);
                }
            });
            els.searchInput.addEventListener("keydown", function (event) {
                if (event.key === "Escape") hideTypeahead();
            });
        }
        if (els.clearSearch) {
            els.clearSearch.addEventListener("click", function () {
                if (els.searchInput) els.searchInput.value = "";
                els.clearSearch.hidden = true;
                state.query = "";
                state.page = 1;
                hideTypeahead();
                loadProducts();
                if (els.searchInput) els.searchInput.focus();
            });
        }
        if (els.typeahead) {
            els.typeahead.addEventListener("click", function (event) {
                const target = event.target.closest("[data-suggest-type]");
                if (!target) return;
                const type = target.getAttribute("data-suggest-type");
                const value = target.getAttribute("data-suggest-value") || "";
                if (type === "product") {
                    window.location.href = target.getAttribute("data-suggest-url") || "/shop";
                } else if (type === "category") {
                    hideTypeahead();
                    setCategory(value);
                } else if (type === "company") {
                    hideTypeahead();
                    setCompany(value);
                }
            });
        }
        document.addEventListener("click", function (event) {
            if (els.heroPanel && !els.heroPanel.contains(event.target) &&
                els.typeahead && !els.typeahead.contains(event.target)) hideTypeahead();
        });
        window.addEventListener("scroll", function () {
            if (els.typeahead && !els.typeahead.hidden) positionTypeahead();
        }, { passive: true });
        window.addEventListener("resize", function () {
            if (els.typeahead && !els.typeahead.hidden) positionTypeahead();
        });
        if (els.nearMe) {
            els.nearMe.addEventListener("click", locateUser);
        }
    }

    function applySearch(immediate) {
        if (!els.searchInput) return;
        const query = els.searchInput.value.trim();
        if (query === state.query && !immediate) return;
        state.query = query;
        state.page = 1;
        hideTypeahead();
        if (immediate) els.searchInput.blur();
        loadProducts();
    }

    function positionTypeahead() {
        if (!els.typeahead || !els.searchForm) return;
        const rect = els.searchForm.getBoundingClientRect();
        const width = Math.min(Math.max(rect.width, 260), window.innerWidth - 24);
        let left = rect.left;
        if (left + width > window.innerWidth - 12) left = window.innerWidth - width - 12;
        els.typeahead.style.left = Math.max(12, left) + "px";
        els.typeahead.style.top = (rect.bottom + 8) + "px";
        els.typeahead.style.width = width + "px";
    }

    function renderTypeahead(data, query) {
        if (!els.typeahead || !query || !data) return;
        const products = Array.isArray(data.items) ? data.items.slice(0, 4) : [];
        const categories = Array.isArray(data.categories_matched) ? data.categories_matched.slice(0, 3) : [];
        const companies = Array.isArray(data.companies_matched) ? data.companies_matched.slice(0, 3) : [];
        if (!products.length && !categories.length && !companies.length) {
            hideTypeahead();
            return;
        }
        let html = "";
        if (products.length) {
            html += '<div class="mgs-typeahead-group-label">' + escapeHtml(t("Products", "Products")) + '</div>';
            html += products.map(function (item) {
                const imageSrc = item.website_image || item.image || "";
                const image = imageSrc && !PLACEHOLDER_RE.test(imageSrc)
                    ? '<img src="' + escapeHtml(imageSrc) + '" alt="" loading="lazy" />'
                    : '<span class="mgs-typeahead-thumb" aria-hidden="true">' + categoryIcon(item.item_group) + '</span>';
                const price = Number(item.price || 0) > 0
                    ? escapeHtml(item.formatted_price || formatMoney(item.price, "ETB"))
                    : t("Price on request", "Price on request");
                return '<button type="button" class="mgs-typeahead-item" data-suggest-type="product" data-suggest-value="' +
                    escapeHtml(item.item_code) + '" data-suggest-url="' + escapeHtml(productDetailUrl(item)) + '">' +
                    image + '<span>' + escapeHtml(item.web_item_name || item.item_name || item.item_code) +
                    '<small>' + escapeHtml(item.company_name || t("Verified seller", "Verified seller")) + ' · ' + price + '</small></span></button>';
            }).join("");
        }
        if (categories.length) {
            html += '<div class="mgs-typeahead-group-label">' + escapeHtml(t("Categories", "Categories")) + '</div>';
            html += categories.map(function (category) {
                return '<button type="button" class="mgs-typeahead-item" data-suggest-type="category" data-suggest-value="' +
                    escapeHtml(category.name) + '"><span class="mgs-typeahead-thumb" aria-hidden="true">' +
                    categoryIcon(category.name) + '</span><span>' + escapeHtml(category.item_group_name || category.name) +
                    '<small>' + escapeHtml(t("Browse category", "Browse category")) + '</small></span></button>';
            }).join("");
        }
        if (companies.length) {
            html += '<div class="mgs-typeahead-group-label">' + escapeHtml(t("Stores", "Stores")) + '</div>';
            html += companies.map(function (company) {
                return '<button type="button" class="mgs-typeahead-item" data-suggest-type="company" data-suggest-value="' +
                    escapeHtml(company.name) + '"><span class="mgs-typeahead-thumb" aria-hidden="true">🏬</span><span>' +
                    escapeHtml(company.company_name || company.name) + '<small>' + escapeHtml(t("View storefront", "View storefront")) + '</small></span></button>';
            }).join("");
        }
        els.typeahead.innerHTML = html;
        positionTypeahead();
        els.typeahead.hidden = false;
    }

    function hideTypeahead() {
        if (!els.typeahead) return;
        els.typeahead.hidden = true;
        els.typeahead.innerHTML = "";
    }

    /* ---------------------------------------------------------
       Filters
       --------------------------------------------------------- */
    function bindFilters() {
        if (els.categoryBar) {
            els.categoryBar.addEventListener("click", function (event) {
                const chip = event.target.closest(".cat-pill");
                if (chip) setCategory(chip.getAttribute("data-category") || "all");
            });
        }
        if (els.categoryFilters) {
            els.categoryFilters.addEventListener("click", function (event) {
                const button = event.target.closest("[data-category]");
                if (button) setCategory(button.getAttribute("data-category") || "all");
            });
        }
        if (els.minPrice) {
            els.minPrice.addEventListener("change", applyPriceFilter);
            els.minPrice.addEventListener("keydown", function (event) {
                if (event.key === "Enter") { event.preventDefault(); applyPriceFilter(); }
            });
        }
        if (els.maxPrice) {
            els.maxPrice.addEventListener("change", applyPriceFilter);
            els.maxPrice.addEventListener("keydown", function (event) {
                if (event.key === "Enter") { event.preventDefault(); applyPriceFilter(); }
            });
        }
        els.ratingRadios.forEach(function (radio) {
            radio.addEventListener("change", function () {
                state.rating = radio.value || "";
                state.page = 1;
                loadProducts();
            });
        });
        if (els.sort) {
            els.sort.addEventListener("change", function () {
                state.sort = els.sort.value || "relevance";
                state.page = 1;
                loadProducts();
            });
        }
        if (els.resetFilters) {
            els.resetFilters.addEventListener("click", resetFilters);
        }
        if (els.filterToggle) {
            els.filterToggle.addEventListener("click", toggleFilters);
        }
        if (els.closeFilters) {
            els.closeFilters.addEventListener("click", function () { closeFilters(false); });
        }
        if (els.applyFilters) {
            els.applyFilters.addEventListener("click", function () { closeFilters(false); });
        }
        if (els.filterBackdrop) {
            els.filterBackdrop.addEventListener("click", function () { closeFilters(false); });
        }
        if (els.clearStore) {
            els.clearStore.addEventListener("click", function () { setCompany(""); });
        }
        if (els.activeFilters) {
            els.activeFilters.addEventListener("click", function (event) {
                const clear = event.target.closest("[data-clear]");
                if (clear) {
                    clearFilter(clear.getAttribute("data-clear"));
                    return;
                }
                if (event.target.closest("[data-clear-all]")) resetFilters();
            });
        }
        if (els.openHadeeda) {
            els.openHadeeda.addEventListener("click", function () {
                if (window.HadeedaChat && typeof window.HadeedaChat.open === "function") {
                    window.HadeedaChat.open();
                } else {
                    window.dispatchEvent(new CustomEvent("ethiobiz:open-chat"));
                    showToast(t("Ask Hadeeda from the home page chat bubble. 🛍️", "Ask Hadeeda from the home page chat bubble. 🛍️"));
                }
            });
        }
        const media = window.matchMedia("(max-width: 1024px)");
        const onChange = function () {
            if (!media.matches) closeFilters(true);
        };
        if (media.addEventListener) media.addEventListener("change", onChange);
        else if (media.addListener) media.addListener(onChange);
    }

    function applyPriceFilter() {
        state.minPrice = els.minPrice && els.minPrice.value !== "" ? String(Math.max(0, Number(els.minPrice.value) || 0)) : "";
        state.maxPrice = els.maxPrice && els.maxPrice.value !== "" ? String(Math.max(0, Number(els.maxPrice.value) || 0)) : "";
        if (state.minPrice && state.maxPrice && Number(state.minPrice) > Number(state.maxPrice)) {
            const swap = state.minPrice;
            state.minPrice = state.maxPrice;
            state.maxPrice = swap;
            if (els.minPrice) els.minPrice.value = state.minPrice;
            if (els.maxPrice) els.maxPrice.value = state.maxPrice;
        }
        state.page = 1;
        loadProducts();
    }

    function setCategory(category) {
        state.category = category || "all";
        state.page = 1;
        renderCategoryRail();
        renderCategoryFilters();
        loadProducts();
    }

    function setCompany(company) {
        state.company = company || "";
        state.page = 1;
        updateStoreBanner(state.company);
        loadProducts();
    }

    function updateStoreBanner(company) {
        if (!els.storeBanner) return;
        if (!company) {
            els.storeBanner.hidden = true;
            if (els.storeName) els.storeName.textContent = t("Verified store", "Verified store");
            return;
        }
        els.storeBanner.hidden = false;
        if (els.storeName) els.storeName.textContent = company;
    }

    function clearFilter(key) {
        if (key === "query") {
            state.query = "";
            if (els.searchInput) els.searchInput.value = "";
            if (els.clearSearch) els.clearSearch.hidden = true;
        } else if (key === "category") {
            state.category = "all";
            renderCategoryRail();
            renderCategoryFilters();
        } else if (key === "price") {
            state.minPrice = "";
            state.maxPrice = "";
            if (els.minPrice) els.minPrice.value = "";
            if (els.maxPrice) els.maxPrice.value = "";
        } else if (key === "rating") {
            state.rating = "";
            els.ratingRadios.forEach(function (radio) { radio.checked = radio.value === ""; });
        } else if (key === "company") {
            state.company = "";
            updateStoreBanner("");
        }
        state.page = 1;
        loadProducts();
    }

    function resetFilters() {
        state.query = "";
        state.category = "all";
        state.minPrice = "";
        state.maxPrice = "";
        state.rating = "";
        state.company = "";
        state.sort = "relevance";
        state.page = 1;
        if (els.searchInput) els.searchInput.value = "";
        if (els.clearSearch) els.clearSearch.hidden = true;
        if (els.minPrice) els.minPrice.value = "";
        if (els.maxPrice) els.maxPrice.value = "";
        if (els.sort) els.sort.value = "relevance";
        els.ratingRadios.forEach(function (radio) { radio.checked = radio.value === ""; });
        updateStoreBanner("");
        renderCategoryRail();
        renderCategoryFilters();
        hideTypeahead();
        loadProducts();
        if (window.matchMedia("(max-width: 1024px)").matches) closeFilters(false);
    }

    function toggleFilters() {
        const mobile = window.matchMedia("(max-width: 1024px)").matches;
        if (mobile) {
            if (document.body.classList.contains("mgs-filters-open")) closeFilters(false);
            else openFilters();
            return;
        }
        const collapsed = els.layout.classList.toggle("sidebar-collapsed");
        if (els.sidebar) els.sidebar.classList.toggle("collapsed", collapsed);
        localStorage.setItem("magala_sidebar_collapsed", collapsed ? "true" : "false");
        updateFilterToggleText();
    }

    function openFilters() {
        state.lastFocused = document.activeElement;
        document.body.classList.add("mgs-filters-open");
        if (els.filterBackdrop) {
            els.filterBackdrop.hidden = false;
            requestAnimationFrame(function () { els.filterBackdrop.classList.add("is-open"); });
        }
        if (els.sidebar) els.sidebar.classList.remove("collapsed");
        if (els.filterToggle) els.filterToggle.setAttribute("aria-expanded", "true");
        setTimeout(function () {
            if (els.closeFilters) els.closeFilters.focus();
        }, 60);
    }

    function closeFilters(silent) {
        document.body.classList.remove("mgs-filters-open");
        if (els.filterBackdrop) {
            els.filterBackdrop.classList.remove("is-open");
            setTimeout(function () { if (els.filterBackdrop) els.filterBackdrop.hidden = true; }, 230);
        }
        if (els.filterToggle) els.filterToggle.setAttribute("aria-expanded", "false");
        if (!silent && state.lastFocused && typeof state.lastFocused.focus === "function") {
            state.lastFocused.focus();
        }
    }

    function restoreSidebarState() {
        if (!els.layout || !els.sidebar) return;
        if (window.matchMedia("(max-width: 1024px)").matches) return;
        const collapsed = localStorage.getItem("magala_sidebar_collapsed") === "true";
        els.layout.classList.toggle("sidebar-collapsed", collapsed);
        els.sidebar.classList.toggle("collapsed", collapsed);
        updateFilterToggleText();
    }

    function updateFilterToggleText() {
        if (!els.filterToggleText) return;
        const collapsed = els.layout && els.layout.classList.contains("sidebar-collapsed");
        els.filterToggleText.textContent = collapsed
            ? t("Show filters", "Show filters")
            : t("Filters", "Filters");
    }

    /* ---------------------------------------------------------
       Products
       --------------------------------------------------------- */
    function loadProducts() {
        if (!els.items) return;
        const seq = ++state.requestSeq;
        state.loading = true;
        els.items.setAttribute("aria-busy", "true");
        if (!state.items.length) renderSkeletons();
        if (els.results && !state.items.length) els.results.textContent = t("Loading products…", "Loading products…");

        const params = new URLSearchParams();
        if (state.query) params.set("query", state.query);
        if (state.category && state.category !== "all") params.set("category", state.category);
        if (state.company) params.set("company", state.company);
        if (state.minPrice) params.set("min_price", state.minPrice);
        if (state.maxPrice) params.set("max_price", state.maxPrice);
        if (state.rating) params.set("min_rating", state.rating);
        if (state.sort) params.set("sort_by", state.sort);
        params.set("page", String(state.page));
        params.set("limit", String(PAGE_SIZE));

        fetch(API.search + "?" + params.toString(), {
            credentials: "same-origin",
            headers: { Accept: "application/json" }
        })
            .then(parseJson)
            .then(function (data) {
                if (seq !== state.requestSeq) return;
                state.loading = false;
                state.lastResponse = data || {};
                state.items = data && Array.isArray(data.items) ? data.items : [];
                state.total = Number((data && data.total) || 0);
                state.totalPages = Math.max(1, Number((data && data.total_pages) || 1));
                if (state.page > state.totalPages) state.page = state.totalPages;
                els.items.setAttribute("aria-busy", "false");
                updateStoreBannerFromItems();
                renderResultsSummary();
                updateAllCount();
                renderActiveFilters();
                renderItems();
                renderPagination();
                if (document.activeElement === els.searchInput) {
                    renderTypeahead(data, state.query);
                }
                syncUrl();
            })
            .catch(function (error) {
                if (seq !== state.requestSeq) return;
                state.loading = false;
                els.items.setAttribute("aria-busy", "false");
                if (els.results) els.results.textContent = t("Could not load products", "Could not load products");
                if (els.resultsSub) els.resultsSub.textContent = t("Check your connection and try again.", "Check your connection and try again.");
                renderError(error);
            });
    }

    function updateStoreBannerFromItems() {
        if (!state.company) return;
        const first = state.items[0];
        if (first && first.company_name) {
            updateStoreBanner(first.company_name);
        }
    }

    function renderResultsSummary() {
        if (!els.results) return;
        const shown = state.items.length;
        const total = state.total;
        if (!total) {
            els.results.innerHTML = escapeHtml(t("No products found", "No products found"));
            if (els.resultsSub) {
                els.resultsSub.textContent = state.query
                    ? tpl("for “{query}” · try a broader search", { query: state.query },
                        "for “" + state.query + "” · try a broader search")
                    : t("Try adjusting your filters", "Try adjusting your filters");
            }
            return;
        }
        els.results.innerHTML = tpl("Showing {shown} of {total} products", {
            shown: "<strong>" + shown + "</strong>",
            total: "<strong>" + total + "</strong>"
        }, "Showing <strong>" + shown + "</strong> of <strong>" + total + "</strong> " +
            (total === 1 ? "product" : "products"));
        if (els.resultsSub) {
            const bits = [];
            if (state.query) bits.push("“" + state.query + "”");
            if (state.category !== "all") bits.push(categoryLabel(state.category));
            if (state.company) bits.push(state.company);
            els.resultsSub.textContent = bits.join(" · ");
        }
    }

    function renderSkeletons() {
        if (!els.items) return;
        let html = "";
        for (let i = 0; i < 8; i += 1) {
            html += '<div class="mgs-skeleton-card mgs-skeleton" aria-hidden="true">' +
                '<div class="mgs-skel mgs-skel-media"></div>' +
                '<div class="mgs-skel mgs-skel-line"></div>' +
                '<div class="mgs-skel mgs-skel-line short"></div>' +
                '<div class="mgs-skel mgs-skel-line tiny"></div></div>';
        }
        els.items.innerHTML = html;
    }

    function renderItems() {
        if (!els.items || state.view === "map") return;
        if (!state.items.length) {
            els.items.innerHTML = emptyStateHtml();
            return;
        }
        const list = state.view === "list";
        els.items.innerHTML = state.items.map(function (item) {
            return list ? listRowHtml(item) : cardHtml(item);
        }).join("");
        attachImageFallbacks(els.items);
    }

    function productDetailUrl(item) {
        const explicit = item && (item.detail_url || item.product_url);
        if (explicit) return String(explicit);
        return "/product/" + encodeURIComponent((item && item.item_code) || "");
    }

    function cardHtml(item) {
        const code = escapeHtml(item.item_code || "");
        const name = escapeHtml(item.web_item_name || item.item_name || item.item_code || t("Product", "Product"));
        const company = escapeHtml(item.company_name || item.company || t("Verified seller", "Verified seller"));
        const initial = escapeHtml((item.company_name || item.company || "S").trim().charAt(0).toUpperCase());
        const group = escapeHtml(item.item_group || t("Products", "Products"));
        const detail = productDetailUrl(item);
        const summary = escapeHtml(stripHtml(item.short_description || item.description || "").slice(0, 120));
        return '<article class="mgs-product-card" tabindex="0" role="link" aria-label="' + name +
            '" data-item-code="' + code + '" data-detail-url="' + escapeHtml(detail) + '">' +
            '<div class="mgs-card-media">' + thumbHtml(item, "card") +
            '<div class="mgs-card-badges">' +
            '<span class="mgs-badge mgs-badge--stock">● ' + escapeHtml(t(item.stock_status || "In Stock", item.stock_status || "In Stock")) + '</span>' +
            '<span class="mgs-badge mgs-badge--category">' + group + '</span>' +
            '</div></div>' +
            '<div class="mgs-card-body">' +
            '<div class="mgs-seller"><span class="mgs-seller-avatar">' + initial + '</span>' +
            '<span class="mgs-seller-name">' + company + '</span></div>' +
            '<h3 class="mgs-card-title">' + name + '</h3>' +
            (summary ? '<p class="mgs-card-summary">' + summary + '</p>' : '') +
            '<div class="mgs-card-meta">' + ratingHtml(item) + '<span>' + group + '</span></div>' +
            '<div class="mgs-card-foot">' + priceHtml(item) +
            '<button type="button" class="mgs-add-btn" data-cart-item="' + code +
            '" aria-label="' + escapeHtml(tpl("Add {name} to cart", { name: name }, "Add " + name + " to cart")) + '"><span aria-hidden="true">＋</span>' +
            '<span class="mgs-add-label">' + escapeHtml(t("Add", "Add")) + '</span></button>' +
            '</div>' +
            '<a class="mgs-view-btn" href="' + escapeHtml(detail) + '">' + escapeHtml(t("View details", "View details")) + ' <span aria-hidden="true">→</span></a>' +
            '</div></article>';
    }

    function listRowHtml(item) {
        const code = escapeHtml(item.item_code || "");
        const name = escapeHtml(item.web_item_name || item.item_name || item.item_code || t("Product", "Product"));
        const company = escapeHtml(item.company_name || item.company || t("Verified seller", "Verified seller"));
        const initial = escapeHtml((item.company_name || item.company || "S").trim().charAt(0).toUpperCase());
        const group = escapeHtml(item.item_group || t("Products", "Products"));
        const detail = productDetailUrl(item);
        const description = escapeHtml(stripHtml(item.short_description || item.description || "").slice(0, 190)) ||
            t("Verified marketplace listing.", "Verified marketplace listing.");
        return '<article class="mgs-list-row" tabindex="0" role="link" aria-label="' + name +
            '" data-item-code="' + code + '" data-detail-url="' + escapeHtml(detail) + '">' +
            '<div class="mgs-list-media">' + thumbHtml(item, "list") + '</div>' +
            '<div class="mgs-list-body">' +
            '<div class="mgs-seller"><span class="mgs-seller-avatar">' + initial + '</span>' +
            '<span class="mgs-seller-name">' + company + '</span></div>' +
            '<h3 class="mgs-card-title">' + name + '</h3>' +
            '<p class="mgs-list-desc">' + description + '</p>' +
            '<div class="mgs-card-meta">' + ratingHtml(item) + '<span>' + group + '</span></div>' +
            '</div>' +
            '<div class="mgs-list-side">' + priceHtml(item) +
            '<button type="button" class="mgs-add-btn" data-cart-item="' + code +
            '" aria-label="' + escapeHtml(tpl("Add {name} to cart", { name: name }, "Add " + name + " to cart")) + '"><span aria-hidden="true">＋</span>' +
            '<span class="mgs-add-label">' + escapeHtml(t("Add to cart", "Add to cart")) + '</span></button>' +
            '<a class="mgs-btn mgs-btn-ghost" href="' + escapeHtml(detail) + '">' + escapeHtml(t("View details", "View details")) + '</a>' +
            '</div></article>';
    }

    function emptyStateHtml() {
        return '<div class="mgs-empty">' +
            '<div class="mgs-empty-icon" aria-hidden="true">🧭</div>' +
            '<h3>' + escapeHtml(t("No products match your filters", "No products match your filters")) + '</h3>' +
            '<p>' + escapeHtml(t("Try a different category, widen your price range, or clear the search to explore the whole marketplace.", "Try a different category, widen your price range, or clear the search to explore the whole marketplace.")) + '</p>' +
            '<div class="mgs-empty-actions">' +
            '<button type="button" class="mgs-btn mgs-btn-primary" data-clear-all>' + escapeHtml(t("Clear filters", "Clear filters")) + '</button>' +
            '<a class="mgs-btn mgs-btn-ghost" href="/map">' + escapeHtml(t("Explore on the map", "Explore on the map")) + '</a>' +
            '</div></div>';
    }

    function renderError(error) {
        if (!els.items) return;
        els.items.innerHTML = '<div class="mgs-error">' +
            '<div class="mgs-error-icon" aria-hidden="true">⚠️</div>' +
            '<h3>' + escapeHtml(t("We could not load the marketplace", "We could not load the marketplace")) + '</h3>' +
            '<p>' + escapeHtml(cleanError(error)) + '</p>' +
            '<div class="mgs-empty-actions">' +
            '<button type="button" class="mgs-btn mgs-btn-primary" data-retry>' + escapeHtml(t("Try again", "Try again")) + '</button>' +
            '<a class="mgs-btn mgs-btn-ghost" href="/shop">' + escapeHtml(t("Reload shop", "Reload shop")) + '</a>' +
            '</div></div>';
    }

    function bindItems() {
        if (!els.items) return;
        els.items.addEventListener("click", function (event) {
            if (event.target.closest("[data-retry]")) { loadProducts(); return; }
            if (event.target.closest("[data-clear-all]")) { resetFilters(); return; }
            const add = event.target.closest("[data-cart-item]");
            if (add) {
                event.preventDefault();
                event.stopPropagation();
                addToCart(add.getAttribute("data-cart-item"), add);
                return;
            }
            if (event.target.closest("a")) return;
            const card = event.target.closest("[data-detail-url]");
            if (card) {
                const url = card.getAttribute("data-detail-url");
                if (url) window.location.href = url;
            }
        });
        els.items.addEventListener("keydown", function (event) {
            if (event.key !== "Enter" && event.key !== " ") return;
            if (event.target.closest("button, a")) return;
            const card = event.target.closest("[data-detail-url]");
            if (card) {
                event.preventDefault();
                const url = card.getAttribute("data-detail-url");
                if (url) window.location.href = url;
            }
        });
    }

    function renderActiveFilters() {
        if (!els.activeFilters) return;
        const chips = [];
        if (state.query) chips.push(filterChip("query", tpl("Search: “{query}”", { query: state.query }, "Search: “" + state.query + "”")));
        if (state.category !== "all") chips.push(filterChip("category", categoryLabel(state.category)));
        if (state.minPrice || state.maxPrice) {
            chips.push(filterChip("price", "ETB " + (state.minPrice || "0") + " – " + (state.maxPrice || "∞")));
        }
        if (state.rating) chips.push(filterChip("rating", tpl("{rating}★ & above", { rating: state.rating }, state.rating + "★ & above")));
        if (state.company) chips.push(filterChip("company", tpl("Store: {name}", { name: state.company }, "Store: " + state.company)));
        if (!chips.length) {
            els.activeFilters.hidden = true;
            els.activeFilters.innerHTML = "";
            return;
        }
        els.activeFilters.hidden = false;
        els.activeFilters.innerHTML = chips.join("") +
            '<button type="button" class="mgs-clear-all" data-clear-all>' + escapeHtml(t("Clear all", "Clear all")) + '</button>';
    }

    function filterChip(key, text) {
        return '<span class="mgs-filter-chip">' + escapeHtml(text) +
            '<button type="button" data-clear="' + escapeHtml(key) +
            '" aria-label="' + escapeHtml(tpl("Remove {name}", { name: text }, "Remove " + text)) + '">✕</button></span>';
    }

    function syncUrl() {
        const params = new URLSearchParams();
        if (state.company) params.set("company", state.company);
        if (state.query) params.set("q", state.query);
        if (state.category !== "all") params.set("category", state.category);
        if (state.sort !== "relevance") params.set("sort", state.sort);
        if (state.minPrice) params.set("min", state.minPrice);
        if (state.maxPrice) params.set("max", state.maxPrice);
        if (state.rating) params.set("rating", state.rating);
        if (state.page > 1) params.set("page", String(state.page));
        if (state.view !== "grid") params.set("view", state.view);
        const query = params.toString();
        const url = window.location.pathname + (query ? "?" + query : "") + window.location.hash;
        try {
            window.history.replaceState(null, "", url);
        } catch (e) {
            /* ignore history errors */
        }
    }

    /* ---------------------------------------------------------
       Pagination
       --------------------------------------------------------- */
    function renderPagination() {
        if (!els.pagination) return;
        if (state.totalPages <= 1) {
            els.pagination.hidden = true;
            els.pagination.innerHTML = "";
            return;
        }
        els.pagination.hidden = false;
        const pages = pageWindow(state.page, state.totalPages);
        let html = '<button type="button" class="btn-page" data-page="' + (state.page - 1) +
            '" aria-label="' + escapeHtml(t("Previous page", "Previous page")) + '"' + (state.page <= 1 ? " disabled" : "") + '>‹</button>';
        pages.forEach(function (page) {
            if (page === "…") {
                html += '<span class="mgs-page-ellipsis">…</span>';
            } else {
                html += '<button type="button" class="btn-page' + (page === state.page ? " active" : "") +
                    '" data-page="' + page + '"' + (page === state.page ? ' aria-current="page"' : "") +
                    '>' + page + '</button>';
            }
        });
        html += '<button type="button" class="btn-page" data-page="' + (state.page + 1) +
            '" aria-label="' + escapeHtml(t("Next page", "Next page")) + '"' + (state.page >= state.totalPages ? " disabled" : "") + '>›</button>';
        html += '<span class="mgs-page-indicator">' + escapeHtml(tpl("Page {page} of {pages}", {
            page: state.page, pages: state.totalPages
        }, "Page " + state.page + " of " + state.totalPages)) + '</span>';
        els.pagination.innerHTML = html;
    }

    function pageWindow(current, total) {
        if (total <= 7) {
            const all = [];
            for (let i = 1; i <= total; i += 1) all.push(i);
            return all;
        }
        const pages = [1];
        const start = Math.max(2, current - 1);
        const end = Math.min(total - 1, current + 1);
        if (start > 2) pages.push("…");
        for (let i = start; i <= end; i += 1) pages.push(i);
        if (end < total - 1) pages.push("…");
        pages.push(total);
        return pages;
    }

    function bindPagination() {
        if (!els.pagination) return;
        els.pagination.addEventListener("click", function (event) {
            const button = event.target.closest("[data-page]");
            if (!button || button.disabled) return;
            const page = Number(button.getAttribute("data-page"));
            if (!page || page === state.page || page < 1 || page > state.totalPages) return;
            state.page = page;
            loadProducts();
            scrollToResults();
        });
    }

    function scrollToResults() {
        if (!els.toolbar) return;
        const top = els.toolbar.getBoundingClientRect().top + window.scrollY - 96;
        window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
    }

    /* ---------------------------------------------------------
       View switching & map
       --------------------------------------------------------- */
    function bindView() {
        els.viewButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                setView(button.getAttribute("data-view") || "grid");
            });
        });
        if (els.mapFit) {
            els.mapFit.addEventListener("click", function () {
                if (state.map.instance && state.map.companies.length) {
                    fitMapToCompanies(state.map.companies);
                }
            });
        }
    }

    function setView(view) {
        if (["grid", "list", "map"].indexOf(view) < 0) view = "grid";
        state.view = view;
        localStorage.setItem("magala_view_mode", view);
        applyView(true);
        syncUrl();
        if (view === "map") initMap(false);
    }

    function applyView(render) {
        if (!els.items) return;
        const isMap = state.view === "map";
        const isList = state.view === "list";
        els.items.hidden = isMap;
        if (els.mapWrap) els.mapWrap.hidden = !isMap;
        if (els.pagination) els.pagination.hidden = isMap || state.totalPages <= 1;
        els.items.classList.toggle("mgs-grid", !isList);
        els.items.classList.toggle("mgs-list", isList);
        els.items.classList.toggle("magala-grid-view", !isList);
        els.items.classList.toggle("magala-list-view", isList);
        els.viewButtons.forEach(function (button) {
            const active = button.getAttribute("data-view") === state.view;
            button.classList.toggle("active", active);
            button.setAttribute("aria-pressed", active ? "true" : "false");
        });
        if (render && !isMap) renderItems();
        if (render && isMap) initMap(false);
    }

    function locateUser() {
        if (!navigator.geolocation) {
            showToast(t("Geolocation is not supported by this browser.", "Geolocation is not supported by this browser."));
            return;
        }
        const button = els.nearMe;
        const original = button ? button.innerHTML : "";
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span aria-hidden="true">⏳</span> Locating…';
        }
        navigator.geolocation.getCurrentPosition(function (position) {
            state.userLat = position.coords.latitude;
            state.userLng = position.coords.longitude;
            if (button) {
                button.disabled = false;
                button.innerHTML = original;
            }
            setView("map");
            state.map.loaded = false;
            state.map.retry = 0;
            initMap(true);
            showToast(t("Map centered on your location. 📍", "Map centered on your location. 📍"));
        }, function () {
            if (button) {
                button.disabled = false;
                button.innerHTML = original;
            }
            showToast(t("Location permission denied. You can still browse all products.", "Location permission denied. You can still browse all products."));
        }, { enableHighAccuracy: false, timeout: 9000, maximumAge: 300000 });
    }

    function initMap(force) {
        if (!els.mapContainer) return;
        if (state.map.loading) return;
        if (state.map.instance && !force) {
            state.map.instance.invalidateSize();
            return;
        }
        if (typeof window.L === "undefined") {
            state.map.retry += 1;
            if (state.map.retry < 40) {
                setTimeout(function () { initMap(force); }, 200);
            } else if (els.mapStatus) {
                setMapStatus("Map library could not load. Please refresh the page.", {}, "Map library could not load. Please refresh the page.");
            }
            return;
        }
        state.map.loading = true;
        if (els.mapStatus) els.mapStatus.textContent = "🗺️ Loading business locations…";
        if (state.map.instance) {
            try { state.map.instance.remove(); } catch (e) { /* ignore */ }
            state.map.instance = null;
            state.map.cluster = null;
        }
        const map = window.L.map(els.mapContainer, {
            scrollWheelZoom: true,
            zoomControl: true
        }).setView([9.0192, 38.7525], 12);
        window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        state.map.instance = map;
        if (typeof window.L.markerClusterGroup === "function") {
            state.map.cluster = window.L.markerClusterGroup({
                showCoverageOnHover: false,
                maxClusterRadius: 52
            });
            map.addLayer(state.map.cluster);
        } else {
            state.map.cluster = window.L.layerGroup().addTo(map);
        }

        const params = new URLSearchParams();
        if (state.category && state.category !== "all") params.set("category", state.category);
        if (state.userLat !== null && state.userLng !== null) {
            params.set("user_lat", String(state.userLat));
            params.set("user_lng", String(state.userLng));
        }
        fetch(API.map + (params.toString() ? "?" + params.toString() : ""), {
            credentials: "same-origin",
            headers: { Accept: "application/json" }
        })
            .then(parseJson)
            .then(function (data) {
                state.map.loading = false;
                const allCompanies = data && Array.isArray(data.companies) ? data.companies : [];
                const companies = state.company
                    ? allCompanies.filter(function (company) {
                        return company.company === state.company || company.company_name === state.company;
                    })
                    : allCompanies;
                state.map.companies = companies;
                state.map.loaded = true;
                if (companies.length === 0) {
                    setMapStatus(state.company
                        ? "No map locations are published for this store yet."
                        : "No verified business locations yet. New stores are added every week.", {},
                        state.company
                            ? "No map locations are published for this store yet."
                            : "No verified business locations yet. New stores are added every week.");
                    return;
                }
                renderMapMarkers(companies);
                setMapStatus("{n} verified business locations on the map", { n: companies.length },
                    companies.length + " verified business location" +
                    (companies.length === 1 ? "" : "s") + " on the map");
            })
            .catch(function (error) {
                state.map.loading = false;
                setMapStatus("Could not load business locations. ", {}, "Could not load business locations. ",
                    cleanError(error));
            });
    }

    function setMapStatus(key, vars, fallback, suffix) {
        state.map.status = { key: key, vars: vars || {}, fallback: fallback, suffix: suffix || "" };
        if (!els.mapStatus) return;
        els.mapStatus.textContent = tpl(key, vars, fallback) + (suffix ? " " + suffix : "");
    }

    function refreshMapStatus() {
        if (!els.mapStatus || !state.map.status) return;
        const status = state.map.status;
        els.mapStatus.textContent = tpl(status.key, status.vars, status.fallback) +
            (status.suffix ? " " + status.suffix : "");
    }

    function renderMapMarkers(companies) {
        if (!state.map.cluster || !state.map.instance) return;
        state.map.cluster.clearLayers();
        companies.forEach(function (company) {
            const lat = Number(company.lat);
            const lng = Number(company.lng);
            if (!isFinite(lat) || !isFinite(lng) || (lat === 0 && lng === 0)) return;
            const color = company.pin_color || "#1FB6AE";
            const initial = escapeHtml((company.company_name || company.name || "S").trim().charAt(0).toUpperCase());
            const icon = window.L.divIcon({
                className: "mgs-custom-pin",
                html: '<div style="width:36px;height:36px;border-radius:50% 50% 50% 6px;transform:rotate(-45deg);' +
                    "background:" + color + ';border:3px solid #ffffff;box-shadow:0 8px 18px rgba(15,23,42,.35);' +
                    'display:flex;align-items:center;justify-content:center;">' +
                    '<span style="transform:rotate(45deg);color:#fff;font-weight:900;font-size:14px;">' + initial + '</span></div>',
                iconSize: [36, 36],
                iconAnchor: [18, 36],
                popupAnchor: [0, -34]
            });
            const marker = window.L.marker([lat, lng], { icon: icon, title: company.company_name || company.name });
            marker.bindPopup(mapPopupHtml(company));
            state.map.cluster.addLayer(marker);
        });
        if (companies.length) fitMapToCompanies(companies);
    }

    function fitMapToCompanies(companies) {
        if (!state.map.instance) return;
        const bounds = [];
        companies.forEach(function (company) {
            const lat = Number(company.lat);
            const lng = Number(company.lng);
            if (isFinite(lat) && isFinite(lng) && !(lat === 0 && lng === 0)) bounds.push([lat, lng]);
        });
        if (bounds.length) {
            state.map.instance.fitBounds(bounds, { padding: [30, 30], maxZoom: 14 });
        }
    }

    function mapPopupHtml(company) {
        const name = escapeHtml(company.company_name || company.name || t("Verified seller", "Verified seller"));
        const address = escapeHtml(company.address || t("Ethiopia", "Ethiopia"));
        const phone = company.phone ? '<div style="font-size:12px;margin-bottom:8px;color:#334155;">📞 ' +
            escapeHtml(company.phone) + '</div>' : "";
        const distance = company.distance_km ? '<div style="font-size:11px;margin-bottom:8px;color:#64748b;">📍 ' +
            escapeHtml(company.distance_km) + ' ' + escapeHtml(t("km away", "km away")) + '</div>' : "";
        const url = "/shop?company=" + encodeURIComponent(company.company || company.company_name || "");
        return '<div style="min-width:210px;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">' +
            '<strong style="display:block;color:#0f766e;font-size:14px;margin-bottom:4px;">' + name + '</strong>' +
            '<div style="color:#64748b;font-size:12px;line-height:1.45;margin-bottom:8px;">' + address + '</div>' +
            phone + distance +
            '<a href="' + escapeHtml(url) + '" style="display:inline-block;background:#0d9488;color:#fff;' +
            'padding:7px 11px;border-radius:8px;font-size:12px;font-weight:800;text-decoration:none;">' +
            escapeHtml(t("View storefront →", "View storefront →")) + '</a></div>';
    }

    /* ---------------------------------------------------------
       Cart
       --------------------------------------------------------- */
    function bindCart() {
        if (els.cartButton) els.cartButton.addEventListener("click", openCart);
        if (els.closeCart) els.closeCart.addEventListener("click", closeCart);
        if (els.cartBackdrop) els.cartBackdrop.addEventListener("click", closeCart);
        if (els.drawerItems) {
            els.drawerItems.addEventListener("click", function (event) {
                const button = event.target.closest("[data-cart-action]");
                if (!button) return;
                const itemCode = button.getAttribute("data-cart-item");
                const action = button.getAttribute("data-cart-action");
                const card = button.closest(".cart-drawer-card");
                const qtyEl = card ? card.querySelector("[data-cart-qty]") : null;
                const current = Number(qtyEl ? qtyEl.textContent : 1) || 1;
                if (action === "remove") {
                    cartAction("remove", itemCode, 0);
                } else if (action === "inc") {
                    cartAction("inc", itemCode, current + 1);
                } else if (action === "dec") {
                    cartAction("dec", itemCode, Math.max(0, current - 1));
                }
            });
        }
        document.addEventListener("keydown", function (event) {
            if (event.key !== "Escape") return;
            hideTypeahead();
            closeCart();
            if (document.body.classList.contains("mgs-filters-open")) closeFilters(false);
        });
        document.querySelectorAll("a.shopping-cart, .shopping-cart a, a.cart-icon, .cart-icon a").forEach(function (link) {
            link.addEventListener("click", function (event) {
                event.preventDefault();
                openCart();
            });
        });
    }

    function refreshCart() {
        if (window.MagalaCart && typeof window.MagalaCart.refresh === "function") {
            window.MagalaCart.refresh().catch(function () { /* ignore */ });
            return;
        }
        fetch(API.cart, { credentials: "same-origin", headers: { Accept: "application/json" } })
            .then(parseJson)
            .then(renderShopCartDrawer)
            .catch(function () { /* guest cart may be empty */ });
    }

    function openCart() {
        if (!els.drawer) return;
        state.lastFocused = document.activeElement;
        els.drawer.classList.add("open");
        els.drawer.setAttribute("aria-hidden", "false");
        if (els.cartBackdrop) {
            els.cartBackdrop.classList.add("open");
            els.cartBackdrop.setAttribute("aria-hidden", "false");
        }
        document.body.classList.add("magala-cart-open");
        setTimeout(function () {
            if (els.closeCart) els.closeCart.focus();
        }, 60);
        if (window.MagalaCart && typeof window.MagalaCart.refresh === "function") {
            window.MagalaCart.refresh().catch(function () { /* ignore */ });
        }
    }

    function closeCart() {
        if (!els.drawer || !els.drawer.classList.contains("open")) return;
        els.drawer.classList.remove("open");
        els.drawer.setAttribute("aria-hidden", "true");
        if (els.cartBackdrop) {
            els.cartBackdrop.classList.remove("open");
            els.cartBackdrop.setAttribute("aria-hidden", "true");
        }
        document.body.classList.remove("magala-cart-open");
        if (state.lastFocused && typeof state.lastFocused.focus === "function") {
            state.lastFocused.focus();
        }
    }

    function cartAction(action, itemCode, qty) {
        if (!itemCode) return;
        if (window.MagalaCart) {
            if (action === "remove" && typeof window.MagalaCart.remove === "function") {
                window.MagalaCart.remove(itemCode);
                return;
            }
            if (typeof window.MagalaCart.updateQty === "function") {
                window.MagalaCart.updateQty(itemCode, qty);
                return;
            }
        }
        postCart(API.qty, { item_code: itemCode, qty: qty })
            .then(function (cart) {
                renderShopCartDrawer(cart);
                if (Number(qty) <= 0) showToast(t("Item removed from cart.", "Item removed from cart."));
            })
            .catch(function (error) {
                handleCartError(error, t("Could not update cart quantity", "Could not update cart quantity"));
            });
    }

    function addToCart(itemCode, button) {
        if (!itemCode) return;
        const original = button ? button.innerHTML : "";
        if (button) {
            button.classList.add("is-busy");
            button.setAttribute("aria-busy", "true");
            button.innerHTML = '<span class="mgs-add-label">' + escapeHtml(t("Adding…", "Adding…")) + '</span>';
        }
        const finish = function (ok) {
            if (!button) return;
            button.classList.remove("is-busy");
            button.removeAttribute("aria-busy");
            if (ok) {
                button.classList.add("is-added");
                button.innerHTML = '<span aria-hidden="true">✓</span><span class="mgs-add-label">' + escapeHtml(t("Added", "Added")) + '</span>';
                setTimeout(function () {
                    button.classList.remove("is-added");
                    button.innerHTML = original;
                }, 1500);
            } else {
                button.innerHTML = original;
            }
        };
        if (window.MagalaCart && typeof window.MagalaCart.add === "function") {
            window.MagalaCart.add(itemCode, 1).then(function () {
                finish(true);
            }).catch(function () {
                finish(false);
            });
            return;
        }
        postCart(API.add, { item_code: itemCode, qty: 1 })
            .then(function (cart) {
                renderShopCartDrawer(cart);
                openCart();
                showToast(t('Added to cart. <a href="/cart">Checkout →</a>', 'Added to cart. <a href="/cart">Checkout →</a>'));
                finish(true);
            })
            .catch(function (error) {
                handleCartError(error, t("Could not add to cart", "Could not add to cart"));
                finish(false);
            });
    }

    function postCart(url, payload) {
        return fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Frappe-CSRF-Token": csrf(),
                Accept: "application/json"
            },
            body: new URLSearchParams(payload || {})
        }).then(parseJson);
    }

    function handleCartError(error, fallback) {
        const message = cleanError(error) || fallback;
        if (/log in|login required|not permitted/i.test(message)) {
            window.location.href = "/login?redirect-to=" + encodeURIComponent(window.location.pathname + window.location.search);
            return;
        }
        showToast(escapeHtml(message));
    }

    function renderShopCartDrawer(cart) {
        cart = cart || { items: [], count: 0, total: 0 };
        const items = Array.isArray(cart.items) ? cart.items : [];
        const count = Number(cart.count || items.reduce(function (sum, item) {
            return sum + Number(item.qty || 0);
        }, 0));
        const currency = cart.currency || "ETB";
        const total = Number(cart.total || 0);
        if (els.cartCount) els.cartCount.textContent = String(count);
        if (els.drawerCount) els.drawerCount.textContent = String(count);
        if (els.drawerTotal) els.drawerTotal.textContent = formatMoney(total, currency);
        if (!els.drawerItems) return;
        if (!items.length) {
            els.drawerItems.innerHTML = '<p class="empty-cart-msg">' + escapeHtml(t("Your cart is empty. Explore items to add!", "Your cart is empty. Explore items to add!")) + '</p>';
            return;
        }
        els.drawerItems.innerHTML = items.map(function (item) {
            const code = escapeHtml(item.item_code || "");
            const name = escapeHtml(item.item_name || item.item_code || t("Item", "Item"));
            const qty = Number(item.qty || 1);
            const amount = Number(item.amount || (Number(item.rate || 0) * qty) || 0);
            const image = item.image && !PLACEHOLDER_RE.test(item.image)
                ? '<img src="' + escapeHtml(item.image) + '" alt="' + name + '" loading="lazy" />'
                : '<span class="mgs-cart-thumb-fallback" aria-hidden="true">' + categoryIcon(item.item_group) + '</span>';
            return '<div class="cart-drawer-card" data-cart-code="' + code + '">' +
                image +
                '<div class="mgs-cart-item-main">' +
                '<div class="mgs-cart-item-name">' + name + '</div>' +
                '<div class="mgs-cart-item-price">' + formatMoney(amount, currency) + '</div>' +
                '<div class="mgs-qty-row">' +
                '<button type="button" class="mgs-qty-btn" data-cart-action="dec" data-cart-item="' + code +
                '" aria-label="' + escapeHtml(t("Decrease quantity", "Decrease quantity")) + '">−</button>' +
                '<span class="mgs-qty-value" data-cart-qty>' + qty + '</span>' +
                '<button type="button" class="mgs-qty-btn" data-cart-action="inc" data-cart-item="' + code +
                '" aria-label="' + escapeHtml(t("Increase quantity", "Increase quantity")) + '">+</button>' +
                '<button type="button" class="mgs-remove-btn" data-cart-action="remove" data-cart-item="' +
                code + '">' + escapeHtml(t("Remove", "Remove")) + '</button>' +
                '</div></div></div>';
        }).join("");
    }

    window.renderShopCartDrawer = renderShopCartDrawer;
    window.addToCart = addToCart;

    function showToast(html) {
        if (!els.toast) return;
        els.toast.innerHTML = html;
        els.toast.classList.add("is-visible");
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () {
            els.toast.classList.remove("is-visible");
        }, 3400);
    }

    /* ---------------------------------------------------------
       Sticky toolbar
       --------------------------------------------------------- */
    function bindSticky() {
        if (!els.toolbar) return;
        let ticking = false;
        const update = function () {
            els.toolbar.classList.toggle("is-stuck", window.scrollY > 190);
            ticking = false;
        };
        window.addEventListener("scroll", function () {
            if (!ticking) {
                window.requestAnimationFrame(update);
                ticking = true;
            }
        }, { passive: true });
        update();
    }
})();
