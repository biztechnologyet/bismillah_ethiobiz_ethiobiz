import frappe

def get_context(context):
    """Context for DOBiz Subscription Management workspace"""
    context.no_cache = 1
    context.title = "DOBiz Subscription Management | EthioBiz"
    
    # Add subscription statistics
    context.active_subscriptions = frappe.db.count("Subscription Contract", {"status": "Active"})
    context.pending_activations = frappe.db.count("Subscription Contract", {"status": "Pending"})
    context.active_coupons = frappe.db.count("DOBiz Coupon", {"active": 1})
    
    # Calculate monthly revenue from active subscriptions
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSubscription Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    context.monthly_revenue = monthly_revenue[0].total if monthly_revenue else 0
    
    return context

def get_subscription_stats():
    """API endpoint for subscription statistics"""
    return {
        "active_subscriptions": frappe.db.count("Subscription Contract", {"status": "Active"}),
        "pending_activations": frappe.db.count("Subscription Contract", {"status": "Pending"}),
        "monthly_revenue": get_monthly_revenue(),
        "active_coupons": frappe.db.count("DOBiz Coupon", {"active": 1}),
        "total_customers": frappe.db.count("Customer")
    }

def get_monthly_revenue():
    """Calculate monthly revenue from subscriptions"""
    monthly_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSubscription Invoice`
        WHERE status = 'Paid' 
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    return monthly_revenue[0].total if monthly_revenue else 0

def get_industry_pricing():
    """Get per-industry pricing configuration"""
    industries = {
        "Healthcare": {"base_price": 9500, "multiplier": 1.0},
        "Hotel Management": {"base_price": 8000, "multiplier": 1.0},
        "Restaurant": {"base_price": 7000, "multiplier": 1.0},
        "Property Management": {"base_price": 8500, "multiplier": 1.0},
        "Manufacturing": {"base_price": 12000, "multiplier": 1.2},
        "Education": {"base_price": 6000, "multiplier": 0.8},
        "Retail & Wholesale": {"base_price": 7500, "multiplier": 1.0},
        "Non-Profit": {"base_price": 5000, "multiplier": 0.7},
        "Professional Services": {"base_price": 9000, "multiplier": 1.0},
        "Transportation": {"base_price": 10000, "multiplier": 1.1},
        "Agriculture": {"base_price": 6500, "multiplier": 0.9},
        "Construction": {"base_price": 11000, "multiplier": 1.2},
        "Logistics": {"base_price": 9500, "multiplier": 1.0},
        "Government": {"base_price": 15000, "multiplier": 1.5}
    }
    return industries
