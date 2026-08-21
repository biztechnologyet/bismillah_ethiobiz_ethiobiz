/**
 * EthioBiz Isolated Brand Controller
 * Bismillah Ar-Rahman Ar-Rahim
 * 
 * Manages strict separation of Dagu, Magala, Walta, and Tibeb branding.
 * Handles logos, backgrounds, and colors dynamically.
 * 
 * © 2025-2026 EthioBiz | Powered by Biz Technology Solutions
 */

(function () {
    'use strict';

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
        default_logo: "/files/ethiobiz_butterfly_logo.png",

        pillars: {
            dagu: {
                id: "dagu",
                name: "Dagu Learning",
                logo: "/files/dagu_logo.png",
                primary: "#2E3A8C",
                rgb: "46, 58, 140",
                routes: ["lms", "education", "dagu"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light.png"
            },
            magala: {
                id: "magala",
                name: "Magala Market",
                logo: "/files/magala_logo.png",
                primary: "#2F6B4F",
                rgb: "47, 107, 79",
                routes: ["selling", "buying", "stock", "crm", "accounting", "magala", "all-products"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_website_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_light_bg.png"
            },
            walta: {
                id: "walta",
                name: "Walta Support",
                logo: "/files/walta_logo.png",
                primary: "#0F3557",
                rgb: "15, 53, 87",
                routes: ["hr", "hrms", "payroll", "projects", "settings", "users", "walta", "helpdesk", "support"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light_1.jpeg"
            },
            tibeb: {
                id: "tibeb",
                name: "Tibeb",
                logo: "/files/tibeb_logo.png",
                primary: "#C9A24D",
                rgb: "201, 162, 77",
                routes: ["tibeb"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light_1.jpeg"
            },
            afocha: {
                id: "afocha",
                name: "Afocha Community",
                logo: "/files/afocha_logo.png",
                primary: "#008080",
                rgb: "0, 128, 128",
                routes: ["afocha", "social"],
                dark_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png",
                light_bg: "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light.png"
            },
            dobiz: {
                id: "dobiz",
                name: "DOBiz Smart ERP",
                logo: "/files/dobiz_logo.png",
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
            logo: "/files/ethiobiz_butterfly_logo.png",
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
            window.__ethiobizBrandInitialized = true;

            this.detectAndApply();

            if (typeof frappe !== 'undefined' && frappe.router) {
                frappe.router.on('change', () => this.detectAndApply());
            }
            $(document).on('page-change', () => this.detectAndApply());

            this._routeCheckInterval = setInterval(() => {
                const route = this.getCurrentRoute();
                if (this.lastRoute !== route) {
                    this.lastRoute = route;
                    this.detectAndApply();
                }
            }, 3000);

            this.initialized = true;
        }

        getCurrentRoute() {
            const hash = window.location.hash.replace('#', '').toLowerCase();
            const path = window.location.pathname.toLowerCase();
            return hash || path;
        }

        detectAndApply() {
            const route = this.getCurrentRoute();

            if (route === '/' || route === '/home' || route.includes('login') || route === '' || route.includes('ethiobiz_new') || route.includes('ethiobiz-new')) {
                this.currentPillar = BRAND_CONFIG.default;
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
            this.updateLogo(p.logo, p.name);
        }

        updateLogo(src, alt) {
            const selectors = ['.navbar-brand img:not(.pillar-brand-logo):not(.hero-brand-logo):not(.superhub-logo-img)', '.app-logo', '#navbar-logo'];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(img => {
                    if (img.classList.contains('pillar-brand-logo') || img.classList.contains('hero-brand-logo') || img.classList.contains('superhub-logo-img')) return;
                    img.src = src;
                    img.alt = alt;
                });
            });
        }
    }

    const manager = new BrandManager();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => manager.init());
    } else {
        manager.init();
    }
})();
