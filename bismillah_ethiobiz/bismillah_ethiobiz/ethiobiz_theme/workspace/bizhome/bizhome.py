import frappe

def get_context(context):
    """Context for BizHome workspace"""
    context.no_cache = 1
    context.title = "BizHome | EthioBiz"
    
    # Add property statistics
    context.active_properties = frappe.db.count("Property", {"status": "Active"})
    context.available_units = frappe.db.count("Property Unit", {"status": "Available"})
    context.pending_applications = frappe.db.count("Lease", {"status": "Pending"})
    
    # Calculate monthly revenue from property and hotel operations
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    context.monthly_revenue = monthly_revenue[0].total if monthly_revenue else 0
    
    return context

def get_property_stats():
    """API endpoint for property statistics"""
    return {
        "active_properties": frappe.db.count("Property", {"status": "Active"}),
        "available_units": frappe.db.count("Property Unit", {"status": "Available"}),
        "pending_applications": frappe.db.count("Lease", {"status": "Pending"}),
        "monthly_revenue": get_monthly_revenue(),
        "total_tenants": frappe.db.count("Tenant"),
        "active_leases": frappe.db.count("Lease", {"status": "Active"})
    }

def get_monthly_revenue():
    """Calculate monthly revenue from property and hotel operations"""
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    return monthly_revenue[0].total if monthly_revenue else 0

def get_occupancy_rate():
    """Calculate property occupancy rate"""
    total_units = frappe.db.count("Property Unit")
    occupied_units = frappe.db.count("Property Unit", {"status": "Occupied"})
    
    if total_units > 0:
        occupancy_rate = (occupied_units / total_units) * 100
    else:
        occupancy_rate = 0
    
    return {
        "total_units": total_units,
        "occupied_units": occupied_units,
        "occupancy_rate": round(occupancy_rate, 2)
    }

def get_hotel_status():
    """Get hotel room status breakdown"""
    hotel_status = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabRoom`
        GROUP BY status
    """, as_dict=True)
    return {row.status: row.count for row in hotel_status}

def get_maintenance_requests():
    """Get maintenance request statistics"""
    maintenance_stats = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabMaintenance Request`
        GROUP BY status
    """, as_dict=True)
    return {row.status: row.count for row in maintenance_stats}

def get_property_performance():
    """Get property performance metrics"""
    property_performance = frappe.db.sql("""
        SELECT p.name, p.property_name, COUNT(pu.name) as total_units,
               SUM(CASE WHEN pu.status = 'Occupied' THEN 1 ELSE 0 END) as occupied_units
        FROM `tabProperty` p
        LEFT JOIN `tabProperty Unit` pu ON pu.property = p.name
        WHERE p.status = 'Active'
        GROUP BY p.name, p.property_name
        ORDER BY occupied_units DESC
        LIMIT 10
    """, as_dict=True)
    return property_performance
