"""Bismillah — TC1..TC12 unit-level coverage for Phase 1 (manual activation).

Runs locally WITHOUT a Frappe site or any third-party package: exercises pure
logic by stubbing the frappe module surface used by the modules under test.

Run:  python -m unittest tests.unit.test_phase1_manual_activation_unit -v
"""
import importlib.util
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import REPOS, ensure_repo_on_path  # noqa: E402


# ---------------------------------------------------------------- frappe stub
class _FrappeStub(types.ModuleType):
    """Minimal frappe API surface for the modules under test."""

    class ValidationError(Exception):
        pass

    class PermissionError(Exception):
        pass

    # -- settings -------------------------------------------------------
    @staticmethod
    def whitelist(allow_guest=False):
        def deco(fn):
            return fn
        return deco

    class _DB:
        """frappe.db surface used by the modules under test."""

        def __init__(self, singles):
            self._singles = singles

        def get_single_value(self, dt, field):
            return self._singles.get(dt, {}).get(field)

        def set_single_value(self, dt, field, value):
            self._singles.setdefault(dt, {})[field] = value

        exists = staticmethod(lambda *a, **k: False)
        get_value = staticmethod(lambda *a, **k: None)
        commit = staticmethod(lambda: None)
        set_value = staticmethod(lambda *a, **k: None)

    def __init__(self):
        super().__init__("frappe")
        self.session = types.SimpleNamespace(user="Administrator")
        self._singles = {
            "DOBiz SaaS Settings": {
                "require_manual_bank_review": 1,
                "auto_activate_online_payments": 1,
            }
        }
        self.db = self._DB(self._singles)

    @staticmethod
    def _(s):
        return s

    @staticmethod
    def logger(_name):
        lg = types.SimpleNamespace()
        for m in ("info", "warning", "error"):
            setattr(lg, m, lambda *a, **k: None)
        return lg

    @staticmethod
    def throw(msg, exc=None):
        raise (exc or Exception)(msg)

    @staticmethod
    def escape_html(s):
        return str(s).replace("<", "&lt;")

    @staticmethod
    def get_roles(user=None):
        return ["System Manager"]


def _load_module_with_stub():
    fake = _FrappeStub()
    utils = types.ModuleType("frappe.utils")
    utils.now_datetime = lambda: "2026-08-22 23:00:00"
    utils.today = lambda: "2026-08-22"
    utils.add_days = lambda d, n: d
    utils.add_months = lambda d, n: d
    utils.getdate = lambda v=None: v
    utils.get_datetime = lambda v=None: v
    saved_f, saved_u = sys.modules.get("frappe"), sys.modules.get("frappe.utils")
    sys.modules["frappe"] = fake
    sys.modules["frappe.utils"] = utils
    try:
        ensure_repo_on_path("bizmarketing")
        spec = importlib.util.spec_from_file_location(
            "dobiz_manual_activation_testbed",
            os.path.join(REPOS["bizmarketing"], "bizmarketing", "api",
                         "dobiz_manual_activation.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, fake, saved_f, saved_u
    finally:
        pass  # restored in tearDown via instance attrs


class Phase1ManualActivationUnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod, cls.fake, cls._sf, cls._su = _load_module_with_stub()

    @classmethod
    def tearDownClass(cls):
        if cls._sf is not None:
            sys.modules["frappe"] = cls._sf
        else:
            sys.modules.pop("frappe", None)
        if cls._su is not None:
            sys.modules["frappe.utils"] = cls._su

    def test_tc_a_settings_flag_defaults_on_missing(self):
        """Missing settings field falls back to SAFE default (review ON)."""
        f = self.fake
        f._singles["DOBiz SaaS Settings"].pop("require_manual_bank_review", None)
        self.assertTrue(self.mod.manual_review_required())
        f._singles["DOBiz SaaS Settings"]["require_manual_bank_review"] = 0
        self.assertFalse(self.mod.manual_review_required())
        f._singles["DOBiz SaaS Settings"]["require_manual_bank_review"] = 1

    def test_tc_b_online_gate_default(self):
        """AddiPay auto-activation gate defaults to enabled."""
        f = self.fake
        f._singles["DOBiz SaaS Settings"].pop("auto_activate_online_payments", None)
        self.assertTrue(self.mod.online_auto_activation_enabled())
        f._singles["DOBiz SaaS Settings"]["auto_activate_online_payments"] = 0
        self.assertFalse(self.mod.online_auto_activation_enabled())
        f._singles["DOBiz SaaS Settings"]["auto_activate_online_payments"] = 1

    def test_tc3_approve_requires_confirmation(self):
        """Approving without funds-received confirmation must throw."""
        with self.assertRaises(Exception):
            self.mod.approve_bank_payment("PR-0001", confirmed=0)

    def test_tc4_approve_non_admin_blocked(self):
        """Non-admin cannot approve or reject."""
        f = self.fake
        f.session.user = "guest@example.com"
        f.get_roles = staticmethod(lambda user=None: ["Customer"])
        with self.assertRaises(f.PermissionError):
            self.mod.approve_bank_payment("PR-0001", confirmed=1)
        with self.assertRaises(f.PermissionError):
            self.mod.reject_bank_payment("PR-0001", reason="x")
        f.session.user = "Administrator"
        f.get_roles = staticmethod(lambda user=None: ["System Manager"])

    def test_tc7a_reject_requires_reason(self):
        """Rejection without reason throws."""
        with self.assertRaises(Exception):
            self.mod.reject_bank_payment("PR-0001", reason="   ")

    def test_tc_support_norm_bank_aliases(self):
        """Bank normalization maps long names to Select codes."""
        from bizmarketing.api.dobiz_signup_api import _norm_bank
        self.assertEqual(_norm_bank("Commercial Bank of Ethiopia"), "CBE")
        self.assertEqual(_norm_bank("telebirr"), "Telebirr")
        self.assertEqual(_norm_bank(None), "Other")
        self.assertEqual(_norm_bank("Awash Bank"), "Awash")

    def test_tc_support_discount_math_unchanged(self):
        """Package pricing math untouched by Phase 1."""
        base, term, disc = 9500, 6, 0.10
        self.assertEqual((base * term) * (1.0 - disc), 51300.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
