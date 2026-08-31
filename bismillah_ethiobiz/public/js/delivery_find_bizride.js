// BISMALLAH ETHIOBIZ DESK DELIVERY BIZRIDE DISPATCH BUTTON
frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('🚀 Find BizRide'), function() {
                openFindBizRideDialog(frm, 'Delivery Note');
            }, __('Dispatch'));
        }
    }
});

frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('🚀 Find BizRide'), function() {
                openFindBizRideDialog(frm, 'Sales Invoice');
            }, __('Dispatch'));
        }
    }
});

function openFindBizRideDialog(frm, doctype) {
    let d = new frappe.ui.Dialog({
        title: __('Find Nearby BizRide Couriers'),
        fields: [
            {
                label: __('Vehicle Type Required'),
                fieldname: 'vehicle_type',
                fieldtype: 'Select',
                options: 'Motorbike\nBajaj\nCar\nTruck',
                default: 'Motorbike',
                reqd: 1
            },
            {
                label: __('Cash on Delivery (COD) Amount (ETB)'),
                fieldname: 'cod_amount',
                fieldtype: 'Currency',
                default: frm.doc.outstanding_amount || 0.0
            }
        ],
        primary_action_label: __('Broadcast to Nearby Riders (15s)'),
        primary_action(values) {
            frappe.call({
                method: 'bismillah_ethiobiz.bizride_api.find_bizride',
                args: {
                    reference_doctype: doctype,
                    reference_name: frm.doc.name,
                    vehicle_type: values.vehicle_type,
                    cod_amount: values.cod_amount
                },
                freeze: true,
                freeze_message: __('Broadcasting delivery request to active couriers within 5km...'),
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        d.hide();
                        frappe.msgprint({
                            title: __('🎉 BizRide Dispatched!'),
                            message: `
                                <b>Delivery ID:</b> ${r.message.delivery_id}<br>
                                <b>Pickup OTP:</b> <span style="font-size:1.2rem; color:#1d4ed8; font-weight:bold;">${r.message.pickup_otp || '----'}</span><br>
                                <b>Delivery OTP:</b> <span style="font-size:1.2rem; color:#059669; font-weight:bold;">${r.message.delivery_otp || '----'}</span><br>
                                <a href="${r.message.tracking_url}" target="_blank" class="btn btn-primary btn-sm mt-2">Track Live Courier Location ➔</a>
                            `,
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    });
    d.show();
}
