import os
import frappe
from frappe.model.document import Document


def _safe_bool(value):
    """Convert Frappe Check field values ('0','1',None,True,False) to real bool.

    Frappe stores Check fields as strings '0'/'1' in MariaDB.
    Python's bool('0') returns True because it's a non-empty string,
    which silently enables features the admin disabled.
    """
    if value is None or value is False:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip() not in ("0", "", "None", "false", "False")

DARK_GRADIENTS = {
    "Obsidian Teal & Emerald Aura (Default)": (
        "radial-gradient(ellipse 80% 50% at 20% -10%, rgba(31, 182, 174, 0.18) 0%, transparent 60%), "
        "radial-gradient(ellipse 60% 40% at 85% 105%, rgba(46, 58, 140, 0.22) 0%, transparent 60%), "
        "radial-gradient(ellipse 50% 30% at 50% 50%, rgba(20, 121, 116, 0.08) 0%, transparent 50%), "
        "linear-gradient(135deg, #0A1118 0%, #0D1B1E 40%, #0E1A1A 70%, #081014 100%)"
    ),
    "Midnight Sapphire & Cyan Glow": (
        "radial-gradient(ellipse 80% 60% at 10% 0%, rgba(36, 144, 239, 0.20) 0%, transparent 55%), "
        "radial-gradient(ellipse 70% 50% at 90% 100%, rgba(99, 102, 241, 0.20) 0%, transparent 60%), "
        "linear-gradient(135deg, #09111E 0%, #0B192C 45%, #081426 100%)"
    ),
    "Abyssal Nebula & Sacred Gold": (
        "radial-gradient(ellipse 70% 50% at 80% 0%, rgba(201, 162, 77, 0.16) 0%, transparent 55%), "
        "radial-gradient(ellipse 60% 40% at 15% 100%, rgba(31, 182, 174, 0.18) 0%, transparent 60%), "
        "linear-gradient(135deg, #0F1117 0%, #151620 50%, #0B0C10 100%)"
    ),
    "Deep Obsidian Minimalist": (
        "linear-gradient(135deg, #0C1017 0%, #0F141C 50%, #080B10 100%)"
    )
}

BRIGHT_GRADIENTS = {
    "Sacred Ivory & Pearl Mist (Default)": (
        "radial-gradient(ellipse 80% 60% at 15% 0%, rgba(31, 182, 174, 0.09) 0%, transparent 50%), "
        "radial-gradient(ellipse 70% 50% at 85% 100%, rgba(46, 58, 140, 0.07) 0%, transparent 50%), "
        "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 45%, #E9ECEF 100%)"
    ),
    "Frosted Cyan & Nordic Sky": (
        "radial-gradient(ellipse 70% 50% at 0% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 50%), "
        "linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 50%, #F8FAFC 100%)"
    ),
    "Alabaster & Golden Horizon": (
        "radial-gradient(ellipse 70% 50% at 100% 0%, rgba(251, 191, 36, 0.10) 0%, transparent 50%), "
        "linear-gradient(135deg, #FFFDF7 0%, #FBF7EE 50%, #F3EDE0 100%)"
    ),
    "Crisp Pure Minimalist": (
        "linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 50%, #F1F5F9 100%)"
    )
}

WEBSITE_GRADIENTS = {
    "Deep Cosmos & Emerald Glass (Default)": (
        "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(31, 182, 174, 0.16) 0%, transparent 60%), "
        "radial-gradient(ellipse 60% 40% at 90% 90%, rgba(46, 58, 140, 0.18) 0%, transparent 60%), "
        "linear-gradient(135deg, #090E14 0%, #0D161B 40%, #0A1215 100%)"
    ),
    "Royal Sapphire & Cyber Teal": (
        "radial-gradient(ellipse 80% 60% at 20% 0%, rgba(14, 165, 233, 0.18) 0%, transparent 60%), "
        "radial-gradient(ellipse 60% 40% at 80% 100%, rgba(99, 102, 241, 0.20) 0%, transparent 60%), "
        "linear-gradient(135deg, #070D18 0%, #0B1729 50%, #050A12 100%)"
    ),
    "Onyx Obsidian & Emerald Pulse": (
        "radial-gradient(circle at 50% 0%, rgba(31, 182, 174, 0.22) 0%, transparent 55%), "
        "linear-gradient(135deg, #080D0F 0%, #0D1416 50%, #05080A 100%)"
    ),
    "Golden Dusk & Deep Slate": (
        "radial-gradient(ellipse 80% 50% at 80% 0%, rgba(201, 162, 77, 0.15) 0%, transparent 55%), "
        "linear-gradient(135deg, #0D0F14 0%, #141720 50%, #0A0B0E 100%)"
    )
}

BLUR_VALUES = {
    "Subtle (10px)": "10px",
    "Balanced (16px)": "16px",
    "Intense Frost (24px)": "24px",
    "Ultra Frosted (32px)": "32px"
}


