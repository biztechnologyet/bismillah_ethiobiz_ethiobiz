# BISMALLAH — Magala marketplace cart + COD / Bank Transfer / AddisPay checkout
import json
from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import cint, cstr, flt, getdate, now_datetime, nowdate

CART_TTL = 60 * 60 * 24 * 7
DEFAULT_COMPANY = "Biz Technology Solutions"
DEFAULT_COD_HINTS = ("product", "food", "dining", "goods")
DEFAULT_JOB_HINTS = ("job", "career")
DEFAULT_BANKS = [
    {"bank": "Commercial Bank of Ethiopia", "account": "1000236131606", "holder": "Hadi Awad"},
    {"bank": "Telebirr SuperApp", "account": "+251 98 676 7576", "holder": "Hadi Awad"},
    {"bank": "Bank of Abyssinia", "account": "94784891", "holder": "Hadi Awad"},
]


def _checkout_settings():
    try:
        if frappe.db.exists("DocType", "Magala Checkout Settings"):
            return frappe.get_single("Magala Checkout Settings")
    except Exception:
        return None
    return None


def _split_hints(raw, defaults):
    if not raw:
        return defaults
    parts = [p.strip().lower() for p in cstr(raw).replace("\n", ",").split(",") if p.strip()]
    return tuple(parts) or defaults


def _cod_hints():
    s = _checkout_settings()
    return _split_hints(getattr(s, "cod_item_groups", None) if s else None, DEFAULT_COD_HINTS)


def _job_hints():
    s = _checkout_settings()
    return _split_hints(getattr(s, "job_item_groups", None) if s else None, DEFAULT_JOB_HINTS)


def is_job_item(item_group):
    g = (item_group or "").lower()
    return any(h in g for h in _job_hints())


def is_cod_eligible(item_group):
    g = (item_group or "").lower()
    if is_job_item(g):
        return False
    s = _checkout_settings()
    if s and not cint(s.enable_cod):
        return False
    return any(h in g for h in _cod_hints()) or g in ("products",)


def _cart_key():
    user = frappe.session.user
    if user and user != "Guest":
        return f"magala_cart:user:{user}"
    sid = getattr(frappe.session, "sid", None) or "anon"
    return f"magala_cart:sid:{sid}"


def _get_cart():
    data = frappe.cache().get_value(_cart_key())
    if not data:
        return {"items": []}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return {"items": []}
    data.setdefault("items", [])
    return data


def _set_cart(cart):
    frappe.cache().set_value(_cart_key(), cart, expires_in_sec=CART_TTL)
    return cart


def _parent_company():
    try:
        return frappe.db.get_single_value("DOBiz SaaS Settings", "parent_company") or DEFAULT_COMPANY
    except Exception:
        return DEFAULT_COMPANY


def _item_meta(item_code):
    item = frappe.db.get_value(
        "Item",
        item_code,
        ["name", "item_name", "item_group", "stock_uom", "is_stock_item", "company", "standard_rate"],
        as_dict=True,
    )
    if not item:
        frappe.throw(_("Item {0} not found").format(item_code))
    wi = frappe.db.get_value(
        "Website Item",
        {"item_code": item_code},
        ["company", "route", "published", "website_image", "web_item_name"],
        as_dict=True,
    ) or {}
    company = wi.get("company") or item.get("company") or _parent_company()
    price = 0
    selling_pl = frappe.db.get_single_value("Selling Settings", "selling_price_list")
    if selling_pl:
        price = flt(
            frappe.db.get_value(
                "Item Price",
                {"item_code": item_code, "price_list": selling_pl, "selling": 1},
                "price_list_rate",
            )
        )
    if not price:
        row = frappe.db.sql(
            """select price_list_rate from `tabItem Price`
               where item_code=%s and selling=1 order by modified desc limit 1""",
            item_code,
        )
        price = flt(row[0][0]) if row else 0
    if not price:
        price = flt(item.get("standard_rate"))
    group = item.get("item_group") or "Products"
    return {
        "item_code": item_code,
        "item_name": wi.get("web_item_name") or item.get("item_name") or item_code,
        "item_group": group,
        "uom": item.get("stock_uom") or "Nos",
        "company": company,
        "rate": flt(price or 0),
        "route": wi.get("route") or "",
        "image": wi.get("website_image") or "",
        "is_job": is_job_item(group),
        "cod_eligible": is_cod_eligible(group),
        "published": cint(wi.get("published") or 0),
    }


