# -*- coding: utf-8 -*-
"""
DOBiz PWA - Custom page renderer for /sw.js and /manifest.webmanifest
Bismillah Ar-Rahman Ar-Rahim

Serves the service worker and web app manifest from DOBiz PWA Settings
with correct MIME types and required headers. Strict 2-string can_render()
means zero impact on any other page.
"""

import json
import os

import frappe
from frappe import _
from frappe.website.page_renderers.base_renderer import BaseRenderer

_SW_ROUTES = ("sw.js", "manifest.webmanifest", "offline.html", "offline")


def _settings():
    try:
        return frappe.get_single("DOBiz PWA Settings")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "PWA Renderer")
        return None


def _bundled_file(relpath):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "pwa")
    path = os.path.join(base, relpath)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


class PWAStaticFile(BaseRenderer):
    def can_render(self):
        return self.path in _SW_ROUTES

    def render(self):
        if self.path not in _SW_ROUTES:
            return self.build_response("", http_status_code=404)

        cfg = _settings()
        if not cfg or not cfg.enabled:
            return self.build_response("", http_status_code=404)

        if self.path == "manifest.webmanifest":
            return self._render_manifest(cfg)
        if self.path in ("offline.html", "offline"):
            return self._render_offline()
        return self._render_sw(cfg)

    # ------------------------------------------------------------------
    def _render_offline(self):
        content = _bundled_file("offline.html")
        if not content:
            return self.build_response("", http_status_code=404)
        return self.build_response(
            content,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )

    # ------------------------------------------------------------------
    def _icon(self, cfg, field, fallback):
        value = cfg.get(field)
        return value if value else fallback

    def _manifest_icons(self, cfg):
        fallback = {
            "icon_192": "/assets/bismillah_ethiobiz/pwa/icons/icon-192.png",
            "icon_512": "/assets/bismillah_ethiobiz/pwa/icons/icon-512.png",
            "icon_maskable": "/assets/bismillah_ethiobiz/pwa/icons/icon-512-maskable.png",
        }
        icons = [
            {
                "src": self._icon(cfg, "icon_192", fallback["icon_192"]),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": self._icon(cfg, "icon_512", fallback["icon_512"]),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": self._icon(cfg, "icon_maskable", fallback["icon_maskable"]),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ]
        return icons

    def _render_manifest(self, cfg):
        manifest = {
            "id": "/",
            "name": cfg.app_name or "DOBiz Smart ERP - EthioBiz",
            "short_name": cfg.short_name or "DOBiz",
            "description": cfg.description or "Rooted in Ethiopia. Built for Humanity.",
            "start_url": cfg.start_url or "/app/dobiz",
            "scope": "/",
            "display": cfg.display or "standalone",
            "display_override": ["window-controls-overlay", "standalone", "minimal-ui"],
            "prefer_related_applications": False,
            "background_color": cfg.background_color or "#0E1A1A",
            "theme_color": cfg.theme_color or "#1FB6AE",
            "categories": ["business", "productivity", "finance"],
            "lang": "en",
            "icons": self._manifest_icons(cfg),
        }
        return self.build_response(
            json.dumps(manifest, indent=2),
            headers={
                "Content-Type": "application/manifest+json",
                "Cache-Control": "max-age=3600",
            },
        )

    def _render_sw(self, cfg):
        template = _bundled_file("sw_template.js")
        if not template:
            return self.build_response("", http_status_code=404)

        values = {
            "CACHE_VERSION": str(cfg.cache_version or "1"),
            "OFFLINE_URL": "/offline",
            "OFFLINE_TITLE": (cfg.offline_title or "You are offline").replace("\\", "\\\\").replace("'", "\\'"),
            "OFFLINE_MESSAGE": (cfg.offline_message or "Reconnect to continue using DOBiz").replace("\\", "\\\\").replace("'", "\\'"),
            "APP_SHORT_NAME": (cfg.short_name or "DOBiz").replace("\\", "\\\\").replace("'", "\\'"),
        }
        body = template
        for key, val in values.items():
            body = body.replace("__%s__" % key, val)

        return self.build_response(
            body,
            headers={
                "Content-Type": "application/javascript; charset=utf-8",
                "Service-Worker-Allowed": "/",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )
