/**
 * EthioBiz Isolated Brand Controller
 * Bismillah Ar-Rahman Ar-Rahim
 * 
 * Manages strict separation of Dagu, Magala, Walta, and Tibeb branding.
 * Handles logos, backgrounds, and colors dynamically.
 * 
 * ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â© 2025 EthioBiz | Powered by Biz Technology Solutions
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

    // BISMALLAH (2026-09-10): custom icons from EthioBiz Theme Settings override
    // the pillar/default logo. The default (fallback) logo is used ONLY when no
    // custom icon is set, so updateLogo never reverts a configured icon.
    let ethiobizCustomIcons = { website: '', desk: '' };

    // BISMALLAH (2026-09-10): optional dark-mode label color from Theme Settings.
    let ethiobizDarkLabelColor = '';

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
            console.log('%cÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“Ãƒâ€šÃ‚Â¨ EthioBiz Brand Manager Initializing...', 'color: #1FB6AE; font-weight: bold;');

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
                    if (typeof window.ethiobizToggleSidebar === 'function') {
                        window.ethiobizToggleSidebar();
                    } else {
                        document.body.classList.toggle('sidebar-collapsed');
                    }
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
            console.log(`%cÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€¦Ã‚Â½Ãƒâ€šÃ‚Â¨ Applying Brand: ${p.name}`, `color: ${p.primary}; font-weight: bold;`);

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
            const appName = BRAND_CONFIG.app_name || 'EthioBiz';
            const currentTitle = (document.title || '').trim();
            const genericTitles = ['', appName, `${appName} | ${appName}`, 'Home', 'Shop', 'Login', 'Cart'];
            if (!window.ETHIOBIZ_PRESERVE_TITLE && genericTitles.includes(currentTitle)) {
                document.title = `${p.name} | ${appName}`;
            }
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
            const isDesk = !!(document.body &&
                (document.body.classList.contains('desk-page') ||
                 document.querySelector('.desk-sidebar') ||
                 document.querySelector('.layout-side-section')));
            // BISMALLAH: a configured Theme icon wins over the pillar/default logo.
            const custom = isDesk ? ethiobizCustomIcons.desk : ethiobizCustomIcons.website;
            const effectiveSrc = custom || src;
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(img => {
                    if (img.closest('.pillar-icon, .sub-icon, .detail-logo, .footer-brand, .legacy-image, .hero-logo, .loader-logo, .pillar-card, .sub-system-card, .final-cta, .detail-image, .hero-content, .ethiobiz-landing, #loading-screen')) return;
                    img.src = effectiveSrc;
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

            const isWebsitePage = !!(document.body && document.body.classList.contains('website-page')) ||
                                  (document.getElementById('page-container') !== null && !window.location.hash.includes('#app'));

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

    // ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Fetch & cache Theme Settings from API ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬
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

    // ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Apply Website / Desk icons from EthioBiz Theme Settings ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬
    // BISMALLAH (2026-09-10): custom icons are optional ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â empty settings keep
    // the default EthioBiz branding untouched. Website icon drives the navbar
    // brand + favicon; desk icon drives the Desk top-left brand.
    function applyThemeIcons(s) {
        if (!s) s = window.__ethiobizThemeSettings || {};
        var websiteIcon = s.website_icon || s.favicon || '';
        var deskIcon = s.desk_icon || '';
        // BISMALLAH: remember configured icons so updateLogo keeps them.
        ethiobizCustomIcons.website = websiteIcon;
        ethiobizCustomIcons.desk = deskIcon;
        var isDesk = !!(document.body &&
            (document.body.classList.contains('desk-page') ||
             document.querySelector('.desk-sidebar') ||
             document.querySelector('.layout-side-section')));

        if (websiteIcon && !isDesk) {
            var fav = document.querySelector('link[rel="icon"], link[rel="shortcut icon"]');
            if (fav) {
                fav.href = websiteIcon;
            } else {
                fav = document.createElement('link');
                fav.rel = 'icon';
                fav.href = websiteIcon;
                document.head.appendChild(fav);
            }
            document.querySelectorAll('.navbar-brand img, #navbar-logo, .app-logo').forEach(img => {
                if (img.closest('.pillar-icon, .sub-icon, .detail-logo, .footer-brand, .legacy-image, .hero-logo, .loader-logo, .pillar-card, .sub-system-card, .final-cta, .detail-image, .hero-content, .ethiobiz-landing, #loading-screen')) return;
                img.src = websiteIcon;
                img.alt = (BRAND_CONFIG && BRAND_CONFIG.app_name) || 'EthioBiz';
                img.style.maxHeight = '35px';
            });
        }

        if (deskIcon && isDesk) {
            document.querySelectorAll('.desk-sidebar .navbar-brand img, .desk-navbar .navbar-brand img, .layout-side-section .navbar-brand img, .navbar-brand img').forEach(img => {
                img.src = deskIcon;
                img.alt = (BRAND_CONFIG && BRAND_CONFIG.app_name) || 'EthioBiz';
                img.style.maxHeight = '35px';
            });
            document.querySelectorAll('#switch-to-app img, .app-switcher-window img, .navbar .app-icon img').forEach(img => {
                img.src = deskIcon;
            });
        }
    }

    window.EthioBizBrandManager = new BrandManager();

    // ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Optional dark-mode label color from Theme Settings ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬
    // BISMALLAH (2026-09-10): expose the chosen color as CSS custom properties
    // on :root. ethiobiz_theme.css reads these variables so EVERY form label
    // and edit-tool control updates in real time ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â no <style> injection battle.
    function _shadeHex(hex, ratio) {
        hex = String(hex || '').trim().replace(/^#/, '');
        if (hex.length === 3) hex = hex.split('').map(function (ch) { return ch + ch; }).join('');
        if (!/^[0-9a-fA-F]{6}$/.test(hex)) return '#94a3b8';
        var n = parseInt(hex, 16);
        var r = Math.round(((n >> 16) & 255) * ratio);
        var g = Math.round(((n >> 8) & 255) * ratio);
        var b = Math.round((n & 255) * ratio);
        return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }
    function applyThemeDarkLabel(s) {
        if (!s) s = window.__ethiobizThemeSettings || {};
        ethiobizDarkLabelColor = s.dark_label_color || '';
        var root = document.documentElement;
        if (!root) return;
        if (ethiobizDarkLabelColor) {
            root.style.setProperty('--ethiobiz-dark-label-color', ethiobizDarkLabelColor);
            root.style.setProperty('--ethiobiz-dark-label-muted', _shadeHex(ethiobizDarkLabelColor, 0.62));
        } else {
            root.style.removeProperty('--ethiobiz-dark-label-color');
            root.style.removeProperty('--ethiobiz-dark-label-muted');
        }
        // live re-apply after short delay so later-rendered desk sections inherit
        var applyLabelAttr = function () {
            if (!document.body) {
                document.addEventListener('DOMContentLoaded', applyLabelAttr, { once: true });
                return;
            }
            document.body.setAttribute('data-eb-label-color', ethiobizDarkLabelColor || 'none');
        };
        setTimeout(applyLabelAttr, 0);
    }

    // Fetch settings first, then init so updateBackground has correct flags
    fetchAndCacheThemeSettings(function(s) {
        window.EthioBizBrandManager.init();
        applyThemeIcons(s);
        applyThemeDarkLabel(s);
    });

    // Desk content mounts asynchronously ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â retry icon override briefly
    let _iconRetries = 0;
    const iconRetryTimer = setInterval(function() {
        if (++_iconRetries > 6) { clearInterval(iconRetryTimer); return; }
        if (document.body && document.querySelector('.desk-sidebar, .layout-side-section')) {
            applyThemeIcons(window.__ethiobizThemeSettings || {});
        }
    }, 1000);

})();

// BISMALLAH ETHIOBIZ FLOATING SIDEBAR V6
(function() {
    function initSidebar() {
        if (typeof frappe === 'undefined') return;
        if (document.querySelector('.web-form')) return;

    // ---------------------------------------------------------------------
    // Sidebar state (BISMALLAH 2026-11-17)
    // Default: COLLAPSED on every full Desk load. The navbar button to the
    // left of the EthioBiz logo toggles expand/collapse for the SPA session.
    // Theme settings must never force the sidebar open or re-collapse it
    // after the user toggles.
    // ---------------------------------------------------------------------
    function updateSidebarToggleUi(collapsed) {
        const btn = document.getElementById('ethio-toggle-btn');
        if (btn) {
            const label = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
            btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
            btn.setAttribute('aria-pressed', collapsed ? 'true' : 'false');
            btn.setAttribute('aria-label', label);
            btn.setAttribute('title', label);
            btn.classList.toggle('is-collapsed', !!collapsed);
        }
        const closeBtn = document.getElementById('ethio-sidebar-close');
        if (closeBtn) {
            closeBtn.setAttribute('title', 'Collapse sidebar');
            closeBtn.setAttribute('aria-label', 'Collapse sidebar');
        }
    }

    // Tracks whether the user explicitly used the toggle/close/outside-click.
    // Until they do, SPA route changes keep the sidebar collapsed by default.
    let _sidebarUserToggled = false;

    function setSidebarCollapsed(collapsed) {
        if (!document.body) return;
        const isCollapsed = !!collapsed;
        document.body.classList.toggle('sidebar-collapsed', isCollapsed);
        // Explicit positive state. Older cached builds only knew
        // `sidebar-collapsed` and removed it on load, which made the sidebar
        // look permanently expanded. `sidebar-expanded` is only present when
        // the user actually expanded the sidebar.
        document.body.classList.toggle('sidebar-expanded', !isCollapsed);
        if (!isCollapsed) {
            document.body.classList.remove('sidebar-mobile-open');
        }
        updateSidebarToggleUi(isCollapsed);
    }

    function toggleSidebar() {
        if (!document.body) return;
        _sidebarUserToggled = true;
        const next = !document.body.classList.contains('sidebar-collapsed');
        setSidebarCollapsed(next);
        console.log('[EthioBiz] Sidebar toggled. Collapsed:', next);
    }

    window.ethiobizToggleSidebar = toggleSidebar;
    window.ethiobizSetSidebarCollapsed = setSidebarCollapsed;

    // Apply before the async theme-settings request so Desk never paints
    // with an expanded sidebar on first load.
    setSidebarCollapsed(true);
    if (!document.body) {
        document.addEventListener('DOMContentLoaded', function () {
            setSidebarCollapsed(true);
        }, { once: true });
    }

    // Block "Try the new Print Designer" at source BEFORE it reaches DOM.
    // `frappe.ready` is NOT guaranteed to exist when app_include_js runs
    // (desk.bundle loads later). Calling it unconditionally used to throw
    // "frappe.ready is not a function" here and abort the whole sidebar IIFE
    // before the CSS/button injection ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â leaving the sidebar permanently open.
    function whenFrappeReady(fn) {
        if (typeof frappe !== 'undefined' && typeof frappe.ready === 'function') {
            frappe.ready(fn);
            return;
        }
        let tries = 0;
        const timer = setInterval(function () {
            if (typeof frappe !== 'undefined' && typeof frappe.ready === 'function') {
                clearInterval(timer);
                frappe.ready(fn);
            } else if (++tries > 200) {
                clearInterval(timer);
                try { fn(); } catch (e) { /* non-fatal */ }
            }
        }, 50);
    }

    whenFrappeReady(function () {
        if (frappe.ui && frappe.ui.Page) {
            var _origAddInner = frappe.ui.Page.prototype.add_inner_message;
            frappe.ui.Page.prototype.add_inner_message = function (msg) {
                if (msg && typeof msg === 'string' && msg.indexOf('Print Designer') !== -1) {
                    return $(document.createElement('span')).addClass('inner-page-message text-muted small').hide();
                }
                return _origAddInner.call(this, msg);
            };
        }
    });

    console.log('[EthioBiz] Sidebar init start (build 2026-11-18-v2.5.5-title-preserve)');
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
            overflow-x: hidden !important;
            -webkit-overflow-scrolling: touch !important;
            overscroll-behavior: contain !important;
            touch-action: pan-y !important;
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
                height: 100dvh !important;
                max-height: 100dvh !important;
                transform: translateX(-100%) !important; /* Hidden by default on mobile */
                overflow-y: auto !important;
                overflow-x: hidden !important;
                -webkit-overflow-scrolling: touch !important;
                overscroll-behavior: contain !important;
                touch-action: pan-y !important;
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
            
            /* Unhide sidebar contents on mobile */
            .layout-side-section .list-sidebar,
            .layout-side-section .desk-sidebar,
            .layout-side-section .form-sidebar,
            .layout-side-section .overlay-sidebar,
            .layout-side-section .sidebar-items,
            .layout-side-section .module-sidebar-nav,
            .layout-side-section .standard-sidebar,
            .layout-side-section .hidden-xs,
            .layout-side-section .hidden-sm {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                transform: none !important;
                position: relative !important;
                width: 100% !important;
                height: auto !important;
                top: auto !important;
                left: auto !important;
                background: transparent !important;
                box-shadow: none !important;
            }

            .layout-side-section .sidebar-item-label,
            .layout-side-section .sidebar-label,
            .layout-side-section a,
            .layout-side-section span {
                color: #F8F6F2 !important;
            }
            [data-theme="light"] .layout-side-section .sidebar-item-label,
            [data-theme="light"] .layout-side-section .sidebar-label,
            [data-theme="light"] .layout-side-section a,
            [data-theme="light"] .layout-side-section span {
                color: #0f172a !important;
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

        /* ------------------------------------------------------------------
         * 5. Mobile Workspace drawer polish (2026-11-17)
         * Scope is intentionally limited to body.ethio-mobile-workspace
         * inside the phone breakpoint. Desktop and the internal doctype
         * mobile drawer keep their existing look.
         * ------------------------------------------------------------------ */
        .ethio-mobile-ws-header { display: none; }

        @media (max-width: 991px) {
            /* The drawer starts below the sticky navbar (50px) so the
             * hamburger and close affordance never sit underneath it. */
            body.ethio-mobile-workspace .layout-side-section {
                top: 50px !important;
                height: calc(100dvh - 50px) !important;
                max-height: calc(100dvh - 50px) !important;
                width: min(86vw, 320px) !important;
                max-width: 320px !important;
                padding-top: 8px !important;
                padding-bottom: calc(18px + env(safe-area-inset-bottom, 0px)) !important;
                border-radius: 0 22px 22px 0 !important;
                border-right: 1px solid rgba(255,255,255,0.12) !important;
                box-shadow: 18px 0 48px rgba(0,0,0,0.45) !important;
                background: linear-gradient(180deg, rgba(14,26,26,0.98) 0%, rgba(9,17,17,0.99) 100%) !important;
                backdrop-filter: blur(24px) !important;
                -webkit-backdrop-filter: blur(24px) !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                -webkit-overflow-scrolling: touch !important;
                overscroll-behavior: contain !important;
                touch-action: pan-y !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace .layout-side-section {
                background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%) !important;
                border-right-color: rgba(15,23,42,0.08) !important;
                box-shadow: 18px 0 48px rgba(15,23,42,0.18) !important;
            }

            /* Header card: workspace identity + close-safe padding */
            body.ethio-mobile-workspace .ethio-mobile-ws-header {
                display: flex !important;
                align-items: center !important;
                gap: 12px !important;
                padding: 8px 52px 14px 16px !important;
                margin: 0 0 8px 0 !important;
                border-bottom: 1px solid rgba(255,255,255,0.08) !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace .ethio-mobile-ws-header {
                border-bottom-color: rgba(15,23,42,0.08) !important;
            }

            body.ethio-mobile-workspace .ethio-mobile-ws-icon {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 38px !important;
                height: 38px !important;
                flex: 0 0 auto !important;
                border-radius: 12px !important;
                color: #ffffff !important;
                background: linear-gradient(135deg, #1FB6AE 0%, #0f766e 100%) !important;
                box-shadow: 0 6px 16px rgba(31,182,174,0.35) !important;
            }

            body.ethio-mobile-workspace .ethio-mobile-ws-text {
                display: flex !important;
                flex-direction: column !important;
                min-width: 0 !important;
            }

            body.ethio-mobile-workspace .ethio-mobile-ws-kicker {
                font-size: 10px !important;
                line-height: 1.2 !important;
                letter-spacing: 0.16em !important;
                text-transform: uppercase !important;
                font-weight: 700 !important;
                color: rgba(248,246,242,0.62) !important;
            }

            body.ethio-mobile-workspace .ethio-mobile-ws-title {
                font-size: 18px !important;
                line-height: 1.25 !important;
                font-weight: 700 !important;
                color: #ffffff !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace .ethio-mobile-ws-kicker {
                color: rgba(15,23,42,0.55) !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace .ethio-mobile-ws-title {
                color: #0f172a !important;
            }

            /* Rounded, touch-friendly workspace links */
            body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item {
                margin: 4px 10px !important;
                padding: 0 !important;
                border-radius: 12px !important;
                background: transparent !important;
                transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
            }

            body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item .item-anchor {
                display: flex !important;
                align-items: center !important;
                gap: 10px !important;
                padding: 11px 12px !important;
                border-radius: 12px !important;
                font-size: 14.5px !important;
                font-weight: 500 !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }

            body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected {
                background: linear-gradient(90deg, rgba(31,182,174,0.24) 0%, rgba(31,182,174,0.06) 100%) !important;
                box-shadow: inset 3px 0 0 #1FB6AE, 0 6px 18px rgba(31,182,174,0.10) !important;
            }

            body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-label {
                color: #ffffff !important;
                font-weight: 650 !important;
            }

            body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item .sidebar-item-icon {
                color: rgba(248,246,242,0.68) !important;
            }

            body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-icon {
                color: #5eead4 !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-label {
                color: #0f172a !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-icon {
                color: #0f766e !important;
            }

            /* Section captions: small, quiet, uppercase */
            body.ethio-mobile-workspace .layout-side-section .standard-sidebar-label {
                padding: 14px 18px 6px !important;
                opacity: 0.85 !important;
            }

            body.ethio-mobile-workspace .layout-side-section .standard-sidebar-label .section-title {
                font-size: 10.5px !important;
                letter-spacing: 0.14em !important;
                text-transform: uppercase !important;
                font-weight: 700 !important;
                color: rgba(248,246,242,0.58) !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace .layout-side-section .standard-sidebar-label .section-title {
                color: rgba(15,23,42,0.52) !important;
            }

            /* Keep the mobile drawer clean: no edit/duplicate controls */
            body.ethio-mobile-workspace .layout-side-section .sidebar-item-control {
                display: none !important;
            }

            /* Circular glass close button, positioned inside the drawer */
            body.ethio-mobile-workspace #ethio-sidebar-close {
                top: 10px !important;
                right: 14px !important;
                width: 34px !important;
                height: 34px !important;
                border-radius: 50% !important;
                background: rgba(255,255,255,0.12) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255,255,255,0.18) !important;
                backdrop-filter: blur(8px) !important;
                -webkit-backdrop-filter: blur(8px) !important;
                box-shadow: 0 4px 14px rgba(0,0,0,0.20) !important;
            }

            [data-theme="light"] body.ethio-mobile-workspace #ethio-sidebar-close {
                background: rgba(15,23,42,0.06) !important;
                color: #0f172a !important;
                border-color: rgba(15,23,42,0.08) !important;
            }

            body.ethio-mobile-workspace #ethio-mobile-hamburger {
                background: linear-gradient(135deg, rgba(31,182,174,0.18) 0%, rgba(31,182,174,0.06) 100%) !important;
                border-color: rgba(31,182,174,0.35) !important;
                color: #1FB6AE !important;
                border-radius: 10px !important;
            }

            body.ethio-mobile-workspace.sidebar-mobile-open .ethio-mobile-overlay {
                background: rgba(2,6,23,0.55) !important;
                backdrop-filter: blur(2px) !important;
                -webkit-backdrop-filter: blur(2px) !important;
            }

            /* Slim, themed scrollbar inside the drawer */
            body.ethio-mobile-workspace .layout-side-section::-webkit-scrollbar {
                width: 4px !important;
            }
            body.ethio-mobile-workspace .layout-side-section::-webkit-scrollbar-thumb {
                background: rgba(255,255,255,0.22) !important;
                border-radius: 999px !important;
            }
            [data-theme="light"] body.ethio-mobile-workspace .layout-side-section::-webkit-scrollbar-thumb {
                background: rgba(15,23,42,0.18) !important;
            }
        }

        /* ------------------------------------------------------------------
         * 6. Unified polished sidebar (desktop + doctype + mobile)
         *    Same visual language as the mobile Workspace drawer:
         *    glass panel, rounded cards, teal selected state, header card.
         *    Desktop keeps its 230px width and collapse/offset behavior.
         *    Internal doctype list/form sidebars get the same treatment.
         * ------------------------------------------------------------------ */
        body .layout-side-section {
            background: linear-gradient(180deg, rgba(14,26,26,0.98) 0%, rgba(9,17,17,0.99) 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 0 22px 22px 0 !important;
            box-shadow: 18px 0 48px rgba(0,0,0,0.32) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            /* Bootstrap's col-lg-2 adds 15px side padding. Remove it so the
             * header, cards and close button use the full 230px rail. */
            padding-left: 0 !important;
            padding-right: 0 !important;
            box-sizing: border-box !important;
        }

        [data-theme="light"] body .layout-side-section {
            background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%) !important;
            border-right-color: rgba(15,23,42,0.08) !important;
            box-shadow: 18px 0 48px rgba(15,23,42,0.12) !important;
        }

        /* Header card shared by workspace, doctype list and doctype form */
        body .ethio-mobile-ws-header {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 10px 52px 14px 16px !important;
            margin: 0 0 8px 0 !important;
            border-bottom: 1px solid rgba(255,255,255,0.08) !important;
            background: linear-gradient(180deg, rgba(31,182,174,0.06) 0%, rgba(31,182,174,0) 100%) !important;
        }

        [data-theme="light"] body .ethio-mobile-ws-header {
            border-bottom-color: rgba(15,23,42,0.08) !important;
            background: linear-gradient(180deg, rgba(31,182,174,0.06) 0%, rgba(31,182,174,0) 100%) !important;
        }

        body .ethio-mobile-ws-icon {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 34px !important;
            height: 34px !important;
            flex: 0 0 auto !important;
            border-radius: 11px !important;
            color: #ffffff !important;
            background: linear-gradient(135deg, #1FB6AE 0%, #0f766e 100%) !important;
            box-shadow: 0 6px 16px rgba(31,182,174,0.35) !important;
        }

        body .ethio-mobile-ws-icon .ethio-ws-icon-list { display: none !important; }
        body .ethio-mobile-ws-header[data-kind="doctype"] .ethio-ws-icon-grid { display: none !important; }
        body .ethio-mobile-ws-header[data-kind="doctype"] .ethio-ws-icon-list { display: block !important; }

        body .ethio-mobile-ws-text {
            display: flex !important;
            flex-direction: column !important;
            min-width: 0 !important;
        }

        body .ethio-mobile-ws-kicker {
            font-size: 10px !important;
            line-height: 1.2 !important;
            letter-spacing: 0.16em !important;
            text-transform: uppercase !important;
            font-weight: 700 !important;
            color: rgba(248,246,242,0.62) !important;
        }

        body .ethio-mobile-ws-title {
            font-size: 16px !important;
            line-height: 1.25 !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        [data-theme="light"] body .ethio-mobile-ws-kicker { color: rgba(15,23,42,0.55) !important; }
        [data-theme="light"] body .ethio-mobile-ws-title { color: #0f172a !important; }

        /* Circular glass close button. On desktop it sits just below the
         * navbar (top 60) beside the header; mobile overrides it to top 10
         * inside the drawer. */
        body #ethio-sidebar-close {
            top: 60px !important;
            right: 12px !important;
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            background: rgba(255,255,255,0.10) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
            box-shadow: 0 4px 14px rgba(0,0,0,0.16) !important;
        }

        [data-theme="light"] body #ethio-sidebar-close {
            background: rgba(15,23,42,0.06) !important;
            color: #0f172a !important;
            border-color: rgba(15,23,42,0.08) !important;
        }

        body #ethio-sidebar-close:hover {
            background: rgba(239,68,68,0.16) !important;
            color: #ef4444 !important;
            border-color: rgba(239,68,68,0.30) !important;
        }

        /* Slim, themed scrollbar */
        body .layout-side-section::-webkit-scrollbar { width: 4px !important; }
        body .layout-side-section::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.22) !important;
            border-radius: 999px !important;
        }
        [data-theme="light"] body .layout-side-section::-webkit-scrollbar-thumb {
            background: rgba(15,23,42,0.18) !important;
        }

        /* Workspace standard items */
        body .layout-side-section .desk-sidebar-item.standard-sidebar-item {
            margin: 4px 10px !important;
            padding: 0 !important;
            border-radius: 10px !important;
            background: transparent !important;
            transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
        }

        body .layout-side-section .desk-sidebar-item.standard-sidebar-item .item-anchor {
            display: flex !important;
            align-items: center !important;
            gap: 9px !important;
            padding: 8px 10px !important;
            border-radius: 10px !important;
            font-size: 13.5px !important;
            font-weight: 500 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            color: rgba(248,246,242,0.92) !important;
        }

        [data-theme="light"] body .layout-side-section .desk-sidebar-item.standard-sidebar-item .item-anchor {
            color: #0f172a !important;
        }

        body .layout-side-section .desk-sidebar-item.standard-sidebar-item:hover {
            background: rgba(31,182,174,0.10) !important;
        }

        body .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected {
            background: linear-gradient(90deg, rgba(31,182,174,0.22) 0%, rgba(31,182,174,0.05) 100%) !important;
            box-shadow: inset 3px 0 0 #1FB6AE, 0 6px 18px rgba(31,182,174,0.08) !important;
        }

        body .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-label {
            color: #ffffff !important;
            font-weight: 650 !important;
        }

        [data-theme="light"] body .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-label {
            color: #0f172a !important;
        }

        body .layout-side-section .desk-sidebar-item.standard-sidebar-item .sidebar-item-icon {
            color: rgba(248,246,242,0.66) !important;
        }

        body .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-icon {
            color: #5eead4 !important;
        }

        [data-theme="light"] body .layout-side-section .desk-sidebar-item.standard-sidebar-item.selected .sidebar-item-icon {
            color: #0f766e !important;
        }

        body .layout-side-section .standard-sidebar-label {
            padding: 12px 16px 4px !important;
            opacity: 0.85 !important;
        }

        body .layout-side-section .standard-sidebar-label .section-title {
            font-size: 10px !important;
            letter-spacing: 0.14em !important;
            text-transform: uppercase !important;
            font-weight: 700 !important;
            color: rgba(248,246,242,0.58) !important;
        }

        [data-theme="light"] body .layout-side-section .standard-sidebar-label .section-title {
            color: rgba(15,23,42,0.52) !important;
        }

        body .layout-side-section .sidebar-item-control {
            opacity: 0 !important;
            transition: opacity 0.15s ease !important;
        }

        body .layout-side-section .desk-sidebar-item.standard-sidebar-item:hover .sidebar-item-control {
            opacity: 1 !important;
        }

        /* Doctype list sidebar cards */
        body .layout-side-section .list-sidebar .sidebar-menu {
            padding: 4px 10px !important;
        }

        body .layout-side-section .list-sidebar .sidebar-menu li {
            margin: 4px 0 !important;
        }

        body .layout-side-section .list-sidebar .dropdown-menu li {
            margin: 0 !important;
        }

        body .layout-side-section .list-sidebar .sidebar-label {
            padding: 12px 8px 4px !important;
            font-size: 10px !important;
            letter-spacing: 0.14em !important;
            text-transform: uppercase !important;
            font-weight: 700 !important;
            color: rgba(248,246,242,0.58) !important;
            opacity: 0.9 !important;
        }

        [data-theme="light"] body .layout-side-section .list-sidebar .sidebar-label {
            color: rgba(15,23,42,0.52) !important;
        }

        body .layout-side-section .list-sidebar .list-sidebar-button,
        body .layout-side-section .list-sidebar .btn-default,
        body .layout-side-section .list-sidebar .btn-primary,
        body .layout-side-section .list-sidebar .list-link > a:not(.dropdown-item) {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 8px !important;
            width: 100% !important;
            padding: 8px 10px !important;
            border-radius: 10px !important;
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            color: rgba(248,246,242,0.92) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            text-align: left !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        [data-theme="light"] body .layout-side-section .list-sidebar .list-sidebar-button,
        [data-theme="light"] body .layout-side-section .list-sidebar .btn-default,
        [data-theme="light"] body .layout-side-section .list-sidebar .btn-primary,
        [data-theme="light"] body .layout-side-section .list-sidebar .list-link > a:not(.dropdown-item) {
            background: rgba(15,23,42,0.035) !important;
            border-color: rgba(15,23,42,0.08) !important;
            color: #0f172a !important;
        }

        body .layout-side-section .list-sidebar .list-sidebar-button:hover,
        body .layout-side-section .list-sidebar .btn-default:hover,
        body .layout-side-section .list-sidebar .btn-primary:hover,
        body .layout-side-section .list-sidebar .list-link > a:not(.dropdown-item):hover {
            background: rgba(31,182,174,0.10) !important;
            border-color: rgba(31,182,174,0.25) !important;
        }

        body .layout-side-section .list-sidebar .current-view {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
        }

        body .layout-side-section .list-sidebar .current-view .list-link {
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }

        body .layout-side-section .list-sidebar .sidebar-action > a {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 30px !important;
            height: 30px !important;
            padding: 0 !important;
            border-radius: 8px !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            color: rgba(248,246,242,0.72) !important;
        }

        [data-theme="light"] body .layout-side-section .list-sidebar .sidebar-action > a {
            color: rgba(15,23,42,0.62) !important;
        }

        body .layout-side-section .list-sidebar .sidebar-action > a:hover {
            background: rgba(31,182,174,0.12) !important;
            color: #1FB6AE !important;
        }

        body .layout-side-section .list-sidebar .divider {
            border-top: 1px solid rgba(255,255,255,0.08) !important;
            margin: 8px 0 !important;
        }

        [data-theme="light"] body .layout-side-section .list-sidebar .divider {
            border-top-color: rgba(15,23,42,0.08) !important;
        }

        body .layout-side-section .list-sidebar .sidebar-section {
            margin-bottom: 8px !important;
        }

        /* Doctype form sidebar cards */
        body .layout-side-section .form-sidebar .sidebar-menu {
            padding: 4px 10px !important;
        }

        body .layout-side-section .form-sidebar .sidebar-menu > li {
            margin: 6px 0 !important;
            padding: 10px 12px !important;
            border-radius: 12px !important;
            background: rgba(255,255,255,0.055) !important;
            border: 1px solid rgba(255,255,255,0.09) !important;
        }

        [data-theme="light"] body .layout-side-section .form-sidebar .sidebar-menu > li {
            background: rgba(15,23,42,0.035) !important;
            border-color: rgba(15,23,42,0.08) !important;
        }

        body .layout-side-section .form-sidebar .form-sidebar-items {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 8px !important;
        }

        body .layout-side-section .form-sidebar .add-assignment-label,
        body .layout-side-section .form-sidebar .attachments-actions span,
        body .layout-side-section .form-sidebar .pill-label {
            color: rgba(248,246,242,0.92) !important;
            font-size: 13px !important;
        }

        [data-theme="light"] body .layout-side-section .form-sidebar .add-assignment-label,
        [data-theme="light"] body .layout-side-section .form-sidebar .attachments-actions span,
        [data-theme="light"] body .layout-side-section .form-sidebar .pill-label {
            color: #0f172a !important;
        }

        body .layout-side-section .form-sidebar .add-assignment-btn {
            color: #5eead4 !important;
            background: rgba(31,182,174,0.10) !important;
            border-radius: 8px !important;
        }

        [data-theme="light"] body .layout-side-section .form-sidebar .add-assignment-btn {
            color: #0f766e !important;
        }

        body .layout-side-section .form-sidebar .sidebar-image-wrapper {
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
        }

        body .layout-side-section .form-sidebar .sidebar-image {
            border-radius: 10px !important;
        }

        /* Respect Frappe's own hide/hidden classes inside the form sidebar.
         * The mobile base rules unhide the sidebar wrapper itself, but they
         * must not resurrect intentionally hidden sections or empty
         * placeholder rows (Follow, page views, auto-repeat, etc.). */
        body .layout-side-section .form-sidebar .hide,
        body .layout-side-section .form-sidebar .hidden,
        body .layout-side-section .form-sidebar .hidden-xs,
        body .layout-side-section .form-sidebar .hidden-sm,
        body .layout-side-section .form-sidebar .ethio-empty-sidebar-item,
        body .layout-side-section .form-sidebar .ethio-empty-sidebar-section {
            display: none !important;
        }

        body .layout-side-section .form-sidebar hr {
            border: 0 !important;
            border-top: 1px solid rgba(255,255,255,0.08) !important;
            margin: 10px 10px !important;
        }

        [data-theme="light"] body .layout-side-section .form-sidebar hr {
            border-top-color: rgba(15,23,42,0.08) !important;
        }

        /* Frappe/Bootstrap can leave an invisible backdrop behind after a
         * modal closes. It must never swallow taps on the page or drawer. */
        .modal-backdrop.fade:not(.show) {
            display: none !important;
            pointer-events: none !important;
        }

        /* Mobile: every sidebar becomes the same polished drawer */
        @media (max-width: 991px) {
            /* The drawer and overlay live inside .layout-main. Frappe's
             * .page-head uses z-index:10, which otherwise paints over the
             * top strip of the drawer and swallows taps on the close
             * button. Raise the drawer's stacking context above page chrome
             * but keep it below the 1020 navbar so the hamburger remains
             * tappable while the drawer is open. */
            body .layout-main {
                z-index: 1010 !important;
            }

            /* Some Desk layouts wrap the drawer and sticky page actions in
             * .container.page-body, which creates its own stacking context.
             * Raise that wrapper only while the drawer is open so the close
             * button and drawer links sit above .page-head/.page-actions,
             * but keep it below the 1020 navbar so the hamburger still works. */
            body.sidebar-mobile-open .container.page-body {
                z-index: 1001 !important;
            }

            body .layout-side-section {
                top: 50px !important;
                height: calc(100dvh - 50px) !important;
                max-height: calc(100dvh - 50px) !important;
                width: min(86vw, 320px) !important;
                max-width: 320px !important;
                padding-top: 8px !important;
                padding-bottom: calc(18px + env(safe-area-inset-bottom, 0px)) !important;
                border-radius: 0 22px 22px 0 !important;
                border-right: 1px solid rgba(255,255,255,0.12) !important;
                box-shadow: 18px 0 48px rgba(0,0,0,0.45) !important;
                background: linear-gradient(180deg, rgba(14,26,26,0.98) 0%, rgba(9,17,17,0.99) 100%) !important;
                backdrop-filter: blur(24px) !important;
                -webkit-backdrop-filter: blur(24px) !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                -webkit-overflow-scrolling: touch !important;
                overscroll-behavior: contain !important;
                touch-action: pan-y !important;
            }

            [data-theme="light"] body .layout-side-section {
                background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%) !important;
                border-right-color: rgba(15,23,42,0.08) !important;
                box-shadow: 18px 0 48px rgba(15,23,42,0.18) !important;
            }

            body .layout-side-section.hide-sidebar,
            body.ethio-no-sidebar .layout-side-section {
                display: none !important;
            }

            body.ethio-no-sidebar #ethio-mobile-hamburger,
            body.ethio-no-sidebar .ethio-mobile-overlay {
                display: none !important;
            }

            body #ethio-sidebar-close {
                top: 10px !important;
                right: 14px !important;
                width: 34px !important;
                height: 34px !important;
            }

            body #ethio-mobile-hamburger {
                background: linear-gradient(135deg, rgba(31,182,174,0.18) 0%, rgba(31,182,174,0.06) 100%) !important;
                border-color: rgba(31,182,174,0.35) !important;
                color: #1FB6AE !important;
                border-radius: 10px !important;
            }

            body.sidebar-mobile-open .ethio-mobile-overlay {
                background: rgba(2,6,23,0.55) !important;
                backdrop-filter: blur(2px) !important;
                -webkit-backdrop-filter: blur(2px) !important;
            }

            body .ethio-mobile-ws-icon {
                width: 38px !important;
                height: 38px !important;
                border-radius: 12px !important;
            }

            body .ethio-mobile-ws-title {
                font-size: 18px !important;
            }

            body .layout-side-section .sidebar-item-control {
                display: none !important;
            }

            body .layout-side-section .desk-sidebar-item.standard-sidebar-item {
                margin: 4px 10px !important;
                padding: 0 !important;
                border-radius: 12px !important;
            }

            body .layout-side-section .desk-sidebar-item.standard-sidebar-item .item-anchor {
                gap: 10px !important;
                padding: 11px 12px !important;
                border-radius: 12px !important;
                font-size: 14.5px !important;
            }

            body .layout-side-section .standard-sidebar-label {
                padding: 14px 18px 6px !important;
            }

            body .layout-side-section .standard-sidebar-label .section-title {
                font-size: 10.5px !important;
            }

            body .layout-side-section .list-sidebar .sidebar-menu {
                padding: 4px 10px !important;
            }

            body .layout-side-section .list-sidebar .sidebar-label {
                padding: 12px 8px 4px !important;
                font-size: 10.5px !important;
            }

            body .layout-side-section .list-sidebar .list-sidebar-button,
            body .layout-side-section .list-sidebar .btn-default,
            body .layout-side-section .list-sidebar .btn-primary,
            body .layout-side-section .list-sidebar .list-link > a:not(.dropdown-item) {
                padding: 11px 12px !important;
                border-radius: 12px !important;
                font-size: 14px !important;
            }

            body .layout-side-section .list-sidebar .sidebar-action > a {
                width: 34px !important;
                height: 34px !important;
                border-radius: 9px !important;
            }

            body .layout-side-section .form-sidebar .sidebar-menu {
                padding: 4px 10px !important;
            }

            body .layout-side-section .form-sidebar .sidebar-menu > li {
                padding: 11px 12px !important;
                border-radius: 12px !important;
            }

            body .layout-side-section .form-sidebar .add-assignment-label,
            body .layout-side-section .form-sidebar .attachments-actions span,
            body .layout-side-section .form-sidebar .pill-label {
                font-size: 14px !important;
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
        // Reuse an old button if a cached build already injected one, but
        // always (re)attach the current handler and a11y attributes. An old
        // `#ethio-toggle-btn` can survive an SPA render without a handler.
        let toggleBtn = document.getElementById('ethio-toggle-btn');
        if (!toggleBtn && brand && brand.parentElement) {
            toggleBtn = document.createElement('div');
            toggleBtn.id = 'ethio-toggle-btn';
            toggleBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`;
            brand.parentElement.insertBefore(toggleBtn, brand);
            console.log('[EthioBiz] Desktop toggle button injected');
        }
        if (toggleBtn) {
            toggleBtn.setAttribute('role', 'button');
            toggleBtn.setAttribute('tabindex', '0');
            if (!toggleBtn.querySelector('svg')) {
                toggleBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`;
            }
            toggleBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleSidebar();
            };
            toggleBtn.onkeydown = (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSidebar();
                }
            };
            // Keep it immediately left of the main EthioBiz logo.
            if (brand && brand.parentElement && toggleBtn.parentElement !== brand.parentElement) {
                brand.parentElement.insertBefore(toggleBtn, brand);
            }
        }
        updateSidebarToggleUi(document.body.classList.contains('sidebar-collapsed'));
        
        // C. Mobile Overlay (for closing sidebar when clicking outside)
        //
        // IMPORTANT STACKING NOTE (2026-11-17):
        // `.layout-main` is `position: relative; z-index: 1`, so it creates a
        // stacking context. The sidebar lives inside that context at z-index
        // 1001. If the overlay is appended to <body> at z-index 1000 it is
        // above the *whole* `.layout-main` context, including the open
        // sidebar ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â every tap and scroll then hits the overlay and the drawer
        // feels "inactive" on mobile. Appending the overlay to the sidebar's
        // parent keeps it in the same context: 1000 < 1001 (sidebar) and
        // 1000 > main content, while the sticky navbar (1020) stays above the
        // overlay so the hamburger remains tappable to close the drawer.
        let overlay = document.getElementById('ethio-mobile-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'ethio-mobile-overlay';
            overlay.className = 'ethio-mobile-overlay';
            console.log('[EthioBiz] Mobile overlay injected');
        }
        overlay.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            document.body.classList.remove('sidebar-mobile-open');
            console.log('[EthioBiz] Mobile sidebar closed via overlay');
        };
        const overlaySidebar = document.querySelector('.layout-side-section');
        const overlayHost = (overlaySidebar && overlaySidebar.parentElement)
            ? overlaySidebar.parentElement
            : document.body;
        if (overlay.parentElement !== overlayHost) {
            overlayHost.appendChild(overlay);
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
                setSidebarCollapsed(true);
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

    // ---------------------------------------------------------------------
    // Unified sidebar chrome (2026-11-17)
    // The same header card, rounded items and glass panel are used by the
    // desktop sidebar, the internal doctype list/form sidebars and the
    // mobile drawer. The body class ethio-mobile-workspace is still used
    // for the Workspace-specific mobile title and item accents.
    // ---------------------------------------------------------------------
    function isWorkspaceRoute() {
        try {
            if (typeof frappe !== 'undefined' && typeof frappe.get_route === 'function') {
                const r = frappe.get_route();
                if (r && r[0] === 'Workspaces') return true;
            }
        } catch (e) { /* route may not be ready yet */ }
        const bodyRoute = document.body ? (document.body.getAttribute('data-route') || '') : '';
        if (bodyRoute.indexOf('Workspaces/') === 0) return true;
        return /^\/app\/private\/home/.test(window.location.pathname || '');
    }

    function isMobileViewport() {
        return !!(window.matchMedia && window.matchMedia('(max-width: 991px)').matches);
    }

    function getSidebarHeaderInfo(side) {
        let route = [];
        try {
            if (typeof frappe !== 'undefined' && typeof frappe.get_route === 'function') {
                route = frappe.get_route() || [];
            }
        } catch (e) { route = []; }
        const first = route[0] || '';
        if (first === 'Workspaces') {
            const sel = side.querySelector('.standard-sidebar-item.selected .sidebar-item-label, .desk-sidebar-item.selected .sidebar-item-label');
            const title = sel ? (sel.textContent || '').trim() : 'Workspace';
            return { kind: 'workspace', kicker: 'Workspace', title: title || 'Workspace' };
        }
        if (first === 'List' || first === 'Form' || first === 'Tree' ||
            first === 'Report' || first === 'query-report' ||
            first === 'Dashboard' || first === 'dashboard') {
            return { kind: 'doctype', kicker: 'Menu', title: route[1] || first || 'Menu' };
        }
        return { kind: 'doctype', kicker: 'Menu', title: route[1] || first || 'Menu' };
    }

    function sidebarHasContent(side) {
        if (!side || side.classList.contains('hide-sidebar')) return false;
        const content = side.querySelector('.list-sidebar, .form-sidebar, .desk-sidebar, .sidebar-menu');
        if (!content) return false;
        // Do not rely on getBoundingClientRect here: while the mobile drawer is
        // closed, or while the desktop form sidebar is display:none, every
        // child rect is 0x0. That previously made us add `ethio-no-sidebar`,
        // which set display:none and then kept the check permanently false.
        try {
            const cs = getComputedStyle(content);
            if (cs.display === 'none' && !isMobileViewport()) return false;
        } catch (e) { /* ignore */ }
        const items = content.querySelectorAll('.standard-sidebar-item, .sidebar-item-container, .list-sidebar-button, .list-link, .sidebar-action, .sidebar-menu > li:not(.ethio-empty-sidebar-item), .form-sidebar .sidebar-menu > li:not(.ethio-empty-sidebar-item)');
        if (items.length > 0) return true;
        return !!(content.innerText && content.innerText.trim().length);
    }

    function hasVisibleText(li) {
        if (li.classList.contains('hidden') || li.classList.contains('hide') ||
            li.classList.contains('hidden-xs') || li.classList.contains('hidden-sm')) {
            return false;
        }
        const walker = document.createTreeWalker(li, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) {
            if (!node.nodeValue || !node.nodeValue.trim()) continue;
            let parent = node.parentElement;
            let hidden = false;
            while (parent && parent !== li) {
                if (parent.classList.contains('hidden') || parent.classList.contains('hide') ||
                    parent.classList.contains('hidden-xs') || parent.classList.contains('hidden-sm') ||
                    parent.getAttribute('aria-hidden') === 'true' ||
                    (parent.style && (parent.style.display === 'none' || parent.style.visibility === 'hidden'))) {
                    hidden = true;
                    break;
                }
                parent = parent.parentElement;
            }
            if (!hidden) return true;
        }
        return false;
    }

    function decorateFormSidebar() {
        const form = document.querySelector('.layout-side-section .form-sidebar');
        if (!form) return;
        form.querySelectorAll('.sidebar-menu').forEach(function(ul) {
            if (ul.classList.contains('hide') || ul.classList.contains('hidden') ||
                ul.classList.contains('hidden-xs') || ul.classList.contains('hidden-sm')) {
                return;
            }
            let visible = false;
            Array.from(ul.children).filter(function(el) { return el.tagName === 'LI'; }).forEach(function(li) {
                let interactive = false;
                li.querySelectorAll('img, input, textarea, select, button, a[href], .rating-icons, .sidebar-image, .form-sidebar-items').forEach(function(el) {
                    if (interactive) return;
                    const r = el.getBoundingClientRect();
                    const cs = getComputedStyle(el);
                    if (r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden') interactive = true;
                });
                const meaningful = hasVisibleText(li) || interactive;
                li.classList.toggle('ethio-empty-sidebar-item', !meaningful);
                if (meaningful && getComputedStyle(li).display !== 'none') visible = true;
            });
            let directContent = false;
            Array.from(ul.children).forEach(function(child) {
                if (child.tagName === 'LI') return;
                const r = child.getBoundingClientRect();
                const cs = getComputedStyle(child);
                if (r.width <= 0 || r.height <= 0 || cs.display === 'none' || cs.visibility === 'hidden') return;
                const text = (child.innerText || '').replace(/\s+/g, ' ').trim();
                let media = false;
                child.querySelectorAll('img, input, textarea, select, button, a[href], svg').forEach(function(el) {
                    if (media) return;
                    const er = el.getBoundingClientRect();
                    const ecs = getComputedStyle(el);
                    if (er.width > 0 && er.height > 0 && ecs.display !== 'none' && ecs.visibility !== 'hidden') media = true;
                });
                if (text.length > 0 || media) directContent = true;
            });
            ul.classList.toggle('ethio-empty-sidebar-section', !visible && !directContent);
        });
    }

    // Frappe reveals/hides form-sidebar rows by toggling classes (for example
    // the Follow/Unfollow links start visible and become `.hidden` after the
    // document loads). Observe only the form sidebar and only class/style
    // changes, then re-evaluate which rows are meaningful. Do not reuse the
    // global sidebar observer here: forceUI writes ARIA attributes on every
    // pass and an attributes:true global observer would feed itself.
    let _formSidebarObserver = null;
    let _formSidebarObserverTarget = null;

    function ensureFormSidebarObserver() {
        const form = document.querySelector('.layout-side-section .form-sidebar');
        if (!form) {
            if (_formSidebarObserver) {
                _formSidebarObserver.disconnect();
                _formSidebarObserver = null;
                _formSidebarObserverTarget = null;
            }
            return;
        }
        if (_formSidebarObserver && _formSidebarObserverTarget === form) return;
        if (_formSidebarObserver) _formSidebarObserver.disconnect();
        _formSidebarObserverTarget = form;
        _formSidebarObserver = new MutationObserver(function() {
            decorateFormSidebar();
        });
        _formSidebarObserver.observe(form, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'style']
        });
    }

    function ensureSidebarHeader() {
        const side = document.querySelector('.layout-side-section');
        if (!side) return;
        const hasContent = sidebarHasContent(side);
        document.body.classList.toggle('ethio-no-sidebar', !hasContent);
        let header = side.querySelector('.ethio-mobile-ws-header');
        if (!hasContent) {
            if (header) header.remove();
            return;
        }
        if (!header) {
            header = document.createElement('div');
            header.className = 'ethio-mobile-ws-header';
            header.innerHTML =
                '<div class="ethio-mobile-ws-icon" aria-hidden="true">' +
                    '<svg class="ethio-ws-icon-grid" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                        '<rect x="3" y="3" width="7" height="7" rx="1.5"></rect>' +
                        '<rect x="14" y="3" width="7" height="7" rx="1.5"></rect>' +
                        '<rect x="3" y="14" width="7" height="7" rx="1.5"></rect>' +
                        '<rect x="14" y="14" width="7" height="7" rx="1.5"></rect>' +
                    '</svg>' +
                    '<svg class="ethio-ws-icon-list" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                        '<line x1="8" y1="6" x2="21" y2="6"></line>' +
                        '<line x1="8" y1="12" x2="21" y2="12"></line>' +
                        '<line x1="8" y1="18" x2="21" y2="18"></line>' +
                        '<line x1="3" y1="6" x2="3.01" y2="6"></line>' +
                        '<line x1="3" y1="12" x2="3.01" y2="12"></line>' +
                        '<line x1="3" y1="18" x2="3.01" y2="18"></line>' +
                    '</svg>' +
                '</div>' +
                '<div class="ethio-mobile-ws-text">' +
                    '<span class="ethio-mobile-ws-kicker">Menu</span>' +
                    '<span class="ethio-mobile-ws-title">Menu</span>' +
                '</div>';
            // Insert before the scrollable sidebar content but after the
            // absolute close button, so the header scrolls with the menu.
            const content = side.querySelector('.list-sidebar, .form-sidebar, .desk-sidebar, .sidebar-menu');
            if (content) side.insertBefore(header, content);
            else side.appendChild(header);
        }
        const info = getSidebarHeaderInfo(side);
        header.setAttribute('data-kind', info.kind);
        const kickerEl = header.querySelector('.ethio-mobile-ws-kicker');
        const titleEl = header.querySelector('.ethio-mobile-ws-title');
        if (kickerEl && kickerEl.textContent !== info.kicker) kickerEl.textContent = info.kicker;
        if (titleEl && titleEl.textContent !== info.title) titleEl.textContent = info.title;
    }

    function updateSidebarChrome() {
        if (!document.body) return;
        const activeWs = isWorkspaceRoute() && isMobileViewport();
        document.body.classList.toggle('ethio-mobile-workspace', activeWs);
        decorateFormSidebar();
        ensureFormSidebarObserver();
        ensureSidebarHeader();
        // Never leave the mobile drawer state on when returning to desktop.
        if (!isMobileViewport()) {
            document.body.classList.remove('sidebar-mobile-open');
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
        updateSidebarChrome();
        // Default collapsed is applied at script load. Do not re-apply here:
        // the async settings response must not override the user's toggle.
        if (conf && conf.hide_sidebar === false) {
            console.log('[EthioBiz] Sidebar enabled; default remains collapsed until the toggle is used.');
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
                updateSidebarChrome();
                _forceUIPending = false;
            });
        }
    });

    init();
    if (document.body) {
        sidebarObserver.observe(document.body, { childList: true, subtree: true });
    }

    // BISMALLAH: Clicking outside the sidebar collapses it. The navbar toggle,
    // the sidebar close button and the mobile hamburger are excluded so the
    // capture listener never fights the explicit toggle action.
    document.addEventListener('click', function (e) {
        const sidebar = document.querySelector('.layout-side-section, .desk-sidebar, .workspace-sidebar');
        if (!sidebar) return;
        if (!(e.target instanceof Element)) return;
        // Native Frappe may add `sidebar-collapsed` first; if our explicit
        // `sidebar-expanded` is still present, normalize the state instead of
        // returning early (otherwise the button UI stays stale).
        if (document.body.classList.contains('sidebar-collapsed') &&
            !document.body.classList.contains('sidebar-expanded')) return;
        if (sidebar.contains(e.target)) return;
        if (e.target.closest('#ethio-toggle-btn, #ethio-sidebar-close, #ethio-mobile-hamburger, .sidebar-toggle-btn, .navbar-sidebar-toggle, .toggle-sidebar, .page-head .page-title [data-action="toggle-sidebar"]')) return;
        setSidebarCollapsed(true);
        sidebar.classList.remove('opened');
        document.body.classList.remove('sidebar-mobile-open');
        console.log('[EthioBiz] Sidebar collapsed via outside click');
    }, true);

    // SPA route safety net: if the user has never toggled, keep the sidebar
    // collapsed across Workspace/Form/List transitions. Once the user makes an
    // explicit choice, respect it for the rest of the session.
    if (typeof frappe !== 'undefined' && frappe.router && typeof frappe.router.on === 'function') {
        frappe.router.on('change', function () {
            if (!_sidebarUserToggled) {
                setSidebarCollapsed(true);
            }
            // On phones the drawer is an overlay; it must never survive a
            // route change and hide the page the user just navigated to.
            if (isMobileViewport()) {
                document.body.classList.remove('sidebar-mobile-open');
            }
            updateSidebarChrome();
        });
    }

    // Keep the workspace-only mobile class in sync when rotating/resizing.
    let _mobileUiResizeTimer = null;
    window.addEventListener('resize', function () {
        clearTimeout(_mobileUiResizeTimer);
        _mobileUiResizeTimer = setTimeout(updateSidebarChrome, 120);
    });

    // Tapping a sidebar link on mobile should reveal the destination page
    // immediately (close the drawer) instead of leaving the drawer open.
    document.addEventListener('click', function (e) {
        if (!isMobileViewport()) return;
        if (!document.body.classList.contains('sidebar-mobile-open')) return;
        if (!(e.target instanceof Element)) return;
        const link = e.target.closest('.layout-side-section a.item-anchor, .layout-side-section a');
        if (!link) return;
        document.body.classList.remove('sidebar-mobile-open');
    }, true);

    function isDocView() {
        // 1. Check frappe router standard route
        if (typeof frappe !== 'undefined' && frappe.get_route) {
            const r = frappe.get_route();
            if (r && r[0] === 'Form') return true;
            if (r && (r[0] === 'List' || r[0] === 'Workspaces' || r[0] === 'Tree' || r[0] === 'query-report' || r[0] === 'dashboard-view')) return false;
        }

        // 2. Check frappe get_route_str
        if (typeof frappe !== 'undefined' && frappe.get_route_str) {
            let rs = '';
            try { rs = frappe.get_route_str(); } catch (e) { rs = ''; }
            if (rs && rs.indexOf('Form/') === 0) return true;
            if (rs && (rs.indexOf('List/') === 0 || rs.indexOf('Workspaces/') === 0)) return false;
        }

        // 3. Check body data-route attribute
        const bodyRoute = document.body ? document.body.getAttribute('data-route') : '';
        if (bodyRoute && bodyRoute.indexOf('Form/') === 0) return true;
        if (bodyRoute && (bodyRoute.indexOf('List/') === 0 || bodyRoute.indexOf('Workspaces/') === 0)) return false;

        // 4. Check window location pathname / hash
        const path = (window.location.pathname || '') + (window.location.hash || '');
        const cleanPath = path.replace(/^[#/]+/, '');
        const segments = cleanPath.split('/').filter(Boolean);
        // Desk format: /app/:doctype/:name  e.g. ['app', 'todo', 'h44qvre6j']
        if (segments.length >= 3 && segments[0] === 'app') {
            const seg2 = segments[2].toLowerCase();
            if (seg2 !== 'view' && seg2 !== 'list' && seg2 !== 'report' && seg2 !== 'dashboard') {
                return true;
            }
        }

        // 5. Check cur_frm
        if (typeof cur_frm !== 'undefined' && cur_frm && cur_frm.docname) return true;

        // 6. Check DOM for form actions / layout
        if (document.querySelector('.page-container[data-page-route^="Form"], .form-page:not(.hide), .form-layout, .page-head [data-label="Save"], .page-head .primary-action, .form-tabs-list')) {
            if (!document.querySelector('.frappe-list, .workspace-page, .report-view')) return true;
        }

        return false;
    }

    // BISMALLAH: Form Title Auto-Size Collapsible Toggle (Default strictly collapsed full-width, arrow only)
    // Mark document-form routes on <html> as early as possible. Frappe sets
    // body[data-route] only on page-change, which is too late for the first
    // paint; this class lets the single-line title CSS apply immediately and
    // prevents the expanded/multiline flicker.
    function setDocRouteClass() {
        const seg = (window.location.pathname || '').replace(/^\/+|\/+$/g, '').split('/');
        let isDoc = false;
        if (seg[0] === 'app' && seg.length >= 2) {
            const second = (seg[1] || '').toLowerCase();
            const third = (seg[2] || '').toLowerCase();
            const nonForm = ['list', 'view', 'report', 'query-report', 'dashboard', 'dashboard-view',
                'workspace', 'workspaces', 'tree', 'modules', 'module', 'setup', 'print', 'background_jobs'];
            if (nonForm.indexOf(second) === -1) {
                if (seg.length === 2) {
                    isDoc = false; // /app/<doctype> is the list view
                } else if (third === 'new') {
                    isDoc = true; // /app/<doctype>/new is a new document form
                } else if (nonForm.indexOf(third) === -1) {
                    isDoc = true; // /app/<doctype>/<name> is a document form
                }
            }
        }
        if (document.documentElement) {
            document.documentElement.classList.toggle('eb-doc-route', isDoc);
        }
        return isDoc;
    }
    window.ebSetDocRouteClass = setDocRouteClass;
    setDocRouteClass();

    function _collapseTitle(titleText, area) {
        if (!titleText) return;
        if (area) {
            area.classList.remove('eb-title-expanded');
            delete area.dataset.ebExpanded;
        }
        titleText.style.setProperty('white-space', 'nowrap', 'important');
        titleText.style.setProperty('overflow', 'hidden', 'important');
        titleText.style.setProperty('text-overflow', 'ellipsis', 'important');
        titleText.style.setProperty('max-width', 'calc(100% - 95px)', 'important');
        titleText.style.setProperty('min-width', '0', 'important');
        titleText.style.setProperty('visibility', 'visible', 'important');
        titleText.style.setProperty('opacity', '1', 'important');
        titleText.style.setProperty('cursor', 'default', 'important');
        titleText.style.removeProperty('word-break');
        titleText.style.removeProperty('overflow-y');
        titleText.style.removeProperty('overflow-x');
        titleText.style.removeProperty('max-height');
        titleText.style.removeProperty('width');
        titleText.style.removeProperty('flex');
    }

    function _expandTitle(titleText, area) {
        if (!titleText) return;
        if (area) {
            area.classList.add('eb-title-expanded');
            area.dataset.ebExpanded = '1';
        }
        titleText.style.setProperty('white-space', 'normal', 'important');
        titleText.style.setProperty('word-break', 'break-word', 'important');
        titleText.style.setProperty('overflow-y', 'auto', 'important');
        titleText.style.setProperty('overflow-x', 'hidden', 'important');
        titleText.style.setProperty('max-width', '100%', 'important');
    }

    function _clearTitleInlineStyles(titleText) {
        if (!titleText) return;
        ['max-width', 'white-space', 'overflow', 'overflow-y', 'overflow-x',
            'text-overflow', 'word-break', 'min-width', 'max-height', 'width',
            'flex', 'visibility', 'opacity', 'cursor'].forEach(function (prop) {
            titleText.style.removeProperty(prop);
        });
    }

    let _titleTogglePending = false;
    function _scheduleTitleToggle() {
        if (_titleTogglePending) return;
        _titleTogglePending = true;
        requestAnimationFrame(function () {
            _titleTogglePending = false;
            initTitleToggle();
        });
    }

    function initTitleToggle() {
        setDocRouteClass();
        if (!isDocView()) {
            // Remove any expand/collapse buttons from List views, Workspaces, Reports
            document.querySelectorAll('.eb-title-toggle-btn').forEach(b => b.remove());
            document.querySelectorAll('.title-area, .page-title').forEach(el => {
                el.classList.remove('eb-title-expanded');
                delete el.dataset.ebExpanded;
            });
            document.querySelectorAll('.page-head .title-text').forEach(t => {
                _clearTitleInlineStyles(t);
            });
            return;
        }

        const titleElements = document.querySelectorAll('.page-head .title-text');
        titleElements.forEach(titleText => {
            const head = titleText.closest('.page-head');
            if (head) head.classList.add('eb-doc-head');

            const area = titleText.closest('.title-area') || titleText.closest('.page-title');
            if (!area) return;

            // The class is the single source of truth. Never leave stale
            // expanded inline styles behind after a page/route reset.
            const isExpanded = area.classList.contains('eb-title-expanded');
            if (isExpanded) {
                _expandTitle(titleText, area);
            } else {
                _collapseTitle(titleText, area);
            }

            let toggle = area.querySelector('.eb-title-toggle-btn');
            if (!toggle) {
                const textContent = (titleText.textContent || '').trim();
                // Only add toggle button for long titles in document forms
                if (textContent.length <= 25) return;

                toggle = document.createElement('span');
                toggle.className = 'eb-title-toggle-btn';
                toggle.setAttribute('role', 'button');
                toggle.setAttribute('tabindex', '0');
                toggle.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggle.click();
                    }
                });
                toggle.addEventListener('click', function (e) {
                    if (e) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                    const nowExpanded = !area.classList.contains('eb-title-expanded');
                    if (nowExpanded) {
                        _expandTitle(titleText, area);
                        toggle.innerHTML = '<span class="eb-arrow" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 15 6-6 6 6"/></svg></span>';
                        toggle.title = 'Collapse';
                        toggle.setAttribute('aria-label', 'Collapse title');
                        toggle.setAttribute('aria-expanded', 'true');
                    } else {
                        _collapseTitle(titleText, area);
                        toggle.innerHTML = '<span class="eb-arrow" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg></span>';
                        toggle.title = 'Expand';
                        toggle.setAttribute('aria-label', 'Expand title');
                        toggle.setAttribute('aria-expanded', 'false');
                    }
                    if (window.updateDocTabsStickyTop) {
                        setTimeout(window.updateDocTabsStickyTop, 50);
                    }
                });
                titleText.parentNode.insertBefore(toggle, titleText.nextSibling);
            }

            if (isExpanded) {
                toggle.innerHTML = '<span class="eb-arrow" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 15 6-6 6 6"/></svg></span>';
                toggle.title = 'Collapse';
                toggle.setAttribute('aria-label', 'Collapse title');
                toggle.setAttribute('aria-expanded', 'true');
            } else {
                toggle.innerHTML = '<span class="eb-arrow" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg></span>';
                toggle.title = 'Expand';
                toggle.setAttribute('aria-label', 'Expand title');
                toggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    window.initTitleToggle = initTitleToggle;

    // Watch for the page head/title being inserted. This is what removes the
    // initial flicker on slow page loads where the fixed timers below fire
    // before Frappe has rendered the form title.
    let _titleObserver = null;
    function _startTitleObserver() {
        if (_titleObserver) return;
        const root = document.documentElement;
        if (!root) return;
        _titleObserver = new MutationObserver(function (mutations) {
            for (const m of mutations) {
                if (m.type !== 'childList') continue;
                for (const node of m.addedNodes) {
                    if (node.nodeType !== 1) continue;
                    const matches = (node.matches && (node.matches('.page-head, .title-text, .page-container, .form-page') ||
                        (node.querySelector && node.querySelector('.page-head, .title-text'))));
                    if (matches) {
                        _scheduleTitleToggle();
                        return;
                    }
                }
            }
        });
        _titleObserver.observe(root, { childList: true, subtree: true });
        _scheduleTitleToggle();
    }
    if (document.documentElement) {
        _startTitleObserver();
    } else {
        document.addEventListener('DOMContentLoaded', _startTitleObserver);
    }

    // Reset expanded state on document/page change so new doc always opens collapsed
    $(document).on('page-change router:change', function () {
        setDocRouteClass();
        document.querySelectorAll('.page-head .title-text').forEach(function (t) {
            const area = t.closest('.title-area') || t.closest('.page-title');
            _collapseTitle(t, area);
        });
        document.querySelectorAll('.title-area, .page-title').forEach(function (el) {
            el.classList.remove('eb-title-expanded');
            delete el.dataset.ebExpanded;
        });
        _scheduleTitleToggle();
    });

    $(document).on('page-change form-refresh form_refresh router:change', function () {
        _scheduleTitleToggle();
        setTimeout(initTitleToggle, 50);
        setTimeout(initTitleToggle, 200);
        setTimeout(initTitleToggle, 600);
        setTimeout(initTitleToggle, 1500);
    });

    // Initial load: apply collapsed state as soon as possible.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTitleToggle);
    } else {
        initTitleToggle();
    }
    setTimeout(initTitleToggle, 100);
    setTimeout(initTitleToggle, 500);
    setTimeout(initTitleToggle, 1500);
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