class EthioBizTheme(Document):
    def validate(self):
        self.generate_theme_css()

    def generate_theme_css(self):
        """Compile and generate dynamic theme CSS variables and atmosphere rules."""
        app_path = frappe.get_app_path("bismillah_ethiobiz")
        css_path = os.path.join(app_path, "public", "css", "generated_theme.css")
        
        dark_grad = DARK_GRADIENTS.get(
            self.dark_gradient_style,
            DARK_GRADIENTS["Obsidian Teal & Emerald Aura (Default)"]
        )
        bright_grad = BRIGHT_GRADIENTS.get(
            self.bright_gradient_style,
            BRIGHT_GRADIENTS["Sacred Ivory & Pearl Mist (Default)"]
        )
        web_grad = WEBSITE_GRADIENTS.get(
            self.website_gradient_style,
            WEBSITE_GRADIENTS["Deep Cosmos & Emerald Glass (Default)"]
        )
        blur_val = BLUR_VALUES.get(
            self.glass_blur_intensity,
            "16px"
        )
        
        # Check if master background switch and sub-switches are enabled
        # BISMALLAH: use _safe_bool — Frappe Check fields store '0'/'1' as strings;
        # Python bool('0') returns True, silently enabling disabled features.
        has_bg_master = _safe_bool(self.enable_background_images)
        desk_bg_enabled = has_bg_master and _safe_bool(self.enable_desk_bg_image)
        web_bg_enabled = has_bg_master and _safe_bool(self.enable_website_bg_image)
        
        if desk_bg_enabled:
            desk_img = self.custom_desk_bg_image or "/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg.png"
            desk_dark_atmosphere = f"linear-gradient(135deg, rgba(10, 17, 24, 0.72) 0%, rgba(14, 26, 26, 0.85) 100%), url('{desk_img}')"
            desk_bright_atmosphere = f"linear-gradient(135deg, rgba(248, 250, 252, 0.82) 0%, rgba(241, 245, 249, 0.90) 100%), url('{self.custom_desk_bg_image or '/assets/bismillah_ethiobiz/images/ethiobiz_desk_bg_light.png'}')"
        else:
            desk_dark_atmosphere = dark_grad
            desk_bright_atmosphere = bright_grad
            
        if web_bg_enabled:
            web_img = self.custom_website_bg_image or "/assets/bismillah_ethiobiz/images/ethiobiz_website_bg.png"
            web_atmosphere = f"linear-gradient(135deg, rgba(9, 14, 20, 0.80) 0%, rgba(13, 22, 27, 0.90) 100%), url('{web_img}')"
        else:
            web_atmosphere = web_grad
            
        primary = self.primary_color or "#1FB6AE"
        navbar_bg = self.navbar_bg_color or "rgba(14, 26, 26, 0.75)"
        navbar_text = self.navbar_text_color or "#F8F6F2"
        body_bg = self.background_color or "#0E1A1A"
        
        css = f"""/**
 * Generated Dynamic EthioBiz Atmosphere & Theme CSS
 * Bismillah Ar-Rahman Ar-Rahim
 */

:root {{
    --ethiobiz-primary: {primary};
    --ethiobiz-primary-color: {primary};
    --ethiobiz-navbar-bg: {navbar_bg};
    --ethiobiz-navbar-text: {navbar_text};
    --ethiobiz-body-bg: {body_bg};
    --ethiobiz-glass-blur: {blur_val};
    --ethiobiz-atmosphere-dark: {desk_dark_atmosphere};
    --ethiobiz-atmosphere-bright: {desk_bright_atmosphere};
    --ethiobiz-website-atmosphere: {web_atmosphere};
    --ethiobiz-bg-images-enabled: {'1' if has_bg_master else '0'};
}}

/* Dynamic Atmosphere Layer */
#ethiobiz-atmosphere {{
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: -9999 !important;
    pointer-events: none !important;
    background: var(--ethiobiz-atmosphere-dark) !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    transform: translateZ(0) !important;
    will-change: transform;
    transition: background 0.8s ease-in-out;
}}

/* Light mode atmosphere */
[data-theme="light"] #ethiobiz-atmosphere,
html[data-theme="light"] #ethiobiz-atmosphere,
body.light-theme #ethiobiz-atmosphere {{
    background: var(--ethiobiz-atmosphere-bright) !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}

/* Website Atmosphere */
body.website-page,
.website-wrapper,
#page-container.website-view {{
    background: var(--ethiobiz-website-atmosphere) !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}

html, body {{
    background-attachment: fixed !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
}}

/* Glass panels & Card styling with configured blur */
.glass-panel,
.card,
.shortcut-widget-box,
.widget,
.number-card-widget,
.onboarding-widget-box {{
    backdrop-filter: blur(var(--ethiobiz-glass-blur, 16px)) !important;
    -webkit-backdrop-filter: blur(var(--ethiobiz-glass-blur, 16px)) !important;
}}
"""
        if self.custom_css:
            css += f"\n/* Custom CSS Overrides */\n{self.custom_css}\n"

        os.makedirs(os.path.dirname(css_path), exist_ok=True)
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css)

        # Also sync to sites/assets if running in bench context
        try:
            site_assets = frappe.get_site_path("public", "css")
            os.makedirs(site_assets, exist_ok=True)
            with open(os.path.join(site_assets, "generated_theme.css"), "w", encoding="utf-8") as f:
                f.write(css)
        except Exception:
            pass

    def on_update(self):
        self.generate_theme_css()
        frappe.clear_cache()
        frappe.publish_realtime("ethiobiz_theme_updated", message={"status": "Theme Updated"})