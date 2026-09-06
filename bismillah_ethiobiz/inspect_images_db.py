import frappe

frappe.init(site="ethiobiz.et", sites_path="sites")
frappe.connect()

print("--- ITEMS ---")
items = frappe.db.get_all("Item", fields=["name", "item_name", "image"], limit=6)
for it in items:
    print(it)

print("--- DOCTORS ---")
if frappe.db.exists("DocType", "Healthcare Practitioner"):
    docs = frappe.db.get_all("Healthcare Practitioner", fields=["name", "practitioner_name", "image"], limit=6)
    for d in docs:
        print(d)

print("--- COMPANIES ---")
comps = frappe.db.get_all("Company", fields=["name", "company_name", "company_logo"], limit=6)
for c in comps:
    print(c)

print("--- BIZSERVICES ---")
if frappe.db.exists("DocType", "BizService Listing"):
    svcs = frappe.db.get_all("BizService Listing", fields=["name", "service_name"], limit=6)
    for s in svcs:
        print(s)

print("--- PROPERTIES ---")
if frappe.db.exists("DocType", "Property Listing"):
    props = frappe.db.get_all("Property Listing", fields=["name", "title", "image"], limit=6)
    for p in props:
        print(p)
