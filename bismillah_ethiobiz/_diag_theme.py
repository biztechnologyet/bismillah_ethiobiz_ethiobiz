import frappe

frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
frappe.connect()

t = frappe.get_single("EthioBiz Theme")
print("PILLARS", len(t.pillars or []))
for p in t.pillars or []:
    print(
        " -",
        getattr(p, "pillar_key", None),
        "|",
        getattr(p, "pillar_name", None),
        "| enabled=",
        getattr(p, "is_enabled", None),
        "| subsystem=",
        getattr(p, "subsystem_key", None),
        "| title_am=",
        getattr(p, "title_am", None),
    )
print("PORTALS", len(t.card_portal_items or []))
for c in t.card_portal_items or []:
    print(
        " *",
        getattr(c, "pillar", None),
        "|",
        getattr(c, "title", None),
        "/",
        getattr(c, "title_am", None),
        "| url=",
        getattr(c, "url", None),
        "| sub=",
        getattr(c, "subsystem_key", None),
        "| enabled=",
        getattr(c, "is_enabled", None),
    )
print("PATCH LOG")
for p in frappe.get_all(
    "Patch Log", fields=["patch"], order_by="creation desc", limit=10
):
    print("  ", p.patch)
frappe.destroy()
