"""
Programmatically create all 18 DocTypes and seed default data for Workstreams I, J, K.
"""
import frappe

def create_doctypes():
    doctypes = [
        # --- ADS MANAGEMENT ---
        {
            "name": "EthioBiz Ad Slot",
            "module": "EthioBiz Theme",
            "custom": 1,
            "is_submittable": 0,
            "autoname": "field:slot_code",
            "title_field": "slot_name",
            "fields": [
                {"fieldname": "slot_code", "fieldtype": "Data", "label": "Slot Code", "unique": 1, "reqd": 1, "read_only": 1},
                {"fieldname": "slot_name", "fieldtype": "Data", "label": "Slot Name", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "width_px", "fieldtype": "Int", "label": "Width (px)", "default": 300},
                {"fieldname": "height_px", "fieldtype": "Int", "label": "Height (px)", "default": 250},
                {"fieldname": "responsive", "fieldtype": "Check", "label": "Responsive", "default": 0},
                {"fieldname": "section_break_status", "fieldtype": "Section Break", "label": "Status"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Available\nReserved\nRented\nMaintenance", "default": "Available", "reqd": 1},
                {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "EthioBiz Ad Campaign",
            "module": "EthioBiz Theme",
            "custom": 1,
            "is_submittable": 1,
            "autoname": "format:AD-CAM-{#####}",
            "title_field": "campaign_name",
            "fields": [
                {"fieldname": "campaign_name", "fieldtype": "Data", "label": "Campaign Name", "reqd": 1},
                {"fieldname": "customer", "fieldtype": "Link", "label": "Customer", "options": "Customer", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "slot", "fieldtype": "Link", "label": "Ad Slot", "options": "EthioBiz Ad Slot", "reqd": 1},
                {"fieldname": "billing_model", "fieldtype": "Select", "label": "Billing Model", "options": "Flat\nCPM\nCPC\nDay", "default": "Flat", "reqd": 1},
                {"fieldname": "rate_etb", "fieldtype": "Currency", "label": "Rate (ETB)", "reqd": 1},
                {"fieldname": "section_break_creative", "fieldtype": "Section Break", "label": "Creative"},
                {"fieldname": "creative_image", "fieldtype": "Attach Image", "label": "Creative Image"},
                {"fieldname": "click_url", "fieldtype": "Data", "label": "Click URL", "options": "URL"},
                {"fieldname": "alt_text", "fieldtype": "Data", "label": "Alt Text"},
                {"fieldname": "section_break_schedule", "fieldtype": "Section Break", "label": "Schedule"},
                {"fieldname": "start_date", "fieldtype": "Date", "label": "Start Date", "reqd": 1},
                {"fieldname": "end_date", "fieldtype": "Date", "label": "End Date", "reqd": 1},
                {"fieldname": "column_break_schedule", "fieldtype": "Column Break"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nPending Approval\nActive\nPaused\nCompleted\nRejected", "default": "Draft", "reqd": 1},
                {"fieldname": "section_break_stats", "fieldtype": "Section Break", "label": "Performance"},
                {"fieldname": "impressions", "fieldtype": "Int", "label": "Impressions", "default": 0, "read_only": 1},
                {"fieldname": "clicks", "fieldtype": "Int", "label": "Clicks", "default": 0, "read_only": 1},
                {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company"},
                {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1}]
        },
        {
            "name": "EthioBiz Ads Settings",
            "module": "EthioBiz Theme",
            "custom": 1,
            "issingle": 1,
            "fields": [
                {"fieldname": "ads_enabled", "fieldtype": "Check", "label": "Enable Ads System", "default": 1},
                {"fieldname": "house_ad_image", "fieldtype": "Attach Image", "label": "Default House Ad Image"},
                {"fieldname": "house_ad_url", "fieldtype": "Data", "label": "Default House Ad URL", "options": "URL"},
                {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company"},
                {"fieldname": "impression_rate_limit", "fieldtype": "Int", "label": "Max Impressions per IP/hour", "default": 100}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },

        # --- SALON & SPA HUB ---
        {
            "name": "Salon Service",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "format:SRV-{####}",
            "title_field": "service_name",
            "fields": [
                {"fieldname": "service_name", "fieldtype": "Data", "label": "Service Name", "reqd": 1, "unique": 1},
                {"fieldname": "item", "fieldtype": "Link", "label": "Item (ERPNext)", "options": "Item"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "duration_minutes", "fieldtype": "Int", "label": "Duration (minutes)", "reqd": 1, "default": 30},
                {"fieldname": "price_etb", "fieldtype": "Currency", "label": "Price (ETB)", "reqd": 1},
                {"fieldname": "for_company", "fieldtype": "Link", "label": "Company", "options": "Company", "reqd": 1},
                {"fieldname": "active", "fieldtype": "Check", "label": "Active", "default": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "Salon Stylist",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "format:STR-{####}",
            "title_field": "stylist_name",
            "fields": [
                {"fieldname": "employee", "fieldtype": "Link", "label": "Employee", "options": "Employee"},
                {"fieldname": "user", "fieldtype": "Link", "label": "User", "options": "User"},
                {"fieldname": "stylist_name", "fieldtype": "Data", "label": "Display Name", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "commission_percent", "fieldtype": "Percent", "label": "Commission %", "default": 0},
                {"fieldname": "active", "fieldtype": "Check", "label": "Active", "default": 1},
                {"fieldname": "skills", "fieldtype": "Table", "label": "Services", "options": "Salon Stylist Service"},
                {"fieldname": "working_hours", "fieldtype": "Small Text", "label": "Working Hours"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "Salon Stylist Service",
            "module": "EthioBiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "salon_service", "fieldtype": "Link", "label": "Service", "options": "Salon Service", "reqd": 1, "in_list_view": 1},
                {"fieldname": "proficiency", "fieldtype": "Select", "label": "Proficiency", "options": "Beginner\nIntermediate\nExpert", "default": "Intermediate", "in_list_view": 1}
            ],
            "permissions": []
        },
        {
            "name": "Salon Appointment",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "format:APT-{YYYY}{MM}{DD}-{####}",
            "title_field": "customer_name",
            "fields": [
                {"fieldname": "customer", "fieldtype": "Link", "label": "Customer", "options": "Customer", "reqd": 1},
                {"fieldname": "customer_name", "fieldtype": "Data", "label": "Customer Name"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "stylist", "fieldtype": "Link", "label": "Stylist", "options": "Salon Stylist", "reqd": 1},
                {"fieldname": "source", "fieldtype": "Select", "label": "Source", "options": "Walk-in\nPhone\nOnline", "default": "Walk-in"},
                {"fieldname": "section_break_date", "fieldtype": "Section Break", "label": "Date & Time"},
                {"fieldname": "appointment_date", "fieldtype": "Date", "label": "Date", "reqd": 1},
                {"fieldname": "start_time", "fieldtype": "Time", "label": "Start Time", "reqd": 1},
                {"fieldname": "column_break_date", "fieldtype": "Column Break"},
                {"fieldname": "end_time", "fieldtype": "Time", "label": "End Time", "reqd": 1},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nBooked\nConfirmed\nIn Service\nCompleted\nCancelled\nNo Show", "default": "Draft", "reqd": 1},
                {"fieldname": "services", "fieldtype": "Table", "label": "Services", "options": "Salon Appointment Service"},
                {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "Salon Appointment Service",
            "module": "EthioBiz Theme",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "salon_service", "fieldtype": "Link", "label": "Service", "options": "Salon Service", "reqd": 1, "in_list_view": 1},
                {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount (ETB)", "in_list_view": 1, "read_only": 1}
            ],
            "permissions": []
        },
        {
            "name": "Salon Settings",
            "module": "EthioBiz Theme",
            "custom": 1,
            "issingle": 1,
            "fields": [
                {"fieldname": "default_company", "fieldtype": "Link", "label": "Default Company", "options": "Company"},
                {"fieldname": "booking_window_days", "fieldtype": "Int", "label": "Booking Window (days)", "default": 30},
                {"fieldname": "reminder_template", "fieldtype": "Small Text", "label": "Reminder Message Template"},
                {"fieldname": "cancellation_policy", "fieldtype": "Small Text", "label": "Cancellation Policy"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },

        # --- BIZBOOKING ENGINE ---
        {
            "name": "BizBooking Industry",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "field:industry_code",
            "title_field": "industry_name",
            "fields": [
                {"fieldname": "industry_code", "fieldtype": "Data", "label": "Code", "unique": 1, "reqd": 1},
                {"fieldname": "industry_name", "fieldtype": "Data", "label": "Industry Name", "reqd": 1},
                {"fieldname": "icon", "fieldtype": "Data", "label": "Icon"},
                {"fieldname": "color", "fieldtype": "Color", "label": "Theme Color", "default": "#1FB6AE"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "enabled", "fieldtype": "Check", "label": "Enabled", "default": 1},
                {"fieldname": "default_slot_granularity", "fieldtype": "Int", "label": "Default Slot Granularity (min)", "default": 30},
                {"fieldname": "default_reminder_offsets", "fieldtype": "Data", "label": "Default Reminder Offsets (JSON)", "default": "[24, 2]"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBooking Company Profile",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "field:company",
            "title_field": "company_name",
            "fields": [
                {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company", "reqd": 1, "unique": 1},
                {"fieldname": "company_name", "fieldtype": "Data", "label": "Display Name"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "timezone", "fieldtype": "Data", "label": "Timezone", "default": "Africa/Addis_Ababa"},
                {"fieldname": "currency", "fieldtype": "Link", "label": "Currency", "options": "Currency", "default": "ETB"},
                {"fieldname": "cancellation_policy", "fieldtype": "Small Text", "label": "Cancellation Policy"},
                {"fieldname": "reminder_offsets", "fieldtype": "Data", "label": "Reminder Offsets (JSON)", "default": "[24, 2]"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBookable Service",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "format:BKS-{####}",
            "title_field": "service_title",
            "fields": [
                {"fieldname": "service_title", "fieldtype": "Data", "label": "Service Title", "reqd": 1},
                {"fieldname": "industry", "fieldtype": "Link", "label": "Industry", "options": "BizBooking Industry", "reqd": 1},
                {"fieldname": "company_profile", "fieldtype": "Link", "label": "Company Profile", "options": "BizBooking Company Profile", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "provider_doctype", "fieldtype": "Select", "label": "Provider DocType", "options": "Practitioner\nSalon Stylist\nAgent\nUser"},
                {"fieldname": "provider_field", "fieldtype": "Data", "label": "Provider Field Name"},
                {"fieldname": "resource", "fieldtype": "Link", "label": "Resource", "options": "BizBooking Resource"},
                {"fieldname": "section_break_pricing", "fieldtype": "Section Break", "label": "Pricing & Duration"},
                {"fieldname": "duration_minutes", "fieldtype": "Int", "label": "Duration (minutes)", "reqd": 1, "default": 30},
                {"fieldname": "price_etb", "fieldtype": "Currency", "label": "Price (ETB)"},
                {"fieldname": "column_break_pricing", "fieldtype": "Column Break"},
                {"fieldname": "buffer_before_min", "fieldtype": "Int", "label": "Buffer Before (min)", "default": 0},
                {"fieldname": "buffer_after_min", "fieldtype": "Int", "label": "Buffer After (min)", "default": 0},
                {"fieldname": "capacity_per_slot", "fieldtype": "Int", "label": "Capacity per Slot", "default": 1},
                {"fieldname": "section_break_payment", "fieldtype": "Section Break", "label": "Payment"},
                {"fieldname": "requires_payment", "fieldtype": "Check", "label": "Requires Payment"},
                {"fieldname": "deposit_percent", "fieldtype": "Percent", "label": "Deposit %"},
                {"fieldname": "vertical_payload_schema", "fieldtype": "Code", "label": "Vertical Payload Schema (JSON)", "options": "JSON"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBooking Provider Config",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "format:PROV-{####}",
            "title_field": "provider_name",
            "fields": [
                {"fieldname": "provider_doctype", "fieldtype": "Select", "label": "Provider DocType", "options": "Practitioner\nSalon Stylist\nAgent\nUser", "reqd": 1},
                {"fieldname": "provider_name", "fieldtype": "Data", "label": "Provider Name", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "service", "fieldtype": "Link", "label": "Service", "options": "BizBookable Service"},
                {"fieldname": "duration_override", "fieldtype": "Int", "label": "Duration Override (min)"},
                {"fieldname": "price_override", "fieldtype": "Currency", "label": "Price Override (ETB)"},
                {"fieldname": "max_per_day", "fieldtype": "Int", "label": "Max Bookings per Day", "default": 0},
                {"fieldname": "auto_confirm", "fieldtype": "Check", "label": "Auto-Confirm Bookings"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBooking Availability Rule",
            "module": "EthioBiz Theme",
            "custom": 1,
            "fields": [
                {"fieldname": "service", "fieldtype": "Link", "label": "Service", "options": "BizBookable Service"},
                {"fieldname": "provider_doctype", "fieldtype": "Select", "label": "Provider DocType", "options": "Practitioner\nSalon Stylist\nAgent\nUser"},
                {"fieldname": "provider_name", "fieldtype": "Data", "label": "Provider Name"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "weekdays", "fieldtype": "Data", "label": "Weekdays"},
                {"fieldname": "window_start", "fieldtype": "Time", "label": "Window Start", "reqd": 1},
                {"fieldname": "window_end", "fieldtype": "Time", "label": "Window End", "reqd": 1},
                {"fieldname": "break_start", "fieldtype": "Time", "label": "Break Start"},
                {"fieldname": "break_end", "fieldtype": "Time", "label": "Break End"},
                {"fieldname": "effective_from", "fieldtype": "Date", "label": "Effective From"},
                {"fieldname": "effective_to", "fieldtype": "Date", "label": "Effective To"},
                {"fieldname": "min_notice_min", "fieldtype": "Int", "label": "Min Notice (minutes)", "default": 0},
                {"fieldname": "max_advance_days", "fieldtype": "Int", "label": "Max Advance (days)", "default": 60}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBooking Blackout",
            "module": "EthioBiz Theme",
            "custom": 1,
            "title_field": "reason",
            "fields": [
                {"fieldname": "service", "fieldtype": "Link", "label": "Service", "options": "BizBookable Service"},
                {"fieldname": "provider_doctype", "fieldtype": "Select", "label": "Provider DocType", "options": "Practitioner\nSalon Stylist\nAgent\nUser"},
                {"fieldname": "provider_name", "fieldtype": "Data", "label": "Provider Name"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date", "reqd": 1},
                {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date", "reqd": 1},
                {"fieldname": "reason", "fieldtype": "Data", "label": "Reason", "reqd": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBooking Resource",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "format:RES-{####}",
            "title_field": "resource_name",
            "fields": [
                {"fieldname": "resource_name", "fieldtype": "Data", "label": "Resource Name", "reqd": 1},
                {"fieldname": "resource_type", "fieldtype": "Select", "label": "Type", "options": "Room\nEquipment\nTable\nVenue"},
                {"fieldname": "capacity", "fieldtype": "Int", "label": "Capacity", "default": 1},
                {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBooking",
            "module": "EthioBiz Theme",
            "custom": 1,
            "autoname": "format:BK-{YYYY}{MM}{DD}-{####}",
            "title_field": "customer_name",
            "fields": [
                {"fieldname": "service", "fieldtype": "Link", "label": "Service", "options": "BizBookable Service", "reqd": 1},
                {"fieldname": "provider_doctype", "fieldtype": "Data", "label": "Provider DocType", "read_only": 1},
                {"fieldname": "provider_name", "fieldtype": "Data", "label": "Provider Name", "read_only": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "customer", "fieldtype": "Link", "label": "Customer", "options": "Customer"},
                {"fieldname": "customer_name", "fieldtype": "Data", "label": "Guest Name"},
                {"fieldname": "customer_phone", "fieldtype": "Phone", "label": "Guest Phone"},
                {"fieldname": "customer_email", "fieldtype": "Data", "label": "Guest Email", "options": "Email"},
                {"fieldname": "section_break_datetime", "fieldtype": "Section Break", "label": "Date & Time"},
                {"fieldname": "booking_date", "fieldtype": "Date", "label": "Date", "reqd": 1},
                {"fieldname": "start_time", "fieldtype": "Time", "label": "Start Time", "reqd": 1},
                {"fieldname": "end_time", "fieldtype": "Time", "label": "End Time", "reqd": 1},
                {"fieldname": "column_break_datetime", "fieldtype": "Column Break"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nHold\nConfirmed\nRescheduled\nCompleted\nCancelled\nNo Show", "default": "Pending", "reqd": 1},
                {"fieldname": "source", "fieldtype": "Select", "label": "Source", "options": "Web\nDesk\nAPI", "default": "Desk"},
                {"fieldname": "section_break_payment", "fieldtype": "Section Break", "label": "Payment", "collapsible": 1},
                {"fieldname": "invoice", "fieldtype": "Link", "label": "Sales Invoice", "options": "Sales Invoice", "read_only": 1},
                {"fieldname": "gateway_ref", "fieldtype": "Data", "label": "Gateway Reference", "read_only": 1},
                {"fieldname": "industry_payload", "fieldtype": "Code", "label": "Industry Payload (JSON)", "options": "JSON"},
                {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "BizBooking Settings",
            "module": "EthioBiz Theme",
            "custom": 1,
            "issingle": 1,
            "fields": [
                {"fieldname": "timezone", "fieldtype": "Data", "label": "Timezone", "default": "Africa/Addis_Ababa"},
                {"fieldname": "slot_granularity_min", "fieldtype": "Int", "label": "Slot Granularity (minutes)", "default": 30},
                {"fieldname": "hold_expiry_min", "fieldtype": "Int", "label": "HOLD Expiry (minutes)", "default": 15},
                {"fieldname": "cancellation_policy", "fieldtype": "Small Text", "label": "Cancellation Policy"},
                {"fieldname": "reminder_offsets", "fieldtype": "Data", "label": "Reminder Offsets (JSON)", "default": "[24, 2]"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },

        # --- AFOCHA SOCIAL GRAPH ---
        {
            "name": "AF Social Follow",
            "module": "EthioBiz Theme",
            "custom": 1,
            "fields": [
                {"fieldname": "user", "fieldtype": "Link", "label": "Follower", "options": "User", "reqd": 1, "in_list_view": 1},
                {"fieldname": "following_user", "fieldtype": "Link", "label": "Following User", "options": "User", "reqd": 1, "in_list_view": 1},
                {"fieldname": "followed_on", "fieldtype": "Datetime", "label": "Followed On", "default": "now"}
            ],
            "permissions": [{"role": "All", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        {
            "name": "AF Social Share",
            "module": "EthioBiz Theme",
            "custom": 1,
            "fields": [
                {"fieldname": "original_post", "fieldtype": "Link", "label": "Original Post", "options": "Afocha Post", "reqd": 1, "in_list_view": 1},
                {"fieldname": "shared_by", "fieldtype": "Link", "label": "Shared By", "options": "User", "reqd": 1, "in_list_view": 1},
                {"fieldname": "quote_text", "fieldtype": "Small Text", "label": "Quote Text"},
                {"fieldname": "shared_on", "fieldtype": "Datetime", "label": "Shared On", "default": "now"}
            ],
            "permissions": [{"role": "All", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },

        # --- DOBIZ PWA SETTINGS ---
        {
            "name": "DOBiz PWA Settings",
            "module": "EthioBiz Theme",
            "custom": 1,
            "issingle": 1,
            "fields": [
                {"fieldname": "enabled", "fieldtype": "Check", "label": "Enable PWA", "default": 1},
                {"fieldname": "app_name", "fieldtype": "Data", "label": "App Name", "default": "DOBiz Smart ERP"},
                {"fieldname": "short_name", "fieldtype": "Data", "label": "Short Name", "default": "DOBiz"},
                {"fieldname": "description", "fieldtype": "Small Text", "label": "App Description", "default": "DOBiz Smart ERP - Ethiopian Enterprise Cloud Operating System"},
                {"fieldname": "theme_color", "fieldtype": "Color", "label": "Theme Color", "default": "#1FB6AE"},
                {"fieldname": "background_color", "fieldtype": "Color", "label": "Background Color", "default": "#0E1A1A"},
                {"fieldname": "start_url", "fieldtype": "Data", "label": "Start URL", "default": "/app/dobiz"},
                {"fieldname": "display", "fieldtype": "Select", "label": "Display Mode", "options": "standalone\nfullscreen\nminimal-ui\nbrowser", "default": "standalone"},
                {"fieldname": "icon_192", "fieldtype": "Attach Image", "label": "Icon 192x192", "default": "/assets/bismillah_ethiobiz/pwa/icons/icon-192.png"},
                {"fieldname": "icon_512", "fieldtype": "Attach Image", "label": "Icon 512x512", "default": "/assets/bismillah_ethiobiz/pwa/icons/icon-512.png"},
                {"fieldname": "icon_maskable", "fieldtype": "Attach Image", "label": "Maskable Icon 512x512", "default": "/assets/bismillah_ethiobiz/pwa/icons/icon-512-maskable.png"},
                {"fieldname": "install_prompt_enabled", "fieldtype": "Check", "label": "Enable Install Prompt Pill", "default": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },

        # --- DAGU INSTRUCTOR REGISTRATION ---
        {
            "name": "Dagu Instructor Registration",
            "module": "EthioBiz Theme",
            "custom": 1,
            "naming_rule": "By \"Naming Series\" field",
            "autoname": "naming_series:",
            "is_submittable": 0,
            "track_changes": 1,
            "title_field": "full_name",
            "sort_field": "creation",
            "sort_order": "DESC",
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "label": "Series", "options": "DAGU-INST-.YYYY.-.#####", "default": "DAGU-INST-.YYYY.-.#####", "hidden": 1},
                {"fieldname": "sec_personal", "fieldtype": "Section Break", "label": "1. Personal & Professional Details"},
                {"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "email", "fieldtype": "Data", "label": "Email Address", "options": "Email", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "phone", "fieldtype": "Data", "label": "Phone Number", "reqd": 1, "in_list_view": 1},
                {"fieldname": "col_break_1", "fieldtype": "Column Break"},
                {"fieldname": "role_expertise", "fieldtype": "Data", "label": "Role / Expertise", "reqd": 1},
                {"fieldname": "company_organization", "fieldtype": "Data", "label": "Company / Organization"},
                {"fieldname": "linkedin_portfolio", "fieldtype": "Data", "label": "LinkedIn / Portfolio Profile"},
                {"fieldname": "brief_bio", "fieldtype": "Small Text", "label": "Brief Bio", "reqd": 1},
                {"fieldname": "sec_course", "fieldtype": "Section Break", "label": "2. Course Proposal"},
                {"fieldname": "proposed_course_title", "fieldtype": "Data", "label": "Proposed Course Title", "reqd": 1, "in_list_view": 1},
                {"fieldname": "target_audience", "fieldtype": "Data", "label": "Target Audience", "reqd": 1},
                {"fieldname": "col_break_2", "fieldtype": "Column Break"},
                {"fieldname": "language_of_instruction", "fieldtype": "Select", "label": "Language of Instruction", "options": "Amharic\nEnglish\nAmharic & English\nOromo\nTigrinya\nOther", "default": "Amharic & English", "reqd": 1},
                {"fieldname": "course_description", "fieldtype": "Text", "label": "Course Description / Outline", "reqd": 1},
                {"fieldname": "sec_qualifications", "fieldtype": "Section Break", "label": "3. Instructor Qualification & Experience"},
                {"fieldname": "teaching_experience", "fieldtype": "Text", "label": "Teaching Experience", "reqd": 1},
                {"fieldname": "why_dagu", "fieldtype": "Text", "label": "Why Dagu? (Motivation)", "reqd": 1},
                {"fieldname": "col_break_3", "fieldtype": "Column Break"},
                {"fieldname": "proof_of_expertise", "fieldtype": "Data", "label": "Proof of Expertise (Link/File URL)"},
                {"fieldname": "sec_business", "fieldtype": "Section Break", "label": "4. Operational & Business Model"},
                {"fieldname": "preferred_course_model", "fieldtype": "Select", "label": "Preferred Course Model", "options": "Paid Course\nFree Course\nSubscription\nHybrid", "default": "Paid Course", "reqd": 1},
                {"fieldname": "availability", "fieldtype": "Select", "label": "Availability", "options": "1 - 5 hours/week\n5 - 10 hours/week\n10 - 20 hours/week\n20+ hours/week / Full-time", "default": "5 - 10 hours/week", "reqd": 1},
                {"fieldname": "col_break_4", "fieldtype": "Column Break"},
                {"fieldname": "technical_equipment", "fieldtype": "Select", "label": "Technical Equipment / Setup", "options": "Yes - High quality mic, camera & quiet setup\nNo - Need assistance/guidance", "default": "Yes - High quality mic, camera & quiet setup", "reqd": 1},
                {"fieldname": "sec_agreement", "fieldtype": "Section Break", "label": "Agreement & Status"},
                {"fieldname": "terms_agreed", "fieldtype": "Check", "label": "I agree to the Terms & Conditions and certify that all information provided is accurate.", "reqd": 1, "default": "0"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Application Status", "options": "Pending\nUnder Review\nApproved\nRejected", "default": "Pending", "in_list_view": 1, "in_standard_filter": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "email": 1, "print": 1, "report": 1, "share": 1, "export": 1},
                {"role": "Marketing User", "read": 1, "write": 1, "create": 1, "delete": 0, "email": 1, "print": 1, "report": 1},
                {"role": "Guest", "read": 1, "write": 1, "create": 1, "delete": 0},
                {"role": "All", "read": 1, "write": 0, "create": 0, "delete": 0}
            ]
        }
    ]

    frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()

    for dt in doctypes:
        name = dt["name"]
        if not frappe.db.exists("DocType", name):
            print(f"Creating DocType: {name}")
            try:
                d = frappe.get_doc({
                    "doctype": "DocType",
                    **dt
                })
                d.insert(ignore_permissions=True)
                print(f"SUCCESS: {name}")
            except Exception as e:
                print(f"FAILED {name}: {e}")
        else:
            print(f"Already exists: {name}")

    # Ensure Web Form dagu-instructor-registration exists
    if not frappe.db.exists("Web Form", "dagu-instructor-registration"):
        print("Creating Web Form: dagu-instructor-registration")
        try:
            wf = frappe.new_doc("Web Form")
            wf.name = "dagu-instructor-registration"
            wf.title = "🎓 Dagu Instructor Registration"
            wf.route = "dagu-instructor-registration"
            wf.doc_type = "Dagu Instructor Registration"
            wf.module = "EthioBiz Theme"
            wf.published = 1
            wf.login_required = 0
            wf.allow_edit = 0
            wf.allow_multiple = 1
            wf.allow_incomplete = 0
            wf.allow_comments = 0
            wf.allow_print = 0
            wf.anonymous = 1
            wf.show_attachments = 0
            wf.button_label = "🚀 SUBMIT APPLICATION"
            wf.introduction_text = "<p class='lead'><strong>Join our expert community. Complete this form to begin your journey as a Dagu Instructor.</strong></p>"
            wf.success_message = "Thank you for applying to become a Dagu Instructor! Our academic team will review your course proposal and contact you shortly InSha'Allah."
            wf.success_url = "/dagu-instructor-registration"

            dt_doc = frappe.get_doc("DocType", "Dagu Instructor Registration")
            for df in dt_doc.fields:
                if df.fieldname not in ["naming_series", "status"]:
                    wf.append("web_form_fields", {
                        "fieldname": df.fieldname,
                        "label": df.label,
                        "fieldtype": df.fieldtype,
                        "options": df.options,
                        "reqd": df.reqd,
                        "default": df.default,
                        "description": df.description,
                        "hidden": 0,
                        "read_only": 0
                    })
            wf.insert(ignore_permissions=True)
            print("SUCCESS: Web Form dagu-instructor-registration")
        except Exception as e:
            print("FAILED Web Form:", e)

    # Ensure default values in Singles tables
    if frappe.db.exists("DocType", "DOBiz PWA Settings"):
        pwa = frappe.get_single("DOBiz PWA Settings")
        pwa.enabled = 1
        pwa.app_name = "DOBiz Smart ERP"
        pwa.short_name = "DOBiz"
        pwa.theme_color = "#1FB6AE"
        pwa.start_url = "/app/dobiz"
        pwa.flags.ignore_permissions = True
        pwa.flags.ignore_mandatory = True
        pwa.save()

    if frappe.db.exists("DocType", "EthioBiz Ads Settings"):
        ads = frappe.get_single("EthioBiz Ads Settings")
        ads.ads_enabled = 1
        ads.flags.ignore_permissions = True
        ads.flags.ignore_mandatory = True
        ads.save()

    frappe.db.commit()
    print("ALL DOCTYPES & WEB FORMS CREATED AND SEEDED SUCCESSFULLY!")

if __name__ == "__main__":
    create_doctypes()


