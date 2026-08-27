import frappe

def get_context(context):
    context.no_cache = 1
    context.title = "Verified Career Opportunities | EthioBiz Jobs"

    # Query all open job openings
    jobs = frappe.get_all(
        "Job Opening",
        filters={"status": "Open"},
        fields=[
            "name", "job_title", "company", "designation",
            "employment_type", "location", "lower_range",
            "upper_range", "currency", "salary_per", "description", "posted_on"
        ],
        order_by="posted_on desc, creation desc"
    )

    company_counts = {}
    for j in jobs:
        comp = j.company or "Biz Technology Solutions"
        company_counts[comp] = company_counts.get(comp, 0) + 1
        
        if j.lower_range and j.upper_range:
            j["salary_str"] = f"{j.lower_range:,.0f} - {j.upper_range:,.0f} {j.currency or 'ETB'} / {j.salary_per or 'mo'}"
        elif j.lower_range:
            j["salary_str"] = f"{j.lower_range:,.0f} {j.currency or 'ETB'} / {j.salary_per or 'mo'}"
        else:
            j["salary_str"] = "Competitive Compensation"

    context.jobs = jobs
    context.companies = [{"name": k, "count": v} for k, v in company_counts.items()]
    return context

@frappe.whitelist(allow_guest=True)
def submit_job_application(job_title=None, applicant_name=None, email_id=None, phone_number=None, company=None, cover_letter=None):
    """Creates a verified Job Applicant record in ERPNext HRMS with attached CV/documents."""
    from frappe.utils.file_manager import save_file
    
    user = frappe.session.user
    if user and user != "Guest":
        u_doc = frappe.get_doc("User", user)
        applicant_name = u_doc.full_name or applicant_name
        email_id = u_doc.email or email_id
        phone_number = u_doc.mobile_no or u_doc.phone or phone_number

    if not applicant_name or not email_id:
        frappe.throw("Applicant Name and Email Address are required.")

    app_doc = frappe.get_doc({
        "doctype": "Job Applicant",
        "applicant_name": applicant_name,
        "email_id": email_id,
        "phone_number": phone_number,
        "job_title": job_title,
        "status": "Open",
        "notes": cover_letter or ""
    })
    app_doc.flags.ignore_permissions = True
    app_doc.insert(ignore_permissions=True)

    # Handle CV / Resume file attachment if uploaded
    if hasattr(frappe.local, "uploaded_file") and frappe.local.uploaded_file:
        file_content = frappe.local.uploaded_file
        file_name = frappe.local.uploaded_filename or "resume.pdf"
        saved = save_file(
            fname=file_name,
            content=file_content,
            dt="Job Applicant",
            dn=app_doc.name,
            df="resume_attachment",
            is_private=1
        )
        app_doc.db_set("resume_attachment", saved.file_url)
    elif frappe.request and frappe.request.files and "cv_file" in frappe.request.files:
        uploaded = frappe.request.files["cv_file"]
        saved = save_file(
            fname=uploaded.filename,
            content=uploaded.read(),
            dt="Job Applicant",
            dn=app_doc.name,
            df="resume_attachment",
            is_private=1
        )
        app_doc.db_set("resume_attachment", saved.file_url)

    return {
        "status": "success",
        "message": "Application submitted successfully with documents! Our HR team has received your profile.",
        "applicant_id": app_doc.name
    }
