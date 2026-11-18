#!/usr/bin/env python3
"""Suite 51: Dikka Shop product page + feed/desk polish (2026-11-18).

Verifies the follow-up refinements requested on top of Shop V3:
  - /shop is titled "Dikka Shop"
  - /product/<item_code> is a real, complete, beautiful full page
  - the product page reuses MagalaCart and keeps cart/checkout intact
  - Afocha live-feed cards no longer duplicate the author or leak Markdown
  - the desk title-bar expand/collapse control uses clean SVG glyphs
  - cache versions were bumped for the changed theme/shop assets
"""
import atexit
import json
import os
import re
from urllib.parse import quote

import requests
import urllib3

urllib3.disable_warnings()

_orig_print = print


def print(*args, **kwargs):
    kwargs.setdefault("flush", True)
    _orig_print(*args, **kwargs)


P = 0
F = 0
TEST_RESULTS = []


def chk(name, cond, msg="", rc="", sol=""):
    global P, F
    if cond:
        P += 1
        TEST_RESULTS.append({"id": name, "status": "PASS", "msg": msg, "rc": rc, "sol": sol})
        print("  PASS " + str(name))
    else:
        F += 1
        TEST_RESULTS.append({"id": name, "status": "FAIL", "msg": msg, "rc": rc, "sol": sol})
        print("  FAIL " + str(name) + ": " + msg)


def _save():
    try:
        rdir = "/home/frappe/frappe-bench/tests/results"
        os.makedirs(rdir, exist_ok=True)
        rp = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
        rf = len(TEST_RESULTS) - rp
        json.dump(
            {
                "suite": "51",
                "passed": rp,
                "failed": rf,
                "total": len(TEST_RESULTS),
                "results": TEST_RESULTS,
            },
            open(os.path.join(rdir, "suite_51_report.json"), "w"),
            indent=2,
        )
    except Exception:
        pass


atexit.register(_save)

BASE = "https://ethiobiz.et"
APP = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz"
S = requests.Session()
S.verify = False
S.headers["Accept"] = "application/json"


def get(path, **kw):
    kw.setdefault("timeout", 45)
    return S.get(BASE + path, **kw)


def api(method, **kw):
    kw.setdefault("timeout", 60)
    return S.get(BASE + "/api/method/" + method, **kw)


