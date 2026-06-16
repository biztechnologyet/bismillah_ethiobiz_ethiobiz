import os
import frappe
from frappe.model.document import Document

class EthioBizTheme(Document):
    def validate(self):
        self.generate_theme_css()

    def generate_theme_css(self):
        # Define paths
        app_path = frappe.get_app_path("bismillah_ethiobiz")
        css_path = os.path.join(app_path, "public", "css", "generated_theme.css")
        
        # Build CSS variables
        css = ":root {\n"
        if self.primary_color:
            css += f"  --primary: {self.primary_color};\n"
            css += f"  --primary-color: {self.primary_color};\n" # Legacy support
            
        if self.navbar_bg_color:
             css += f"  --navbar-bg: {self.navbar_bg_color};\n"
             # Override standard frappe navbar classes
             css += f"  --navbar-bg-color: {self.navbar_bg_color};\n"
             
        if self.background_color:
             css += f"  --body-bg: {self.background_color};\n"
             
        css += "}\n"
        
        # Specific overrides
        if self.navbar_bg_color:
            css += f".navbar {{ background-color: {self.navbar_bg_color} !important; }}\n"
        if self.navbar_text_color:
             css += f".navbar-light .navbar-nav .nav-link {{ color: {self.navbar_text_color} !important; }}\n"
             css += f".navbar-light .navbar-brand {{ color: {self.navbar_text_color} !important; }}\n"

        # Append Custom CSS
        if self.custom_css:
            css += f"\n/* Custom CSS */\n{self.custom_css}\n"

        # Write file
        with open(css_path, "w") as f:
            f.write(css)
            
        # Also, if logo changes, we might want to update website settings or similar, 
        # but for now let's just Stick to CSS injection. 
        # Actually for 'Logo', Frappe usually handles it via Website Settings, 
        # but for internal desk, we might need a JS hack or CSS background image if standard one isn't used.
        # Let's try to override the logo via CSS if possible or just store it.
        pass

    def on_update(self):
        # Ensure the CSS is regenerated
        self.generate_theme_css()
        frappe.clear_cache()
        frappe.publish_realtime("ethiobiz_theme_updated", message="Theme Updated")