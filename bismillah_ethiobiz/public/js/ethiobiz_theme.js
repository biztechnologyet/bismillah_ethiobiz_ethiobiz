/**
 * EthioBiz Isolated Brand Controller
 * Bismillah Ar-Rahman Ar-Rahim
 * 
 * Manages strict separation of Dagu, Magala, Walta, and Tibeb branding in Desk.
 * Completely passive on public website pages so that all brand logos,
 * pillar cards, launchpad icons, and catalog images render their authentic assets.
 * 
 * © 2025-2026 EthioBiz | Powered by Biz Technology Solutions
 */

(function () {
    'use strict';

    // Clear stale service worker caches if present
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

    // Do NOT run on public website pages - allow HTML templates to render authentic logos
    const path = window.location.pathname.toLowerCase();
    if (!path.startsWith('/app') && !path.startsWith('/desk')) {
        // Public website mode: do not touch ANY image or logo on the page
        return;
    }

    if (window.__ethiobizBrandInitialized) return;

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
                routes: ["lms", "education", "dagu"]
            },
            magala: {
                id: "magala",
                name: "Magala Market",
                logo: "/files/magala_logo.png",
                primary: "#2F6B4F",
                rgb: "47, 107, 79",
                routes: ["selling", "buying", "stock", "crm", "accounting", "magala"]
            },
            walta: {
                id: "walta",
                name: "Walta Support",
                logo: "/files/walta_logo.png",
                primary: "#0F3557",
                rgb: "15, 53, 87",
                routes: ["hr", "hrms", "payroll", "projects", "settings", "users", "walta", "helpdesk", "support"]
            },
            tibeb: {
                id: "tibeb",
                name: "Tibeb",
                logo: "/files/tibeb_logo.png",
                primary: "#C9A24D",
                rgb: "201, 162, 77",
                routes: ["tibeb"]
            },
            afocha: {
                id: "afocha",
                name: "Afocha Community",
                logo: "/files/afocha_logo.png",
                primary: "#008080",
                rgb: "0, 128, 128",
                routes: ["afocha", "social"]
            },
            dobiz: {
                id: "dobiz",
                name: "DOBiz Smart ERP",
                logo: "/files/dobiz_logo.png",
                primary: "#1FB6AE",
                rgb: "31, 182, 174",
                routes: ["app", "desk", "workspace"]
            }
        },

        default: {
            id: "ethiobiz",
            name: "EthioBiz",
            logo: "/files/ethiobiz_butterfly_logo.png",
            primary: "#1FB6AE",
            rgb: "31, 182, 174"
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

            this.initialized = true;
        }

        getCurrentRoute() {
            const hash = window.location.hash.replace('#', '').toLowerCase();
            const path = window.location.pathname.toLowerCase();
            return hash || path;
        }

        detectAndApply() {
            const route = this.getCurrentRoute();
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
            // Only update Desk navbar logo in /app
            const deskLogo = document.querySelector('.navbar .navbar-brand .app-logo, .navbar-home .app-logo');
            if (deskLogo) {
                deskLogo.src = p.logo;
                deskLogo.alt = p.name;
            }
        }
    }

    const manager = new BrandManager();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => manager.init());
    } else {
        manager.init();
    }
})();
