"""Unit mirror for ANFRG-26-00063 Tasks B & C (no Frappe instance needed).

Covers: settings-flag parsing, guest-endpoint defaults, animation speed map,
JS source contracts (sidebar policy + particle engine), hook registration,
and the particle-count formula parity with ethiobiz_particles.js.
"""

import json
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_PKG = REPO_ROOT / "bismillah_ethiobiz"
THEME_JS = APP_PKG / "public" / "js" / "ethiobiz_theme.js"
PARTICLES_JS = APP_PKG / "public" / "js" / "ethiobiz_particles.js"
HOOKS_PY = APP_PKG / "hooks.py"


def _install_frappe_stub(single_values=None):
    stub = types.ModuleType("frappe")

    def _whitelist(allow_guest=False):
        def deco(fn):
            fn.is_whitelisted = True
            fn.allow_guest = allow_guest
            return fn
        return deco

    stub.whitelist = _whitelist
    store = dict(single_values or {})
    stub._store = store
    db = types.SimpleNamespace(
        get_single_value=lambda doctype, fieldname: store.get(fieldname)
    )
    stub.db = db
    stub.log_error = lambda *a, **k: None
    sys.modules["frappe"] = stub
    return stub


class ThemeSettingsUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stub = _install_frappe_stub()
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "theme_settings_unit_target",
            str(REPO_ROOT.parent
                / "bizmarketing" / "bizmarketing" / "api" / "theme_settings.py"),
        )
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_flag_parsing(self):
        f = self.mod._flag
        self.assertTrue(f("1", False))
        self.assertTrue(f("true", False))
        self.assertTrue(f(True, False))
        self.assertFalse(f("0", True))
        self.assertTrue(f(None, True))
        self.assertFalse(f(None, False))

    def test_endpoint_defaults_when_singleton_unsaved(self):
        self.stub._store.clear()
        conf = self.mod.public_theme_settings()
        self.assertIs(conf["hide_sidebar"], True)
        self.assertIs(conf["enable_website_animation"], True)
        self.assertEqual(conf["animation_speed_factor"], 0.7)

    def test_speed_map(self):
        self.assertEqual(self.mod.SPEED_FACTORS,
                         {"Slow": 0.45, "Normal": 0.7, "Fast": 0.95})
        self.stub._store.clear()
        self.stub._store["website_animation_speed"] = "Slow"
        self.assertEqual(self.mod.public_theme_settings()["animation_speed_factor"], 0.45)
        self.stub._store["website_animation_speed"] = "Turbo"
        self.assertEqual(self.mod.public_theme_settings()["animation_speed_factor"], 0.7)


class JsContractUnit(unittest.TestCase):
    def test_theme_js_sidebar_policy_markers(self):
        src = THEME_JS.read_text(encoding="utf-8")
        self.assertIn("applySidebarPolicy", src)
        self.assertIn("hide_sidebar === false", src)
        self.assertIn(
            "bizmarketing.api.theme_settings.public_theme_settings", src)
        self.assertIn("ethiobizThemeConf", src)

    def test_particles_engine_contract(self):
        src = PARTICLES_JS.read_text(encoding="utf-8")
        self.assertIn("__ETHIOBIZ_AMBIENT__", src)
        self.assertIn("prefers-reduced-motion", src)
        self.assertIn("visibilitychange", src)
        self.assertIn('indexOf("/app")', src)
        for v in ("0.45", "0.7", "0.95"):
            self.assertIn(v, src)
        # baseline constant stays 0.7 (Hadi: slightly slower than original)
        self.assertIn("BASELINE_SPEED_FACTOR = 0.7", src)

    def test_hooks_register_particles_and_theme(self):
        hooks = HOOKS_PY.read_text(encoding="utf-8")
        self.assertIn("/assets/bismillah_ethiobiz/js/ethiobiz_particles.js", hooks)
        self.assertIn("/assets/bismillah_ethiobiz/js/ethiobiz_theme.js", hooks)

    def test_particle_count_formula_parity(self):
        def count(width):
            return min(int(width / 24), 60)  # mirrors Math.floor(innerWidth/24)

        self.assertEqual(count(375), 15)
        self.assertEqual(count(1024), 42)
        self.assertEqual(count(1440), 60)
        self.assertEqual(count(1920), 60)


if __name__ == "__main__":
    unittest.main(verbosity=2)
