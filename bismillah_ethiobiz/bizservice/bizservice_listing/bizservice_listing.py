# -*- coding: utf-8 -*-
# Bismillah Ar-Rahman Ar-Rahim
# BizService Listing — generic service listing for all providers

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt


class BizServiceListing(Document):
    def validate(self):
        if not self.slug and self.service_name:
            self.slug = frappe.scrub(self.service_name)
        if not self.website_page and self.slug:
            self.website_page = self.slug
        if not self.serving_city and not self.serving_region:
            self.serving_city = "Addis Ababa"

    def get_public_dict(self):
        images = []
        for img in self.get("images") or []:
            if img.get("image"):
                images.append({"image": img.get("image"), "caption": img.get("caption"), "is_primary": img.get("is_primary")})
        practitioners = []
        for pr in self.get("practitioners") or []:
            practitioners.append({"name": pr.get("practitioner_name"), "role": pr.get("role_title"), "phone": pr.get("phone")})
        return {
            "name": self.name,
            "service_name": self.service_name,
            "slug": self.slug or self.name,
            "company": self.company,
            "category": self.category,
            "price": flt(self.price),
            "price_type": self.price_type,
            "currency": self.currency or "ETB",
            "duration_minutes": self.duration_minutes,
            "requires_travel": bool(self.requires_travel),
            "serving_region": self.serving_region,
            "serving_city": self.serving_city,
            "featured": bool(self.featured),
            "is_active": bool(self.is_active),
            "average_rating": flt(self.average_rating),
            "total_bookings": int(self.total_bookings or 0),
            "description": self.get("description") or "",
            "website_page": self.website_page or "",
            "images": images,
            "practitioners": practitioners,
        }
