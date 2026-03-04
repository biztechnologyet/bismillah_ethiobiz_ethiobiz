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
        }

        init() {
            if (this.initialized) return;
            console.log('%c✨ EthioBiz Brand Manager Initializing...', 'color: #1FB6AE; font-weight: bold;');

            this.detectAndApply();

            if (typeof frappe !== 'undefined' && frappe.router) {
                frappe.router.on('change', () => this.detectAndApply());
            }
            $(document).on('page-change', () => this.detectAndApply());

            setInterval(() => {
                const route = this.getCurrentRoute();
                if (this.lastRoute !== route) {
                    this.lastRoute = route;
                    this.detectAndApply();
                }
            }, 1000);

            this.initialized = true;

            // F. Global Sidebar Toggle (One-time registration)
            $(document).on('click.ethiobiz', '.sidebar-toggle-btn, .toggle-sidebar', () => {
                document.body.classList.toggle('sidebar-collapsed');
                const isNowCollapsed = document.body.classList.contains('sidebar-collapsed');
                console.log('[EthioBiz] Sidebar Toggled. Collapsed:', isNowCollapsed);
            });
        }

        getCurrentRoute() {
            const hash = window.location.hash.replace('#', '').toLowerCase();
            const path = window.location.pathname.toLowerCase();
            return hash || path;
        }

        detectAndApply() {
            const route = this.getCurrentRoute();

            if (route === '/' || route.includes('login') || route === '') {
                this.currentPillar = BRAND_CONFIG.default;
                this.applyPillar();
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
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    // Header/Tab reordering removed as per user request
                    if (window.location.href.includes('walta') || window.location.href.includes('helpdesk')) {
                        document.querySelectorAll('h1, h2, .onboarding-step-title, .desk-sidebar-item-label, .onboarding-step-description').forEach(el => {
                            if (el.innerText.includes('Frappe Helpdesk')) {
                                el.innerText = el.innerText.replace(/Frappe Helpdesk/g, 'Walta Support');
                            }
                        });
                    }
                });
            });

            observer.observe(document.body, { childList: true, subtree: true });

            if (window.location.href.includes('walta') || window.location.href.includes('helpdesk')) {
                const targetText = "Frappe Helpdesk";
                const replaceText = "Walta Support";

                const globalScrub = () => {
                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                    let node;
                    while (node = walker.nextNode()) {
                        if (node.nodeValue.includes(targetText)) {
                            node.nodeValue = node.nodeValue.replace(new RegExp(targetText, 'g'), replaceText);
                        }
                    }
                    $(`div:contains("${targetText}"), span:contains("${targetText}"), h1:contains("${targetText}"), h2:contains("${targetText}")`).each(function () {
                        const contents = $(this).contents();
                        contents.each(function () {
                            if (this.nodeType === 3 && this.nodeValue.includes(targetText)) {
                                this.nodeValue = this.nodeValue.replace(new RegExp(targetText, 'g'), replaceText);
                            }
                        });
                    });
                };

                const textObserver = new MutationObserver(() => globalScrub());
                textObserver.observe(document.body, { childList: true, subtree: true, characterData: true });

                let scrubCount = 0;
                const scrubInt = setInterval(() => {
                    globalScrub();
                    if (++scrubCount > 120) clearInterval(scrubInt);
                }, 500);
            }

            // E. Dagu Specifics
            if (p.id === 'dagu') {
                const helpLinks = document.querySelectorAll('a[href*="help"]');
                helpLinks.forEach(link => {
                    link.href = '/walta/documentations';
                    link.innerText = 'Walta > Documentations';
                });
                $('.help-sidebar').hide();
            }
        }

        updateLogo(src, alt) {
            const selectors = ['.navbar-brand img', '.app-logo', 'img[src*="logo"]', '#navbar-logo'];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(img => {
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
            const bgUrl = isDark ? p.dark_bg : p.light_bg;

            let styleEl = document.getElementById('ethiobiz-nuclear-bg');
            if (!styleEl) {
                styleEl = document.createElement('style');
                styleEl.id = 'ethiobiz-nuclear-bg';
                document.head.appendChild(styleEl);
            }

            styleEl.textContent = `
                html, body {
                    background-image: url("${bgUrl}") !important;
                    background-attachment: fixed !important;
                    background-size: cover !important;
                    background-position: center !important;
                    background-color: ${isDark ? '#0E1A1A' : '#F8F6F2'} !important;
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

    window.EthioBizBrandManager = new BrandManager();
    window.EthioBizBrandManager.init();

})();

// BISMALLAH ETHIOBIZ FLOATING SIDEBAR V6
frappe.ready(function () {
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
            }
            
            .layout-side-section > * {
                max-width: 100% !important;
                overflow-x: hidden !important;
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
        // A. Toggle Button
        const brand = document.querySelector('.navbar-brand');
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
            console.log('[EthioBiz] Toggle button injected');
        }

        // B. Close Button
        const sidebar = document.querySelector('.layout-side-section');
        if (sidebar && !document.getElementById('ethio-sidebar-close')) {
            const closeBtn = document.createElement('div');
            closeBtn.id = 'ethio-sidebar-close';
            closeBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;
            closeBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                document.body.classList.add('sidebar-collapsed');
            };
            sidebar.insertBefore(closeBtn, sidebar.firstChild);
            console.log('[EthioBiz] Close button injected');
        }
        // C. Hide Dagu LMS Popup (Right Panel & Sidebar)
        // Right Panel
        const rightPanels = document.querySelectorAll('.fixed.right-0, .bg-surface-modal');
        rightPanels.forEach(el => {
            if (el && el.innerText && el.innerText.includes('Welcome to Dagu Learning')) {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.setAttribute('style', 'display: none !important; visibility: hidden !important;');
            }
        });

        // Sidebar Widget
        const sidebarWidgets = document.querySelectorAll('div');
        sidebarWidgets.forEach(el => {
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
    }

    function init() {
        forceUI();

        // Force Collapse (3s grace)
        let collapseInterval = setInterval(() => {
            if (!document.body.classList.contains('sidebar-collapsed')) {
                document.body.classList.add('sidebar-collapsed');
                console.log('[EthioBiz] Forced collapse');
            }
        }, 100);
        setTimeout(() => clearInterval(collapseInterval), 3000);
    }

    // Observer
    const observer = new MutationObserver(() => {
        forceUI();
    });

    init();
    observer.observe(document.body, { childList: true, subtree: true });

    // Fallback
    setInterval(forceUI, 500);
});
// END BISMALLAH ETHIOBIZ FLOATING SIDEBAR V6