@frappe.whitelist(allow_guest=True)
def get_item_checkout_meta(item_code):
    return _item_meta(item_code)


@frappe.whitelist(allow_guest=True)
def get_bank_accounts():
    s = _checkout_settings()
    if s and s.bank_accounts:
        return [
            {
                "bank": row.bank_name,
                "account": row.account_no,
                "holder": row.account_holder,
                "instructions": row.instructions,
            }
            for row in s.bank_accounts
        ]
    return DEFAULT_BANKS


def _is_guest():
    return (frappe.session.user or "Guest") == "Guest"


def _require_login():
    if _is_guest():
        frappe.throw(_("Please log in to add items and complete Magala checkout."), title=_("Login required"))


def _webshop_update(item_code, qty):
    """Keep Frappe Webshop Quotation (the native /cart table) in sync."""
    if _is_guest():
        return
    try:
        from webshop.webshop.shopping_cart.cart import update_cart

        update_cart(item_code, flt(qty))
    except Exception as e:
        frappe.logger("ethiobiz").error(f"Magala webshop cart sync skipped: {e}")


def _webshop_lines():
    if _is_guest():
        return []
    try:
        from webshop.webshop.shopping_cart.cart import get_cart_quotation

        data = get_cart_quotation() or {}
        doc = data.get("doc") if isinstance(data, dict) else data
        if not doc:
            return []
        items = getattr(doc, "items", None) or (doc.get("items") if isinstance(doc, dict) else None) or []
        out = []
        for row in items:
            code = row.get("item_code") if isinstance(row, dict) else getattr(row, "item_code", None)
            qty = row.get("qty") if isinstance(row, dict) else getattr(row, "qty", 0)
            if code:
                out.append({"item_code": code, "qty": flt(qty or 1)})
        return out
    except Exception as e:
        frappe.logger("ethiobiz").error(f"Magala webshop cart read skipped: {e}")
        return []


def _clear_webshop_quotation():
    for row in list(_webshop_lines()):
        _webshop_update(row["item_code"], 0)


def _merged_cart_rows():
    by_code = {}
    for row in (_get_cart().get("items") or []) + _webshop_lines():
        code = row.get("item_code")
        if not code:
            continue
        qty = flt(row.get("qty") or 1)
        if code in by_code:
            by_code[code]["qty"] = max(flt(by_code[code].get("qty") or 0), qty)
        else:
            by_code[code] = {"item_code": code, "qty": qty}
    return list(by_code.values())


def _link_user_to_customer(user, customer, email=None, phone=None, customer_name=None):
    if not user or user == "Guest" or not customer:
        return
    try:
        if frappe.get_meta("User").has_field("customer"):
            existing = frappe.db.get_value("User", user, "customer")
            if not existing:
                frappe.db.set_value("User", user, "customer", customer, update_modified=False)
    except Exception:
        pass
    try:
        if email and frappe.db.exists("Customer", customer):
            if not frappe.db.get_value("Customer", customer, "email_id"):
                frappe.db.set_value("Customer", customer, "email_id", email, update_modified=False)
            if phone and not frappe.db.get_value("Customer", customer, "mobile_no"):
                frappe.db.set_value("Customer", customer, "mobile_no", phone, update_modified=False)
    except Exception:
        pass


