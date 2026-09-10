# -*- coding: utf-8 -*-
"""
DOBiz PWA Settings - Whitelisted helpers
Bismillah Ar-Rahman Ar-Rahim
"""

import frappe

DEFAULTS = {
    "enabled": 1,
    "app_name": "DOBiz Smart ERP - EthioBiz",
    "short_name": "DOBiz",
    "description": "Rooted in Ethiopia. Built for Humanity.",
    "theme_color": "#1FB6AE",
    "background_color": "#0E1A1A",
    "start_url": "/app/dobiz",
    "display": "standalone",
    "offline_title": "You are offline",
    "offline_message": "Reconnect to continue using DOBiz",
    "install_prompt_enabled": 1,
    "cache_version": "1",
}


def _doctype_json():
    import os

    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "doctype", "dobiz_pwa_settings", "dobiz_pwa_settings.json")
    with open(path, "r", encoding="utf-8") as fh:
        return frappe._dict(__import__("json").load(fh))


def create_doctype():
    """Create the DOBiz PWA Settings doctype + seed defaults (idempotent, no migrate)."""
    if frappe.db.exists("DocType", "DOBiz PWA Settings"):
        if not frappe.db.exists("DOBiz PWA Settings", "DOBiz PWA Settings"):
            _seed_defaults()
        return {"created": 0}

    dt_def = _doctype_json()
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": dt_def["name"],
        "module": "EthioBiz Theme",
        "custom": 1,
        "issingle": 1,
        "fields": dt_def["fields"],
        "permissions": dt_def.get("permissions", [{"role": "System Manager", "read": 1, "write": 1}]),
    })
    doc.insert(ignore_permissions=True)
    _seed_defaults()
    frappe.db.commit()
    frappe.clear_cache()
    return {"created": 1}


def _seed_defaults():
    doc = frappe.new_doc("DOBiz PWA Settings")
    for k, v in DEFAULTS.items():
        doc.set(k, v)
    doc.save(ignore_permissions=True)
    frappe.db.commit()


def _doc():
    return frappe.get_doc("DOBiz PWA Settings")

FALLBACK_ICONS = {
    "icon_192": "/assets/bismillah_ethiobiz/pwa/icons/icon-192.png",
    "icon_512": "/assets/bismillah_ethiobiz/pwa/icons/icon-512.png",
    "icon_maskable": "/assets/bismillah_ethiobiz/pwa/icons/icon-512-maskable.png",
}


def _doc():
    return frappe.get_doc("DOBiz PWA Settings")


@frappe.whitelist(allow_guest=True)
def get_config():
    """Return the active PWA config for pwa_register.js."""
    try:
        cfg = _doc()
    except frappe.DoesNotExistError:
        frappe.log_error("DOBiz PWA Settings doctype not found", "PWA")
        return None

    config = {k: cfg.get(k) for k in DEFAULTS if cfg.meta.has_field(k)}
    if not config.get("enabled"):
        return {"enabled": 0}

    for key, fallback in FALLBACK_ICONS.items():
        val = cfg.get(key)
        config[key] = val if val else fallback

    config["scope"] = "/"
    config["register_url"] = "/sw.js"
    config["manifest_url"] = "/manifest.webmanifest"
    return config


@frappe.whitelist()
def reset_defaults():
    """Reset the single doctype to shipped defaults."""
    if not frappe.has_permission("DOBiz PWA Settings", "write"):
        frappe.throw("Not permitted", frappe.PermissionError)

    try:
        cfg = _doc()
    except frappe.DoesNotExistError:
        cfg = frappe.new_doc("DOBiz PWA Settings")

    for k, v in DEFAULTS.items():
        cfg.set(k, v)
    cfg.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_document_cache("DOBiz PWA Settings", "DOBiz PWA Settings")
    return {"ok": 1}
