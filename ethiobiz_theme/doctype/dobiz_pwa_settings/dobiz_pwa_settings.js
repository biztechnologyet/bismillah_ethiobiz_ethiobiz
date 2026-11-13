frappe.ui.form.on("DOBiz PWA Settings", {
    refresh: function (frm) {
        frm.add_custom_button(__("Reset to Defaults"), function () {
            frappe.call({
                method: "bismillah_ethiobiz.pwa_settings.reset_defaults",
                callback: function (r) {
                    frappe.msgprint(__("PWA settings restored to defaults."));
                    frm.refresh();
                }
            });
        });
    }
});
