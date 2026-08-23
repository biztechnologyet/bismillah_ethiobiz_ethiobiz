"""ANFRG-26-00063 Phase-2 server suite — Tasks B (sidebar) & C (animation).

Runner pattern (same as phase1):
    python runner_suite_theme.py  ->  /tmp/anfrg_phase2_results.json
"""

import json

import frappe

frappe.init(site="ethiobiz.et", sites_path="/home/frappe/frappe-bench/sites")
frappe.set_user("Administrator")
frappe.connect()

from bizmarketing.api.theme_settings import (  # noqa: E402
    SPEED_FACTORS,
    public_theme_settings,
)

RESULTS = {"suite": "anfrg_phase2_theme", "results": []}


def record(name, ok, detail=""):
    RESULTS["results"].append(
        {"test": name, "ok": bool(ok), "detail": str(detail)[:400]}
    )
    print(("PASS " if ok else "FAIL ") + name + (" | " + str(detail) if detail and not ok else ""))


def tc_sb1_doctype_and_field():
    meta = frappe.get_meta("EthioBiz Theme")
    df = next((f for f in meta.fields if f.fieldname == "hide_sidebar"), None)
    record(
        "TC-SB1 EthioBiz Theme is Single with hide_sidebar Check default 1",
        meta.issingle == 1
        and df is not None
        and df.fieldtype == "Check"
        and (df.default or "1") in ("1", 1),
        f"issingle={meta.issingle} df={df and (df.fieldtype, df.default)}",
    )


def tc_sb2_endpoint_defaults():
    conf = public_theme_settings()
    ok = (
        isinstance(conf, dict)
        and conf.get("hide_sidebar") is True
        and conf.get("enable_website_animation") is True
        and conf.get("animation_speed_factor") == SPEED_FACTORS["Normal"]
    )
    record("TC-SB2 endpoint guest-safe defaults", ok, conf)


def tc_sb3_disable_enable_roundtrip():
    frappe.db.set_single_value("EthioBiz Theme", "hide_sidebar", 0)
    disabled = public_theme_settings()["hide_sidebar"]
    frappe.db.set_single_value("EthioBiz Theme", "hide_sidebar", 1)
    enabled = public_theme_settings()["hide_sidebar"]
    record(
        "TC-SB3 admin disable->enable roundtrip",
        disabled is False and enabled is True,
        f"disabled={disabled} enabled={enabled}",
    )


def tc_sb4_speed_map():
    checks = {
        "Slow": SPEED_FACTORS["Slow"],
        "Normal": SPEED_FACTORS["Normal"],
        "Fast": SPEED_FACTORS["Fast"],
    }
    ok = checks == {"Slow": 0.45, "Normal": 0.7, "Fast": 0.95}
    meta = frappe.get_meta("EthioBiz Theme")
    sel = next(
        (
            f
            for f in meta.fields
            if f.fieldname == "website_animation_speed"
        ),
        None,
    )
    opts_ok = sel is not None and sel.fieldtype == "Select" and all(
        o in (sel.options or "") for o in ("Slow", "Normal", "Fast")
    )
    record("TC-SB4 speed Select + factor map", ok and opts_ok,
           f"map={checks} select={(sel and (sel.fieldtype, sel.options))}")


def tc_sb5_js_policy_markers():
    app_js = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/public/js/ethiobiz_theme.js"
    src = open(app_js, encoding="utf-8").read()
    hooks_src = open(
        "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/hooks.py",
        encoding="utf-8",
    ).read()
    ok = (
        "applySidebarPolicy" in src
        and "hide_sidebar === false" in src
        and "ethiobiz_particles.js" in hooks_src
    )
    record("TC-SB5 theme JS policy markers + particles registered", ok)


def tc_bg1_animation_fields():
    meta = frappe.get_meta("EthioBiz Theme")
    chk = next((f for f in meta.fields if f.fieldname == "enable_website_animation"), None)
    record(
        "TC-BG1 enable_website_animation field default on",
        chk is not None and chk.fieldtype == "Check" and (chk.default or "1") in ("1", 1),
    )


def tc_bg2_engine_source_guards():
    p = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/public/js/ethiobiz_particles.js"
    try:
        src = open(p, encoding="utf-8").read()
    except OSError:
        return record("TC-BG2 particle engine source guards", False, "file missing")
    ok = (
        "__ETHIOBIZ_AMBIENT__" in src
        and "prefers-reduced-motion" in src
        and "visibilitychange" in src
        and "0.7" in src
        and "/app" in src
    )
    record("TC-BG2 particle engine source guards", ok)


def tc_bg3_endpoint_animation_toggle():
    conf_on = public_theme_settings()
    frappe.db.set_single_value("EthioBiz Theme", "enable_website_animation", 0)
    conf_off = public_theme_settings()
    frappe.db.set_single_value("EthioBiz Theme", "enable_website_animation", 1)
    ok = conf_on["enable_website_animation"] is True and conf_off[
        "enable_website_animation"
    ] is False
    factor_ok = isinstance(conf_on["animation_speed_factor"], float)
    record("TC-BG3 animation toggle via endpoint", ok and factor_ok,
           f"on={conf_on} off={conf_off}")


def run():
    print("=" * 60)
    for fn in (
        tc_sb1_doctype_and_field,
        tc_sb2_endpoint_defaults,
        tc_sb3_disable_enable_roundtrip,
        tc_sb4_speed_map,
        tc_sb5_js_policy_markers,
        tc_bg1_animation_fields,
        tc_bg2_engine_source_guards,
        tc_bg3_endpoint_animation_toggle,
    ):
        try:
            fn()
        except Exception as e:
            record(fn.__name__ + " EXCEPTION", False, repr(e))
    total = len(RESULTS["results"])
    failed = sum(1 for r in RESULTS["results"] if not r["ok"])
    summary = dict(RESULTS, total=total, passed=total - failed, failed=failed)
    print(f"SUITE TOTAL={total} PASSED={summary['passed']} FAILED={failed}")
    return summary


if __name__ == "__main__" or True:
    summary = run()
    with open("/tmp/anfrg_phase2_results.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("RESULTS_SAVED=/tmp/anfrg_phase2_results.json")
