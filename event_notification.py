import frappe
from frappe.desk.doctype.event.event import send_event_digest as original_send_event_digest


def send_event_digest():
    from frappe.desk.doctype.event.event import get_events, get_enabled_system_users, is_email_notifications_enabled_for_type
    from frappe.utils import getdate, format_datetime


    today = getdate()

    users = [
        user
        for user in get_enabled_system_users()
        if is_email_notifications_enabled_for_type(user.name, "Event Reminders")
    ]

    for user in users:
        events = get_events(today, today, user.name, for_reminder=True)
        if not events:
            continue

        event_names = [e.name for e in events]

        participants = frappe.get_all(
            "Event Participants",
            filters={
                "parent": ["in", event_names],
                "parenttype": "Event",
                "reference_doctype": "User",
            },
            fields=["parent", "reference_docname"],
        )

        user_events = {p.parent for p in participants if p.reference_docname == user.name}

        filtered = [e for e in events if e.owner == user.name or e.name in user_events]

        if not filtered:
            continue

        frappe.set_user_lang(user.name, user.language)

        for e in filtered:
            e.starts_on = format_datetime(e.starts_on, "hh:mm a")
            if e.all_day:
                e.starts_on = "All Day"

        frappe.sendmail(
            recipients=user.email,
            subject=frappe._("Upcoming Events for Today"),
            template="upcoming_events",
            args={
                "events": filtered,
            },
            header=[frappe._("Events in Today's Calendar"), "blue"],
        )