def _buyer_profile(require=True):
    """Name, email, phone, Customer, and shipping address from the logged-in User."""
    if _is_guest():
        if require:
            _require_login()
        return {
            "logged_in": False,
            "full_name": "",
            "email": "",
            "phone": "",
            "customer": None,
            "address_name": None,
            "shipping_address": "",
            "login_url": "/login?redirect-to=/cart",
        }
    user = frappe.session.user
    udoc = frappe.get_cached_doc("User", user)
    email = cstr(udoc.email or user).strip()
    full_name = cstr(udoc.full_name or " ".join(filter(None, [udoc.first_name, udoc.last_name]))).strip()
    phone = cstr(udoc.mobile_no or udoc.phone).strip()
    customer = None
    if frappe.get_meta("User").has_field("customer"):
        customer = udoc.get("customer")
    if not customer and email:
        customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    contact = frappe.db.get_value("Contact", {"user": user}, "name")
    if not contact and email:
        contact = frappe.db.get_value("Contact", {"email_id": email}, "name")
    if contact:
        crow = frappe.db.get_value("Contact", contact, ["mobile_no", "phone", "full_name"], as_dict=True) or {}
        if not phone:
            phone = cstr(crow.get("mobile_no") or crow.get("phone")).strip()
        if not full_name:
            full_name = cstr(crow.get("full_name")).strip()
        if not customer:
            customer = frappe.db.get_value(
                "Dynamic Link",
                {"parenttype": "Contact", "parent": contact, "link_doctype": "Customer"},
                "link_name",
            )
    address_name = None
    shipping_address = ""
    if customer:
        if not phone:
            phone = cstr(frappe.db.get_value("Customer", customer, "mobile_no")).strip()
        if not full_name:
            full_name = cstr(frappe.db.get_value("Customer", customer, "customer_name")).strip()
        links = frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
            pluck="parent",
        )
        chosen = None
        for aname in links:
            ad = frappe.db.get_value(
                "Address",
                aname,
                ["name", "address_type", "disabled", "address_line1", "address_line2", "city", "state", "pincode", "country"],
                as_dict=True,
            )
            if not ad or ad.get("disabled"):
                continue
            if (ad.address_type or "").lower() == "shipping":
                chosen = ad
                break
            if not chosen:
                chosen = ad
        if chosen:
            address_name = chosen.name
            shipping_address = ", ".join(
                filter(
                    None,
                    [
                        chosen.address_line1,
                        chosen.address_line2,
                        chosen.city,
                        chosen.state,
                        chosen.pincode,
                        chosen.country,
                    ],
                )
            )
    if not full_name:
        full_name = email.split("@")[0] if email else user
    return {
        "logged_in": True,
        "user": user,
        "full_name": full_name,
        "email": email if "@" in email else "",
        "phone": phone,
        "customer": customer,
        "address_name": address_name,
        "shipping_address": shipping_address,
        "login_url": "/login?redirect-to=/cart",
    }


@frappe.whitelist(allow_guest=True)
def get_buyer_profile():
    return _buyer_profile(require=False)


@frappe.whitelist(allow_guest=True)
def get_checkout_options():
    """Public storefront config so cart/shop honor Magala Checkout Settings."""
    s = _checkout_settings()
    enable_addispay = True if not s else bool(cint(s.enable_addispay))
    enable_bank = True if not s else bool(cint(s.enable_bank_transfer))
    enable_cod = True if not s else bool(cint(s.enable_cod))
    default = (getattr(s, "default_payment_method", None) if s else None) or "AddisPay"
    if default == "AddisPay" and not enable_addispay:
        default = "Bank Transfer" if enable_bank else "Cash upon Delivery"
    return {
        "enable_addispay": enable_addispay,
        "enable_bank_transfer": enable_bank,
        "enable_cod": enable_cod,
        "show_payment_badges": True if not s else bool(cint(s.show_payment_badges)),
        "default_payment_method": default,
        "currency": (getattr(s, "currency", None) if s else None) or "ETB",
        "addispay_label": (getattr(s, "addispay_label", None) if s else None) or "AddisPay Payment",
        "addispay_description": (getattr(s, "addispay_description", None) if s else None)
        or "Cards, Telebirr, CBE Birr, and bank apps on a secure AddisPay page.",
        "bank_label": (getattr(s, "bank_label", None) if s else None) or "Bank Transfer",
        "bank_description": (getattr(s, "bank_description", None) if s else None)
        or "Pay to the accounts below, then submit your bank reference.",
        "cod_label": (getattr(s, "cod_label", None) if s else None) or "Cash upon Delivery",
        "cod_description": (getattr(s, "cod_description", None) if s else None)
        or "Pay the courier in cash when your order arrives.",
        "bank_accounts": get_bank_accounts(),
        "sandbox": bool(cint(getattr(s, "addispay_sandbox_mode", 1))) if s else True,
    }


