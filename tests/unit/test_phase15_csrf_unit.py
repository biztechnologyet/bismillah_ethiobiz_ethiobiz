"""Unit mirror for ANFRG-26-00063 Phase 15 (CSRF fix) — no Frappe needed.

Verifies source contracts: central ebFetch/ebPostForm helpers exist and are
registered FIRST, all four broken call sites now route through them, error
surfacing via ebToast replaced silent console.error-only failures.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_PKG = REPO_ROOT / "bismillah_ethiobiz"
FETCH_JS = APP_PKG / "public" / "js" / "ethiobiz_fetch.js"
FORUM_HTML = APP_PKG / "www" / "forum.html"
SOCIAL_HTML = APP_PKG / "www" / "social.html"
HOOKS_PY = APP_PKG / "hooks.py"


class EbFetchContract(unittest.TestCase):
    def test_helper_exists_with_csrf_and_toast(self):
        src = FETCH_JS.read_text(encoding="utf-8")
        self.assertIn("window.ebFetch", src)
        self.assertIn("X-Frappe-CSRF-Token", src)
        self.assertIn("window.ebToast", src)
        self.assertIn("csrf_token=([^;]+)", src)
        self.assertIn("meta[name=\"csrf-token\"]", src)
        self.assertIn("window.ebPostForm", src)

    def test_registered_first_in_hooks(self):
        hooks = HOOKS_PY.read_text(encoding="utf-8")
        m = re.search(r"web_include_js\s*=\s*\[(.*?)\]", hooks, re.S)
        self.assertIsNotNone(m, "web_include_js block missing")
        entries = re.findall(r"\"([^\"]+\.js)", m.group(1))
        self.assertTrue(entries, "no js entries")
        self.assertTrue(
            entries[0].startswith("/assets/bismillah_ethiobiz/js/ethiobiz_fetch.js"),
            f"ebFetch not first: {entries[0]}")

    def test_forum_call_sites_use_helpers(self):
        src = FORUM_HTML.read_text(encoding="utf-8")
        self.assertIn("ebFetch('/api/method/bismillah_ethiobiz.walta_forum_api.like_forum_topic",
                      src)
        self.assertIn("ebPostForm('bismillah_ethiobiz.walta_forum_api.add_forum_reply'",
                      src)
        # no bare authenticated POST fetches left in forum page
        self.assertNotIn("fetch('/api/method/bismillah_ethiobiz.walta_forum_api.add_forum_reply'", src)

    def test_social_call_sites_use_helpers(self):
        src = SOCIAL_HTML.read_text(encoding="utf-8")
        self.assertIn("ebPostForm('bismillah_ethiobiz.afocha_api.create_social_post'", src)
        self.assertIn("ebPostForm('bismillah_ethiobiz.afocha_api.add_post_comment'", src)
        self.assertIn("ebFetch('/api/method/bismillah_ethiobiz.afocha_api.like_social_post", src)
        self.assertIn("ebFetch('/api/method/bismillah_ethiobiz.afocha_api.vote_poll", src)
        self.assertNotIn("fetch('/api/method/bismillah_ethiobiz.afocha_api.add_post_comment'", src)
        self.assertNotIn("fetch('/api/method/bismillah_ethiobiz.afocha_api.create_social_post'", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
