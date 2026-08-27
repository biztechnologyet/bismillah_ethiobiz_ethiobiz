"""
P4 UI/UX TEST SUITE — TC35-TC40
Tests for Workstreams A-L: theme CSS, chat widget, particles, inline AI, filters, account menu.
Run: bench --site ethiobiz.et execute bismillah_ethiobiz.tests.test_p4_ui_ux
"""
import frappe
import json
import requests

SITE = "https://ethiobiz.et"
API = f"{SITE}/api/method"

def _get(path, **kwargs):
    """Guest-safe GET request."""
    return requests.get(f"{API}/{path}", verify=False, timeout=30, **kwargs)

def _auth_get(path, user, pwd, **kwargs):
    """Authenticated GET via session."""
    s = requests.Session()
    s.get(f"{SITE}/login", verify=False)
    s.post(f"{SITE}/api/method/login", data={"usr": user, "pwd": pwd}, verify=False)
    return s.get(f"{API}/{path}", verify=False, timeout=30, **kwargs)


def test_tc35_theme_css_served():
    """TC35: Theme CSS is served correctly with all P4 markers."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/css/ethiobiz_theme.css", verify=False, timeout=30)
    assert r.status_code == 200, f"CSS not served: {r.status_code}"
    css = r.text
    assert len(css) > 30000, f"CSS too small: {len(css)} bytes"
    assert "P4-B:" in css, "Missing P4-B marker (full-width headers)"
    assert "P4-C:" in css, "Missing P4-C marker (collapsible filters)"
    assert "P4-L:" in css, "Missing P4-L marker (account menu cleanup)"
    assert '[data-theme="light"]' in css, "Missing light-theme guards"
    print("TC35 PASS: Theme CSS served with all P4 markers")


def test_tc36_light_dark_inputs():
    """TC36: Input fields have correct light/dark variants."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/css/ethiobiz_theme.css", verify=False, timeout=30)
    css = r.text
    # Dark variant exists
    assert 'body[data-route*="app"]:not([data-theme="light"]) input.form-control' in css, \
        "Missing dark-mode input rule"
    # Light variant exists
    assert 'body[data-route*="app"][data-theme="light"] input.form-control' in css, \
        "Missing light-mode input rule"
    print("TC36 PASS: Light/dark input variants present")


def test_tc37_page_head_full_width():
    """TC37: Page head title is full-width via P4-B CSS."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/css/ethiobiz_theme.css", verify=False, timeout=30)
    css = r.text
    assert ".page-head-content" in css, "Missing page-head-content rule"
    assert 'flex-direction: column' in css, "Missing flex-direction column"
    assert ".page-title" in css and "width: 100%" in css, "Missing page-title full width"
    assert ".page-actions" in css and "justify-content: flex-end" in css, "Missing page-actions right-align"
    assert ".page-head .container" in css and "max-width: 100%" in css, "Missing container override"
    print("TC37 PASS: Page head full-width CSS rules present")


def test_tc38_chat_widget_config():
    """TC38: Chat widget config API returns correct data."""
    r = _get("bismillah_ethiobiz.api.get_chat_config")
    assert r.status_code == 200, f"Chat config API failed: {r.status_code}"
    data = r.json()["message"]
    assert data["enabled"] is True, "Chat widget not enabled"
    title = data.get("widget_title", "")
    assert "Hadeeda" in title or "HADEEDA" in title or "hadeeda" in title.lower(), f"Wrong title: {title}"
    assert data["widget_primary_color"] == "#1FB6AE", "Wrong primary color"
    assert "webhook_url" in data and data["webhook_url"], "Missing webhook URL"
    print("TC38 PASS: Chat widget config correct")


def test_tc39_chat_js_served():
    """TC39: Chat JS served with correct HADEEDA BizAi label."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_chat.js", verify=False, timeout=30)
    assert r.status_code == 200, f"Chat JS not served: {r.status_code}"
    js = r.text
    assert "HADEEDA BizAi" in js, "Missing HADEEDA BizAi label"
    assert "P4-E: LIGHT-MODE CHAT" in js, "Missing light-mode chat CSS"
    assert "flex-direction: row" in js, "Missing footer flex-direction row"
    assert "min-width: 40px" in js, "Missing textarea min-width fix"
    assert "box-sizing: border-box" in js, "Missing box-sizing fix"
    print("TC39 PASS: Chat JS served with correct fixes")


def test_tc40_particles_desk_support():
    """TC40: Particles JS supports desk (no /app exclusion), has light gradients."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_particles.js", verify=False, timeout=30)
    assert r.status_code == 200, f"Particles JS not served: {r.status_code}"
    js = r.text
    assert 'indexOf("/app")' not in js, "Still has /app exclusion"
    assert "data-theme" in js and "light" in js, "Missing light-mode gradient variants"
    assert "aurora-blob-1" in js, "Missing aurora blob definitions"
    print("TC40 PASS: Particles JS desk support + light gradients")


def test_tc35b_hooks_include_all():
    """TC35b: Hooks include all JS/CSS for both desk and website."""
    hooks_path = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/hooks.py"
    # Read from server via API (indirect check)
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_desk_filters.js", verify=False, timeout=30)
    assert r.status_code == 200, "Desk filters JS not served"
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js", verify=False, timeout=30)
    assert r.status_code == 200, "Inline AI JS not served"
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_particles.js", verify=False, timeout=30)
    assert r.status_code == 200, "Particles JS not served"
    print("TC35b PASS: All JS assets served")


def test_chat_light_mode_api():
    """Test: get_user_particle_pref API works for guests."""
    r = _get("bismillah_ethiobiz.api.get_user_particle_pref")
    assert r.status_code == 200, f"Particle pref API failed: {r.status_code}"
    data = r.json()["message"]
    assert "enabled" in data, "Missing enabled field"
    print("PASS: Particle pref API returns correct data")


def run_all():
    """Run all P4 tests."""
    frappe.connect()
    tests = [
        test_tc35_theme_css_served,
        test_tc35b_hooks_include_all,
        test_tc36_light_dark_inputs,
        test_tc37_page_head_full_width,
        test_tc38_chat_widget_config,
        test_tc39_chat_js_served,
        test_tc40_particles_desk_support,
        test_chat_light_mode_api,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n=== P4 SUITE: {passed} PASS, {failed} FAIL, {len(tests)} TOTAL ===")
    frappe.destroy()
    return failed == 0


if __name__ == "__main__":
    run_all()