@frappe.whitelist(allow_guest=True)
def get_cart():
    merged_rows = _merged_cart_rows()
    _set_cart({"items": merged_rows})
    items = []
    total = 0
    for row in merged_rows:
        try:
            meta = _item_meta(row["item_code"])
        except Exception:
            continue
        qty = flt(row.get("qty") or 1)
        amount = qty * flt(meta["rate"])
        total += amount
        items.append({**meta, "qty": qty, "amount": amount})
    opts = get_checkout_options()
    buyer = _buyer_profile(require=False)
    return {
        "items": items,
        "total": total,
        "currency": opts.get("currency") or "ETB",
        "count": int(sum(flt(i.get("qty") or 0) for i in items)),
        "cod_available": bool(items) and all(i.get("cod_eligible") for i in items) and opts.get("enable_cod"),
        "options": opts,
        "logged_in": buyer.get("logged_in"),
        "buyer": buyer,
    }


@frappe.whitelist(allow_guest=True)
def add_to_cart(item_code, qty=1):
    _require_login()
    qty = flt(qty or 1)
    if qty <= 0:
        frappe.throw(_("Quantity must be greater than zero"))
    meta = _item_meta(item_code)
    if meta["is_job"]:
        frappe.throw(_("Jobs cannot be added to the shopping cart. Please use Apply Now."))
    cart = _get_cart()
    found = False
    for row in cart["items"]:
        if row["item_code"] == item_code:
            row["qty"] = flt(row.get("qty") or 0) + qty
            found = True
            break
    if not found:
        cart["items"].append({"item_code": item_code, "qty": qty})
    _set_cart(cart)
    _webshop_update(item_code, next((r["qty"] for r in cart["items"] if r["item_code"] == item_code), qty))
    return get_cart()


@frappe.whitelist(allow_guest=True)
def update_cart_qty(item_code, qty):
    qty = flt(qty or 0)
    cart = _get_cart()
    if qty <= 0:
        cart["items"] = [r for r in cart["items"] if r.get("item_code") != item_code]
    else:
        for row in cart["items"]:
            if row["item_code"] == item_code:
                row["qty"] = qty
                break
    _set_cart(cart)
    _webshop_update(item_code, qty)
    return get_cart()


@frappe.whitelist(allow_guest=True)
def clear_cart():
    _set_cart({"items": []})
    _clear_webshop_quotation()
    return get_cart()


def _ensure_customer(email, customer_name, phone):
    email = (email or "").strip()
    if email and frappe.db.exists("Customer", {"email_id": email}):
        return frappe.db.get_value("Customer", {"email_id": email}, "name")
    if email and frappe.db.exists("Customer", email):
        return email
    name = (customer_name or email or "Magala Guest").strip()
    doc = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": name,
            "customer_type": "Individual",
            "customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual",
            "territory": frappe.db.get_single_value("Selling Settings", "territory") or "Ethiopia",
            "email_id": email,
            "mobile_no": phone,
        }
    )
    try:
        doc.insert(ignore_permissions=True)
    except Exception:
        existing = frappe.db.get_value("Customer", {"customer_name": name}, "name")
        if existing:
            return existing
        raise
    return doc.name


def _ensure_mode_of_payment(name, type_="Cash"):
    if frappe.db.exists("Mode of Payment", name):
        return name
    mop = frappe.get_doc(
        {
            "doctype": "Mode of Payment",
            "mode_of_payment": name,
            "type": type_,
            "enabled": 1,
        }
    )
    mop.insert(ignore_permissions=True)
    return name


