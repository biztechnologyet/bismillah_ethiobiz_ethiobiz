# 40. EthioBiz Omnichannel Identity, Universal Booking & 5 Pillars Stabilization

**Bismallah Ar-Rahman Ar-Rahim**  
**Date**: September 4, 2026  
**System**: EthioBiz.et Enterprise Cloud Ecosystem  
**Author**: Antigravity Enterprise Agent System  

---

## 1. Executive Summary

This expert specification documents the architectural enhancements, bug resolutions, and system hardening performed across the EthioBiz.et multi-industry platform:
1. **Universal User, Customer & Patient Identity Auto-Registration Engine** (`ethiobiz_identity.py`).
2. **Resilient Public Booking & Application Endpoints** (`bizbooking_api.py`, `bizhome_api.py`, `bizservice_api.py`, and `bizservice_booking.py`).
3. **Multi-Tier Frontend Modal Controller** for `/bizhome` and universal feeds (supporting Bootstrap 5, Bootstrap 4 jQuery, and pure DOM fallback).
4. **Hero Section 5 Pillars Floating Menu Hover Bridge** (eliminating the mouse hover gap with invisible pointer bridges and grace timers).
5. **10 Verified Industry Routes** returning `HTTP/2 200 OK`.
6. **14-Industry Realistic Data Seeding** (42 Ethiopian enterprise companies and 126 authentic products and services).
7. **Production Deployment & Synchronization Protocols** (Gunicorn `--preload` graceful reloads, Git repository sync, and container persistence).

---

## 2. Universal Identity & Customer Auto-Registration Engine

### 2.1 The Problem
In earlier builds, guest inquiries, service bookings, doctor appointments, and rental lease applications threw `403 PermissionError` or failed because Frappe required an authenticated user or did not automatically bind transactions to ERPNext `Customer` or Healthcare `Patient` records.

### 2.2 The Solution (`ethiobiz_identity.py`)
The universal registration engine `ensure_registered_party(full_name, phone, email, party_type)` provides complete, idempotent, 3-tier identity provisioning:

```python
def ensure_registered_party(full_name=None, phone=None, email=None, party_type="Customer"):
    """
    Guarantees that ANY party interacting with EthioBiz has:
    1. A valid Frappe User (Website User, Role: Customer or Patient)
    2. An ERPNext Customer linked to that user
    3. A Healthcare Patient record if party_type == 'Patient' or Healthcare is active
    """
```

#### Step-by-Step Flow:
1. **Session Check**: If the user is logged in (`frappe.session.user != 'Guest'`), their existing record is resolved and used.
2. **User Auto-Creation**: For guests, a clean phone number (`+251...`) or sanitized email is resolved. If none exists, an email is derived (`user.<slug>.<phone>@ethiobiz.et`). A new `User` is created with:
   - `user_type = "Website User"`
   - `send_welcome_email = 0`
   - Role `"Customer"` added to `user.roles`
3. **ERPNext Customer Binding**:
   - Searches `Customer` by mobile, email, or customer name.
   - If not found, creates `Customer` with `customer_name`, `customer_type="Individual"`, `customer_group="Individual"`, and `territory="Ethiopia"`.
4. **Healthcare Patient Binding**:
   - When `party_type == "Patient"` or during clinical appointments, checks for existing `Patient`.
   - If creating, explicitly sets `invite_user = 0` to prevent collision with already-created Frappe `User`.
   - Automatically links `customer = customer_name` and `user_id = user_name`.
   - Determines gender heuristically (e.g., detecting prefixes `W/ro`, `W/rt`, `Mrs`, `Ms`).

---

## 3. Resilient Booking & Application APIs

### 3.1 Parameter Aliasing & `**kwargs` Tolerance
Web forms, mobile PWAs, and homepage feed cards use varying property names (`customer_name` vs `patient_name` vs `name`; `booking_date` vs `appointment_date` vs `check_in`; `phone` vs `mobile`).

All public endpoints were upgraded to accept optional keyword arguments (`**kwargs`) and alias resolution:

```python
# In create_appointment:
practitioner = practitioner or kwargs.get("doctor") or kwargs.get("doctor_id") or "HLC-PRAC-2026-00001"
date = date or kwargs.get("appointment_date") or str(today())
time_slot = time_slot or kwargs.get("appointment_time") or kwargs.get("time") or "10:00"
patient_name = patient_name or kwargs.get("customer_name") or kwargs.get("name") or kwargs.get("full_name")
patient_phone = patient_phone or kwargs.get("customer_phone") or kwargs.get("phone") or kwargs.get("mobile")

# In book_service:
service_id = service_id or service_name or kwargs.get("service")
b_date = booking_date or date or appointment_date or str(frappe.utils.now_datetime().date())
b_time = booking_time or time_slot or appointment_time or "14:00"

# In book_property_stay:
property_id = property_id or kwargs.get("property") or kwargs.get("property_name")
check_in = check_in or kwargs.get("start_date") or kwargs.get("checkin")
check_out = check_out or kwargs.get("end_date") or kwargs.get("checkout")

# In request_property_lease:
customer_name = customer_name or kwargs.get("applicant_name") or kwargs.get("name")
customer_phone = customer_phone or kwargs.get("applicant_phone") or kwargs.get("phone")
start_date = start_date or kwargs.get("proposed_start_date") or today()
```

### 3.2 Dynamic Slot Conflict & Double-Booking Protection
In `bizservice_api.py`, `validate_time_slot` checks active bookings on that date. It dynamically excludes already-booked slots from `valid_slots`, ensuring clear feedback to the user:
```python
booked = frappe.get_all(
    "BizService Booking",
    filters={"service": listing, "booking_date": date,
             "status": ["not in", ["Cancelled", "No-Show"]]},
    pluck="booking_time"
)
booked_set = set(cstr(b)[:5] for b in booked)
slots = [s for s in slots if s not in booked_set]
valid = req in slots
```

### 3.3 Provider Document Sharing & Error Log Title Limit Fix
In `bizservice_booking.py`, when a guest books a service, Frappe previously threw `No permission to share BizService Booking` and triggered `CharacterLengthExceededError` because `frappe.log_error()` had an unshortened exception message passed as the first positional argument (which Frappe 15 interprets as `title`, capped at 140 chars).

Fixed with:
```python
share_add(self.doctype, self.name, self.practitioner_user, read=1, write=1, submit=1, flags={"ignore_share_permission": True})
# And explicit keyword arguments on log_error:
frappe.log_error(title="BizService Share", message=f"Share failed for {self.name}->{self.practitioner_user}: {e}")
```

---

## 4. Multi-Tier Frontend Modal Architecture (`bizhome.js` & `bizhome.html`)

### 4.1 Root Cause of Modal Failures
Frappe 15 Web serves Bootstrap 4 (`bootstrap-4-web.bundle.js`), whereas Bootstrap 5 syntax (`new bootstrap.Modal()`, `data-bs-toggle`, `data-bs-dismiss`) was used in template markups. This threw:
`TypeError: bootstrap.Modal is not a constructor`

### 4.2 Three-Tier Resilient Controller
Implemented in `bismillah_ethiobiz/public/js/bizhome.js`:

```javascript
window.showBizHomeModal = function(modalId) {
    var modalEl = document.getElementById(modalId);
    if (!modalEl) return;
    
    // Tier 1: Bootstrap 5
    if (window.bootstrap && typeof window.bootstrap.Modal === 'function') {
        var instance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        instance.show();
        return;
    }
    // Tier 2: Bootstrap 4 jQuery
    if (window.jQuery && typeof window.jQuery.fn.modal === 'function') {
        window.jQuery(modalEl).modal('show');
        return;
    }
    // Tier 3: Resilient DOM Fallback
    modalEl.classList.add('show');
    modalEl.style.display = 'block';
    modalEl.removeAttribute('aria-hidden');
    modalEl.setAttribute('aria-modal', 'true');
    document.body.classList.add('modal-open');
    
    // Dynamic Backdrop
    var bd = document.getElementById('bizhome-manual-backdrop');
    if (!bd) {
        bd = document.createElement('div');
        bd.id = 'bizhome-manual-backdrop';
        bd.className = 'modal-backdrop fade show';
        document.body.appendChild(bd);
    }
};
```
Close handlers are attached to:
- `[data-dismiss="modal"]` and `[data-bs-dismiss="modal"]`
- Close buttons (`.btn-close`, `.close`)
- Outside backdrop clicks
- `Escape` key press

