/**
 * DOBiz PWA - Registration
 * Bismillah Ar-Rahman Ar-Rahim
 *
 * Injects the manifest link + theme-color, registers /sw.js at scope "/",
 * and shows a themed "Install DOBiz" prompt on /app routes.
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

    function injectManifest() {
        if (document.querySelector('link[rel="manifest"]')) return;
        var link = document.createElement("link");
        link.rel = "manifest";
        link.href = "/manifest.webmanifest";
        document.head.appendChild(link);

        if (!document.querySelector('meta[name="theme-color"]')) {
            var meta = document.createElement("meta");
            meta.name = "theme-color";
            meta.content = config.theme_color;
            document.head.appendChild(meta);
        }
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

        pill = document.createElement("button");
        pill.textContent = "Install DOBiz SmartERP";
        pill.setAttribute("type", "button");
        pill.style.cssText = [
            "position:fixed", "left:24px", "bottom:24px", "z-index:99999",
            "display:inline-flex", "align-items:center", "gap:8px",
            "padding:12px 22px", "border:0", "border-radius:999px",
            "background:linear-gradient(135deg,#1FB6AE,#149a93)", "color:#fff",
            "font-size:14px", "font-weight:600", "font-family:inherit",
            "cursor:pointer", "box-shadow:0 8px 28px rgba(0,0,0,.35)",
            "transition:transform .15s ease, box-shadow .15s ease"
        ].join(";");
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
        hidePill();
    });

    function boot() {
        injectManifest();
        loadConfig().then(function () {
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
