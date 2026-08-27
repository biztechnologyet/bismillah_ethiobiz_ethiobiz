/* Magala checkout website JS — cart badge, listing CTAs, /cart payment panel */
(function () {
    const API = {
        cart: "/api/method/bismillah_ethiobiz.magala_checkout.get_cart",
        add: "/api/method/bismillah_ethiobiz.magala_checkout.add_to_cart",
        qty: "/api/method/bismillah_ethiobiz.magala_checkout.update_cart_qty",
        place: "/api/method/bismillah_ethiobiz.magala_checkout.place_order",
        banks: "/api/method/bismillah_ethiobiz.magala_checkout.get_bank_accounts",
        options: "/api/method/bismillah_ethiobiz.magala_checkout.get_checkout_options",
        meta: "/api/method/bismillah_ethiobiz.magala_checkout.get_item_checkout_meta",
        bankRef: "/api/method/bismillah_ethiobiz.magala_checkout.submit_bank_reference",
        verify: "/api/method/bismillah_ethiobiz.magala_checkout.verify_return",
    };

    function csrf() {
        if (window.frappe && frappe.csrf_token) return frappe.csrf_token;
        const m = document.cookie.match(/csrf_token=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : "";
    }

    function unwrapApi(res) {
        if (res == null) return {};
        if (typeof res === "string") {
            const t = res.trim();
            if (t.startsWith("{") || t.startsWith("[")) {
                try { return unwrapApi(JSON.parse(t)); } catch (e) { return { message: t }; }
            }
            return { message: t };
        }
        if (typeof res !== "object") return { message: String(res) };
        if (res.tx_ref || res.reference) return res;
        if (res.message && typeof res.message === "object") return unwrapApi(res.message);
        return res;
    }

    function post(url, data) {
        const body = new URLSearchParams(data || {});
        return fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Frappe-CSRF-Token": csrf(),
            },
            body,
        }).then((r) => r.json()).then((j) => {
            if (j.exc) throw new Error((j._server_messages && j._server_messages) || j.exc);
            return unwrapApi(j.message !== undefined ? j.message : j);
        });
    }

    function get(url) {
        return fetch(url, { credentials: "same-origin" }).then((r) => r.json()).then((j) => j.message !== undefined ? j.message : j);
    }

    function toast(html) {
        let el = document.getElementById("magala-toast");
        if (!el) {
            el = document.createElement("div");
            el.id = "magala-toast";
            el.className = "magala-toast";
            document.body.appendChild(el);
        }
        el.innerHTML = html;
        el.style.display = "block";
        setTimeout(() => { el.style.display = "none"; }, 4000);
    }

    function renderBadge(cart) {
        let badge = document.getElementById("magala-cart-badge");
        if (!badge) {
            badge = document.createElement("a");
            badge.id = "magala-cart-badge";
            badge.className = "magala-cart-badge";
            badge.href = "/cart";
            const nav = document.querySelector(".navbar .navbar-nav, .web-footer, header nav, .navbar");
            const host = document.querySelector(".navbar-collapse") || document.querySelector("header") || document.body;
            host.appendChild(badge);
        }
        const count = (cart && cart.count) || 0;
        badge.innerHTML = `🛒 Cart <span class="magala-cart-count">${count}</span>`;
    }

    window.MagalaCart = {
        refresh() {
            return get(API.cart).then((cart) => {
                renderBadge(cart);
                return cart;
            }).catch(() => ({ items: [], count: 0, total: 0 }));
        },
        add(itemCode, qty) {
            return post(API.add, { item_code: itemCode, qty: qty || 1 }).then((cart) => {
                renderBadge(cart);
                toast(`Added to cart. <a href="/cart" style="color:#5eead4;font-weight:800;">Checkout →</a>`);
                if (location.pathname.replace(/\/$/, "") === "/cart") {
                    window.location.reload();
                }
                return cart;
            }).catch((e) => {
                const msg = (e && e.message) ? String(e.message).replace(/<[^>]+>/g, " ").slice(0, 220) : "Could not add to cart";
                if (/log in/i.test(msg)) {
                    window.location.href = "/login?redirect-to=" + encodeURIComponent(location.pathname + location.search);
                    return;
                }
                alert(msg);
                throw e;
            });
        },
    };

    function extractItemCode(card) {
        const $c = card;
        const data = $c.getAttribute("data-item-code") || ($c.querySelector("[data-item-code]") && $c.querySelector("[data-item-code]").getAttribute("data-item-code"));
        if (data) return data;
        const href = ($c.querySelector("a[href]") && $c.querySelector("a[href]").getAttribute("href")) || "";
        const m = href.match(/\/(?:products|all-products)\/([^/?#]+)/) || href.match(/^\/([^/?#]+)$/);
        if (m) return decodeURIComponent(m[1]);
        return "";
    }

    function enhanceCard(card) {
        if (card.getAttribute("data-magala-enhanced")) return;
        const text = (card.textContent || "").toLowerCase();
        const isJob = text.includes("job") || text.includes("career") || text.includes("apply now");
        const itemCode = card.getAttribute("data-item-code") || extractItemCode(card);
        if (!itemCode && !isJob) {
            card.setAttribute("data-magala-enhanced", "1");
            return;
        }
        card.setAttribute("data-magala-enhanced", "1");
        if (card.querySelector(".magala-card-cta")) return;

        const badges = document.createElement("div");
        badges.className = "magala-pay-badges";
        if (isJob) {
            badges.innerHTML = `<span class="magala-pay-badge">Apply Now</span>`;
        } else {
            const o = window.MagalaCheckoutOptions || {};
            if (o.show_payment_badges === false) {
                badges.innerHTML = "";
            } else {
                const group = text;
                const cod = o.enable_cod !== false && (group.includes("food") || group.includes("dining") || group.includes("product"));
                badges.innerHTML =
                    (cod ? `<span class="magala-pay-badge cod">${o.cod_label || "COD"}</span>` : "") +
                    (o.enable_bank_transfer !== false ? `<span class="magala-pay-badge">${o.bank_label || "Bank"}</span>` : "") +
                    (o.enable_addispay !== false ? `<span class="magala-pay-badge">${o.addispay_label || "AddisPay"}</span>` : "");
            }
        }
        const cta = document.createElement("div");
        cta.className = "magala-card-cta";
        if (isJob) {
            const a = card.querySelector("a[href]");
            cta.innerHTML = `<a class="magala-btn-ghost" href="${a ? a.getAttribute("href") : "/jobs"}">Apply Now</a>`;
        } else {
            const view = card.querySelector("a[href]");
            cta.innerHTML = `<button type="button" class="magala-btn-cart">Add to Cart</button>` +
                (view ? `<a class="magala-btn-ghost" href="${view.getAttribute("href")}">View</a>` : "");
            cta.querySelector(".magala-btn-cart").addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                const code = itemCode || extractItemCode(card);
                if (!code) {
                    alert("This item is not available for cart yet.");
                    return;
                }
                window.MagalaCart.add(code, 1);
            });
        }
        card.appendChild(badges);
        card.appendChild(cta);
    }

    function enhanceListings() {
        document.querySelectorAll(".item-card, .shop-card, .product-card").forEach(enhanceCard);
        document.querySelectorAll(".btn-add-to-cart, .btn-add-to-cart-list").forEach((btn) => {
            if (btn.getAttribute("data-magala-bound")) return;
            btn.setAttribute("data-magala-bound", "1");
            btn.addEventListener("click", function (e) {
                const code = btn.getAttribute("data-item-code") || (btn.closest("[data-item-code]") && btn.closest("[data-item-code]").getAttribute("data-item-code"));
                if (code) {
                    e.preventDefault();
                    e.stopPropagation();
                    window.MagalaCart.add(code, 1);
                }
            }, true);
        });
        enhanceItemPage();
    }

    function enhanceItemPage() {
        if (document.getElementById("magala-item-pay")) return;
        const addBtn = document.querySelector(".btn-add-to-cart, #add-to-cart, button[data-item-code]");
        const itemCode = (addBtn && addBtn.getAttribute("data-item-code")) ||
            (document.querySelector("[data-item-code]") && document.querySelector("[data-item-code]").getAttribute("data-item-code"));
        const host = document.querySelector(".item-details, .product-details, .web-item-container, .page-content") || document.querySelector("main");
        if (!host || document.body.classList.contains("cart-page")) return;
        const path = location.pathname;
        if (path === "/cart" || path === "/shop" || path === "/all-products") return;
        if (!itemCode && !addBtn) return;
        const box = document.createElement("div");
        box.id = "magala-item-pay";
        box.innerHTML = `<div class="magala-pay-badges" style="margin:12px 0;">
            <span class="magala-pay-badge">Bank Transfer</span>
            <span class="magala-pay-badge">AddisPay</span>
            <span class="magala-pay-badge cod">COD (goods & food)</span>
        </div>
        <button type="button" class="magala-btn-cart" id="magala-item-add">Add to Cart</button>
        <a class="magala-btn-ghost" href="/cart" style="margin-left:8px;">Go to Cart</a>`;
        host.appendChild(box);
        document.getElementById("magala-item-add").addEventListener("click", function () {
            const code = itemCode || prompt("Item code");
            if (code) window.MagalaCart.add(code, 1);
        });
    }

    function cartPageHost() {
        return document.querySelector("#page-cart .cart-payment-addresses")
            || document.querySelector("#page-cart .col-lg-4, #page-cart .cart-totals, #page-cart .payment-summary")
            || document.querySelector("#page-cart .page_content")
            || document.querySelector("#page-cart main")
            || document.querySelector("#page-cart")
            || document.querySelector("main.container")
            || document.querySelector("main")
            || document.body;
    }

    function fixWebshopTemplateGlitches() {
        document.querySelectorAll("#page-cart td, #page-cart th, #page-cart .item-name, #page-cart a").forEach((el) => {
            if ((el.textContent || "").trim() === "d.web_item_name") {
                el.remove();
            }
        });
        document.querySelectorAll("#page-cart .btn-place-order, #page-cart button.place-order, #page-cart .btn-request-for-quotation").forEach((btn) => {
            if (btn.id === "magala-place") return;
            btn.style.display = "none";
        });
    }

    function paymentHost(page) {
        const summary = document.querySelector("#page-cart .cart-payment-addresses, #page-cart .number-card, #page-cart .cart-totals");
        if (summary) return summary;
        const tableWrap = document.querySelector("#page-cart table") && document.querySelector("#page-cart table").closest(".frappe-card, .cart-container, .col-lg-8, .col-md-8");
        if (tableWrap && tableWrap.parentElement) {
            const cols = tableWrap.parentElement.querySelector(".col-lg-4, .col-md-4");
            if (cols) return cols;
        }
        return page;
    }

    function renderCartPage(cart) {
        fixWebshopTemplateGlitches();
        const page = cartPageHost();
        const host = paymentHost(page);
        let box = document.getElementById("magala-checkout-box");
        if (!box) {
            box = document.createElement("div");
            box.id = "magala-checkout-box";
            box.className = "magala-checkout-box magala-unified";
        }
        if (box.parentElement !== host) {
            host.appendChild(box);
        }

        const o = cart.options || window.MagalaCheckoutOptions || {};
        const cur = o.currency || "ETB";
        const def = o.default_payment_method || "AddisPay";
        const buyer = cart.buyer || {};
        const methods = [];
        if (o.enable_addispay !== false) {
            methods.push({ v: "AddisPay", icon: "\u{1F4B3}", label: o.addispay_label || "AddisPay", desc: o.addispay_description || "Cards, Telebirr, CBE Birr, bank apps." });
        }
        if (o.enable_bank_transfer !== false) {
            methods.push({ v: "Bank Transfer", icon: "\u{1F3E6}", label: o.bank_label || "Bank Transfer", desc: o.bank_description || "Pay to the accounts below, then submit your reference." });
        }
        if (o.enable_cod !== false) {
            methods.push({
                v: "Cash upon Delivery", icon: "\u{1F4B5}",
                label: o.cod_label || "Cash on Delivery",
                desc: !cart.cod_available ? "Only for product and food carts (configurable in Magala Checkout Settings)." : (o.cod_description || "Pay the courier in cash when your order arrives."),
                disabled: !cart.cod_available,
            });
        }
        const methodHtml = methods.length
            ? `<div class="magala-pay-row">${methods.map((m) => {
                const checked = (!m.disabled && m.v === def) ? "checked" : "";
                return `<label class="magala-pay-option ${checked ? "selected" : ""} ${m.disabled ? "disabled" : ""}">
                    <input type="radio" name="magala-pay" value="${m.v}" ${checked} ${m.disabled ? "disabled" : ""}>
                    <span class="magala-pay-icon">${m.icon || ""}</span>
                    <span>
                        <div class="magala-pay-label">${m.label}</div>
                        <div class="magala-pay-desc">${m.desc || ""}</div>
                    </span>
                </label>`;
            }).join("")}</div>`
            : "<p>No payment methods enabled. Open <strong>Magala Checkout Settings</strong> in Desk.</p>";

        const loginGate = !cart.logged_in
            ? `<p class="magala-login-gate">Please <a href="/login?redirect-to=/cart">log in</a> to place this order. Your cart items stay on this page.</p>`
            : "";
        const profile = cart.logged_in
            ? `<div class="magala-buyer-chip"><strong>${buyer.full_name || ""}</strong> · ${buyer.email || ""} · ${buyer.phone || "add phone on your profile"}
               ${buyer.shipping_address ? `<div class="magala-ship">${buyer.shipping_address}</div>` : `<div class="magala-ship">Add a shipping Address on your Customer record for Cash upon Delivery.</div>`}</div>`
            : "";
        const emptyHint = (!cart.items || !cart.items.length)
            ? `<p>Your cart is empty. Browse <a href="/all-products">All Products</a> or <a href="/shop">Shop</a>.</p>`
            : "";

        box.innerHTML = `
            <h4>Payment</h4>
            ${emptyHint}
            ${profile}
            ${loginGate}
            <p style="font-weight:800;margin:12px 0;">Grand Total: ${(cart.total || 0).toLocaleString()} ${cur}${o.sandbox && o.enable_addispay !== false ? ' <span class="magala-pay-badge">AddisPay UAT</span>' : ""}</p>
            <textarea class="magala-field" id="magala-address" rows="2" placeholder="Delivery notes / address override (optional for AddisPay &amp; Bank Transfer)">${buyer.shipping_address || ""}</textarea>
            ${methodHtml}
            <div id="magala-bank-box" style="display:none;background:#f8fafc;border-radius:12px;padding:12px;margin-bottom:12px;font-size:13px;"></div>
            <button type="button" class="magala-place-btn" id="magala-place" ${cart.logged_in && cart.items && cart.items.length ? "" : "disabled"}>Place Order</button>
            <div id="magala-result" style="margin-top:12px;"></div>
        `;
        get(API.banks).then((banks) => {
            const el = document.getElementById("magala-bank-box");
            if (!el) return;
            el.innerHTML = "<strong>Settlement accounts</strong>" + (banks || []).map((b) =>
                `<div style="display:flex;justify-content:space-between;padding:4px 0;gap:8px;"><span>${b.bank}${b.holder ? " · " + b.holder : ""}</span><strong>${b.account}</strong></div>${b.instructions ? "<small>" + b.instructions + "</small>" : ""}`
            ).join("");
        });
        box.querySelectorAll("input[name=magala-pay]").forEach((r) => {
            r.addEventListener("change", () => {
                box.querySelectorAll(".magala-pay-option").forEach((opt) => opt.classList.remove("selected"));
                r.closest(".magala-pay-option").classList.add("selected");
                document.getElementById("magala-bank-box").style.display = r.value === "Bank Transfer" ? "block" : "none";
            });
        });
        const placeBtn = document.getElementById("magala-place");
        if (placeBtn) {
            placeBtn.addEventListener("click", function () {
                if (!cart.logged_in) {
                    window.location.href = "/login?redirect-to=/cart";
                    return;
                }
                const method = (document.querySelector("input[name=magala-pay]:checked") || {}).value;
                const payload = {
                    payment_method: method,
                    delivery_address: document.getElementById("magala-address").value,
                };
                const btn = this;
                btn.disabled = true;
                btn.textContent = "Placing order…";
                post(API.place, payload).then((raw) => {
                    const res = unwrapApi(raw);
                    const tx = res.tx_ref || res.reference || res.payment_name || res.payment || "";
                    if (res.redirect) {
                        window.location.href = res.redirect;
                        return;
                    }
                    let extra = "";
                    if (res.payment_method === "Bank Transfer") {
                        extra = `<p>Transfer <strong>${(res.amount || 0).toLocaleString()} ETB</strong> then enter your bank slip ID below.</p>
                        <input class="magala-field" id="magala-ref" placeholder="Bank reference / slip ID">
                        <button type="button" class="magala-place-btn" id="magala-ref-btn">Submit bank reference</button>`;
                    }
                    const resultEl = document.getElementById("magala-result");
                    if (resultEl) {
                        resultEl.innerHTML =
                            `<div style="color:#0f766e;font-weight:800;">${res.message || "Order placed."}</div>
                             <div>Reference: <strong>${tx || "(saving…)"}</strong></div>
                             ${res.payment_name ? `<div>Payment: <strong>${res.payment_name}</strong></div>` : ""}${extra}`;
                    }
                    if (res.payment_method === "Bank Transfer" && tx) {
                        document.getElementById("magala-ref-btn").addEventListener("click", () => {
                            post(API.bankRef, {
                                tx_ref: tx,
                                bank_name: "Commercial Bank of Ethiopia",
                                reference_no: document.getElementById("magala-ref").value,
                                paid_by: (cart.buyer && cart.buyer.full_name) || "",
                            }).then(() => {
                                document.getElementById("magala-result").innerHTML += "<p>Receipt submitted. We will confirm funds shortly.</p>";
                            });
                        });
                    }
                    MagalaCart.refresh();
                }).catch((e) => {
                    alert(String(e.message || e).replace(/<[^>]+>/g, " ").slice(0, 280));
                }).finally(() => {
                    btn.disabled = false;
                    btn.textContent = "Place Order";
                });
            });
        }
        MagalaCart.refresh();
    }

    function bootMagala() {
        get(API.options).then((o) => {
            window.MagalaCheckoutOptions = o || {};
            MagalaCart.refresh();
            enhanceListings();
        }).catch(() => {
            MagalaCart.refresh();
            enhanceListings();
        });
        const obs = new MutationObserver(() => enhanceListings());
        obs.observe(document.body, { childList: true, subtree: true });
        if (location.pathname.replace(/\/$/, "") === "/cart") {
            MagalaCart.refresh().then(renderCartPage);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bootMagala);
    } else {
        bootMagala();
    }
})();
