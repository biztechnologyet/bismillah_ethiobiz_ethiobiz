frappe.ui.force_vertical_layout = function () {
    // Determine if the current view is a Document/Form view
    const isDoc = (function () {
        if (typeof cur_frm !== 'undefined' && cur_frm && cur_frm.docname) return true;
        const route = (typeof frappe !== 'undefined' && frappe.get_route) ? frappe.get_route() : [];
        if (route && route[0] === 'app' && route.length === 3 && route[2] !== 'view') return true;
        if (document.querySelector('.form-page:not(.hide), .form-container:not(.hide)')) return true;
        return false;
    })();

    const pageHeads = document.querySelectorAll('.page-head');
    pageHeads.forEach(head => {
        const headContent = head.querySelector('.page-head-content');
        const title = head.querySelector('.page-title');
        const actions = head.querySelector('.page-actions');

        if (!isDoc) {
            // Non-document views (List View, Workspace, Reports, Dashboards):
            // KEEP NATIVE CLEAN HORIZONTAL LAYOUT - DO NOT SQUISH TITLE
            head.classList.remove('eb-doc-head');
            if (headContent) {
                headContent.style.removeProperty('display');
                headContent.style.removeProperty('flex-direction');
                headContent.style.removeProperty('gap');
                headContent.style.removeProperty('padding');
            }
            if (title) {
                title.style.removeProperty('width');
                title.style.removeProperty('max-width');
                title.style.removeProperty('flex');
                const titleText = title.querySelector('.title-text');
                if (titleText) {
                    titleText.style.removeProperty('max-width');
                    titleText.style.removeProperty('white-space');
                    titleText.style.removeProperty('overflow');
                    titleText.style.removeProperty('text-overflow');
                    titleText.style.removeProperty('word-break');
                }
            }
            if (actions) {
                actions.style.removeProperty('width');
                actions.style.removeProperty('margin-top');
                actions.style.removeProperty('padding-top');
                actions.style.removeProperty('border-top');
            }
            if (title && title.parentElement && !title.parentElement.classList.contains('row')) {
                title.parentElement.classList.add('row');
                title.parentElement.style.removeProperty('display');
                title.parentElement.style.removeProperty('flex-direction');
                title.parentElement.style.removeProperty('align-items');
                title.parentElement.style.removeProperty('width');
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
            headContent.style.setProperty('gap', '6px', 'important');
            headContent.style.setProperty('padding', '10px 16px 6px', 'important');
        }

        if (title) {
            title.classList.remove('col-md-4', 'col-sm-6', 'col-8', 'col-xs-7');
            title.style.setProperty('width', '100%', 'important');
            title.style.setProperty('max-width', '100%', 'important');
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
                    titleText.style.setProperty('max-width', 'calc(100% - 75px)', 'important');
                }
                titleText.style.setProperty('font-size', '1.35rem', 'important');
                titleText.style.setProperty('font-weight', '800', 'important');
                titleText.style.setProperty('line-height', '1.3', 'important');
                titleText.style.setProperty('box-sizing', 'border-box', 'important');
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
$(document).on('page-change form-refresh', function () {
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
