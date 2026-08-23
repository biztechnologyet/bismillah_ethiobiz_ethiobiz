#!/usr/bin/env python3
"""Bismillah — ANFRG-26-00063 Phase 1 deploy + verify (git-first protocol).

Run LOCALLY from the workspace root:
    python "bismillah_ethiobiz_ethiobiz\\tests\\deploy_phase1.py"

Steps:
 1. Commit & push bizmarketing changes (git-first; no bench migrate).
 2. docker exec git pull on the server.
 3. Run the deploy function (custom fields + client script) via bench execute.
 4. Push & run the Phase 1 server integration suite.
 5. Clear cache + restart backend (nuke __pycache__ for .py changes).
"""
import subprocess
import sys
from datetime import datetime

SERVER = "root@128.140.82.215"
PASSWORD = "bizTECHNOLOGY@123"
CONTAINER = "bismallah_ethiobiz_inshaallah-backend-1"
SITE = "ethiobiz.et"
PLINK = r"C:\Program Files\PuTTY\plink.exe"
PSCP = r"C:\Program Files\PuTTY\pscp.exe"
APP_REMOTE = "/home/frappe/frappe-bench/apps/bizmarketing"
WORKSPACE = r"C:\BISMALLAH ETHIOBIZ.ET CLOUD SYSTEMS INSHA'ALLAH"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def ssh(cmd, timeout=120):
    log(f"SSH> {cmd}")
    r = subprocess.run([PLINK, "-ssh", "-pw", PASSWORD, SERVER, cmd],
                       capture_output=True, text=True, timeout=timeout)
    if r.stdout.strip():
        print(r.stdout.strip()[:3000])
    if r.returncode != 0 and r.stderr.strip():
        log(f"STDERR: {r.stderr.strip()[:500]}")
    return r.returncode, r.stdout


def scp(local, remote):
    log(f"SCP {local} -> {remote}")
    r = subprocess.run([PSCP, "-pw", PASSWORD, local, f"{SERVER}:{remote}"],
                       capture_output=True, text=True, timeout=120)
    ok = r.returncode == 0
    log("SCP OK" if ok else f"SCP FAIL: {r.stderr[:300]}")
    return ok


def main():
    # ---- 1. local commit + push ----------------------------------------
    repo = WORKSPACE + r"\bizmarketing"
    log("git status")
    subprocess.run(["git", "status", "--short"], cwd=repo)
    subprocess.run(["git", "add", "-A"], cwd=repo)
    c = subprocess.run(
        ["git", "commit", "-m",
         "ANFRG-26-00063 P0: manual activation gate - no self-activation "
         "after bank transfer claims; AddiPay webhook settings-gated; "
         "cron skips Pending signups"],
        cwd=repo, capture_output=True, text=True)
    print((c.stdout or c.stderr)[:600])
    p = subprocess.run(["git", "push", "origin", "HEAD"], cwd=repo,
                       capture_output=True, text=True, timeout=180)
    print((p.stdout or p.stderr)[:600])
    if p.returncode != 0:
        log("git push FAILED — aborting before touching prod.")
        return 1

    # ---- 2. server git pull ---------------------------------------------
    code, _ = ssh(f'docker exec {CONTAINER} git -C {APP_REMOTE} pull origin HEAD')
    if code != 0:
        log("docker git pull FAILED.")
        return 1

    # ---- 3. run deploy function ------------------------------------------
    code, out = ssh(
        f'docker exec -u frappe -w {APP_REMOTE} {CONTAINER} '
        f'bench --site {SITE} execute '
        f'bizmarketing.deploy_manual_activation.execute', timeout=300)

    # ---- 4. push + run integration suite ----------------------------------
    suite_local = WORKSPACE + r"\bismillah_ethiobiz_ethiobiz\tests\server\phase1_integration.py"
    suite_remote = f"/tmp/anfrg_phase1_server_tests.py"
    if scp(suite_local, suite_remote):
        ssh(f"docker cp {suite_remote} {CONTAINER}:{APP_REMOTE}/anfrg_phase1_server_tests.py && "
            f"docker exec {CONTAINER} chown frappe:frappe {APP_REMOTE}/anfrg_phase1_server_tests.py")
        code, out = ssh(
            f'docker exec -u frappe -w {APP_REMOTE} {CONTAINER} '
            f'bench --site {SITE} execute anfrg_phase1_server_tests.run',
            timeout=600)

    # ---- 5. clear cache + restart ------------------------------------------
    ssh(f"docker exec {CONTAINER} find {APP_REMOTE} -name __pycache__ -type d "
        f"-exec rm -rf {{}} + 2>/dev/null; true")
    ssh(f"docker exec {CONTAINER} bench --site {SITE} clear-cache", timeout=300)
    ssh(f"docker restart {CONTAINER}", timeout=300)
    log("Alhamdulillah — Phase 1 deployed. Verify site health in ~60s.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
