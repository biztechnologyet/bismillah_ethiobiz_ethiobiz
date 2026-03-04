import frappe

def update_website_context(context):
    """
    Force inject EthioBiz assets into context
    """
    # CSS
    if not context.get("web_include_css"):
        context.web_include_css = []
    
    css_files = [
        "/assets/bismillah_ethiobiz/css/ethiobiz_theme.css",
        "/assets/bismillah_ethiobiz/css/walta.css"
    ]
    for css in css_files:
        if css not in context.web_include_css:
            context.web_include_css.append(css)

    # JS
    if not context.get("web_include_js"):
        context.web_include_js = []
        
    js_files = [
        "/assets/bismillah_ethiobiz/js/embedding_block.js",
        "/assets/bismillah_ethiobiz/js/ethiobiz_theme.js", 
        "/assets/bismillah_ethiobiz/js/walta.js"
    ]
    for js in js_files:
        if js not in context.web_include_js:
            context.web_include_js.append(js)
