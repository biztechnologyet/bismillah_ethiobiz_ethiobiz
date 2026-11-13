/**
 * EthioBiz Desk Filters — Universal Collapsible Filter Toolbar
 * Enables sleek collapsible filter bar across Frappe v15 List Views, Report Views & Kanban
 * Persists collapse/expand state per DocType in localStorage.
 */
(function () {
    const LS_PREFIX = "eb_filter_collapsed_";

    function getActiveFilterCount(filterSection) {
        if (!filterSection) return 0;
        let count = 0;
        // Check input values that are non-empty
        const inputs = filterSection.querySelectorAll('input:not([type="hidden"]), select');
        inputs.forEach(input => {
            if (input.value && input.value.trim() !== '' && input.value !== 'Open' && input.value !== 'All') {
                count++;
            }
        });
        // Check filter pills / tags
        const filterPills = filterSection.querySelectorAll('.filter-pill, .filter-tag, .btn-group.filter');
        if (filterPills.length) {
            count = Math.max(count, filterPills.length);
        }
        return count;
    }

    function initCollapsibleFilters() {
        const curRoute = (frappe.get_route && frappe.get_route()) || [];
        if (!curRoute.length) return;
        const viewType = curRoute[0];
        if (viewType !== 'List' && viewType !== 'query-report' && viewType !== 'Report') return;

        const doctype = curRoute[1] || 'default';
        const filterSections = document.querySelectorAll('.standard-filter-section, .list-filters, .filter-section');

        filterSections.forEach(section => {
            if (section.dataset.ebCollapsibleInit) return;
            section.dataset.ebCollapsibleInit = "1";

            const lsKey = LS_PREFIX + doctype;
            const savedState = localStorage.getItem(lsKey);
            // Default to collapsed if no preference set, to save screen space
            const isCollapsed = savedState === null ? true : savedState === '1';

            const activeCount = getActiveFilterCount(section);

            // Create toggle button container
            const toggleWrap = document.createElement('div');
            toggleWrap.className = 'eb-filter-toggle-container';
            toggleWrap.innerHTML = `
                <button type="button" class="eb-filter-toggle-btn" title="Toggle filter tools visibility">
                    <span class="eb-filter-icon">${isCollapsed ? '▶' : '▼'}</span>
                    <span>Filter Controls</span>
                    <span class="eb-filter-badge" style="${activeCount > 0 ? '' : 'display:none;'}">${activeCount} Active</span>
                </button>
            `;

            section.parentNode.insertBefore(toggleWrap, section);

            if (isCollapsed) {
                section.classList.add('eb-collapsed');
            }

            const btn = toggleWrap.querySelector('.eb-filter-toggle-btn');
            const icon = toggleWrap.querySelector('.eb-filter-icon');
            const badge = toggleWrap.querySelector('.eb-filter-badge');

            btn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                section.classList.toggle('eb-collapsed');
                const nowCollapsed = section.classList.contains('eb-collapsed');
                icon.textContent = nowCollapsed ? '▶' : '▼';
                localStorage.setItem(lsKey, nowCollapsed ? '1' : '0');
            });

            // Periodically refresh active filter counter badge
            section.addEventListener('change', function () {
                const count = getActiveFilterCount(section);
                if (count > 0) {
                    badge.textContent = `${count} Active`;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            });
        });
    }

    // Attach to Frappe navigation and refresh hooks
    $(document).on('page-change list_view_refresh report_refresh', function () {
        setTimeout(initCollapsibleFilters, 250);
        setTimeout(initCollapsibleFilters, 750);
    });

    if (typeof frappe !== 'undefined') {
        frappe.router && frappe.router.on && frappe.router.on('change', function () {
            setTimeout(initCollapsibleFilters, 300);
        });
    }

    $(function () {
        setTimeout(initCollapsibleFilters, 500);
    });
})();

