/**
 * DOBiz PWA - Registration (v1.0.3)
 * Bismillah Ar-Rahman Ar-Rahim
 *
 * Injects the manifest link + theme-color, registers /sw.js at scope "/",
 * shows a themed "Install DOBiz" prompt on /app routes, and applies the
 * EthioBiz icon everywhere: favicon, apple-touch-icon, install button.
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

    var ICON_BASE = "/assets/bismillah_ethiobiz/pwa/icons";

    function injectHeadLinks() {
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

    function registerSW() {
        if (location.protocol !== "https:" && location.hostname !== "localhost" && location.hostname !== "127.0.0.1") return;
        navigator.serviceWorker.register("/sw.js", { scope: "/" }).then(function () {
            console.debug("[DOBiz PWA] service worker registered");
        }).catch(function (err) {
            console.debug("[DOBiz PWA] service worker registration failed:", err);
        });
    }

    function loadConfig() {
        return fetch("/api/method/bismillah_ethiobiz.pwa_settings.get_config", { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.message) config = Object.assign(config, data.message);
            })
            .catch(function () {});
    }

    var installPrompt = null;
    var pill = null;

    function hidePill() {
        if (pill && pill.parentNode) pill.parentNode.removeChild(pill);
        pill = null;
    }

    function isAppRoute() {
        return window.location.pathname === "/app" || window.location.pathname.indexOf("/app/") === 0;
    }

    function showPill() {
        if (!config.install_prompt_enabled || pill) return;
        if (!isAppRoute()) return;
        if (isAlreadyInstalled()) return;

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
            if (installPrompt) {
                installPrompt.prompt();
            }
        });
        document.body.appendChild(pill);
    }

    window.addEventListener("beforeinstallprompt", function (e) {
        e.preventDefault();
        installPrompt = e;
        showPill();
    });

    window.addEventListener("appinstalled", function () {
        installPrompt = null;
        markInstalled();
        hidePill();
    });

    function boot() {
        loadConfig().then(function () {
            injectHeadLinks();
            registerSW();
            showPill();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
