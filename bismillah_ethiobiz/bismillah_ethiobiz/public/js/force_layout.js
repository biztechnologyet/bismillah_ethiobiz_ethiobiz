frappe.ui.force_vertical_layout = function () {
    // 2-Tier Header Layout Enforcement for Frappe Desk
    // Tier 1: Full-Width Title Bar (100% width, no squishing, status pill aligned)
    // Tier 2: Dedicated Actions Bar below Title, aligned to Right (Save, < >, print)
    // Tier 3: Form Body & Tabs starting cleanly below Actions
    const pageHeads = document.querySelectorAll('.page-head');
    pageHeads.forEach(head => {
        const headContent = head.querySelector('.page-head-content');
        const title = head.querySelector('.page-title');
        const actions = head.querySelector('.page-actions');

        if (headContent) {
            headContent.style.setProperty('display', 'flex', 'important');
            headContent.style.setProperty('flex-direction', 'column', 'important');
            headContent.style.setProperty('align-items', 'stretch', 'important');
            headContent.style.setProperty('width', '100%', 'important');
            headContent.style.setProperty('gap', '8px', 'important');
            headContent.style.setProperty('padding', '10px 16px 8px', 'important');
        }

        if (title) {
            title.classList.remove('col-md-4', 'col-sm-6', 'col-8', 'col-xs-7');
            title.style.setProperty('width', '100%', 'important');
            title.style.setProperty('max-width', '100%', 'important');
            title.style.setProperty('flex', '1 1 100%', 'important');
            title.style.setProperty('display', 'flex', 'important');
            title.style.setProperty('align-items', 'center', 'important');
            title.style.setProperty('justify-content', 'flex-start', 'important');
            title.style.setProperty('margin-bottom', '4px', 'important');

            const titleText = title.querySelector('.title-text');
            if (titleText) {
                titleText.style.setProperty('white-space', 'normal', 'important');
                titleText.style.setProperty('word-break', 'break-word', 'important');
                titleText.style.setProperty('font-size', '1.4rem', 'important');
                titleText.style.setProperty('font-weight', '800', 'important');
                titleText.style.setProperty('line-height', '1.3', 'important');
            }
        }

        if (actions) {
            actions.classList.remove('col-md-8', 'col-sm-6', 'col-4', 'col-xs-5', 'text-right');
            actions.style.setProperty('width', '100%', 'important');
            actions.style.setProperty('display', 'flex', 'important');
            actions.style.setProperty('justify-content', 'flex-end', 'important');
            actions.style.setProperty('align-items', 'center', 'important');
            actions.style.setProperty('gap', '8px', 'important');
            actions.style.setProperty('margin-top', '2px', 'important');
            actions.style.setProperty('padding-top', '6px', 'important');
            actions.style.setProperty('border-top', '1px solid rgba(0, 0, 0, 0.05)', 'important');
        }

        if (title && title.parentElement && title.parentElement.classList.contains('row')) {
            title.parentElement.classList.remove('row');
            title.parentElement.style.display = 'flex';
            title.parentElement.style.flexDirection = 'column';
            title.parentElement.style.alignItems = 'stretch';
            title.parentElement.style.width = '100%';
        }
    });
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
