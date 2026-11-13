from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist()
def get_onboarding_status():
    """Override frappe.onboarding.get_onboarding_status to always return completed."""
    return {
        "learning_onboarding_status": [
            {"status": "Completed", "stage": "Create a Course", "is_complete": 1},
            {"status": "Completed", "stage": "Create a Lesson", "is_complete": 1},
            {"status": "Completed", "stage": "Add course mentors", "is_complete": 1},
            {"status": "Completed", "stage": "Create a Quiz", "is_complete": 1},
            {"status": "Completed", "stage": "Publish the course", "is_complete": 1},
            {"status": "Completed", "stage": "View your course", "is_complete": 1},
            {"status": "Completed", "stage": "Enroll a Student", "is_complete": 1},
            {"status": "Completed", "stage": "Generate certificates", "is_complete": 1}
        ],
        "helpdesk_onboarding_status": [
            {"status": "Completed", "stage": "Create an Agent", "is_complete": 1},
            {"status": "Completed", "stage": "Create an Assignment", "is_complete": 1},
            {"status": "Completed", "stage": "Respond to a Ticket", "is_complete": 1},
            {"status": "Completed", "stage": "Resolve a Ticket", "is_complete": 1},
            {"status": "Completed", "stage": "Add Knowledge Base Article", "is_complete": 1}
        ],
        "is_complete": 1
    }

@frappe.whitelist()
def update_user_onboarding_status(steps, app_name):
    """No-op override: silently ignore onboarding updates."""
    pass
