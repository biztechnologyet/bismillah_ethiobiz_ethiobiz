/**
 * DOBiz Smart ERP - Service Worker (server-rendered from DOBiz PWA Settings)
 * Bismillah Ar-Rahman Ar-Rahim
 *
 * Strategy:
 *  - Navigations ......... network-first, fallback to cache, then offline page
 *  - /api/* & /app/method  network-only (never stale auth/CSRF)
 *  - /assets/* ............ cache-first (hashed/versioned bundles) + background refresh
 *  - everything else ...... network-only with cached fallback when offline
 */
"use strict";

var VERSION = "__CACHE_VERSION__";
var CACHE = "dobiz-pwa-v" + VERSION;
var OFFLINE_URL = "__OFFLINE_URL__";
var OFFLINE_TITLE = "__OFFLINE_TITLE__";
var OFFLINE_MESSAGE = "__OFFLINE_MESSAGE__";
var APP_NAME = "__APP_SHORT_NAME__";

var HASHED_BUNDLE = /\/assets\/.+?\/(dist|bundle|js|css)\/.+\.(js|css|png|jpg|jpeg|svg|webp|woff2?)$/;

function isNavigation(request) {
    return request.mode === "navigate" || (request.method === "GET" && request.headers.get("accept") && request.headers.get("accept").indexOf("text/html") !== -1);
}

function isApi(request) {
    var url = new URL(request.url);
    return url.pathname.indexOf("/api/") === 0 || url.pathname.indexOf("/app/method/") === 0;
}

function isAsset(request) {
    var url = new URL(request.url);
    return url.pathname.indexOf("/assets/") === 0;
}

function isAppPage(request) {
    var url = new URL(request.url);
    return url.pathname === "/" || url.pathname.indexOf("/app") === 0 || url.pathname.indexOf("/login") === 0;
}

function offlinePage() {
    var body = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>", APP_NAME, " - ", OFFLINE_TITLE, "</title>",
        "<style>",
        "*{margin:0;padding:0;box-sizing:border-box}",
        "body{min-height:100vh;display:flex;align-items:center;justify-content:center;",
        "background:radial-gradient(1200px 600px at 50% -10%,rgba(31,182,174,.35),transparent 60%),#0E1A1A;",
        "color:#F8FAFA;font-family:-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;text-align:center}",
        ".card{padding:48px 32px;max-width:420px}",
        "img{width:96px;height:96px;border-radius:24px;box-shadow:0 12px 40px rgba(0,0,0,.45)}",
        "h1{margin:24px 0 8px;font-size:24px;font-weight:700}",
        "p{color:#9FB3B8;font-size:15px;line-height:1.5}",
        "button{margin-top:28px;padding:12px 28px;border:0;border-radius:999px;background:#1FB6AE;color:#fff;",
        "font-size:15px;font-weight:600;cursor:pointer}",
        "button:hover{background:#18a49c}",
        "</style></head><body><div class=\"card\">",
        '<img src="/assets/bismillah_ethiobiz/pwa/icons/icon-192.png" alt="', APP_NAME, '">',
        "<h1>", OFFLINE_TITLE, "</h1><p>", OFFLINE_MESSAGE, "</p>",
        "<button onclick=\"location.reload()\">Retry</button>",
        "</div></body></html>"
    ].join("");
    return new Response(body, {
        status: 503,
        headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" }
    });
}

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE)
            .then(function (cache) {
                var requests = [OFFLINE_URL];
                return cache.addAll(requests);
            })
            .then(function () {
                return self.skipWaiting();
            })
            .catch(function () {
                return self.skipWaiting();
            })
    );
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys()
            .then(function (keys) {
                return Promise.all(
                    keys
                        .filter(function (k) { return k.indexOf("dobiz-pwa-v") === 0 && k !== CACHE; })
                        .map(function (k) { return caches.delete(k); })
                );
            })
            .then(function () {
                return self.clients.claim();
            })
    );
});

function networkFirst(request) {
    return fetch(request)
        .then(function (response) {
            if (response && response.ok) {
                var copy = response.clone();
                caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
            }
            return response;
        })
        .catch(function () {
            return caches.match(request).then(function (cached) {
                return cached || offlinePage();
            });
        });
}

function cacheFirst(request) {
    return caches.match(request).then(function (cached) {
        if (cached) {
            fetch(request)
                .then(function (response) {
                    if (response && response.ok) {
                        var copy = response.clone();
                        caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
                    }
                })
                .catch(function () {});
            return cached;
        }
        return fetch(request).then(function (response) {
            if (response && response.ok) {
                var copy = response.clone();
                caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
            }
            return response;
        });
    });
}

function networkWithFallback(request) {
    return fetch(request).catch(function () {
        return caches.match(request).then(function (cached) {
            return cached || (isNavigation(request) ? offlinePage() : Response.error());
        });
    });
}

self.addEventListener("fetch", function (event) {
    var request = event.request;
    if (request.method !== "GET") return;

    var url = new URL(request.url);
    if (url.origin !== location.origin) return;

    if (isApi(request)) {
        return;
    }

    if (isNavigation(request)) {
        event.respondWith(networkFirst(request));
        return;
    }

    if (isAsset(request)) {
        event.respondWith(cacheFirst(request));
        return;
    }

    if (isAppPage(request)) {
        event.respondWith(networkFirst(request));
        return;
    }

    event.respondWith(networkWithFallback(request));
});
