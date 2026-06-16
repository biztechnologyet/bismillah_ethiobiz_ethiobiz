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
    # Analysis of 1355 DocTypes on ethiobiz.et production (2026-06-16)
    # 235 native + 86 existing custom = 321 with company
    # ~183 new custom fields added here = ~504 total with company
    # Remaining: system/core DocTypes that should NEVER have company
    DOCTYPES_NEEDING_COMPANY = [
        # === EXISTING (from v1) ===
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
        # Quality Management
        "Quality Action",
        "Quality Feedback",
        "Quality Feedback Template",
        "Quality Goal",
        "Quality Meeting",
        "Quality Procedure",
        "Quality Review",
        "Quality Inspection Parameter",
        "Quality Inspection Parameter Group",
        "Quality Inspection Template",

        # === NEW PHASE 1 (2026-06-16) ===
        
        # Contacts
        "Address",
        "Contact",

        # Desk — user daily work
        "Event",
        "Note",
        "ToDo",

        # FTelephony
        "TP Call Log",
        "TP Exotel Settings",
        "TP Telephony Agent",
        "TP Twilio Settings",

        # Healthcare — ALL non-table DocTypes
        "ABDM Request",
        "Antibiotic",
        "Appointment Type",
        "Body Part",
        "Clinical Note",
        "Clinical Note Type",
        "Clinical Procedure Template",
        "Code System",
        "Code Value",
        "Code Value Set",
        "Complaint",
        "Diagnosis",
        "Dosage Form",
        "Exercise Difficulty Level",
        "Exercise Type",
        "Fee Validity",
        "Healthcare Activity",
        "Healthcare Practitioner",
        "Healthcare Service Unit Type",
        "Healthcare Settings",
        "Lab Test Sample",
        "Lab Test Template",
        "Lab Test UOM",
        "Medical Department",
        "Medication",
        "Medication Class",
        "Nursing Checklist Template",
        "Observation Template",
        "Organism",
        "Patient",
        "Patient Assessment Parameter",
        "Patient Assessment Template",
        "Patient Care Type",
        "Patient History Settings",
        "Patient Medical Record",
        "Practitioner Schedule",
        "Prescription Dosage",
        "Prescription Duration",
        "Sample Type",
        "Sensitivity",
        "Service Request Category",
        "Service Request Reason",
        "Specimen",
        "Therapy Plan Template",
        "Therapy Type",
        "Treatment Plan Template",

        # Helpdesk — ALL non-table DocTypes
        "HD Action",
        "HD Agent",
        "HD Article",
        "HD Article Category",
        "HD Article Feedback",
        "HD Customer",
        "HD Desk Account Request",
        "HD Email Feedback",
        "HD Escalation Rule",
        "HD Form Script",
        "HD Notification",
        "HD Organization",
        "HD Portal Signup Request",
        "HD Saved Reply",
        "HD Service Holiday List",
        "HD Service Level Agreement",
        "HD Settings",
        "HD Stopword",
        "HD Synonyms",
        "HD Team",
        "HD Ticket",
        "HD Ticket Activity",
        "HD Ticket Comment",
        "HD Ticket Feedback Option",
        "HD Ticket Priority",
        "HD Ticket Status",
        "HD Ticket Template",
        "HD Ticket Type",
        "HD View",

        # IT Management — ALL non-table DocTypes
        "Configuration Item",
        "Configuration Item Type",
        "Cycle Type",
        "Encryption Type",
        "Floor",
        "Host Domain",
        "IP Address",
        "IT Backup",
        "IT Checklist",
        "IT Checklist Type",
        "IT Hardware",
        "IT Landscape",
        "IT Management Settings",
        "IT Service Report",
        "IT Software",
        "ITM Host Item",
        "ITM Landscape",
        "ITM Location",
        "ITM Software",
        "ITM Software Instance",
        "ITM Solution",
        "ITM Solution Type",
        "ITM User Account",
        "ITM User Account Type",
        "ITM User Group",
        "ITM User Group Type",
        "Licence",
        "Local Area Network",
        "Location Room",
        "Network Interface Controller",
        "Network Jack",
        "Retention Type",
        "Socket",
        "Software Instance",
        "Software Version",
        "Solution",
        "Solution Type",
        "Subnet",
        "Trip",
        "User Account",
        "User Account Type",
        "User Group",
        "User Group Type",

        # LMS — ALL non-table DocTypes
        "Course Chapter",
        "Course Evaluator",
        "Course Lesson",
        "Function",
        "Industry",
        "LMS Assignment",
        "LMS Assignment Submission",
        "LMS Badge",
        "LMS Badge Assignment",
        "LMS Batch",
        "LMS Batch Enrollment",
        "LMS Batch Feedback",
        "LMS Category",
        "LMS Certificate",
        "LMS Certificate Evaluation",
        "LMS Certificate Request",
        "LMS Coupon",
        "LMS Course",
        "LMS Course Interest",
        "LMS Course Mentor Mapping",
        "LMS Course Progress",
        "LMS Course Review",
        "LMS Enrollment",
        "LMS Lesson Note",
        "LMS Live Class",
        "LMS Live Class Participant",
        "LMS Mentor Request",
        "LMS Payment",
        "LMS Program",
        "LMS Programming Exercise",
        "LMS Programming Exercise Submission",
        "LMS Question",
        "LMS Quiz",
        "LMS Quiz Submission",
        "LMS Settings",
        "LMS Source",
        "LMS Timetable Template",
        "LMS Video Watch Duration",
        "LMS Zoom Settings",
        "User Skill",
        "Zoom Settings",

        # Non Profit — ALL non-table DocTypes
        "Certification Application",
        "Certified Consultant",
        "Chapter",
        "Donor Type",
        "Member",
        "Membership Type",
        "Volunteer",
        "Volunteer Type",

        # Telephony
        "Call Log",
        "Incoming Call Settings",
        "Telephony Call Type",
        "Voice Call Settings",

        # Webshop
        "Item Review",
        "Website Item",
        "Wishlist",
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
                "insert_after": "",
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
        # Healthcare DocTypes with native company
        "Inpatient Medication Entry", "Inpatient Medication Order", "Patient Appointment",
        "Patient Encounter", "Therapy Plan",
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