def _create_sales_order(company, customer, items, payment_method, delivery_address, phone):
    delivery_date = getdate(nowdate())
    so_items = []
    for it in items:
        so_items.append(
            {
                "item_code": it["item_code"],
                "item_name": it["item_name"],
                "qty": it["qty"],
                "rate": it["rate"],
                "uom": it.get("uom") or "Nos",
                "conversion_factor": 1,
                "delivery_date": delivery_date,
            }
        )
    so = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "company": company,
            "customer": customer,
            "transaction_date": nowdate(),
            "delivery_date": delivery_date,
            "order_type": "Sales",
            "currency": get_checkout_options().get("currency") or "ETB",
            "selling_price_list": frappe.db.get_value("Company", company, "default_selling_price_list")
            or frappe.db.get_single_value("Selling Settings", "selling_price_list")
            or "Standard Selling",
            "items": so_items,
            "po_no": payment_method,
        }
    )
    if phone:
        so.contact_mobile = phone
    try:
        so.insert(ignore_permissions=True)
        so.submit()
    except Exception as e:
        frappe.logger("ethiobiz").error(f"Magala SO submit failed, leaving draft: {e}")
        if so.name:
            try:
                so.db_set("status", so.status)
            except Exception:
                pass
    return so


@frappe.whitelist(allow_guest=True)
def place_order(
    payment_method,
    customer_name=None,
    email=None,
    phone=None,
    delivery_address=None,
    bank_name=None,
    reference_no=None,
    paid_by=None,
):
    payment_method = cstr(payment_method).strip()
    allowed = {
        "Cash upon Delivery": "Cash upon Delivery",
        "COD": "Cash upon Delivery",
        "Bank Transfer": "Bank Transfer",
        "AddisPay": "AddisPay",
        "AddisPay Payment": "AddisPay",
    }
    if payment_method not in allowed:
        frappe.throw(_("Invalid payment method"))
    payment_method = allowed[payment_method]
    buyer = _buyer_profile(require=True)
    customer_name = buyer.get("full_name")
    email = buyer.get("email")
    phone = buyer.get("phone")
    if not delivery_address:
        delivery_address = buyer.get("shipping_address")
    opts = get_checkout_options()
    if not phone:
        phone = cstr(getattr(_checkout_settings(), "addispay_default_phone", None) or "")
    if payment_method == "AddisPay" and not opts.get("enable_addispay"):
        frappe.throw(_("AddisPay is disabled in Magala Checkout Settings"))
    if payment_method == "Bank Transfer" and not opts.get("enable_bank_transfer"):
        frappe.throw(_("Bank Transfer is disabled in Magala Checkout Settings"))
    if payment_method == "Cash upon Delivery" and not opts.get("enable_cod"):
        frappe.throw(_("Cash upon Delivery is disabled in Magala Checkout Settings"))

    cart = get_cart()
    items = cart.get("items") or []
    if not items:
        frappe.throw(_("Your cart is empty"))

    email = cstr(email or "").strip()
    if not email or "@" not in email:
        frappe.throw(_("Your user account has no email. Update your profile, then try again."))
    if payment_method == "Cash upon Delivery":
        if not delivery_address:
            frappe.throw(_("Add a shipping address on your Customer / Address record before using Cash upon Delivery."))
        if not cart.get("cod_available"):
            frappe.throw(_("Cash upon Delivery is only available for products and food items"))

    customer = buyer.get("customer") or _ensure_customer(email, customer_name or email.split("@")[0], phone)
    _link_user_to_customer(frappe.session.user, customer, email, phone, customer_name)
    grouped = defaultdict(list)
    for it in items:
        grouped[it["company"]].append(it)

    mop_map = {
        "Cash upon Delivery": ("Cash upon Delivery", "Cash"),
        "Bank Transfer": ("Bank Transfer", "Bank"),
        "AddisPay": ("AddisPay", "Bank"),
    }
    mop_name, mop_type = mop_map[payment_method]
    _ensure_mode_of_payment(mop_name, mop_type)

    tx_ref = f"MAGALA-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}-{frappe.generate_hash(length=6)}"
    payment = frappe.get_doc(
        {
            "doctype": "Magala Shop Payment",
            "payment_method": payment_method,
            "status": "Pending",
            "payment_status": "Pending",
            "tx_ref": tx_ref,
            "customer": customer,
            "customer_name": customer_name or customer,
            "email": email,
            "phone": phone,
            "delivery_address": delivery_address,
            "amount": flt(cart["total"]),
            "currency": "ETB",
            "company": _parent_company(),
            "mode_of_payment": mop_name,
            "bank_name": bank_name,
            "reference_no": reference_no,
            "paid_by": paid_by or customer_name,
        }
    )

    sales_orders = []
    for company, company_items in grouped.items():
        try:
            so = _create_sales_order(
                company, customer, company_items, payment_method, delivery_address, phone
            )
            amt = sum(flt(i["qty"]) * flt(i["rate"]) for i in company_items)
            payment.append(
                "sales_orders",
                {"sales_order": so.name, "company": company, "amount": amt},
            )
            sales_orders.append({"name": so.name, "company": company, "amount": amt, "docstatus": so.docstatus})
        except Exception as e:
            frappe.logger("ethiobiz").error(f"Magala SO create failed for {company}: {e}")
            payment.notes = (payment.notes or "") + f"\nSO failed for {company}: {e}"

    payment.insert(ignore_permissions=True)
    frappe.db.commit()

    result = {
        "payment": payment.name,
        "tx_ref": tx_ref,
        "sales_orders": sales_orders,
        "amount": flt(payment.amount),
        "payment_method": payment_method,
        "bank_accounts": get_bank_accounts() if payment_method == "Bank Transfer" else [],
    }

    if payment_method == "AddisPay":
        from bizmarketing.api.addispay import initiate_shop_payment

        ap = initiate_shop_payment(
            tx_ref=tx_ref,
            amount=payment.amount,
            customer_email=email,
            customer_name=customer_name or customer,
            phone_number=phone,
            description=f"Magala {tx_ref}",
        )
        payment.db_set("addispay_uuid", ap.get("uuid"))
        payment.db_set("addispay_nonce", ap.get("nonce"))
        frappe.db.commit()
        result["checkout_url"] = ap.get("checkout_url")
        result["uuid"] = ap.get("uuid")
        result["redirect"] = ap.get("redirect")
        result["status"] = "redirect"
    else:
        result["status"] = "placed"
        result["message"] = (
            "Order placed. Pay cash to the courier."
            if payment_method == "Cash upon Delivery"
            else "Order placed. Submit your bank reference so we can confirm funds."
        )

    clear_cart()
    return result


