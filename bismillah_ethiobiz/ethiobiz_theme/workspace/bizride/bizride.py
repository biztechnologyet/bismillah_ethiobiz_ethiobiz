import frappe

def get_context(context):
    """Context for BizRide workspace"""
    context.no_cache = 1
    context.title = "BizRide | EthioBiz"
    
    # Add delivery statistics
    context.active_deliveries = frappe.db.count("Delivery Trip", {"status": "In Transit"})
    context.today_rides = frappe.db.count("Delivery Trip", {"delivery_date": frappe.utils.today()})
    context.available_drivers = frappe.db.count("Driver", {"status": "Active"})
    
    # Calculate monthly revenue from delivery invoices
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    context.monthly_revenue = monthly_revenue[0].total if monthly_revenue else 0
    
    return context

def get_delivery_stats():
    """API endpoint for delivery statistics"""
    return {
        "active_deliveries": frappe.db.count("Delivery Trip", {"status": "In Transit"}),
        "today_rides": frappe.db.count("Delivery Trip", {"delivery_date": frappe.utils.today()}),
        "available_drivers": frappe.db.count("Driver", {"status": "Active"}),
        "monthly_revenue": get_monthly_revenue(),
        "total_vehicles": frappe.db.count("Vehicle", {"status": "Active"}),
        "total_shipments": frappe.db.count("Shipment")
    }

def get_monthly_revenue():
    """Calculate monthly revenue from delivery operations"""
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    return monthly_revenue[0].total if monthly_revenue else 0

def get_fleet_status():
    """Get fleet vehicle status breakdown"""
    fleet_status = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabVehicle`
        GROUP BY status
    """, as_dict=True)
    return {row.status: row.count for row in fleet_status}

def get_driver_performance():
    """Get driver performance metrics"""
    driver_performance = frappe.db.sql("""
        SELECT d.name, d.full_name, COUNT(dt.name) as total_deliveries,
               AVG(dt.delivery_time) as avg_delivery_time
        FROM `tabDriver` d
        LEFT JOIN `tabDelivery Trip` dt ON dt.driver = d.name
        WHERE d.status = 'Active'
        GROUP BY d.name, d.full_name
        ORDER BY total_deliveries DESC
        LIMIT 10
    """, as_dict=True)
    return driver_performance
