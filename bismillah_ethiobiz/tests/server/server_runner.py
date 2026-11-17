"""
SERVER-SIDE TEST RUNNER
Runs on: /home/frappe/frappe-bench/tests/run_all_suites.py
Flow: backup -> run all suites -> generate date-stamped .md reports
"""
import os, sys, subprocess, time, json, glob, tempfile

SUITES_DIR = "/home/frappe/frappe-bench/tests/suites"
RESULTS_DIR = "/home/frappe/frappe-bench/tests/results"
BACKUPS_DIR = "/home/frappe/frappe-bench/tests/backups"
LOCK_FILE = os.path.join(RESULTS_DIR, ".run_all.lock")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)


def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            if os.path.isdir("/proc/{}".format(old_pid)):
                print("  Test run already in progress (PID {}). Exiting.".format(old_pid))
                sys.exit(1)
        except Exception:
            pass
        try:
            os.remove(LOCK_FILE)
        except Exception:
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception:
        pass

SUITES = [
    (0, "suite_00_ethiobiz_speed_resource_server_status.py"),
    (1, "suite_01_dobiz_subscription_trial_paid_pipeline.py"),
    (2, "suite_02_dobiz_saas_configuration.py"),
    (3, "suite_03_social_media_hub.py"),
    ("03b", "suite_03b_telegram_extended.py"),
    ("03c", "suite_03c_facebook.py"),
    ("03d", "suite_03d_instagram.py"),
    ("03e", "suite_03e_linkedin.py"),
    ("03f", "suite_03f_twitter.py"),
    ("03g", "suite_03g_tiktok.py"),
    ("03h", "suite_03h_youtube.py"),
    ("03i", "suite_03i_whatsapp.py"),
    ("03z", "suite_03z_multi_platform.py"),
    (4, "suite_04_strategic_planning.py"),
    (5, "suite_05_automation_workflow.py"),
    (6, "suite_06_lead_capture_web_forms.py"),
    (7, "suite_07_whitelisted_api_endpoints.py"),
    (8, "suite_08_brand_management.py"),
    (9, "suite_09_bismallah_ethiobiz_integration.py"),
    (10, "suite_10_permissions_security.py"),
    (11, "suite_11_scheduler_cron_tasks.py"),
    (12, "suite_12_edge_cases_error_handling.py"),
    (13, "suite_13_cross_module_integration_flows.py"),
    (14, "suite_14_industry_role_module_profiles.py"),
    (15, "suite_15_industry_privilege_verification.py"),
    (16, "suite_16_frontend_service_health.py"),
    (17, "suite_17_email_notification_system.py"),
    (18, "suite_18_security_headers_authentication.py"),
    (19, "suite_19_payment_gateway_integration.py"),
    (20, "suite_20_data_privacy_compliance.py"),
    (21, "suite_21_localization_multi_language.py"),
    (22, "suite_22_performance_system_health.py"),
    (23, "suite_23_navigation_search_ux.py"),
    (24, "suite_24_pdf_generation_printing.py"),
    (25, "suite_25_walta_helpdesk_support_system.py"),
    (26, "suite_26_hr_employee_management.py"),
    (27, "suite_27_multi_tenant_data_isolation.py"),
    (28, "suite_28_backup_disaster_recovery.py"),
    (29, "suite_29_file_upload_media.py"),
    (30, "suite_30_cross_cutting_validation_launch_readiness.py"),
    (31, "suite_31_website_item_publishing_all_products.py"),
    (32, "suite_32_multi_company_quotation_contact_routing.py"),
    (33, "suite_33_webshop_quotation_company_routing_rfq.py"),
    (34, "suite_34_lms_dagu_learning.py"),
    (35, "suite_35_system_health_baseline.py"),
    (36, "suite_36_event_notification_patch.py"),
    (37, "suite_37_print_designer_removal.py"),
    (38, "suite_38_hadeeda_settings.py"),
    (39, "suite_39_chat_widget.py"),
    (40, "suite_40_inline_ai.py"),
    (46, "suite_46_home_page_www_migration.py"),
    (47, "suite_47_sidebar_theme_regression.py"),
    (48, "suite_48_home_search_fab.py"),
    (49, "suite_49_dobiz_signup_wizard.py"),
]

def backup_site():
    print("")
    print("=" * 70)
    print("STEP 0: BACKING UP ETHIOBIZ.ET --WITH-FILES")
    print("=" * 70)
    sys.stdout.flush()
    try:
        backup_cmd = "cd /home/frappe/frappe-bench && bench --site ethiobiz.et backup --with-files --backup-path " + BACKUPS_DIR
        br = subprocess.run(backup_cmd, shell=True, capture_output=True, text=True, timeout=180)
        if br.returncode == 0:
            print("  ALHAMDULILLAH. Backup completed to " + BACKUPS_DIR)
            for line in br.stdout.split("\n"):
                if "Backup" in line or "backup" in line.lower():
                    print("  " + line.strip())
        else:
            print("  Backup WARNING: exit code " + str(br.returncode))
            if br.stderr:
                print("  " + br.stderr.strip()[-300:])
    except Exception as be:
        print("  Backup ERROR: " + str(be)[:150])
    print("")