@frappe.whitelist(allow_guest=True)
def submit_bank_reference(tx_ref, bank_name, reference_no, paid_by=None):
    name = frappe.db.get_value("Magala Shop Payment", {"tx_ref": tx_ref}, "name")
    if not name:
        frappe.throw(_("Payment not found"))
    doc = frappe.get_doc("Magala Shop Payment", name)
    if doc.payment_method != "Bank Transfer":
        frappe.throw(_("This order is not a bank transfer"))
    doc.db_set("bank_name", bank_name)
    doc.db_set("reference_no", reference_no)
    if paid_by:
        doc.db_set("paid_by", paid_by)
    doc.db_set("payment_status", "Pending")
    frappe.db.commit()
    return {"success": True, "payment": doc.name}


def _is_admin():
    if frappe.session.user == "Administrator":
        return True
    return bool({"System Manager", "Accounts Manager"}.intersection(frappe.get_roles()))


@frappe.whitelist()
def approve_bank_payment(payment_name, confirmed=0):
    if not _is_admin():
        frappe.throw(_("Not permitted"))
    if not cint(confirmed):
        frappe.throw(_("Confirm that funds were received"))
    doc = frappe.get_doc("Magala Shop Payment", payment_name)
    if doc.payment_status == "Approved":
        return {"success": True, "message": "Already approved"}
    _mark_paid(doc)
    doc.db_set("payment_status", "Approved")
    doc.db_set("status", "Completed")
    doc.db_set("approved_by", frappe.session.user)
    doc.db_set("approved_on", now_datetime())
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def reject_bank_payment(payment_name, reason):
    if not _is_admin():
        frappe.throw(_("Not permitted"))
    if not cstr(reason).strip():
        frappe.throw(_("Reason is required"))
    doc = frappe.get_doc("Magala Shop Payment", payment_name)
    doc.db_set("payment_status", "Rejected")
    doc.db_set("status", "Failed")
    doc.db_set("admin_remarks", reason)
    frappe.db.commit()
    return {"success": True}


