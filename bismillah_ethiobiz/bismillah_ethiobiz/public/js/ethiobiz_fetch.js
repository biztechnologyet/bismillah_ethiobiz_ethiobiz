/**
 * Bismillah — EthioBiz central fetch helper (InSha'Allah)
 * ANFRG-26-00063 Phase 15: fixes Walta forum / Afocha social authenticated
 * POSTs that failed silently because the X-Frappe-CSRF-Token header was
 * missing. Loaded FIRST via web_include_js so page inline scripts can use it.
 *
 *   ebFetch(url, options)  -> Promise<Response>  (adds CSRF header on non-GET)
 *   ebToast(message)       -> user-visible error surface (no more silent fails)
 */
(function () {
  "use strict";

  if (window.ebFetch) return;

  window.ebCsrfToken = function () {
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;
    var match = document.cookie.match(/csrf_token=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
  };

  window.ebToast = function (message, isError) {
    try {
      var id = "eb-toast-holder";
      var holder = document.getElementById(id);
      if (!holder) {
        holder = document.createElement("div");
        holder.id = id;
        holder.style.cssText =
          "position:fixed;bottom:18px;left:50%;transform:translateX(-50%);" +
          "z-index:99999;display:flex;flex-direction:column;gap:8px;" +
          "pointer-events:none;max-width:92vw;";
        document.body.appendChild(holder);
      }
      var t = document.createElement("div");
      t.style.cssText =
        "background:" + (isError === false ? "#0d9488" : "#b91c1c") + ";" +
        "color:#fff;padding:10px 16px;border-radius:10px;font-size:13px;" +
        "font-weight:600;box-shadow:0 6px 18px rgba(0,0,0,.25);opacity:0;" +
        "transition:opacity .25s;text-align:center;";
      t.textContent = String(message || "").slice(0, 220);
      holder.appendChild(t);
      requestAnimationFrame(function () { t.style.opacity = "1"; });
      setTimeout(function () {
        t.style.opacity = "0";
        setTimeout(function () { t.remove(); }, 300);
      }, 4500);
    } catch (e) { /* never break the caller */ }
  };

  window.ebFetch = function (url, options) {
    options = options || {};
    options.headers = Object.assign({}, options.headers || {});
    options.credentials = options.credentials || "same-origin";
    var method = (options.method || "GET").toUpperCase();
    if (method !== "GET" && !options.headers["X-Frappe-CSRF-Token"]) {
      var token = window.ebCsrfToken();
      if (token) options.headers["X-Frappe-CSRF-Token"] = token;
    }
    return fetch(url, options).catch(function (err) {
      console.error("[ebFetch] network failure:", err);
      window.ebToast("Network problem — please check your connection and retry.");
      throw err;
    });
  };

  /**
   * Convenience for the common API shape used by Walta/Afocha pages:
   * posts form-encoded data, parses JSON, toasts server exceptions,
   * resolves with parsed body (or null).
   */
  window.ebPostForm = function (apiMethod, params) {
    var body = new URLSearchParams(params || {});
    return window.ebFetch("/api/method/" + apiMethod, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body
    }).then(function (r) {
      return r.json().catch(function () { return null; }).then(function (j) {
        if (!r.ok || (j && j.exc)) {
          var msg = (j && j._server_messages &&
            JSON.parse(j._server_messages).join(" ")) ||
            (j && j.exception) ||
            "Action failed — are you logged in?";
          window.ebToast(String(msg).replace(/<[^>]*>/g, " ").trim());
        }
        return j;
      });
    });
  };
})();
