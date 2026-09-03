/**
 * EthioBiz Isolated Brand Controller
 * Bismillah Ar-Rahman Ar-Rahim
 * 
 * Manages strict separation of Dagu, Magala, Walta, and Tibeb branding.
 * Handles logos, backgrounds, and colors dynamically.
 * 
 * © 2025 EthioBiz | Powered by Biz Technology Solutions
 */

(function () {
    'use strict';

    // BISMALLAH - Auto-clear stale PWA CacheStorage and force asset refresh
    if (window.caches) {
        try {
            caches.keys().then(function(names) {
                for (var i = 0; i < names.length; i++) {
                    if (names[i].indexOf('ethiobiz') !== -1 || names[i].indexOf('frappe') !== -1) {
                        caches.delete(names[i]);
                    }
                }
            });
        } catch (e) {}
    }

    if (window.__ethiobizBrandInitialized) return;
    if (document.querySelector('.web-form') || window.location.pathname.match(/\/(trial|new|edit)\//)) {
        window.__ethiobizBrandInitialized = true;
        return;
    }

    const BRAND_CONFIG = {
        app_name: "EthioBiz",
        default_logo: "/assets/bismillah_ethiobiz/images/ethiobiz-glass-logo.png",

        pillars: {
            dagu: {
                id: "dagu",
                name: "Dagu Learning",
                logo: "/assets/bismillah_ethiobiz/images/ethiobiz-glass-logo.png",
                primary: "#2E3A8C",
                rgb: "46, 58, 140",
                routes: ["lms", "education", "dagu"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light.png"
            },
            magala: {
                id: "magala",
                name: "Magala Market",
                logo: "/assets/bismillah_ethiobiz/images/ethiobiz-glass-logo.png",
                primary: "#2F6B4F",
                rgb: "47, 107, 79",
                routes: ["selling", "buying", "stock", "crm", "accounting", "magala", "all-products"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_website_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_light_bg.png"
            },
            walta: {
                id: "walta",
                name: "Walta Support",
                logo: "/assets/bismillah_ethiobiz/walta_real_logo.png",
                primary: "#0F3557",
                rgb: "15, 53, 87",
                routes: ["hr", "hrms", "payroll", "projects", "settings", "users", "walta", "helpdesk", "support"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light_1.jpeg"
            },
            tibeb: {
                id: "tibeb",
                name: "Tibeb",
                logo: "/assets/bismillah_ethiobiz/images/ethiobiz_logo.png",
                primary: "#C9A24D",
                rgb: "201, 162, 77",
                routes: ["tibeb"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light_1.jpeg"
            },
            dobiz: {
                id: "dobiz",
                name: "DOBiz Smart ERP",
                logo: "/assets/bismillah_ethiobiz/images/ethiobiz-glass-logo.png",
                primary: "#1FB6AE",
                rgb: "31, 182, 174",
                routes: ["app", "desk", "workspace"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light.png"
            }
        },

        default: {
            id: "ethiobiz",
            name: "EthioBiz",
            logo: "/assets/bismillah_ethiobiz/images/ethiobiz-glass-logo.png",
            primary: "#1FB6AE",
            rgb: "31, 182, 174",
            dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
            light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light.png"
        }
    };

    class BrandManager {
        constructor() {
            this.currentPillar = BRAND_CONFIG.default;
            this.initialized = false;
            this.contentObserver = null;
            this.textObserver = null;
        }

        init() {
            if (this.initialized) return;
            window.__ethiobizBrandInitialized = true;
            console.log('%c✨ EthioBiz Brand Manager Initializing...', 'color: #1FB6AE; font-weight: bold;');

            this.detectAndApply();

            if (typeof frappe !== 'undefined' && frappe.router) {
                frappe.router.on('change', () => this.detectAndApply());
            }
            if (typeof $ !== 'undefined') {
                $(document).on('page-change', () => this.detectAndApply());
            } else {
                document.addEventListener('page-change', () => this.detectAndApply());
            }

            this._routeCheckInterval = setInterval(() => {
                const route = this.getCurrentRoute();
                if (this.lastRoute !== route) {
                    this.lastRoute = route;
                    this.detectAndApply();
                }
            }, 3000);
            window.addEventListener('hashchange', () => this.detectAndApply());
            window.addEventListener('popstate', () => this.detectAndApply());

            this.initialized = true;

            // F. Global Sidebar Toggle (One-time registration via native delegation)
            document.addEventListener('click', (e) => {
                if (e.target.closest('.sidebar-toggle-btn, .toggle-sidebar')) {
                    document.body.classList.toggle('sidebar-collapsed');
                    const isNowCollapsed = document.body.classList.contains('sidebar-collapsed');
                    console.log('[EthioBiz] Sidebar Toggled. Collapsed:', isNowCollapsed);
                }
            });
        }

        getCurrentRoute() {
            const hash = window.location.hash.replace('#', '').toLowerCase();
            const path = window.location.pathname.toLowerCase();
            return hash || path;
        }

        detectAndApply() {
            const route = this.getCurrentRoute();

            if (route === '/' || route.includes('login') || route === '' || route.includes('ethiobiz_new') || route.includes('ethiobiz-new')) {
                this.currentPillar = BRAND_CONFIG.default;
                this.applyColorsOnly(this.currentPillar);
                return;
            }

            let matched = BRAND_CONFIG.default;
            for (let key in BRAND_CONFIG.pillars) {
                const p = BRAND_CONFIG.pillars[key];
                if (p.routes.some(r => route.includes(r))) {
                    matched = p;
                    break;
                }
            }

            this.currentPillar = matched;
            this.applyPillar();
        }

        applyPillar() {
            const p = this.currentPillar;
            console.log(`%c🎨 Applying Brand: ${p.name}`, `color: ${p.primary}; font-weight: bold;`);

            this.updateLogo(p.logo, p.name);
            this.updateColors(p.primary, p.rgb);
            this.updateBackground(p);
            this.setDocumentBranding(p);
            this.applyContentFixes(p);
        }

        applyColorsOnly(p) {
            this.updateColors(p.primary, p.rgb);
            this.updateBackground(p);
        }

        setDocumentBranding(p) {
            document.title = `${p.name} | ${BRAND_CONFIG.app_name}`;
            let themeColorMeta = document.querySelector('meta[name="theme-color"]');
            if (!themeColorMeta) {
                themeColorMeta = document.createElement('meta');
                themeColorMeta.name = 'theme-color';
                document.head.appendChild(themeColorMeta);
            }
            themeColorMeta.content = p.primary;

            let appleTitleMeta = document.querySelector('meta[name="apple-mobile-web-app-title"]');
            if (!appleTitleMeta) {
                appleTitleMeta = document.createElement('meta');
                appleTitleMeta.name = appleTitleMeta.id = 'apple-mobile-web-app-title';
                document.head.appendChild(appleTitleMeta);
            }
            appleTitleMeta.content = p.name;

            let appNameMeta = document.querySelector('meta[name="application-name"]');
            if (!appNameMeta) {
                appNameMeta = document.createElement('meta');
                appNameMeta.name = 'application-name';
                document.head.appendChild(appNameMeta);
            }
            appNameMeta.content = p.name;
        }

        applyContentFixes(p) {
            if (this.contentObserver) this.contentObserver.disconnect();
            if (this.textObserver) this.textObserver.disconnect();

            let _contentDebounce = false;
            this.contentObserver = new MutationObserver((mutations) => {
                if (_contentDebounce) return;
                _contentDebounce = true;
                requestAnimationFrame(() => {
                    if (window.location.href.includes('walta') || window.location.href.includes('helpdesk')) {
                        document.querySelectorAll('h1, h2, .onboarding-step-title, .desk-sidebar-item-label, .onboarding-step-description').forEach(el => {
                            if (el.innerText.includes('Frappe Helpdesk')) {
                                el.innerText = el.innerText.replace(/Frappe Helpdesk/g, 'Walta Support');
                            }
                        });
                    }
                    _contentDebounce = false;
                });
            });

            if (document.body) {
                this.contentObserver.observe(document.body, { childList: true, subtree: true });
            }

            if (window.location.href.includes('walta') || window.location.href.includes('helpdesk')) {
                const targetText = "Frappe Helpdesk";
                const replaceText = "Walta Support";

                const globalScrub = () => {
                    if (!document.body) return;
                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                    let node;
                    while (node = walker.nextNode()) {
                        if (node.nodeValue.includes(targetText)) {
                            node.nodeValue = node.nodeValue.replace(new RegExp(targetText, 'g'), replaceText);
                        }
                    }
                    if (typeof $ !== 'undefined') {
                        $(`div:contains("${targetText}"), span:contains("${targetText}"), h1:contains("${targetText}"), h2:contains("${targetText}")`).each(function () {
                            const contents = $(this).contents();
                            contents.each(function () {
                                if (this.nodeType === 3 && this.nodeValue.includes(targetText)) {
                                    this.nodeValue = this.nodeValue.replace(new RegExp(targetText, 'g'), replaceText);
                                }
                            });
                        });
                    }
                };

                let _textDebounce = false;
                this.textObserver = new MutationObserver(() => {
                    if (_textDebounce) return;
                    _textDebounce = true;
                    requestAnimationFrame(() => { globalScrub(); _textDebounce = false; });
                });
                if (document.body) {
                    this.textObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
                }

                let scrubCount = 0;
                const scrubInt = setInterval(() => {
                    globalScrub();
                    if (++scrubCount > 30) clearInterval(scrubInt);
                }, 2000);
            }

            // E. Dagu Specifics
            if (p.id === 'dagu') {
                const helpLinks = document.querySelectorAll('a[href*="help"]');
                helpLinks.forEach(link => {
                    link.href = '/walta/documentations';
                    link.innerText = 'Walta > Documentations';
                });
                document.querySelectorAll('.help-sidebar').forEach(el => el.style.display = 'none');
            }
        }

        updateLogo(src, alt) {
            const selectors = ['.navbar-brand img', '.app-logo', '#navbar-logo'];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(img => {
                    if (img.closest('.pillar-icon, .sub-icon, .detail-logo, .footer-brand, .legacy-image, .hero-logo, .loader-logo, .pillar-card, .sub-system-card, .final-cta, .detail-image, .hero-content, .ethiobiz-landing, #loading-screen')) return;
                    img.src = src;
                    img.alt = alt;
                    img.style.maxHeight = '35px';
                });
            });
        }

        updateColors(primary, rgb) {
            document.documentElement.style.setProperty('--primary-color', primary, 'important');
            document.documentElement.style.setProperty('--primary-rgb', rgb, 'important');

            let styleEl = document.getElementById('ethiobiz-dynamic-colors');
            if (!styleEl) {
                styleEl = document.createElement('style');
                styleEl.id = 'ethiobiz-dynamic-colors';
                document.head.appendChild(styleEl);
            }
            styleEl.textContent = `
                :root {
                    --primary: ${primary} !important;
                    --blue-500: ${primary} !important;
                    --btn-primary-bg: ${primary} !important;
                }
                .btn-primary, [data-action="primary"] {
                    background-color: ${primary} !important;
                    border-color: ${primary} !important;
                }
                a:not(.btn) { color: ${primary}; }
                .ce-toolbar__plus { background-color: ${primary} !important; }
            `;
        }

        updateBackground(p) {
            // Fix: Prioritize explicit data-theme over system preference
            const explicitTheme = document.documentElement.getAttribute('data-theme');
            const isDark = explicitTheme
                ? explicitTheme === 'dark'
                : window.matchMedia('(prefers-color-scheme: dark)').matches;

            const isWebsitePage = document.body.classList.contains('website-page') ||
                                  document.getElementById('page-container') !== null && !window.location.hash.includes('#app');

            // Read from cached theme settings (fetched by the API)
            const cached = window.__ethiobizThemeSettings || null;

            const masterBgEnabled = cached ? cached.enable_background_images : false;
            const deskBgEnabled   = cached ? cached.enable_desk_bg_image      : false;
            const webBgEnabled    = cached ? cached.enable_website_bg_image   : false;

            // Determine if bg image should be applied for this context
            const bgImagesEnabled = masterBgEnabled && (isWebsitePage ? webBgEnabled : deskBgEnabled);

            let styleEl = document.getElementById('ethiobiz-nuclear-bg');
            if (!styleEl) {
                styleEl = document.createElement('style');
                styleEl.id = 'ethiobiz-nuclear-bg';
                document.head.appendChild(styleEl);
            }

            if (bgImagesEnabled) {
                const bgUrl = isDark ? p.dark_bg : p.light_bg;
                styleEl.textContent = `
                    html, body {
                        background-image: url("${bgUrl}") !important;
                        background-attachment: fixed !important;
                        background-size: cover !important;
                        background-position: center !important;
                        background-color: ${isDark ? '#0E1A1A' : '#F8FAFC'} !important;
                    }
                    #app, .desk-container, .layout-main, .page-container, .workspace-page, .form-page, .content, #page-container, .layout-main-section-wrapper {
                        background: transparent !important;
                        background-color: transparent !important;
                    }
                    [data-theme="light"] .dropdown-menu {
                        background: rgba(255,255,255,0.9) !important;
                        color: black !important;
                    }
                    [data-theme="light"] .dropdown-item { color: black !important; }
                `;
            } else {
                // Ultra-fast pure CSS gradient atmosphere with zero image load delay
                styleEl.textContent = `
                    html, body {
                        background: ${isDark ? 'var(--ethiobiz-atmosphere-dark, radial-gradient(ellipse 80% 50% at 20% -10%, rgba(31, 182, 174, 0.18) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 85% 105%, rgba(46, 58, 140, 0.22) 0%, transparent 60%), linear-gradient(135deg, #0A1118 0%, #0D1B1E 40%, #0E1A1A 70%, #081014 100%))' : 'var(--ethiobiz-atmosphere-bright, radial-gradient(ellipse 80% 60% at 15% 0%, rgba(31, 182, 174, 0.09) 0%, transparent 50%), radial-gradient(ellipse 70% 50% at 85% 100%, rgba(46, 58, 140, 0.07) 0%, transparent 50%), linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 45%, #E9ECEF 100%))'} !important;
                        background-attachment: fixed !important;
                        background-size: cover !important;
                        background-position: center !important;
                    }
                    #app, .desk-container, .layout-main, .page-container, .workspace-page, .form-page, .content, #page-container, .layout-main-section-wrapper {
                        background: transparent !important;
                        background-color: transparent !important;
                    }
                    [data-theme="light"] .dropdown-menu {
                        background: rgba(255,255,255,0.9) !important;
                        color: black !important;
                    }
                    [data-theme="light"] .dropdown-item { color: black !important; }
                `;
            }
        }
    }

    // ─── Fetch & cache Theme Settings from API ───────────────────────────────
    function fetchAndCacheThemeSettings(callback) {
        if (window.__ethiobizThemeSettings) {
            if (callback) callback(window.__ethiobizThemeSettings);
            return;
        }
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/method/bismillah_ethiobiz.api.get_theme_settings', true);
        xhr.onload = function() {
            try {
                var res = JSON.parse(xhr.responseText);
                var s = (res && res.message) || {};
                window.__ethiobizThemeSettings = s;
                // Expose desk animation flag for particles.js too
                window.__ethiobizDeskAnimEnabled = s.enable_desk_animation !== false;
                if (callback) callback(s);
            } catch(e) {
                window.__ethiobizThemeSettings = {};
                if (callback) callback({});
            }
        };
        xhr.onerror = function() {
            window.__ethiobizThemeSettings = {};
            if (callback) callback({});
        };
        xhr.send();
    }

    window.EthioBizBrandManager = new BrandManager();

    // Fetch settings first, then init so updateBackground has correct flags
    fetchAndCacheThemeSettings(function() {
        window.EthioBizBrandManager.init();
    });

})();

// BISMALLAH ETHIOBIZ FLOATING SIDEBAR V6
(function() {
    function initSidebar() {
        if (typeof frappe === 'undefined') return;
        if (document.querySelector('.web-form')) return;

    // Block "Try the new Print Designer" at source BEFORE it reaches DOM
    // Override frappe Page prototype add_inner_message
    if (frappe.ui && frappe.ui.Page) {
        var _origAddInner = frappe.ui.Page.prototype.add_inner_message;
        frappe.ui.Page.prototype.add_inner_message = function (msg) {
            if (msg && typeof msg === 'string' && msg.indexOf('Print Designer') !== -1) {
                return $(document.createElement('span')).addClass('inner-page-message text-muted small').hide();
            }
            return _origAddInner.call(this, msg);
        };
    }

    console.log('[EthioBiz] V6 Sidebar Init via Theme - ' + new Date().toISOString());

    const css = `
        :root { --sidebar-width: 230px; }
        
        /* 1. Glassmorphism & Floating - DARK MODE COMPATIBLE */
        .layout-side-section {
            background-color: rgba(14, 26, 26, 0.85) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255,255,255,0.1) !important;
            box-shadow: 10px 0 25px rgba(0,0,0,0.3) !important;
            z-index: 1001 !important;
            position: fixed !important; 
            height: 100vh !important;
            top: 0 !important;
            left: 0 !important;
            width: var(--sidebar-width) !important;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            overflow-y: auto !important;
            padding-top: 50px !important;
        }
        
        /* Light mode sidebar override */
        [data-theme="light"] .layout-side-section {
            background-color: rgba(255, 255, 255, 0.75) !important;
            border-right: 1px solid rgba(0,0,0,0.1) !important;
            box-shadow: 10px 0 25px rgba(0,0,0,0.05) !important;
        }


        /* Collapsed State */
        body.sidebar-collapsed .layout-side-section {
            transform: translateX(-100%) !important;
        }
        body:not(.sidebar-collapsed) .layout-side-section {
            transform: translateX(0) !important;
        }
        
        /* Main Content Shift (Desktop) */
        @media (min-width: 992px) {
            body.sidebar-collapsed .layout-main-section {
                margin-left: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
            }
            body:not(.sidebar-collapsed) .layout-main-section {
                margin-left: var(--sidebar-width) !important;
                width: calc(100% - var(--sidebar-width)) !important;
            }
        }

        /* 2. Toggle Button (GitHub Style) */
        #ethio-toggle-btn {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 4px !important;
            margin-right: 12px !important;
            cursor: pointer !important;
            color: var(--text-color) !important;
            background: rgba(0,0,0,0.05) !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            border-radius: 6px !important;
            height: 32px !important;
            width: 32px !important;
            transition: all 0.2s !important;
            flex-shrink: 0 !important;
        }
        #ethio-toggle-btn:hover { 
            background-color: rgba(0,0,0,0.1) !important; 
            transform: scale(1.05) !important;
        }
        
        /* 3. Close Button */
        #ethio-sidebar-close {
            position: absolute !important;
            top: 10px !important;
            right: 10px !important;
            width: 30px !important;
            height: 30px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            background: rgba(255,255,255,0.7) !important;
            color: #555 !important;
            transition: all 0.2s !important;
            z-index: 9999 !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
        }
        #ethio-sidebar-close:hover { 
            background: rgba(255,0,0,0.15) !important; 
            color: red !important;
        }
        
        /* 4. Mobile Fixes */
        @media (max-width: 991px) {
            .layout-side-section {
                width: 85% !important;
                max-width: 300px !important;
                transform: translateX(-100%) !important; /* Hidden by default on mobile */
            }
            
            /* Show sidebar when active */
            body.sidebar-mobile-open .layout-side-section {
                transform: translateX(0) !important;
            }
            
            /* Overlay for mobile */
            .ethio-mobile-overlay {
                display: none !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                background: rgba(0,0,0,0.5) !important;
                z-index: 1000 !important;
            }
            
            body.sidebar-mobile-open .ethio-mobile-overlay {
                display: block !important;
            }
            
            .layout-side-section .sidebar-menu,
            .layout-side-section .desk-sidebar {
                padding-left: 10px !important;
                padding-right: 10px !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            
            .layout-side-section .standard-sidebar-item,
            .layout-side-section a,
            .layout-side-section .sidebar-label {
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                max-width: 100% !important;
                display: block !important;
                padding: 12px 8px !important; /* Larger touch targets */
                font-size: 16px !important; /* Larger text for mobile */
            }
            
            .layout-side-section > * {
                max-width: 100% !important;
                overflow-x: hidden !important;
            }
            
            /* Mobile hamburger button */
            #ethio-mobile-hamburger {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 40px !important;
                height: 40px !important;
                margin-right: 12px !important;
                cursor: pointer !important;
                background: rgba(0,0,0,0.05) !important;
                border: 1px solid rgba(0,0,0,0.1) !important;
                border-radius: 8px !important;
                color: var(--text-color) !important;
            }
            
            #ethio-mobile-hamburger:hover {
                background: rgba(0,0,0,0.1) !important;
            }
            
            /* Hide desktop toggle on mobile */
            #ethio-toggle-btn {
                display: none !important;
            }
        }
        
        /* Desktop: hide mobile hamburger */
        @media (min-width: 992px) {
            #ethio-mobile-hamburger {
                display: none !important;
            }
        }
    `;

    // Inject CSS
    const style = document.createElement('style');
    style.id = 'ethio-sidebar-style-v6';
    style.innerHTML = css;
    if (!document.getElementById('ethio-sidebar-style-v6')) {
        document.head.appendChild(style);
    }

    function forceUI() {
        // A. Mobile Hamburger Button (for mobile devices)
        const brand = document.querySelector('.navbar-brand');
        if (brand && brand.parentElement && !document.getElementById('ethio-mobile-hamburger')) {
            const mobileBtn = document.createElement('div');
            mobileBtn.id = 'ethio-mobile-hamburger';
            mobileBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`;
            mobileBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                document.body.classList.toggle('sidebar-mobile-open');
                console.log('[EthioBiz] Mobile sidebar toggled');
            };
            brand.parentElement.insertBefore(mobileBtn, brand);
            console.log('[EthioBiz] Mobile hamburger button injected');
        }

        // B. Desktop Toggle Button (for desktop)
        if (brand && brand.parentElement && !document.getElementById('ethio-toggle-btn')) {
            const btn = document.createElement('div');
            btn.id = 'ethio-toggle-btn';
            btn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`;
            btn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                document.body.classList.toggle('sidebar-collapsed');
            };
            brand.parentElement.insertBefore(btn, brand);
            console.log('[EthioBiz] Desktop toggle button injected');
        }
        
        // C. Mobile Overlay (for closing sidebar when clicking outside)
        if (!document.getElementById('ethio-mobile-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'ethio-mobile-overlay';
            overlay.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                document.body.classList.remove('sidebar-mobile-open');
                console.log('[EthioBiz] Mobile sidebar closed via overlay');
            };
            document.body.appendChild(overlay);
            console.log('[EthioBiz] Mobile overlay injected');
        }

        // D. Close Button (works for both desktop and mobile)
        const sidebar = document.querySelector('.layout-side-section');
        if (sidebar && !document.getElementById('ethio-sidebar-close')) {
            const closeBtn = document.createElement('div');
            closeBtn.id = 'ethio-sidebar-close';
            closeBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;
            closeBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                document.body.classList.add('sidebar-collapsed');
                document.body.classList.remove('sidebar-mobile-open');
                console.log('[EthioBiz] Sidebar closed (both modes)');
            };
            sidebar.insertBefore(closeBtn, sidebar.firstChild);
            console.log('[EthioBiz] Close button injected');
        }
        // E. Hide Dagu LMS Popup (Right Panel & Sidebar)
        // Right Panel
        const rightPanels = document.querySelectorAll('.fixed.right-0, .bg-surface-modal');
        rightPanels.forEach(el => {
            if (el && el.innerText && el.innerText.includes('Welcome to Dagu Learning')) {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.setAttribute('style', 'display: none !important; visibility: hidden !important;');
            }
        });

        const gettingStartedDivs = document.querySelectorAll('.bg-surface-white div, .rounded-lg div, .onboarding-step-title');
        gettingStartedDivs.forEach(el => {
            if (el.innerText === 'Getting started' && el.nextElementSibling && el.nextElementSibling.innerText.includes('Continue')) {
                let parent = el.parentElement;
                while (parent && parent !== document.body) {
                    if (parent.tagName === 'DIV' && (parent.classList.contains('bg-surface-white') || parent.classList.contains('rounded-lg'))) {
                        parent.style.display = 'none';
                        break;
                    }
                    parent = parent.parentElement;
                }
            }
        });

        // F. Hide Navbar Help Dropdown Third-Party Items (Frappe School, Support, Forum, Docs)
        const helpDropdown = document.querySelector('.dropdown-help .dropdown-menu, #help-menu, .navbar-nav .dropdown-menu');
        if (helpDropdown) {
            const thirdPartyLabels = ['Frappe School', 'Frappe Support', 'User Forum', 'Documentation', 'Report an Issue'];
            helpDropdown.querySelectorAll('.dropdown-item, a').forEach(function(item) {
                var text = (item.textContent || '').trim();
                if (thirdPartyLabels.indexOf(text) !== -1 || 
                    (item.href && (item.href.indexOf('frappe') !== -1 || item.href.indexOf('erpnext') !== -1 || item.href.indexOf('discuss.') !== -1))) {
                    item.style.display = 'none';
                    item.classList.add('ethiobiz-hidden');
                }
            });
        }

    }

    let sidebarObserver = null;
    let _forceUIPending = false;

    // --- EthioBiz Theme settings bridge (ANFRG-26-00063 Task B) ---
    const CONF_URL = '/api/method/bizmarketing.api.theme_settings.public_theme_settings';
    const CONF_KEY = 'ethiobizThemeConf';

    function readConfCache() {
        try {
            const raw = sessionStorage.getItem(CONF_KEY);
            if (!raw) return null;
            const conf = JSON.parse(raw);
            if (!conf || Date.now() - (conf._t || 0) > 600000) return null;
            return conf;
        } catch (e) { return null; }
    }

    function saveConfCache(conf) {
        try {
            conf._t = Date.now();
            sessionStorage.setItem(CONF_KEY, JSON.stringify(conf));
        } catch (e) { /* ignore */ }
    }

    function applySidebarPolicy(conf) {
        forceUI();
        if (conf && conf.hide_sidebar === false) {
            document.body.classList.remove('sidebar-collapsed');
            console.log('[EthioBiz] Sidebar ENABLED via EthioBiz Theme settings');
            return;
        }
        if (document.querySelector('.desk-container')) {
            let collapseCount = 0;
            let collapseInterval = setInterval(() => {
                if (!document.body.classList.contains('sidebar-collapsed')) {
                    document.body.classList.add('sidebar-collapsed');
                    console.log('[EthioBiz] Forced collapse');
                }
                if (++collapseCount > 15) clearInterval(collapseInterval);
            }, 200);
        }
    }

    function init() {
        const cached = readConfCache();
        if (cached) { applySidebarPolicy(cached); return; }
        fetch(CONF_URL)
            .then(r => r.json())
            .then(res => {
                const conf = (res && res.message) || {};
                saveConfCache(conf);
                applySidebarPolicy(conf);
            })
            .catch(() => applySidebarPolicy({}));
    }

    if (sidebarObserver) sidebarObserver.disconnect();
    sidebarObserver = new MutationObserver(() => {
        if (!_forceUIPending) {
            _forceUIPending = true;
            requestAnimationFrame(() => {
                forceUI();
                _forceUIPending = false;
            });
        }
    });

    init();
    if (document.body) {
        sidebarObserver.observe(document.body, { childList: true, subtree: true });
    }
}

if (typeof frappe !== 'undefined' && frappe.ready) {
    frappe.ready(initSidebar);
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    initSidebar();
}
})();
// END BISMALLAH ETHIOBIZ FLOATING SIDEBAR V6
