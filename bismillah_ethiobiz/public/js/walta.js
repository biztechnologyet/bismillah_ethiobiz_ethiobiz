/* Walta JS - Global Branding Script */

frappe.provide("walta");

walta.config = {
    app_renames: {
        "ERPNext": "DOBiz",
        "Helpdesk": "Walta",
        "Learning": "Dagu",
        "Frappe HR": "DOBiz HR",
        "HR": "DOBiz HR"
    },
    text_replacements: {
        "Welcome to Frappe Helpdesk": "Welcome to Walta",
        "Frappe Helpdesk": "Walta"
    }
};

walta.setup = function () {
    // console.log("Walta Branding Active");
};

walta.apply_branding = function () {
    // 1. Text Replacements (Recursive check)
    walta.replace_text_content(document.body);

    // 2. App Switcher / Menu renaming
    $(".app-item-title, .app-title").each(function () {
        let text = $(this).text().trim();
        if (walta.config.app_renames[text]) {
            $(this).text(walta.config.app_renames[text]);
        }
    });

    // 3. Navbar Brand fallback
    if ($(".navbar-brand span").text().includes("Helpdesk")) {
        $(".navbar-brand span").text("Walta");
    }
};

walta.replace_text_content = function (root) {
    // Helper to replace text in text nodes
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while (node = walker.nextNode()) {
        let val = node.nodeValue;
        // Check specifically for the Welcome message
        if (val && val.includes("Welcome to Frappe Helpdesk")) {
            node.nodeValue = val.replace("Welcome to Frappe Helpdesk", "Welcome to Walta");
        }
        // General replacements if needed (be careful not to break code/attributes)
    }
};

// Aggressive Polling for Dynamic Modals (Getting Started)
walta.init_observer = function () {
    // 1. Mutation Observer for DOM changes
    const observer = new MutationObserver((mutations) => {
        // Debounce slightly to avoid performance hit
        if (walta.timer) clearTimeout(walta.timer);
        walta.timer = setTimeout(walta.apply_branding, 50);
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    // 2. Fallback Interval (every 1 sec) to catch anything missed
    setInterval(walta.apply_branding, 1000);
};

// Init
$(document).ready(function () {
    walta.setup();
    walta.init_observer();
    walta.apply_branding();
});
