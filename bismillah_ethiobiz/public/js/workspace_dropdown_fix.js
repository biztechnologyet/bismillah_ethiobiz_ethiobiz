/**
 * WORKSPACE DROPDOWN Z-INDEX FIX
 * Dynamically ensures all dropdown menus appear on top
 */
(function () {
    'use strict';

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

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
    });

    // Also listen for Bootstrap dropdown events
    if (typeof $ !== 'undefined') {
        $(document).on('shown.bs.dropdown', fixDropdownZIndex);
        $(document).on('show.bs.dropdown', fixDropdownZIndex);
    }

    // Run periodically as a fallback
    setInterval(fixDropdownZIndex, 500);

    console.log('✅ Workspace Dropdown Z-Index Fix Loaded');
})();
