/* EthioBiz GA4 loader - single source of truth.
 * Loaded on website pages and desk. Safe against double-loading. */
(function () {
  "use strict";
  var ID = "G-HCTLQ3QN5R";
  if (window.__ethiobizGA4) return;
  window.__ethiobizGA4 = true;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(s);

  gtag("js", new Date());
  gtag("config", ID);

  var last = location.href;
  function onRoute() {
    if (location.href === last) return;
    last = location.href;
    gtag("event", "page_view", {
      page_location: location.href,
      page_title: document.title
    });
  }
  ["pushState", "replaceState"].forEach(function (m) {
    var orig = history[m];
    history[m] = function () {
      var r = orig.apply(this, arguments);
      onRoute();
      return r;
    };
  });
  window.addEventListener("popstate", onRoute);

  window.ethiobizTrack = function (name, params) {
    if (typeof gtag === "function") gtag("event", name, params || {});
  };
})();