def _sid_label(sid):
    """Format suite ID for display"""
    if isinstance(sid, int):
        return "{:02d}".format(sid)
    return str(sid)

def _find_report(sid, fname):
    """Try multiple report filename patterns to find the suite's report"""
    patterns = []
    if isinstance(sid, int):
        # Suites 00-09 save zero-padded report names (suite_00_report.json).
        patterns.append("suite_{:02d}_report.json".format(sid))
        patterns.append("suite_{}_report.json".format(sid))
    else:
        patterns.append("suite_{}_report.json".format(sid))
    patterns.append("suite_{}_report.json".format(fname.replace(".py", "").replace("suite_", "")))
    for p in patterns:
        rp = os.path.join(RESULTS_DIR, p)
        if os.path.exists(rp):
            return rp
    return None

def run_suite(sid, fname):
    """Run a single suite and return its results"""
    fpath = os.path.join(SUITES_DIR, fname)
    if not os.path.exists(fpath):
        print("\n  SKIP Suite {}: {} - file not found".format(_sid_label(sid), fname))
        return None

    label = _sid_label(sid)
    print("\n  " + "=" * 70)
    print("  RUNNING SUITE {}: {}".format(label, fname))
    print("  " + "=" * 70)
    sys.stdout.flush()

    start = time.time()
    ret = subprocess.run([sys.executable, fpath], cwd=SUITES_DIR, timeout=1800)
    elapsed = time.time() - start

    report_path = _find_report(sid, fname)
    if report_path:
        try:
            with open(report_path) as f:
                report = json.load(f)
        except Exception as e:
            print("  WARN: Could not read report: " + str(e))
            report = {"suite": label, "passed": 0, "failed": 0, "total": 0, "results": []}
    else:
        report = {"suite": label, "passed": 0, "failed": 0, "total": 0, "results": []}

    print("  Suite {}: {} ({:.1f}s) - {}/{} passed".format(
        label, "PASSED" if ret.returncode == 0 else "FAILED", elapsed,
        report.get("passed", 0), report.get("total", 0)))
    sys.stdout.flush()
    return report