---

## 5. Hero Section 5 Pillars Hover Gap Fix

### 5.1 The Root Cause
A visual gap existed between the 5 Pillar trigger button cards (`.pillar-btn`) and the absolute-positioned dropdown listings (`.pillar-dropdown-menu`). When users moved the cursor downward from the button toward the menu items, the pointer crossed a transparent 10–18px dead zone, causing the browser to immediately fire `mouseleave` and hide the menu before the user could click any link.

### 5.2 The Complete Solution

#### 1. CSS Geometry & Invisible Hover Bridge:
```css
/* Position menu overlapping trigger by 6px */
.pillar-dropdown-wrap .pillar-dropdown-menu {
    top: calc(100% - 6px) !important;
    padding-bottom: 12px !important;
    margin-bottom: -12px !important;
}

/* Invisible Pointer Bridge */
.pillar-dropdown-wrap .pillar-dropdown-menu::before {
    content: "" !important;
    position: absolute !important;
    top: -24px !important;
    left: 0 !important;
    right: 0 !important;
    height: 30px !important;
    background: transparent !important;
    pointer-events: auto !important;
    z-index: 100 !important;
}
```

#### 2. JavaScript Grace Engine (450ms Debounce):
```javascript
var dropdownWraps = document.querySelectorAll('.pillar-dropdown-wrap');
dropdownWraps.forEach(function(wrap) {
    var timer = null;
    var menu = wrap.querySelector('.pillar-dropdown-menu');

    function openWrap() {
        if (timer) clearTimeout(timer);
        dropdownWraps.forEach(function(w) { if (w !== wrap) w.classList.remove('is-open'); });
        wrap.classList.add('is-open');
    }

    function closeWrapWithGrace() {
        if (timer) clearTimeout(timer);
        timer = setTimeout(function() {
            wrap.classList.remove('is-open');
        }, 450); // 450ms generous buffer
    }

    wrap.addEventListener('mouseenter', openWrap);
    wrap.addEventListener('mouseleave', closeWrapWithGrace);
    if (menu) {
        menu.addEventListener('mouseenter', openWrap);
        menu.addEventListener('mouseleave', closeWrapWithGrace);
    }
});
```

---

## 6. Verification of 10 Core Industry Routes

All 10 vertical routes are verified returning `HTTP/2 200 OK` via Nginx reverse proxy and Gunicorn backend:

| Vertical Route | Description | HTTP Status |
| :--- | :--- | :--- |
| `/bizhealth` | Telehealth, Doctors, Diagnostics & Clinics | **200 OK** |
| `/bizservice` | Professional, Technical & Creative Services | **200 OK** |
| `/bizhome` | Real Estate, Villa Rentals & Daily Stays | **200 OK** |
| `/bizfix` | Electronics, Appliances & Home Repairs | **200 OK** |
| `/jobs` | Careers, Verified Recruitment & Talents | **200 OK** |
| `/shop` | Magala E-Commerce & Verified Merchants | **200 OK** |
| `/forum` | EthioBiz Community Discussions & Q&A | **200 OK** |
| `/social` | Enterprise Social Feed & Networking | **200 OK** |
| `/bizride` | Logistics, Courier & Mobility Dispatch | **200 OK** |
| `/bizmap` | Interactive Ethiopian Enterprise Geo-Directory | **200 OK** |

---

## 7. Operational Maintenance & Deployment Protocols

### 7.1 Reloading Gunicorn with Preload
In Frappe Docker deployments, Gunicorn runs with `--preload frappe.app:application`.
When Python files are updated on disk:
- Simply restarting Redis or running `clear-cache` does NOT reload python bytecode.
- Run `kill -HUP <gunicorn_master_pid>` on host to gracefully reload workers without interrupting background processes.

### 7.2 Git Synchronization
- **Local Remote**: `https://github.com/biztechnologyet/bismillah_ethiobiz_ethiobiz.git`
- **Server Container App Directory**: `/home/frappe/frappe-bench/apps/bismillah_ethiobiz`
- Always verify container permissions with `chown -R frappe:frappe` if root operations occur.
- Synchronized branch: `origin/main`.

---

**End of Specification 40 - Insha'Allah**
