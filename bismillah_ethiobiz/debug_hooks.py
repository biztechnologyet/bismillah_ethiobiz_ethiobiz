"""Debug web_include_css/js on the cart page context."""
import frappe

def execute():
    # Check what hooks actually provide
    hooks = frappe.get_hooks()
    print("=== HOOKS ===")
    print("web_include_css:", hooks.get("web_include_css"))
    print("web_include_js:", hooks.get("web_include_js"))
    
    # Check Website Settings head_html
    ws_head = frappe.db.get_single_value("Website Settings", "head_html") or ""
    print("\n=== Website Settings head_html ===")
    print(repr(ws_head[:200]) if ws_head else "EMPTY")
    
    # Check Website Settings custom_css
    ws_css = frappe.db.get_single_value("Website Settings", "custom_css") or ""
    print("\n=== Website Settings custom_css ===")
    print(repr(ws_css[:200]) if ws_css else "EMPTY")
    
    # Simulate update_website_context
    context = {"web_include_css": list(hooks.get("web_include_css", [])), "web_include_js": list(hooks.get("web_include_js", []))}
    print("\n=== BEFORE update_website_context ===")
    print("css:", context["web_include_css"])
    print("js:", context["web_include_js"])
    
    # Check if website_script.js exists
    import os
    site_path = frappe.get_site_path("public", "website_script.js")
    print(f"\n=== website_script.js exists: {os.path.exists(site_path)} ===")
    if os.path.exists(site_path):
        with open(site_path) as f:
            content = f.read()
            print(f"Size: {len(content)} bytes")
            if content.strip():
                print(f"First 500 chars: {content[:500]}")