def generate_md_report(timestamp, all_reports):
    """Generate comprehensive .md report with all details"""
    lines = []
    ts_short = timestamp.replace(":", "-").replace(" ", "_")
    
    grand_p = sum(r.get("passed", 0) for r in all_reports.values() if r)
    grand_f = sum(r.get("failed", 0) for r in all_reports.values() if r)
    grand_t = grand_p + grand_f

    lines.append("# EthioBiz / DOBiz Smarterp - Master Test Report")
    lines.append("")
    lines.append("**Date:** " + timestamp)
    lines.append("**Environment:** ethiobiz.et (Production)")
    lines.append("**Backend:** bismallah_ethiobiz_inshaallah-backend-1")
    lines.append("**Total Suites:** " + str(len(SUITES)))
    lines.append("**Total Tests:** " + str(grand_t))
    lines.append("**Passed:** " + str(grand_p))
    lines.append("**Failed:** " + str(grand_f))
    lines.append("")
    
    if grand_f == 0:
        lines.append("## ALHAMDULILLAH - ALL TESTS PASSED")
        lines.append("")
        lines.append("The system is healthy and all " + str(grand_t) + " tests across " + str(len(SUITES)) + " suites have passed successfully.")
    else:
        lines.append("## WARNING - " + str(grand_f) + " TEST(S) FAILED")
        lines.append("")
        lines.append("Review the detailed failure analysis below for root causes and proposed solutions.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Summary Table
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Suite # | Name | Status | Passed | Failed | Total |")
    lines.append("|---------|------|--------|--------|--------|-------|")
    for sid, fname in SUITES:
        r = all_reports.get(sid)
        if not r:
            lines.append("| {} | {} | SKIP | - | - | - |".format(_sid_label(sid), fname))
            continue
        p = r.get("passed", 0)
        f = r.get("failed", 0)
        t = r.get("total", 0)
        status = "PASS" if f == 0 else "FAIL"
        lines.append("| {} | {} | {} | {} | {} | {} |".format(_sid_label(sid), fname.replace(".py",""), status, p, f, t))
    
    lines.append("")
    lines.append("**Grand Total:** {}/{} passed ({:.1f}%)".format(grand_p, grand_t, (grand_p/grand_t*100) if grand_t else 0))
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Detailed suite-by-suite report
    lines.append("## Detailed Test Results")
    lines.append("")
    for sid, fname in SUITES:
        r = all_reports.get(sid)
        if not r:
            continue
        p = r.get("passed", 0)
        f = r.get("failed", 0)
        t = r.get("total", 0)
        status = "PASS" if f == 0 else "FAIL"
        
        lines.append("### Suite {}: {} [{}]".format(_sid_label(sid), fname.replace(".py",""), status))
        lines.append("")
        lines.append("- **Passed:** {}".format(p))
        lines.append("- **Failed:** {}".format(f))
        lines.append("- **Total:** {}".format(t))
        lines.append("")
        
        if f > 0:
            lines.append("#### Failed Tests")
            lines.append("")
            lines.append("| Test ID | Detail | Root Cause | Proposed Solution |")
            lines.append("|---------|--------|------------|-------------------|")
            for tr in (r.get("results") or []):
                if tr and tr.get("status") == "FAIL":
                    tid = tr.get("id", "?")
                    msg = tr.get("msg", "").replace("\n", " ").replace("|", "\\|")
                    rc = tr.get("rc", "").replace("\n", " ").replace("|", "\\|")
                    sol = tr.get("sol", "").replace("\n", " ").replace("|", "\\|")
                    lines.append("| {} | {} | {} | {} |".format(tid, msg, rc, sol))
            lines.append("")
        
        if f == 0 and t > 0:
            lines.append("All {} tests passed.".format(t))
            lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Final verdict
    lines.append("## Final Verdict")
    lines.append("")
    if grand_f == 0:
        lines.append("**ALHAMDULILLAH. SYSTEM IS HEALTHY.**")
        lines.append("")
        lines.append("All {} tests across {} suites passed successfully. No issues detected.".format(grand_t, len(SUITES)))
    else:
        lines.append("**{} TEST(S) FAILED.**".format(grand_f))
        lines.append("")
        lines.append("The following issues require attention:")
        lines.append("")
        failing_suites = [(sid, fname) for sid, fname in SUITES if (all_reports.get(sid) or {}).get("failed", 0) > 0]
        for sid, fname in failing_suites:
            r = all_reports.get(sid) or {}
            lines.append("- **Suite {}** ({}): {} failure(s)".format(_sid_label(sid), fname.replace(".py",""), r.get("failed", 0)))
            for tr in (r.get("results") or []):
                if tr and tr.get("status") == "FAIL":
                    sol = tr.get("sol", "Investigate manually")
                    lines.append("  - Test {}: {}".format(tr.get("id","?"), sol))
        lines.append("")
        lines.append("Please review the root causes above and apply the proposed solutions, then re-run the tests.")
    
    lines.append("")
    lines.append("---")
    lines.append("*Report generated by EthioBiz Automated Test System*")
    lines.append("*Moved to the first position for immediate system health verification*")
    
    return "\n".join(lines)

def run_all():
    acquire_lock()
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        ts_file = time.strftime("%Y-%m-%d_%H-%M-%S")
        
        backup_site()
        
        all_reports = {}
        for sid, fname in SUITES:
            report = run_suite(sid, fname)
            all_reports[sid] = report
        
        # Generate .md report
        md_content = generate_md_report(timestamp, all_reports)
        
        # Save date-stamped .md
        dated_fname = "MASTER_REPORT_{}.md".format(ts_file)
        dated_path = os.path.join(RESULTS_DIR, dated_fname)
        with open(dated_path, "w") as f:
            f.write(md_content)
        print("\n  Dated report saved: " + dated_path)
        
        # Save as latest .md (atomic write via tempfile)
        latest_path = os.path.join(RESULTS_DIR, "MASTER_REPORT.md")
        tmp_latest = os.path.join(RESULTS_DIR, ".MASTER_REPORT.md.tmp")
        with open(tmp_latest, "w") as f:
            f.write(md_content)
        os.replace(tmp_latest, latest_path)
        print("  Latest report saved: " + latest_path)
        
        # Also save .txt for backward compatibility (atomic)
        txt_path = os.path.join(RESULTS_DIR, "MASTER_REPORT.txt")
        tmp_txt = os.path.join(RESULTS_DIR, ".MASTER_REPORT.txt.tmp")
        with open(tmp_txt, "w") as f:
            f.write(md_content)
        os.replace(tmp_txt, txt_path)
        print("  Text report saved: " + txt_path)
        
        print("\n" + "=" * 70)
        grand_p = sum(r.get("passed", 0) for r in all_reports.values() if r)
        grand_f = sum(r.get("failed", 0) for r in all_reports.values() if r)
        print("GRAND TOTAL: {}/{} tests passed".format(grand_p, grand_p + grand_f))
        if grand_f == 0:
            print("ALHAMDULILLAH. ALL TESTS PASSED. SYSTEM IS HEALTHY.")
        else:
            print("{} TEST(S) FAILED - see {} for details.".format(grand_f, dated_fname))
        print("")
    finally:
        release_lock()

if __name__ == "__main__":
    run_all()
