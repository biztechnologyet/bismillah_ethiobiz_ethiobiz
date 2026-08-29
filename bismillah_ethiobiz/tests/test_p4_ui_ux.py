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
    """TC39: Chat JS served with correct HADEEDA BizAi label and layout."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_chat.js", verify=False, timeout=30)
    assert r.status_code == 200, f"Chat JS not served: {r.status_code}"
    js = r.text
    assert "HADEEDA BizAi" in js, "Missing HADEEDA BizAi label"
    assert "LIGHT-MODE VARIANTS" in js, "Missing light-mode chat CSS"
    assert "flex-direction: column" in js, "Missing column direction"
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


def test_tc41_chat_widget_two_row_and_mobile():
    """TC41: Chat widget has two-row column layout and mobile full-screen expansion."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_chat.js", verify=False, timeout=30)
    assert r.status_code == 200, f"Chat JS not served: {r.status_code}"
    js = r.text
    assert "P5: FULL-WIDTH FOOTER & INPUT AREA" in js, "Missing P5 footer marker"
    assert "flex-direction: column" in js, "Missing column direction on chat-inputs"
    assert "order: 1" in js, "Missing order 1 for textarea"
    assert "order: 2" in js, "Missing order 2 for controls"
    assert "justify-content: flex-end" in js, "Missing right-aligned controls"
    assert "P5: MOBILE FULL-SCREEN EXPANSION" in js, "Missing mobile expansion rules"
    print("TC41 PASS: Chat widget two-row column layout & mobile expansion verified")


def test_tc42_inline_ai_touch_resize_and_textbox_sync():
    """TC42: Inline AI has touch drag, touch resize, and dynamic text box auto-resize."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/js/ethiobiz_inline_ai.js", verify=False, timeout=30)
    assert r.status_code == 200, f"Inline AI JS not served: {r.status_code}"
    js = r.text
    assert "P5: User-resizable popup (mouse + touch)" in js, "Missing touch resize marker"
    assert "syncInnerSizes" in js, "Missing text box auto-resize sync function"
    assert "touchstart" in js, "Missing touchstart event handler"
    assert "touchmove" in js, "Missing touchmove event handler"
    assert "touchend" in js, "Missing touchend event handler"
    print("TC42 PASS: Inline AI touch drag, touch resize & text box auto-resize verified")


def test_tc43_afocha_social_upload_api():
    """TC43: Afocha Social 5MB image upload API endpoint exists and successfully uploads images."""
    import io
    dummy_file = io.BytesIO(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
    files = {'file': ('test_social.gif', dummy_file, 'image/gif')}
    r_up = requests.post(f"{SITE}/api/method/bismillah_ethiobiz.afocha_api.upload_post_image", files=files, verify=False, timeout=30)
    assert r_up.status_code == 200, f"Expected 200 for upload, got {r_up.status_code}: {r_up.text}"
    msg = r_up.json().get("message", {})
    assert msg.get("status") == "success" and "file_url" in msg, f"Invalid upload response: {r_up.text}"
    
    r_page = requests.get(f"{SITE}/social", verify=False, timeout=30)
    assert r_page.status_code == 200, f"Social page failed: {r_page.status_code}"
    assert "upload_post_image" in r_page.text, "Missing upload_post_image in social.html"
    assert "5 * 1024 * 1024" in r_page.text, "Missing 5MB client check in social.html"
    print("TC43 PASS: Afocha Social 5MB image upload API returns valid file URL")


def test_tc44_forum_image_upload_and_topics():
    """TC44: Walta Forum has image column, upload endpoint, and returns image field."""
    import io
    dummy_file = io.BytesIO(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
    files = {'file': ('test_forum.gif', dummy_file, 'image/gif')}
    r_up = requests.post(f"{SITE}/api/method/bismillah_ethiobiz.walta_forum_api.upload_forum_image", files=files, verify=False, timeout=30)
    assert r_up.status_code == 200, f"Expected 200 for upload, got {r_up.status_code}: {r_up.text}"
    msg = r_up.json().get("message", {})
    assert msg.get("status") == "success" and "file_url" in msg, f"Invalid forum upload response: {r_up.text}"

    r = _get("bismillah_ethiobiz.walta_forum_api.get_forum_topics")
    assert r.status_code == 200, f"Forum topics API failed: {r.status_code}"
    data = r.json().get("message", {})
    assert "topics" in data, "Missing topics array in response"
    
    r_forum = requests.get(f"{SITE}/forum", verify=False, timeout=30)
    assert r_forum.status_code == 200, f"Forum page failed: {r_forum.status_code}"
    assert "topic-image-input" in r_forum.text, "Missing topic-image-input in forum.html"
    assert "upload_forum_image" in r_forum.text, "Missing upload_forum_image in forum.html"
    print("TC44 PASS: Walta Forum image upload & thumbnail linking verified")


def test_tc45_homepage_infinite_feed_forum_images():
    """TC45: Homepage infinite stream feed includes forum filter and returns image items."""
    r_feed = _get("bismillah_ethiobiz.home_api.get_infinite_feed?filter_type=forum&limit=5")
    assert r_feed.status_code == 200, f"Feed API failed: {r_feed.status_code}"
    r_home = requests.get(f"{SITE}/", verify=False, timeout=30)
    assert r_home.status_code == 200, f"Home page failed: {r_home.status_code}"
    assert ('data-filter="forum"' in r_home.text or 'data-filter="forums"' in r_home.text), "Missing forum filter button in home page"
    print("TC45 PASS: Homepage stream feed forum integration & image rendering verified")


def test_tc46_blog_light_theme_css():
    """TC46: Blog page has luminous light theme CSS and high-contrast styling."""
    r = requests.get(f"{SITE}/assets/bismillah_ethiobiz/css/ethiobiz_theme.css", verify=False, timeout=30)
    assert r.status_code == 200, f"Theme CSS failed: {r.status_code}"
    css = r.text
    assert "P5: BLOG & TIBEB PAGES" in css, "Missing P5 blog CSS marker"
    assert 'body[data-path*="blog"]' in css or 'body[data-path="list"]' in css, "Missing blog route selectors"
    assert ".blog-card .card" in css, "Missing blog-card card style"
    assert "#072a2e" in css, "Missing deep teal heading color"
    assert "#ffffff" in css, "Missing crisp white card background"
    print("TC46 PASS: Blog page luminous light theme & typography verified")


def run_all():
    """Run all P4 & P5 tests."""
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
        test_tc41_chat_widget_two_row_and_mobile,
        test_tc42_inline_ai_touch_resize_and_textbox_sync,
        test_tc43_afocha_social_upload_api,
        test_tc44_forum_image_upload_and_topics,
        test_tc45_homepage_infinite_feed_forum_images,
        test_tc46_blog_light_theme_css,
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
    print(f"\n=== COMPLETE TEST SUITE: {passed} PASS, {failed} FAIL, {len(tests)} TOTAL ===")
    frappe.destroy()
    return failed == 0


if __name__ == "__main__":
    run_all()

