frappe.ui.force_vertical_layout = function () {
    // Aggressive Layout Enforcement for Vertical Header
    const title = document.querySelector('.page-title');
    const actions = document.querySelector('.page-actions');
    const headContent = document.querySelector('.page-head-content');

    if (title) {
        // Remove Bootstrap grid classes that constrain width
        title.classList.remove('col-md-4', 'col-sm-6', 'col-8');
        title.style.setProperty('width', '100%', 'important');
        title.style.setProperty('max-width', '100%', 'important');
        title.style.setProperty('flex', '0 0 100%', 'important');
    }

    if (actions) {
        // Remove Bootstrap grid classes
        actions.classList.remove('col-md-8', 'col-sm-6', 'col-4', 'text-right');
        actions.style.setProperty('width', '100%', 'important');
        actions.style.setProperty('margin-left', '0', 'important');
    }

    if (headContent) {
        headContent.style.setProperty('flex-direction', 'column', 'important');
    }

    // Safety check: ensure no other "row" parents are constraining
    if (title && title.parentElement && title.parentElement.classList.contains('row')) {
        title.parentElement.classList.remove('row');
        title.parentElement.style.display = 'flex';
        title.parentElement.style.flexDirection = 'column';
    }
};

// Run on page change
$(document).on('page-change', function () {
    setTimeout(frappe.ui.force_vertical_layout, 500);
    setTimeout(frappe.ui.force_vertical_layout, 2000); // Retry for slow loads
});

// Run immediately
frappe.ui.force_vertical_layout();
