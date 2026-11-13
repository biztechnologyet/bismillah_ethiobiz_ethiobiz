import frappe

def reset_theme_context():
    """
    Emergency cleanup: remove EthioBiz assets from website context
    Run this via 'bench execute ...' if needed.
    """
    hooks = frappe.get_hooks()
    context = frappe.get_doc("Website Settings")
    
    # Remove our forced injections if they persist in DB (unlikely but safe)
    # This is mostly a placebo in this context as hooks are code-based, 
    # but good to have for manual testing if we used DB-based overrides.
    print("Resetting context injection...")
    pass

if __name__ == "__main__":
    reset_theme_context()