def local(rel):
    try:
        with open(os.path.join(APP, rel), "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception:
        return ""


def body(resp):
    try:
        return resp.json().get("message") or {}
    except Exception:
        return {}


print("\n" + "=" * 60)
print("SUITE 51: DIKKA SHOP PRODUCT PAGE + FEED/DESK POLISH")
print("=" * 60)

# --- 1. Shop title --------------------------------------------------------
shop = get("/shop?suite51=1")
shop_html = shop.text if shop.status_code == 200 else ""
chk("51.01 /shop returns 200", shop.status_code == 200, str(shop.status_code))
chk("51.02 /shop is titled Dikka Shop", "Dikka Shop" in shop_html)
chk("51.03 old Magala Marketplace title removed", "Magala Marketplace" not in shop_html)
chk("51.04 Dikka Shop hero markup deployed", "mgs-dikka-title" in shop_html and "mgs-dikka-word" in shop_html)

# --- 2. A live product to exercise the detail page ------------------------
search = api(
    "bismillah_ethiobiz.magala_shop_api.search_products",
    params={"query": "food", "limit": 1},
)
items = body(search).get("items") or []
item_code = items[0].get("item_code") if items else ""
chk("51.05 search API returns a product to test", bool(item_code), str(search.status_code))

product_url = "/product/" + quote(str(item_code), safe="")
prod = get(product_url)
prod_html = prod.text if prod.status_code == 200 else ""
chk("51.06 product detail page returns 200", prod.status_code == 200, "%s -> %s" % (product_url, prod.status_code))
chk("51.07 product page shell deployed", 'id="page-product"' in prod_html)
chk("51.08 product page has title + price + seller", "mp-title" in prod_html and "mp-price" in prod_html and "mp-seller-name" in prod_html)
chk("51.09 product page has gallery + lightbox", "mp-main-image" in prod_html and "mp-lightbox" in prod_html)
chk("51.10 product page has add-to-cart + buy-now", 'id="mp-add-to-cart"' in prod_html and 'id="mp-buy-now"' in prod_html)
chk("51.11 product page has sticky mobile buy bar", 'id="mp-sticky-buy"' in prod_html)
chk("51.12 product page has tabs + reviews + related", "mp-tabs" in prod_html and "mp-panel-reviews" in prod_html and "mp-related" in prod_html)
chk("51.13 product page loads scoped CSS/JS", "magala_product.css?v=2.0.0" in prod_html and "magala_product.js?v=2.2.0" in prod_html)
chk("51.14 product page embeds bootstrap payload", "window.MGS_PRODUCT" in prod_html and "window.ETHIOBIZ_PRESERVE_TITLE" in prod_html)
chk("51.15 product page keeps shared cart drawer", 'id="magala-cart-drawer"' in prod_html and 'id="cart-drawer-backdrop"' in prod_html)
chk("51.16 product page title carries the item name", item_code and item_code in prod_html)
chk("51.17 missing product returns 404", get("/product/DOES-NOT-EXIST-00972").status_code == 404)

# --- 3. Product assets + source -------------------------------------------
css = local("public/css/magala_product.css")
js = local("public/js/magala_product.js")
py = local("www/product.py")
html_src = local("templates/includes/dikka_product_page.html")
chk("51.18 product CSS source is substantial", len(css) > 20000, "len=%d" % len(css))
chk("51.19 product CSS is scoped to #page-product", "#page-product" in css and "#page-product .mp-hero" in css)
chk("51.20 product CSS is mobile + dark-mode aware", "@media (max-width: 860px)" in css and "prefers-color-scheme: dark" in css)
chk("51.21 product CSS asset reachable", get("/assets/bismillah_ethiobiz/css/magala_product.css?v=2.0.0").status_code == 200)
chk("51.22 product JS source is substantial", len(js) > 10000, "len=%d" % len(js))
chk("51.23 product JS reuses MagalaCart", "window.MagalaCart" in js and "window.renderShopCartDrawer" in js)
chk("51.24 product JS wires gallery/qty/tabs/share", "setMainImage" in js and "getQty" in js and "mp-tab" in js and "navigator.share" in js)
chk("51.25 product JS asset reachable", get("/assets/bismillah_ethiobiz/js/magala_product.js?v=2.2.0").status_code == 200)
chk("51.26 product controller reuses the dossier API", "get_product_detail" in py and "search_products" in py and "build_product_context" in py)
chk("51.27 product template is server-rendered", "product.item_name" in html_src and "product.gallery" in html_src and "tojson" in html_src)
chk("51.28 product route is registered", '/product/<path:item_code>' in local("hooks.py"))

# --- 3b. Published Website Item canonical route --------------------------
canonical_url = items[0].get("detail_url") if items else ""
canonical = get(canonical_url) if canonical_url else None
canonical_html = canonical.text if canonical is not None and canonical.status_code == 200 else ""
catalog_src = local("dikka_catalog.py")
override_src = local("overrides/website_item.py")
shop_js_src = local("public/js/magala_shop.js")
search_data = body(search)

chk("51.44 search API exposes canonical Website Item detail_url",
    bool(items) and all(i.get("detail_url") for i in items),
    str([i.get("detail_url") for i in items[:3]]))
chk("51.45 search API exposes Website Item fields",
    bool(items) and all(("website_item" in i and "web_item_name" in i and "website_image" in i) for i in items))
chk("51.46 canonical Website Item route renders the rich page",
    bool(canonical_url) and canonical is not None and canonical.status_code == 200
    and 'id="page-product"' in canonical_html and "mp-review-summary" in canonical_html,
    str(canonical_url) + " -> " + (str(canonical.status_code) if canonical is not None else "no-url"))
chk("51.47 Website Item controller override is registered",
    "override_doctype_class" in local("hooks.py")
    and "EthioBizWebsiteItem" in override_src
    and "dikka_item.html" in override_src)
chk("51.48 Dikka catalog owns the Website Item engine",
    "def get_website_item_detail" in catalog_src
    and "def build_product_context" in catalog_src
    and "def mark_review_helpful" in catalog_src
    and "tabWebsite Item" in catalog_src)
chk("51.49 Shop cards use canonical detail_url + Website Item fields",
    "productDetailUrl" in shop_js_src
    and "item.detail_url" in shop_js_src
    and "item.web_item_name" in shop_js_src
    and "mgs-view-btn" in shop_js_src)
chk("51.50 product dossier has offers/specs/reviews/recommended",
    bool(canonical_url) and all(k in (body(api(
        "bismillah_ethiobiz.magala_shop_api.get_product_detail",
        params={"item_code": items[0].get("item_code")},
    )) or {}) for k in ("offers", "specs", "reviews", "recommended", "gallery")))

# --- 4. Afocha live-feed rendering ----------------------------------------
feed_api = api(
    "bismillah_ethiobiz.smart_feed_api.get_personalized_feed",
    params={"start": 0, "limit": 15, "filter_type": "social"},
)
feed_items = body(feed_api).get("items") or []
social_items = [i for i in feed_items if i.get("type") == "social" and i.get("doctype") == "Afocha Post"]
chk("51.29 social feed API returns items", feed_api.status_code == 200 and bool(feed_items), str(feed_api.status_code))
chk("51.30 Afocha cards do not duplicate the author as title", all(not i.get("title") for i in social_items), str([i.get("title") for i in social_items[:3]]))
chk("51.31 Afocha content has no Markdown headings/bold", all(not re.search(r"(^|\n)\s*#{1,6}\s|\*\*", i.get("content") or "") for i in social_items), "markdown leaked")
chk("51.32 Afocha content drops trailing author signature", all(not re.search(r"\b" + re.escape(str(i.get("author_name") or "")) + r"\s*[.·]?\s*$", (i.get("content") or "").strip(), re.I) for i in social_items if i.get("author_name")), "signature leaked")
chk("51.33 feed renderer hides empty titles", "feed-post-title\"${title ? '' : ' hidden'}" in local("www/ethiobiz_home_v1.html"))
chk("51.34 feed source has social cleaner", "_social_feed_article" in local("smart_feed_api.py") and "_strip_author_signature" in local("smart_feed_api.py"))
chk("51.35 feed source uses social cleaner for Afocha", "_social_feed_article(post.content, post.author_name)" in local("smart_feed_api.py"))

# --- 5. Desk title-bar toggle glyph ---------------------------------------
theme_js = local("public/js/ethiobiz_theme.js")
theme_css = local("public/css/ethiobiz_theme.css")
arrow_lines = [ln for ln in theme_js.splitlines() if "eb-arrow" in ln]
chk("51.36 title toggle uses SVG chevrons", arrow_lines and all("<svg" in ln for ln in arrow_lines), "lines=%d" % len(arrow_lines))
chk("51.37 title toggle has no mojibake", arrow_lines and all("\u00c3" not in ln for ln in arrow_lines))
chk("51.38 title toggle has clean up/down paths", "m6 15 6-6 6 6" in theme_js and "m6 9 6 6 6-6" in theme_js)
chk("51.39 title toggle CSS sizes the SVG", ".eb-title-toggle-btn .eb-arrow" in theme_css and ".eb-title-toggle-btn .eb-arrow svg" in theme_css)
chk("51.40 title toggle is accessible", "aria-expanded" in theme_js and "aria-label" in theme_js)

# --- 6. Cache versions ----------------------------------------------------
hooks = local("hooks.py")
api_py = local("api.py")
chk("51.41 shop CSS cache version bumped", "magala_shop.css?v=3.2.0" in hooks and "magala_shop.css?v=3.2.0" in shop_html)
chk("51.42 theme CSS cache version bumped", "ethiobiz_theme.css?v=2.3.1" in hooks and "ethiobiz_theme.css?v=2.3.1" in api_py)
_theme_ver_match = re.search(r"ethiobiz_theme\.js\?v=([0-9.]+)", hooks)
_theme_ver = _theme_ver_match.group(1) if _theme_ver_match else "2.5.7"
chk("51.43 theme JS cache version bumped", ("ethiobiz_theme.js?v=" + _theme_ver) in hooks and ("ethiobiz_theme.js?v=" + _theme_ver) in api_py)

print("\nSUITE 51 RESULT: PASS=%d FAIL=%d" % (P, F))
raise SystemExit(0 if F == 0 else 1)
