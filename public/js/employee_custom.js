frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        // Hide Insurance Section
        frm.toggle_display('insurance_section', false);
        
        // Rename Passport Detail Section (Visual only)
        // Note: Field 'passport_detail' is setting the section header.
        // We can try to change the label of the section break if we can access it.
        // Or simply rely on the Custom Field 'ID Type' being inserted there.
        
        // Let's assume we have a custom field 'id_type'
        frm.trigger('id_type');
    },
    
    id_type: function(frm) {
        // Logic to adjust labels based on ID Type if needed
        // For now just ensure the section looks right
        if(frm.doc.id_type) {
            // Example: Change 'Passport Number' label to 'ID Number'
            // frappe.meta.get_docfield('Employee', 'passport_number', frm.doc.name).label = 'ID Number';
            // frm.refresh_field('passport_number');
            
            // Allow generic handling
            frm.set_df_property('passport_number', 'label', frm.doc.id_type + ' Number');
            frm.set_df_property('date_of_issue', 'label', 'Issue Date');
            frm.set_df_property('valid_upto', 'label', 'Expiry Date');
            frm.set_df_property('place_of_issue', 'label', 'Place of Issue');
        }
    }
});
