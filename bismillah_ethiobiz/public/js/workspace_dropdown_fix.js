/**
 * WORKSPACE DROPDOWN Z-INDEX FIX
 * Dynamically ensures all dropdown menus appear on top
 */
(function () {
    'use strict';

    if (document.querySelector('.web-form')) return;

    // Function to fix dropdown z-index
    function fixDropdownZIndex() {
        // Find all visible dropdown menus
        const dropdowns = document.querySelectorAll('.dropdown-menu.show, .dropdown-menu:not(.hide)');

        dropdowns.forEach(dropdown => {
            // Force extremely high z-index with inline style (highest priority)
            dropdown.style.setProperty('z-index', '2147483647', 'important');
            dropdown.style.setProperty('position', 'absolute', 'important');

            // Also boost parent's z-index
            let parent = dropdown.closest('.widget, .grid-item, .sidebar-item, .workspace-sidebar-item, .dropdown, .standard-sidebar-item, .page-actions, .page-head, .standard-actions, .header-actions');
            if (parent) {
                parent.style.setProperty('z-index', '2147483646', 'important');
                parent.style.setProperty('position', 'relative', 'important');
            }

            // Special handling for sidebar menus - boost the entire sidebar section
            let sidebarParent = dropdown.closest('.desk-sidebar, .workspace-sidebar, .standard-sidebar');
            if (sidebarParent) {
                sidebarParent.style.setProperty('z-index', '2147483645', 'important');
                sidebarParent.style.setProperty('position', 'relative', 'important');
            }
        });

        // Also ensure sidebar items themselves don't create stacking issues
        document.querySelectorAll('.sidebar-item, .standard-sidebar-item').forEach(item => {
            item.style.setProperty('overflow', 'visible', 'important');
        });

        repositionMobileDropdowns();
    }

    // MOBILE DROPDOWN REPOSITION (additive, 2026-09-10)
    // On mobile (<768px) Bootstrap/Popper places some desk menus off-screen or
    // mis-aligned, so this pins every open menu below its toggle button,
    // right-aligned and clamped inside the viewport. Desktop is untouched.
    function repositionMobileDropdowns() {
        if (window.innerWidth > 768) return;
        var vw = document.documentElement.clientWidth || window.innerWidth;
        var vh = document.documentElement.clientHeight || window.innerHeight;
        var PAD = 8;

        document.querySelectorAll('.dropdown-menu.show').forEach(function (menu) {
            if (menu.closest('.navbar')) return;

            var toggle = (function () {
                var grp = menu.closest('.menu-btn-group, .actions-btn-group, .dropdown, .btn-group');
                if (grp) {
                    var t = grp.querySelector('[data-toggle="dropdown"]') || grp.querySelector('button, .btn');
                    if (t) return t;
                }
                var prev = menu.previousElementSibling;
                if (prev && prev.matches('button, .btn')) return prev;
                return null;
            })();
            if (!toggle) return;

            var tr = toggle.getBoundingClientRect();
            var mr = menu.getBoundingClientRect();
            var menuW = Math.min(mr.width, vw - PAD * 2);
            var menuH = mr.height;

            if (menuW < mr.width) {
                menu.style.setProperty('max-width', menuW + 'px', 'important');
            }

            var rightAlign = menu.classList.contains('dropdown-menu-right') || (tr.left + menuW > vw - PAD);
            var left = rightAlign ? Math.max(PAD, tr.right - menuW) : Math.max(PAD, tr.left);
            left = Math.min(left, vw - menuW - PAD);

            var top = tr.bottom + 6;
            if (top + menuH > vh - PAD) {
                top = Math.max(PAD, tr.top - menuH - 6);
            }

            var op = menu.offsetParent;
            if (op) {
                var or = op.getBoundingClientRect();
                menu.style.setProperty('top', Math.round(top - or.top) + 'px', 'important');
                menu.style.setProperty('left', Math.round(left - or.left) + 'px', 'important');
            } else {
                menu.style.setProperty('top', Math.round(top + window.scrollY) + 'px', 'important');
                menu.style.setProperty('left', Math.round(left + window.scrollX) + 'px', 'important');
            }

            menu.style.setProperty('position', 'absolute', 'important');
            menu.style.setProperty('transform', 'none', 'important');
            menu.style.setProperty('will-change', 'auto', 'important');
        });
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixDropdownZIndex);
    } else {
        fixDropdownZIndex();
    }

    // Watch for dropdown menu additions/changes
    const observer = new MutationObserver((mutations) => {
        let shouldFix = false;
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length || mutation.attributeName === 'class') {
                shouldFix = true;
            }
        });
        if (shouldFix) {
            setTimeout(fixDropdownZIndex, 10);
        }
    });

    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class']
        });
    }

    // Also listen for Bootstrap dropdown events
    if (typeof $ !== 'undefined') {
        $(document).on('shown.bs.dropdown', fixDropdownZIndex);
        $(document).on('show.bs.dropdown', fixDropdownZIndex);
    }

    // Run periodically as a fallback
    setInterval(fixDropdownZIndex, 500);

    console.log('✅ Workspace Dropdown Z-Index Fix Loaded');
})();