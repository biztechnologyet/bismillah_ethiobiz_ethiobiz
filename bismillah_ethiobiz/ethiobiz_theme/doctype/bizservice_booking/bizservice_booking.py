# -*- coding: utf-8 -*-
# Bismillah Ar-Rahman Ar-Rahim
# BizService Booking — universal service booking (submittable)

from __future__ import unicode_literals
import frappe
from frappe import _  # noqa: F401
from frappe.model.document import Document
from frappe.utils import flt


class BizServiceBooking(Document):
    def validate(self):
        self.set_total_amount()
        self.validate_booking_window()
        self.assign_provider_user()

    def after_insert(self):
        self.share_with_provider()

    def on_submit(self):
        self.increment_listing_stats()
        self.auto_dispatch_bizride()

    def on_cancel(self):
        self.decrement_listing_stats()

    def resolve_provider_user(self):
        """Return the provider User who should manage this booking in Desk.

        Resolution order (per booked listing):
          1. any assigned practitioner row that has a `user` set and is active
          2. the listing's owner if they are (or become) a Service Provider
          3. the session user when it is not a guest booking
        """
        if self.service:
            try:
                listing = frappe.get_doc("BizService Listing", self.service)
            except Exception:
                listing = None
            if listing:
                for p in (listing.practitioners or []):
                    if p.get("user") and p.get("is_active", 1):
                        return p.get("user")
                owner = listing.owner
                if owner and owner not in ("Administrator", "Guest", None):
                    return owner
        caller = frappe.session.user
        if caller and caller not in ("Administrator", "Guest", None):
            return caller
        return None

    def assign_provider_user(self):
        if not self.practitioner_user:
            self.practitioner_user = self.resolve_provider_user()

    def share_with_provider(self):
        """Grant the managing provider read/write on this booking so it shows in Desk."""
        if not self.practitioner_user or self.practitioner_user == frappe.session.user:
            return
        try:
            from frappe.share import add as share_add
            if not frappe.db.exists("DocShare",
                                    {"share_doctype": self.doctype, "share_name": self.name,
                                     "user": self.practitioner_user}):
                share_add(self.doctype, self.name, self.practitioner_user, read=1, write=1, submit=1, flags={"ignore_share_permission": True})
        except Exception as e:
            frappe.log_error(title="BizService Share", message=f"Share failed for {self.name}->{self.practitioner_user}: {e}")

    def set_total_amount(self):
        if self.items:
            total = sum(flt(i.amount) for i in (self.items or []))
            if total:
                self.total_amount = total
        if not self.total_amount and self.service:
            listing = frappe.db.get_value("BizService Listing", self.service, "price")
            self.total_amount = flt(listing)

    def validate_booking_window(self):
        settings_company = frappe.db.get_single_value("BizService Settings", "company")
        window_days = frappe.db.get_single_value("BizService Settings", "booking_window_days") or 30
        if not window_days:
            window_days = 30
        from frappe.utils import add_days, date_diff, nowdate
        if self.booking_date and date_diff(self.booking_date, nowdate()) > int(window_days):
            frappe.throw(f"Booking date is outside the {window_days}-day booking window")

    def increment_listing_stats(self):
        if not self.service:
            return
        listing = frappe.get_doc("BizService Listing", self.service)
        listing.db_set("total_bookings", int(listing.total_bookings or 0) + 1)
        listing.reload()

    def decrement_listing_stats(self):
        if not self.service:
            return
        listing = frappe.get_doc("BizService Listing", self.service)
        listing.db_set("total_bookings", max(0, int(listing.total_bookings or 0) - 1))
        listing.reload()

    def auto_dispatch_bizride(self):
        """When the booked listing requires travel + settings enable auto-dispatch,
        create a BizRide Delivery for home dispatch (Phase 1 cross-cut gap closure)."""
        if not self.service:
            return
        listing = frappe.get_doc("BizService Listing", self.service)
        if not listing.requires_travel:
            return
        # If BizService Settings exist and explicitly disable auto-dispatch, respect it.
        try:
            auto = frappe.db.get_single_value("BizService Settings", "auto_dispatch_bizride")
            if auto == 0:
                return
        except Exception:
            pass
        if self.bizride_delivery:
            return
        if not frappe.db.exists("DocType", "BizRide Delivery"):
            return
        delivery = frappe.get_doc({
            "doctype": "BizRide Delivery",
            "ref_doctype": "BizService Booking",
            "ref_name": self.name,
            "delivery_type": "Service Dispatch",
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "pickup_address": frappe.db.get_value("BizService Listing", self.service, "company") or "",
            "delivery_address": self.customer_address,
            "status": "Requested",
        })
        try:
            delivery.insert(ignore_permissions=True)
            self.db_set("bizride_delivery", delivery.name)
            # Auto-accept path is dispatched via the real BizRide dispatch engine on confirm
        except Exception as e:
            frappe.log_error(f"BizService auto BizRide dispatch failed: {e}", "BizService")
