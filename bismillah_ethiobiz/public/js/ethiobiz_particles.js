/**
 * Bismillah — EthioBiz site-wide ambient background (InSha'Allah)
 * Extracted from the home Web Page constellation engine (ANFRG-26-00063 Task C).
 * - Site-wide: creates the ambient wrapper + canvas on every website page.
 * - Slightly slower than the original (SPEED_FACTOR baseline 0.7).
 * - Gated by EthioBiz Theme settings via bizmarketing.api.theme_settings.
 *   public_theme_settings (enable_website_animation, website_animation_speed).
 * - Respects prefers-reduced-motion; pauses when the tab is hidden.
 */
(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (window.__ETHIOBIZ_AMBIENT__) return;

  var BASELINE_SPEED_FACTOR = 0.7;
  var SPEED_FACTORS = { Slow: 0.45, Normal: 0.7, Fast: 0.95 };
  var CONF_URL =
    "/api/method/bizmarketing.api.theme_settings.public_theme_settings";
  var CACHE_KEY = "ethiobizThemeConf";

  function readCache() {
    try {
      var raw = sessionStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      var conf = JSON.parse(raw);
      if (!conf || Date.now() - (conf._t || 0) > 600000) return null;
      return conf;
    } catch (e) {
      return null;
    }
  }

  function writeCache(conf) {
    try {
      conf._t = Date.now();
      sessionStorage.setItem(CACHE_KEY, JSON.stringify(conf));
    } catch (e) { /* private mode — ignore */ }
  }

  function fetchConf(cb) {
    var cached = readCache();
    if (cached) return cb(cached);
    var xhr = new XMLHttpRequest();
    xhr.open("GET", CONF_URL, true);
    xhr.onload = function () {
      var conf = {};
      try {
        var res = JSON.parse(xhr.responseText);
        conf = (res && res.message) || {};
      } catch (e) { /* fall through to defaults */ }
      writeCache(conf);
      cb(conf);
    };
    xhr.onerror = function () {
      cb({ enable_website_animation: false, animation_speed_factor: BASELINE_SPEED_FACTOR });
    };
    xhr.send();
  }

  function injectCss() {
    if (document.getElementById("ethio-ambient-css")) return;
    var style = document.createElement("style");
    style.id = "ethio-ambient-css";
    style.textContent =
      "#ambient-canvas-wrapper{position:fixed;top:0;left:0;width:100vw;height:100vh;" +
      "pointer-events:none;z-index:0;overflow:hidden}" +
      "#ethio-canvas{width:100%;height:100%;display:block;opacity:.85}" +
      ".aurora-blob{position:absolute;border-radius:50%;filter:blur(90px);opacity:.35}" +
      ".aurora-blob-1{width:44vw;height:44vw;left:-10vw;top:-12vw;background:radial-gradient(circle,rgba(13,148,136,.55),transparent 65%);animation:aurora-drift-1 26s ease-in-out infinite alternate}" +
      ".aurora-blob-2{width:38vw;height:38vw;right:-8vw;top:22vh;background:radial-gradient(circle,rgba(245,158,11,.4),transparent 65%);animation:aurora-drift-2 32s ease-in-out infinite alternate}" +
      ".aurora-blob-3{width:30vw;height:30vw;left:28vw;bottom:-14vh;background:radial-gradient(circle,rgba(56,189,248,.4),transparent 65%);animation:aurora-drift-3 29s ease-in-out infinite alternate}" +
      "@keyframes aurora-drift-1{to{transform:translate(6vw,4vh) scale(1.08)}}" +
      "@keyframes aurora-drift-2{to{transform:translate(-5vw,-3vh) scale(.94)}}" +
      "@keyframes aurora-drift-3{to{transform:translate(4vw,-5vh) scale(1.06)}}" +
      "[data-theme='light'] #ethio-canvas{opacity:.45}" +
      "[data-theme='light'] .aurora-blob-1{background:radial-gradient(circle,rgba(13,148,136,.28),transparent 65%)}" +
      "[data-theme='light'] .aurora-blob-2{background:radial-gradient(circle,rgba(99,102,241,.22),transparent 65%)}" +
      "[data-theme='light'] .aurora-blob-3{background:radial-gradient(circle,rgba(59,130,246,.22),transparent 65%)}";
    document.head.appendChild(style);
  }

  function ensureDom() {
    var wrapper = document.getElementById("ambient-canvas-wrapper");
    if (!wrapper) {
      wrapper = document.createElement("div");
      wrapper.id = "ambient-canvas-wrapper";
      for (var i = 1; i <= 3; i++) {
        var blob = document.createElement("div");
        blob.className = "aurora-blob aurora-blob-" + i;
        wrapper.appendChild(blob);
      }
      var canvas = document.createElement("canvas");
      canvas.id = "ethio-canvas";
      wrapper.appendChild(canvas);
      document.body.insertBefore(wrapper, document.body.firstChild);
    }
    return document.getElementById("ethio-canvas");
  }

  function startEngine(canvas, speedFactor) {
    if (canvas.dataset.ethioAmbientRunning) return;
    canvas.dataset.ethioAmbientRunning = "1";

    var ctx = canvas.getContext("2d");
    var width = 0;
    var height = 0;
    var particles = [];
    var rafId = null;

    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    }
    window.addEventListener("resize", resize);
    resize();

    var particleCount = Math.min(Math.floor(window.innerWidth / 24), 60);
    var colors = [
      "rgba(0, 128, 128, 0.45)",
      "rgba(245, 158, 11, 0.35)",
      "rgba(56, 189, 248, 0.35)",
      "rgba(13, 148, 136, 0.4)"
    ];

    for (var i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.45 * speedFactor,
        vy: (Math.random() - 0.5) * 0.45 * speedFactor,
        radius: Math.random() * 2.2 + 1,
        color: colors[Math.floor(Math.random() * colors.length)]
      });
    }

    function render() {
      ctx.clearRect(0, 0, width, height);
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();

        for (var j = i + 1; j < particles.length; j++) {
          var p2 = particles[j];
          var dx = p.x - p2.x;
          var dy = p.y - p2.y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 110) {
            ctx.beginPath();
            ctx.strokeStyle = "rgba(0, 128, 128, " + 0.15 * (1 - dist / 110) + ")";
            ctx.lineWidth = 0.8;
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }
      rafId = requestAnimationFrame(render);
    }

    function play() {
      if (rafId === null) rafId = requestAnimationFrame(render);
    }
    function pause() {
      if (rafId !== null) {
        cancelAnimationFrame(rafId);
        rafId = null;
      }
    }
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) pause(); else play();
    });
    play();
  }

  function boot(conf) {
    if (conf.enable_website_animation === false) {
      console.log("[EthioBiz] Ambient background disabled by settings");
      return;
    }
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      console.log("[EthioBiz] Ambient background skipped (reduced motion)");
      return;
    }
    var raw = SPEED_FACTORS[conf.website_animation_speed];
    var factor =
      typeof conf.animation_speed_factor === "number"
        ? conf.animation_speed_factor
        : (typeof raw === "number" ? raw : BASELINE_SPEED_FACTOR);
    injectCss();
    var canvas = ensureDom();
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        startEngine(ensureDom(), factor);
      });
    } else {
      startEngine(canvas, factor);
    }
    console.log("[EthioBiz] Ambient background live (speed x" + factor + ")");
  }

  fetchConf(boot);
  window.__ETHIOBIZ_AMBIENT__ = true;
})();