def _mark_paid(doc):
    for row in doc.sales_orders or []:
        so_name = row.sales_order
        if not so_name or not frappe.db.exists("Sales Order", so_name):
            continue
        so = frappe.get_doc("Sales Order", so_name)
        try:
            so.db_set("advance_paid", flt(row.amount or so.grand_total))
        except Exception:
            pass
        try:
            if so.docstatus == 1 and frappe.db.exists("DocType", "Payment Entry"):
                pe = frappe.get_doc(
                    {
                        "doctype": "Payment Entry",
                        "payment_type": "Receive",
                        "party_type": "Customer",
                        "party": doc.customer,
                        "company": so.company,
                        "paid_amount": flt(row.amount or so.grand_total),
                        "received_amount": flt(row.amount or so.grand_total),
                        "mode_of_payment": doc.mode_of_payment,
                        "reference_no": doc.tx_ref,
                        "reference_date": nowdate(),
                    }
                )
                pe.insert(ignore_permissions=True)
        except Exception as e:
            frappe.logger("ethiobiz").error(f"Magala Payment Entry skipped: {e}")


def mark_addispay_success(tx_ref, uuid=None):
    name = frappe.db.get_value("Magala Shop Payment", {"tx_ref": tx_ref}, "name")
    if not name and uuid:
        name = frappe.db.get_value("Magala Shop Payment", {"addispay_uuid": uuid}, "name")
    if not name:
        return False
    doc = frappe.get_doc("Magala Shop Payment", name)
    if doc.status == "Completed" and doc.payment_status == "Approved":
        return True
    if uuid:
        doc.db_set("addispay_uuid", uuid)
    _mark_paid(doc)
    doc.db_set("status", "Completed")
    doc.db_set("payment_status", "Approved")
    doc.db_set("approved_on", now_datetime())
    frappe.db.commit()
    return True


def mark_addispay_failed(tx_ref, uuid=None):
    name = frappe.db.get_value("Magala Shop Payment", {"tx_ref": tx_ref}, "name")
    if not name:
        return False
    doc = frappe.get_doc("Magala Shop Payment", name)
    doc.db_set("status", "Failed")
    frappe.db.commit()
    return True


@frappe.whitelist(allow_guest=True)
def verify_return(tx_ref=None, uuid=None, status=None):
    tx_ref = tx_ref or frappe.form_dict.get("tx_ref")
    uuid = uuid or frappe.form_dict.get("uuid")
    status = cstr(status or frappe.form_dict.get("status")).lower()
    if not tx_ref:
        frappe.throw(_("Missing tx_ref"))
    failed = status in ("failed", "fail", "error", "cancelled", "canceled")
    if failed:
        mark_addispay_failed(tx_ref, uuid)
        return {"status": "failed", "tx_ref": tx_ref}
    mark_addispay_success(tx_ref, uuid)
    name = frappe.db.get_value("Magala Shop Payment", {"tx_ref": tx_ref}, "name")
    doc = frappe.get_doc("Magala Shop Payment", name) if name else None
    return {
        "status": "success",
        "tx_ref": tx_ref,
        "payment": name,
        "amount": flt(doc.amount) if doc else 0,
        "payment_method": doc.payment_method if doc else "AddisPay",
    }
