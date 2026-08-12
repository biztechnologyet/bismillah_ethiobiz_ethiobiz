app_name = "bismillah_ethiobiz"
app_title = "Bismillah EthioBiz"
app_publisher = "Bismillah"
app_description = "Custom EthioBiz ERPNext Customizations for Ethiopian Market"
app_email = "info@ethiobiz.et"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css?v=2.7.1",
    "/assets/bismillah_ethiobiz/css/generated_theme.css?v=2.7.1"
]
app_include_js = [
    "/assets/bismillah_ethiobiz/js/bismillah_ethiobiz.js?v=2.7.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js?v=2.7.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.7.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.7.1"
]

# include js, css files in header of web template (login, etc)
web_include_css = [
    "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css?v=2.7.1",
    "/assets/bismillah_ethiobiz/css/generated_theme.css?v=2.7.1"
]
web_include_js = [
    "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js?v=2.7.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_chat.js?v=2.7.1",
    "/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js?v=2.7.1"
]

# Client-side bindings
# --------------------

doctype_js = {
    "Employee": "public/js/employee_custom.js",
    "Project": "public/js/project_custom.js"
}

# Document Events
# ---------------
doc_events = {
    "Workspace": {
        "before_insert": "bismillah_ethiobiz.overrides.validate_workspace_permissions",
        "before_save": "bismillah_ethiobiz.overrides.validate_workspace_permissions"
    },
    "Company": {
        "before_insert": "bismillah_ethiobiz.overrides.validate_company_permissions"
    }
}

# Fixtures
# --------
fixtures = [
    "Custom Role",
    "Property Setter",
    "Custom Field"
]

# Boot Injection
# --------------
boot_session = "bismillah_ethiobiz.boot.boot_session"

# Auto-Company: Set user's default company on login
on_session_creation = "bismillah_ethiobiz.auto_company.on_session_creation"

# Multi-Company Isolation: Apply custom fields and property setters after migrate
after_migrate = "bismillah_ethiobiz.setup_multi_company.after_migrate"
