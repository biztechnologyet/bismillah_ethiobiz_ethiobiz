# -*- coding: utf-8 -*-
"""
EthioBiz Multi-Company Isolation - Custom Fields
Bismillah Ar-Rahman Ar-Rahim

Defines custom 'company' fields for all DocTypes that need multi-company
isolation but don't have a native company field.

These are applied via `bench migrate` through the fixtures in hooks.py.
© 2026 EthioBiz | Powered by Biz Technology Solutions
"""


def get_custom_fields():
    """
    Returns a dict of {doctype: [field_definitions]} for Custom Fields.
    Used by hooks.py fixtures to install company fields on all required DocTypes.
    
    The 'company' field is added as a Link to Company with default='Company'
    which is the Frappe macro that resolves to the current session's default company.
    """
    
    # All DocTypes that need a company field added for multi-company isolation
    # These were identified by analyzing 631+ DocTypes on ethiobiz.et production
    # Excludes: System/Core DocTypes, DocTypes that already have native company fields
    DOCTYPES_NEEDING_COMPANY = [
        # Accounts
        "Bank Guarantee",
        "Cashier Closing",
        "Subscription Plan",
        # Assets
        "Asset Activity",
        "Asset Category",
        "Asset Maintenance Log",
        "Asset Shift Allocation",
        "Asset Shift Factor",
        "Location",
        # Buying
        "Supplier",
        "Supplier Scorecard",
        "Supplier Scorecard Criteria",
        "Supplier Scorecard Period",
        "Supplier Scorecard Standing",
        "Supplier Scorecard Variable",
        # CRM
        "Appointment",
        "Campaign",
        "Contract",
        "Contract Template",
        # Education
        "Article",
        "Assessment Plan",
        "Assessment Result",
        "Course",
        "Course Activity",
        "Course Enrollment",
        "Course Schedule",
        "Guardian",
        "Instructor",
        "Payment Record",
        "Program",
        "Program Enrollment",
        "Question",
        "Quiz",
        "Quiz Activity",
        "Student",
        "Student Admission",
        "Student Applicant",
        "Student Attendance",
        "Student Group",
        "Student Leave Application",
        "Student Log",
        "Topic",
        # HR
        "Compensatory Leave Request",
        "Daily Work Summary",
        "Employee Checkin",
        "Employee Grievance",
        "Employee Referral",
        "Employee Skill Map",
        "Expense Claim Type",
        "Interview",
        "Interview Feedback",
        "Job Applicant",
        "Leave Adjustment",
        "Training Feedback",
        "Training Result",
        "Vehicle Log",
        # Job
        "Job Opportunity",
        # Letter Module
        "Letter Log",
        # Marketing
        "Lead Score Log",
        # Non Profit
        "Donor",
        # Projects
        "Activity Cost",
        "Project Update",
        # Selling
        "Customer",
        # Setup
        "Currency Exchange",
        "Driver",
        "Employee Group",
        "Sales Partner",
        "Sales Person",
        "Terms and Conditions",
        "Vehicle",
        # Stock
        "Item",
        "Item Price",
    ]
    
    custom_fields = {}
    
    for dt in DOCTYPES_NEEDING_COMPANY:
        custom_fields[dt] = [
            {
                "fieldname": "company",
                "label": "Company",
                "fieldtype": "Link",
                "options": "Company",
                "default": "Company",
                "reqd": 0,
                "hidden": 0,
                "in_list_view": 0,
                "in_standard_filter": 1,
                "allow_on_submit": 1,
                "insert_after": "",  # Frappe will place it at the end
                "translatable": 0,
            }
        ]
    
    return custom_fields


