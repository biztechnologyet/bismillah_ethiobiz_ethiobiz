/**
 * DOBiz PWA - Registration (v1.0.4)
 * Bismillah Ar-Rahman Ar-Rahim
 *
 * Injects the manifest link + theme-color synchronously, registers /sw.js at
 * scope "/", and shows a themed "Install DOBiz" pill on /app routes.
 *
 * v1.0.4 changes:
 *  - manifest link + meta tags injected synchronously at script run (Chrome
 *    installability sees it immediately, not after the async config fetch)
 *  - service worker registration starts immediately, before config loads
 *  - beforeinstallprompt is armed synchronously
 *  - the install pill ALWAYS responds on click: if a prompt is available it
 *    shows the browser install dialog; otherwise it opens a guided install
 *    modal (Chrome/Edge address-bar icon, Android menu, iOS Share menu) so a
 *    click never silently does nothing
 *  - busy state while prompting, re-arm after dismiss, hide after install
 * Never throws.
 */
(function () {
    "use strict";

    if (window.__dobizPwaRegistered) return;
    window.__dobizPwaRegistered = true;

    if (!("serviceWorker" in navigator)) return;
    if (document.querySelector(".web-form") || window.location.pathname.match(/\/(trial|new|edit)\//)) return;

    var DEFAULTS = {
        theme_color: "#1FB6AE",
        start_url: "/app/dobiz",
        install_prompt_enabled: 1,
        short_name: "DOBiz",
        enabled: 1
    };

    var config = Object.assign({}, DEFAULTS);

    var LS_INSTALLED = "dobiz_pwa_installed";
    var ICON_BASE = "/assets/bismillah_ethiobiz/pwa/icons";

    function isAlreadyInstalled() {
        try {
            if (localStorage.getItem(LS_INSTALLED)) return true;
        } catch (e) {}
        if (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches) return true;
        if (navigator.standalone) return true;
        return false;
    }

    function markInstalled() {
        try {
            localStorage.setItem(LS_INSTALLED, "1");
        } catch (e) {}
    }

    function isIOS() {
        return /iPhone|iPad|iPod/i.test(navigator.userAgent);
    }

    function isAndroid() {
        return /Android/i.test(navigator.userAgent);
    }

    // ---------------------------------------------------------------
    // Head injection (synchronous, ASAP)
    // ---------------------------------------------------------------
    function addLink(rel, href, attrs) {
        var link = document.createElement("link");
        link.rel = rel;
        link.href = href;
        if (attrs) {
            for (var k in attrs) {
                if (Object.prototype.hasOwnProperty.call(attrs, k)) link.setAttribute(k, attrs[k]);
            }
        }
        document.head.appendChild(link);
    }

    function addMeta(name, content) {
        if (document.querySelector('meta[name="' + name + '"]')) return;
        var meta = document.createElement("meta");
        meta.name = name;
        meta.content = content;
        document.head.appendChild(meta);
    }

    function injectHeadLinks() {
        if (!document.querySelector('link[rel="manifest"]')) addLink("manifest", "/manifest.webmanifest");
        if (!document.querySelector('link[rel="icon"][sizes="32x32"]')) addLink("icon", ICON_BASE + "/favicon-32.png", { type: "image/png", sizes: "32x32" });
        if (!document.querySelector('link[rel="icon"][sizes="16x16"]')) addLink("icon", ICON_BASE + "/favicon-16.png", { type: "image/png", sizes: "16x16" });
        if (!document.querySelector('link[rel="apple-touch-icon"]')) addLink("apple-touch-icon", ICON_BASE + "/apple-touch-icon.png");

        addMeta("theme-color", config.theme_color);
        addMeta("mobile-web-app-capable", "yes");
        addMeta("apple-mobile-web-app-capable", "yes");
        addMeta("apple-mobile-web-app-status-bar-style", "black-translucent");
        addMeta("apple-mobile-web-app-title", config.short_name);
    }

    // ---------------------------------------------------------------
    // Service worker
    // ---------------------------------------------------------------
    function registerSW() {
        if (location.protocol !== "https:" && location.hostname !== "localhost" && location.hostname !== "127.0.0.1") return;
        navigator.serviceWorker.register("/sw.js", { scope: "/" }).then(function () {
            console.debug("[DOBiz PWA] service worker registered");
        }).catch(function (err) {
            console.debug("[DOBiz PWA] service worker registration failed:", err);
        });
    }

    // ---------------------------------------------------------------
    // Config
    // ---------------------------------------------------------------
    function loadConfig() {
        return fetch("/api/method/bismillah_ethiobiz.pwa_settings.get_config", { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.message) config = Object.assign(config, data.message);
            })
            .catch(function () {});
    }

    // ---------------------------------------------------------------
    // Install pill
    // ---------------------------------------------------------------
    var installPrompt = null;
    var pill = null;
    var modal = null;

    function hidePill() {
        if (pill && pill.parentNode) pill.parentNode.removeChild(pill);
        pill = null;
    }

    function hideModal() {
        if (modal && modal.parentNode) modal.parentNode.removeChild(modal);
        modal = null;
    }

    function isAppRoute() {
        return window.location.pathname === "/app" || window.location.pathname.indexOf("/app/") === 0;
    }

    function openFallbackModal() {
        hideModal();
        modal = document.createElement("div");
        modal.setAttribute("role", "dialog");
        modal.setAttribute("aria-label", "Install DOBiz");
        modal.style.cssText = [
            "position:fixed", "inset:0", "z-index:100000",
            "display:flex", "align-items:center", "justify-content:center",
            "background:rgba(10,20,20,.55)", "backdrop-filter:blur(3px)",
            "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
        ].join(";");

        var card = document.createElement("div");
        card.style.cssText = [
            "width:min(92vw,420px)", "max-height:88vh", "overflow:auto",
            "background:#FFFFFF", "color:#14201f",
            "border-radius:18px", "padding:28px 24px", "text-align:center",
            "box-shadow:0 24px 64px rgba(0,0,0,.45)"
        ].join(";");

        var img = document.createElement("img");
        img.src = ICON_BASE + "/icon-192.png";
        img.alt = "DOBiz";
        img.width = 72;
        img.height = 72;
        img.style.cssText = "border-radius:16px;box-shadow:0 6px 18px rgba(0,0,0,.25);margin:0 auto 12px;display:block";
        card.appendChild(img);

        var title = document.createElement("h2");
        title.textContent = "Install DOBiz SmartERP";
        title.style.cssText = "margin:0 0 6px;font-size:19px;font-weight:700";
        card.appendChild(title);

        var sub = document.createElement("p");
        sub.textContent = "Add DOBiz to your screen for a full standalone app experience.";
        sub.style.cssText = "margin:0 0 16px;color:#5b6b6a;font-size:13.5px;line-height:1.5";
        card.appendChild(sub);

        var steps = document.createElement("ol");
        steps.style.cssText = "margin:0 auto 20px;padding:0 0 0 20px;text-align:left;color:#2b3b3a;font-size:13.5px;line-height:1.8;max-width:320px";

        var items = [];
        if (isIOS()) {
            items.push("Tap the Share button (square with an up arrow) in Safari.");
            items.push("Scroll down and tap \u201CAdd to Home Screen\u201D.");
            items.push("Tap \u201CAdd\u201D in the top-right. DOBiz will appear on your home screen.");
        } else if (isAndroid()) {
            items.push("Open the browser\u2019s three-dot menu (top-right).");
            items.push("Tap \u201CInstall app\u201D or \u201CAdd to Home screen\u201D.");
            items.push("Confirm to install. DOBiz will launch in its own window.");
        } else {
            items.push("Look at the top-right of the address bar for the install icon.");
            items.push("Click the install icon and choose \u201CInstall\u201D.");
            items.push("If the icon is missing, open the browser menu (\u22EE) and pick \u201CInstall DOBiz SmartERP\u201D or \u201CCast, save and share \u203A Install page as app\u201D.");
        }
        items.forEach(function (text) {
            var li = document.createElement("li");
            li.textContent = text;
            steps.appendChild(li);
        });
        card.appendChild(steps);

        var note = document.createElement("p");
        note.textContent = "Tip: once installed, DOBiz works offline and launches fullscreen.";
        note.style.cssText = "margin:0 0 18px;color:#9aa7a6;font-size:12.5px";
        card.appendChild(note);

        var closeBtn = document.createElement("button");
        closeBtn.setAttribute("type", "button");
        closeBtn.textContent = "Got it";
        closeBtn.style.cssText = [
            "padding:11px 30px", "border:0", "border-radius:999px",
            "background:linear-gradient(135deg,#1FB6AE,#149a93)", "color:#fff",
            "font-size:14px", "font-weight:600", "font-family:inherit", "cursor:pointer"
        ].join(";");
        closeBtn.addEventListener("click", hideModal);
        card.appendChild(closeBtn);

        modal.appendChild(card);
        modal.addEventListener("click", function (e) {
            if (e.target === modal) hideModal();
        });
        document.body.appendChild(modal);
    }

    function buildPill() {
        pill = document.createElement("button");
        pill.setAttribute("type", "button");
        pill.style.cssText = [
            "position:fixed", "left:24px", "bottom:24px", "z-index:99999",
            "display:inline-flex", "align-items:center", "gap:10px",
            "padding:10px 22px 10px 12px", "border:0", "border-radius:999px",
            "background:linear-gradient(135deg,#1FB6AE,#149a93)", "color:#fff",
            "font-size:14px", "font-weight:600", "font-family:inherit",
            "cursor:pointer", "box-shadow:0 8px 28px rgba(0,0,0,.35)",
            "transition:transform .15s ease, box-shadow .15s ease"
        ].join(";");

        var img = document.createElement("img");
        img.src = ICON_BASE + "/icon-192.png";
        img.alt = "";
        img.width = 30;
        img.height = 30;
        img.style.cssText = "border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,.3);display:block";
        pill.appendChild(img);

        var span = document.createElement("span");
        span.textContent = "Install DOBiz SmartERP";
        pill.appendChild(span);

        pill.addEventListener("mouseenter", function () {
            pill.style.transform = "translateY(-2px)";
            pill.style.boxShadow = "0 12px 32px rgba(0,0,0,.4)";
        });
        pill.addEventListener("mouseleave", function () {
            pill.style.transform = "";
            pill.style.boxShadow = "";
        });

        pill.addEventListener("click", function (e) {
            e.preventDefault();
            if (!installPrompt) {
                openFallbackModal();
                return;
            }
            if (pill.getAttribute("data-busy")) return;
            pill.setAttribute("data-busy", "1");
            span.textContent = "Installing\u2026";
            try {
                installPrompt.prompt();
            } catch (err) {
                pill.removeAttribute("data-busy");
                span.textContent = "Install DOBiz SmartERP";
                openFallbackModal();
                return;
            }
            if (installPrompt.userChoice) {
                installPrompt.userChoice.then(function (choice) {
                    if (choice && choice.outcome === "accepted") {
                        markInstalled();
                        hidePill();
                    } else {
                        pill.removeAttribute("data-busy");
                        span.textContent = "Install DOBiz SmartERP";
                    }
                }).catch(function () {
                    pill.removeAttribute("data-busy");
                    span.textContent = "Install DOBiz SmartERP";
                });
            } else {
                pill.removeAttribute("data-busy");
                span.textContent = "Install DOBiz SmartERP";
            }
        });

        document.body.appendChild(pill);
    }

    function showPill() {
        if (!config.install_prompt_enabled || pill) return;
        if (!isAppRoute()) return;
        if (isAlreadyInstalled()) return;
        buildPill();
    }

    // ---------------------------------------------------------------
    // Installability events (armed synchronously)
    // ---------------------------------------------------------------
    window.addEventListener("beforeinstallprompt", function (e) {
        e.preventDefault();
        installPrompt = e;
        showPill();
    });

    window.addEventListener("appinstalled", function () {
        installPrompt = null;
        markInstalled();
        hidePill();
        hideModal();
    });

    // ---------------------------------------------------------------
    // Boot: synchronously inject + register, then apply config
    // ---------------------------------------------------------------
    function boot() {
        injectHeadLinks();
        registerSW();
        loadConfig().then(function () {
            injectHeadLinks();
            showPill();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();

