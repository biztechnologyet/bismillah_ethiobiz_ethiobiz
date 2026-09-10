"""Unit tests for ethiobiz_identity (no live site required).

Run:  python -m unittest tests.unit.test_ethiobiz_identity_unit -v
"""
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import ensure_repo_on_path  # noqa: E402

ensure_repo_on_path("bismillah_ethiobiz")


def _install_frappe_stub(user="Administrator", companies=None, customers=None, users=None):
    companies = set(companies or ["Acme Clinic"])
    customers = dict(customers or {})
    users = dict(users or {
        "Administrator": {"email": "admin@ethiobiz.et", "full_name": "Admin", "mobile_no": "0911000000", "phone": ""},
        "buyer@example.com": {"email": "buyer@example.com", "full_name": "Buyer One", "mobile_no": "0911222333", "phone": ""},
    })

    class PermissionError(Exception):
        pass

    class _DB:
        def exists(self, dt, name=None):
            if dt == "DocType":
                return True
            if dt == "Company":
                return name in companies
            if dt == "Customer":
                if isinstance(name, dict):
                    return False
                return name in customers
            if dt == "User":
                return name in users
            return False

        def get_value(self, dt, name, field=None):
            if dt == "User":
                rec = users.get(name) or {}
                return rec.get(field)
            if dt == "Customer":
                if isinstance(name, dict):
                    email = name.get("email_id")
                    for k, v in customers.items():
                        if v.get("email_id") == email:
                            return k
                    cname = name.get("customer_name")
                    for k, v in customers.items():
                        if v.get("customer_name") == cname:
                            return k
                    return None
                rec = customers.get(name) or {}
                return rec.get(field) if field else name
            return None

        def get_single_value(self, dt, field):
            return None

    class _Doc:
        def __init__(self, d):
            self._d = d
            self.name = d.get("customer_name") or "CUST-NEW"
            self.flags = types.SimpleNamespace()

        def insert(self, ignore_permissions=False):
            customers[self.name] = dict(self._d)
            customers[self.name]["email_id"] = self._d.get("email_id")
            customers[self.name]["customer_name"] = self._d.get("customer_name")
            return self

    fr = types.ModuleType("frappe")
    fr.PermissionError = PermissionError
    fr.session = types.SimpleNamespace(user=user)
    fr.db = _DB()
    fr._ = lambda s: s

    def throw(msg, exc=None):
        raise (exc or Exception)(msg)

    fr.throw = throw
    fr.get_doc = lambda d: _Doc(d)
    sys.modules["frappe"] = fr
    return fr, customers


class IdentityTests(unittest.TestCase):
    def setUp(self):
        for k in list(sys.modules):
            if k == "frappe" or k.startswith("bismillah_ethiobiz.ethiobiz_identity"):
                sys.modules.pop(k, None)

    def test_guest_require_login_throws(self):
        _install_frappe_stub(user="Guest")
        from bismillah_ethiobiz.ethiobiz_identity import require_login
        import frappe
        with self.assertRaises(frappe.PermissionError):
            require_login()

    def test_authed_user_passes_require_login(self):
        _install_frappe_stub(user="buyer@example.com")
        from bismillah_ethiobiz.ethiobiz_identity import require_login
        self.assertEqual(require_login(), "buyer@example.com")

    def test_get_or_create_customer_creates(self):
        fr, customers = _install_frappe_stub(user="buyer@example.com")
        from bismillah_ethiobiz.ethiobiz_identity import get_or_create_customer_for_user
        name = get_or_create_customer_for_user("buyer@example.com")
        self.assertEqual(name, "Buyer One")
        self.assertIn("Buyer One", customers)

    def test_resolve_company_throws_when_blank(self):
        _install_frappe_stub()
        from bismillah_ethiobiz.ethiobiz_identity import resolve_booking_company
        with self.assertRaises(Exception):
            resolve_booking_company("")

    def test_resolve_company_throws_when_unknown(self):
        _install_frappe_stub(companies=["Acme Clinic"])
        from bismillah_ethiobiz.ethiobiz_identity import resolve_booking_company
        with self.assertRaises(Exception):
            resolve_booking_company("Ghost Co")

    def test_resolve_company_ok(self):
        _install_frappe_stub(companies=["Acme Clinic"])
        from bismillah_ethiobiz.ethiobiz_identity import resolve_booking_company
        self.assertEqual(resolve_booking_company("Acme Clinic"), "Acme Clinic")


if __name__ == "__main__":
    unittest.main()