def get_property_setters():
    """
    Returns a list of Property Setter definitions.
    These enforce 'default = Company' on DocTypes that already have a native
    company field but may not have the session-default set.
    """
    
    # DocTypes that already have a native company field
    # We enforce the default to 'Company' (Frappe session macro)
    DOCTYPES_WITH_NATIVE_COMPANY = [
        "Account", "Account Closing Balance", "Accounting Dimension Filter",
        "Accounting Period", "Advance Payment Ledger Entry", "Bank Account",
        "Bank Statement Import", "Bank Transaction", "Budget", "Cost Center",
        "Cost Center Allocation", "Dunning", "Dunning Type", "Exchange Rate Revaluation",
        "GL Entry", "Invoice Discounting", "Item Tax Template", "Journal Entry",
        "Journal Entry Template", "Ledger Merge", "Loyalty Point Entry", "Loyalty Program",
        "Payment Entry", "Payment Gateway Account", "Payment Ledger Entry", "Payment Order",
        "Payment Request", "Period Closing Voucher", "POS Closing Entry", "POS Invoice",
        "POS Invoice Merge Log", "POS Opening Entry", "POS Profile", "Pricing Rule",
        "Process Deferred Accounting", "Process Payment Reconciliation",
        "Process Statement Of Accounts", "Promotional Scheme", "Purchase Invoice",
        "Purchase Taxes and Charges Template", "Repost Accounting Ledger",
        "Repost Payment Ledger", "Sales Invoice", "Sales Taxes and Charges Template",
        "Share Transfer", "Shareholder", "Shipping Rule", "Subscription", "Tax Rule",
        "Unreconcile Payment",
        "Asset", "Asset Capitalization", "Asset Depreciation Schedule", "Asset Maintenance",
        "Asset Maintenance Team", "Asset Movement", "Asset Repair", "Asset Value Adjustment",
        "Purchase Order", "Request for Quotation", "Supplier Quotation",
        "Letter",
        "Lead", "Opportunity", "Prospect",
        "Fee Schedule", "Fee Structure", "Fees",
        "Appointment Letter", "Appraisal", "Appraisal Cycle", "Attendance",
        "Attendance Request", "Employee Advance", "Employee Onboarding",
        "Employee Onboarding Template", "Employee Performance Feedback",
        "Employee Promotion", "Employee Separation", "Employee Separation Template",
        "Employee Transfer", "Exit Interview", "Expense Claim", "Full and Final Statement",
        "Goal", "Job Offer", "Job Opening", "Job Requisition", "Leave Allocation",
        "Leave Application", "Leave Block List", "Leave Encashment", "Leave Ledger Entry",
        "Leave Period", "Leave Policy Assignment", "Overtime Slip", "Shift Assignment",
        "Shift Request", "Shift Schedule Assignment", "Staffing Plan", "Training Event",
        "Training Program", "Travel Request",
        "LMS Job Application",
        "Maintenance Schedule", "Maintenance Visit",
        "Blanket Order", "BOM", "BOM Creator", "Job Card", "Plant Floor",
        "Production Plan", "Work Order",
        "Business Plan", "Campaign Contact", "Campaign Pillar", "Campaign Target",
        "DOBiz Trial Signup", "Instructor Application", "Lead Scoring Rule",
        "Marketing Campaign", "Marketing Funnel", "Marketing KPI", "Marketing Persona",
        "Marketing Strategy", "Marketing Workflow", "Post Engagement", "Publishing Queue",
        "Social Media Account", "Social Media Post", "Tibeb Mentor Subscriber",
        "Donation", "Grant Application", "Membership", "Tax Exemption 80G Certificate",
        "Additional Salary", "Arrear", "Employee Benefit Application",
        "Employee Benefit Claim", "Employee Benefit Ledger", "Employee Incentive",
        "Employee Other Income", "Employee Tax Exemption Declaration",
        "Employee Tax Exemption Proof Submission", "Gratuity", "Income Tax Slab",
        "Payroll Correction", "Payroll Entry", "Payroll Period", "Retention Bonus",
        "Salary Slip", "Salary Structure", "Salary Structure Assignment", "Salary Withholding",
        "Project", "Task", "Timesheet",
        "Import Supplier Invoice", "Lower Deduction Certificate",
        "Installation Note", "Quotation", "Sales Order",
        "Authorization Rule", "Department", "Email Digest", "Employee",
        "Transaction Deletion Record",
        "Closing Stock Balance", "Delivery Note", "Delivery Trip", "Landed Cost Voucher",
        "Material Request", "Pick List", "Purchase Receipt", "Putaway Rule",
        "Quality Inspection", "Repost Item Valuation", "Serial and Batch Bundle",
        "Serial No", "Stock Entry", "Stock Ledger Entry", "Stock Reconciliation",
        "Stock Reservation Entry", "Warehouse",
        "Subcontracting Order", "Subcontracting Receipt",
        "Issue", "Warranty Claim",
    ]
    
    property_setters = []
    
    for dt in DOCTYPES_WITH_NATIVE_COMPANY:
        property_setters.append({
            "doctype_or_field": "DocField",
            "doc_type": dt,
            "field_name": "company",
            "property": "default",
            "value": "Company",
            "property_type": "Data",
        })
    
    return property_setters
