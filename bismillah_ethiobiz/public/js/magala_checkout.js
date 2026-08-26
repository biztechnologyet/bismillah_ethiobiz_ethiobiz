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
            return j.message !== undefined ? j.message : j;
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
                return cart;
            }).catch((e) => {
                alert((e && e.message) ? String(e.message).replace(/<[^>]+>/g, " ").slice(0, 220) : "Could not add to cart");
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
        return document.querySelector("#page-cart .page_content")
            || document.querySelector("#page-cart main")
            || document.querySelector("#page-cart")
            || document.querySelector("main.container")
            || document.querySelector("main")
            || document.body;
    }

    function renderCartPage(cart) {
        const page = cartPageHost();
        let box = document.getElementById("magala-checkout-box");
        if (!box) {
            box = document.createElement("div");
            box.id = "magala-checkout-box";
            box.className = "magala-checkout-box";
        }
        const empty = page.querySelector(".cart-empty");
        if (empty) {
            page.insertBefore(box, empty);
        } else if (box.parentElement !== page) {
            page.insertBefore(box, page.firstChild);
        }
        const itemsHtml = (cart.items || []).map((it) => `
            <div style="display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px dashed #e2e8f0;">
                <div>
                    <strong>${it.item_name}</strong>
                    <div style="font-size:12px;color:#64748b;">${it.company || ""} · ${it.item_group || ""}</div>
                </div>
                <div style="text-align:right;">
                    <div>${Number(it.qty)} × ${Number(it.rate).toLocaleString()} ETB</div>
                    <button type="button" class="magala-remove" data-code="${it.item_code}" style="border:none;background:none;color:#e21d38;font-size:12px;">Remove</button>
                </div>
            </div>`).join("") || `<p>Your Magala cart is empty. Browse <a href="/all-products">All Products</a> or <a href="/shop">Shop</a>.</p>`;

        const o = cart.options || window.MagalaCheckoutOptions || {};
        const cur = o.currency || "ETB";
        const def = o.default_payment_method || "AddisPay";
        const methods = [];
        if (o.enable_addispay !== false) {
            methods.push({ v: "AddisPay", label: o.addispay_label || "AddisPay Payment", desc: o.addispay_description || "Cards, Telebirr, CBE Birr, bank apps." });
        }
        if (o.enable_bank_transfer !== false) {
            methods.push({ v: "Bank Transfer", label: o.bank_label || "Bank Transfer", desc: o.bank_description || "Pay to the accounts below, then submit your reference." });
        }
        if (o.enable_cod !== false) {
            methods.push({
                v: "Cash upon Delivery",
                label: o.cod_label || "Cash upon Delivery",
                desc: !cart.cod_available ? "Only for product and food carts (configurable in Magala Checkout Settings)." : (o.cod_description || "Pay the courier in cash."),
                disabled: !cart.cod_available,
            });
        }
        const methodHtml = methods.map((m) => {
            const checked = (!m.disabled && m.v === def) ? "checked" : "";
            return `<label class="magala-pay-option ${checked ? "selected" : ""} ${m.disabled ? "disabled" : ""}"><input type="radio" name="magala-pay" value="${m.v}" ${checked} ${m.disabled ? "disabled" : ""}>
                <span><strong>${m.label}</strong><br><small>${m.desc || ""}</small></span></label>`;
        }).join("") || "<p>No payment methods enabled. Open <strong>Magala Checkout Settings</strong> in Desk.</p>";
        box.innerHTML = `
            <h4>Magala Checkout</h4>
            <div id="magala-cart-lines">${itemsHtml}</div>
            <p style="font-weight:800;margin:12px 0;">Total: ${(cart.total || 0).toLocaleString()} ${cur}${o.sandbox && o.enable_addispay !== false ? ' <span class="magala-pay-badge">AddisPay UAT</span>' : ""}</p>
            <input class="magala-field" id="magala-name" placeholder="Full name">
            <input class="magala-field" id="magala-email" type="email" placeholder="Email">
            <input class="magala-field" id="magala-phone" placeholder="Phone (09… or 251…)">
            <textarea class="magala-field" id="magala-address" rows="2" placeholder="Delivery address (required for Cash upon Delivery)"></textarea>
            ${methodHtml}
            <div id="magala-bank-box" style="display:none;background:#f8fafc;border-radius:12px;padding:12px;margin-bottom:12px;font-size:13px;"></div>
            <button type="button" class="magala-place-btn" id="magala-place">Place Order</button>
            <div id="magala-result" style="margin-top:12px;"></div>
        `;
        box.querySelectorAll(".magala-remove").forEach((b) => {
            b.addEventListener("click", () => {
                post(API.qty, { item_code: b.getAttribute("data-code"), qty: 0 }).then(renderCartPage);
            });
        });
        get(API.banks).then((banks) => {
            const el = document.getElementById("magala-bank-box");
            if (!el) return;
            el.innerHTML = "<strong>Settlement accounts</strong>" + (banks || []).map((b) =>
                `<div style="display:flex;justify-content:space-between;padding:4px 0;gap:8px;"><span>${b.bank}${b.holder ? " · " + b.holder : ""}</span><strong>${b.account}</strong></div>${b.instructions ? "<small>" + b.instructions + "</small>" : ""}`
            ).join("");
        });
        box.querySelectorAll("input[name=magala-pay]").forEach((r) => {
            r.addEventListener("change", () => {
                box.querySelectorAll(".magala-pay-option").forEach((o) => o.classList.remove("selected"));
                r.closest(".magala-pay-option").classList.add("selected");
                document.getElementById("magala-bank-box").style.display = r.value === "Bank Transfer" ? "block" : "none";
            });
        });
        document.getElementById("magala-place").addEventListener("click", function () {
            const method = (document.querySelector("input[name=magala-pay]:checked") || {}).value;
            const payload = {
                payment_method: method,
                customer_name: document.getElementById("magala-name").value,
                email: document.getElementById("magala-email").value,
                phone: document.getElementById("magala-phone").value,
                delivery_address: document.getElementById("magala-address").value,
            };
            const btn = this;
            btn.disabled = true;
            btn.textContent = "Placing order…";
            post(API.place, payload).then((res) => {
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
                document.getElementById("magala-result").innerHTML =
                    `<div style="color:#0f766e;font-weight:800;">${res.message || "Order placed."}</div>
                     <div>Reference: <strong>${res.tx_ref}</strong></div>${extra}`;
                if (res.payment_method === "Bank Transfer") {
                    document.getElementById("magala-ref-btn").addEventListener("click", () => {
                        post(API.bankRef, {
                            tx_ref: res.tx_ref,
                            bank_name: "Commercial Bank of Ethiopia",
                            reference_no: document.getElementById("magala-ref").value,
                            paid_by: document.getElementById("magala-name").value,
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
