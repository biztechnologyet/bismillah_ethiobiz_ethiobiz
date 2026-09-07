frappe.ui.force_vertical_layout = function () {
    // Robust Document/Form view detection
    const isDoc = (function () {
        // 1. Check frappe router standard route
        if (typeof frappe !== 'undefined' && frappe.get_route) {
            const r = frappe.get_route();
            if (r && r[0] === 'Form') return true;
            if (r && (r[0] === 'List' || r[0] === 'Workspaces' || r[0] === 'Tree' || r[0] === 'query-report' || r[0] === 'dashboard-view')) return false;
        }

        // 2. Check frappe get_route_str
        if (typeof frappe !== 'undefined' && frappe.get_route_str) {
            const rs = frappe.get_route_str();
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
    })();

    const pageHeads = document.querySelectorAll('.page-head');
    pageHeads.forEach(head => {
        const headContent = head.querySelector('.page-head-content');
        const title = head.querySelector('.page-title');
        const actions = head.querySelector('.page-actions');

        if (!isDoc) {
            // Non-document views (List View, Workspace, Reports, Dashboards):
            // KEEP NATIVE CLEAN HORIZONTAL ROW - DO NOT SQUISH TITLE
            head.classList.remove('eb-doc-head');
            if (headContent) {
                headContent.style.setProperty('display', 'flex', 'important');
                headContent.style.setProperty('flex-direction', 'row', 'important');
                headContent.style.setProperty('align-items', 'center', 'important');
                headContent.style.setProperty('justify-content', 'space-between', 'important');
                headContent.style.removeProperty('gap');
                headContent.style.removeProperty('padding');
            }
            if (title) {
                title.style.setProperty('width', 'auto', 'important');
                title.style.setProperty('max-width', 'none', 'important');
                title.style.setProperty('flex', '0 1 auto', 'important');
                title.style.setProperty('display', 'flex', 'important');
                title.style.setProperty('align-items', 'center', 'important');
                const titleText = title.querySelector('.title-text');
                if (titleText) {
                    titleText.style.setProperty('max-width', 'none', 'important');
                    titleText.style.setProperty('width', 'auto', 'important');
                    titleText.style.setProperty('white-space', 'nowrap', 'important');
                    titleText.style.setProperty('overflow', 'visible', 'important');
                    titleText.style.setProperty('text-overflow', 'clip', 'important');
                    titleText.style.removeProperty('word-break');
                }
            }
            if (actions) {
                actions.style.setProperty('width', 'auto', 'important');
                actions.style.setProperty('display', 'flex', 'important');
                actions.style.setProperty('align-items', 'center', 'important');
                actions.style.setProperty('justify-content', 'flex-end', 'important');
                actions.style.removeProperty('margin-top');
                actions.style.removeProperty('padding-top');
                actions.style.removeProperty('border-top');
            }
            head.querySelectorAll('.eb-title-toggle-btn').forEach(b => b.remove());
            return;
        }

        // DOCUMENT / FORM VIEW: Enforce 2-Tier Header Layout
        head.classList.add('eb-doc-head');
        if (headContent) {
            headContent.style.setProperty('display', 'flex', 'important');
            headContent.style.setProperty('flex-direction', 'column', 'important');
            headContent.style.setProperty('align-items', 'stretch', 'important');
            headContent.style.setProperty('width', '100%', 'important');
            headContent.style.setProperty('max-width', '100%', 'important');
            headContent.style.setProperty('box-sizing', 'border-box', 'important');
            headContent.style.setProperty('overflow', 'hidden', 'important');
            headContent.style.setProperty('gap', '4px', 'important');
            headContent.style.setProperty('padding', '8px 16px 6px', 'important');
        }

        if (title) {
            title.classList.remove('col-md-4', 'col-sm-6', 'col-8', 'col-xs-7');
            title.style.setProperty('width', '100%', 'important');
            title.style.setProperty('max-width', '100%', 'important');
            title.style.setProperty('min-width', '0', 'important');
            title.style.setProperty('flex', '1 1 100%', 'important');
            title.style.setProperty('display', 'flex', 'important');
            title.style.setProperty('align-items', 'center', 'important');
            title.style.setProperty('justify-content', 'flex-start', 'important');
            title.style.setProperty('margin-bottom', '2px', 'important');
            title.style.setProperty('box-sizing', 'border-box', 'important');
            title.style.setProperty('overflow', 'hidden', 'important');

            const titleText = title.querySelector('.title-text');
            if (titleText) {
                const area = titleText.closest('.title-area') || title.querySelector('.title-area') || title;
                const isExpanded = area.classList.contains('eb-title-expanded') || !!area.dataset.ebExpanded;

                if (isExpanded) {
                    titleText.style.setProperty('white-space', 'normal', 'important');
                    titleText.style.setProperty('word-break', 'break-word', 'important');
                    titleText.style.setProperty('overflow-y', 'auto', 'important');
                    titleText.style.setProperty('max-width', '100%', 'important');
                } else {
                    titleText.style.setProperty('white-space', 'nowrap', 'important');
                    titleText.style.setProperty('overflow', 'hidden', 'important');
                    titleText.style.setProperty('text-overflow', 'ellipsis', 'important');
                    titleText.style.setProperty('max-width', 'calc(100% - 95px)', 'important');
                }
                titleText.style.setProperty('min-width', '0', 'important');
                titleText.style.setProperty('font-size', '1.35rem', 'important');
                titleText.style.setProperty('font-weight', '800', 'important');
                titleText.style.setProperty('line-height', '1.3', 'important');
                titleText.style.setProperty('box-sizing', 'border-box', 'important');
                titleText.style.setProperty('visibility', 'visible', 'important');
                titleText.style.setProperty('opacity', '1', 'important');
            }
        }

        if (actions) {
            actions.classList.remove('col-md-8', 'col-sm-6', 'col-4', 'col-xs-5', 'text-right');
            actions.style.setProperty('width', '100%', 'important');
            actions.style.setProperty('max-width', '100%', 'important');
            actions.style.setProperty('display', 'flex', 'important');
            actions.style.setProperty('justify-content', 'flex-end', 'important');
            actions.style.setProperty('align-items', 'center', 'important');
            actions.style.setProperty('gap', '8px', 'important');
            actions.style.setProperty('margin-top', '2px', 'important');
            actions.style.setProperty('padding-top', '6px', 'important');
            actions.style.setProperty('border-top', '1px solid rgba(0, 0, 0, 0.05)', 'important');
            actions.style.setProperty('box-sizing', 'border-box', 'important');
            actions.style.setProperty('flex-wrap', 'wrap', 'important');
        }

        if (title && title.parentElement && title.parentElement.classList.contains('row')) {
            title.parentElement.classList.remove('row');
            title.parentElement.style.display = 'flex';
            title.parentElement.style.flexDirection = 'column';
            title.parentElement.style.alignItems = 'stretch';
            title.parentElement.style.width = '100%';
        }
    });

    if (window.initTitleToggle) {
        window.initTitleToggle();
    }
};

// Run on page events
$(document).on('page-change form-refresh form_refresh router:change', function () {
    if (document.querySelector('.web-form')) return;
    setTimeout(frappe.ui.force_vertical_layout, 150);
    setTimeout(frappe.ui.force_vertical_layout, 600);
    setTimeout(frappe.ui.force_vertical_layout, 1500);
});

// Run immediately
if (typeof frappe !== 'undefined' && frappe.ui) {
    if (!document.querySelector('.web-form')) {
        frappe.ui.force_vertical_layout();
    }
}
