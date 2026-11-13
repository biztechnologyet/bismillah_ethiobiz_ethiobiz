import frappe

def get_context(context):
    """Context for BizFix workspace"""
    context.no_cache = 1
    context.title = "BizFix | EthioBiz"
    
    # Add service statistics
    context.active_providers = frappe.db.count("Service Provider", {"status": "Active"})
    context.today_requests = frappe.db.count("Service Request", {"request_date": frappe.utils.today()})
    context.pending_assignments = frappe.db.count("Service Assignment", {"status": "Pending"})
    
    # Calculate monthly revenue from service operations
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    context.monthly_revenue = monthly_revenue[0].total if monthly_revenue else 0
    
    return context

def get_service_stats():
    """API endpoint for service statistics"""
    return {
        "active_providers": frappe.db.count("Service Provider", {"status": "Active"}),
        "today_requests": frappe.db.count("Service Request", {"request_date": frappe.utils.today()}),
        "pending_assignments": frappe.db.count("Service Assignment", {"status": "Pending"}),
        "monthly_revenue": get_monthly_revenue(),
        "total_categories": frappe.db.count("Service Category"),
        "total_packages": frappe.db.count("Service Package")
    }

def get_monthly_revenue():
    """Calculate monthly revenue from service operations"""
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    return monthly_revenue[0].total if monthly_revenue else 0

def get_provider_performance():
    """Get provider performance metrics"""
    provider_performance = frappe.db.sql("""
        SELECT sp.name, sp.provider_name, COUNT(sa.name) as total_assignments,
               AVG(pr.rating) as avg_rating
        FROM `tabService Provider` sp
        LEFT JOIN `tabService Assignment` sa ON sa.provider = sp.name
        LEFT JOIN `tabProvider Rating` pr ON pr.provider = sp.name
        WHERE sp.status = 'Active'
        GROUP BY sp.name, sp.provider_name
        ORDER BY total_assignments DESC
        LIMIT 10
    """, as_dict=True)
    return provider_performance

def get_service_category_stats():
    """Get service category statistics"""
    category_stats = frappe.db.sql("""
        SELECT sc.name, sc.category_name, COUNT(sr.name) as total_requests
        FROM `tabService Category` sc
        LEFT JOIN `tabService Request` sr ON sr.service_category = sc.name
        GROUP BY sc.name, sc.category_name
        ORDER BY total_requests DESC
        LIMIT 10
    """, as_dict=True)
    return category_stats

def get_request_status_breakdown():
    """Get service request status breakdown"""
    status_breakdown = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabService Request`
        GROUP BY status
    """, as_dict=True)
    return {row.status: row.count for row in status_breakdown}
