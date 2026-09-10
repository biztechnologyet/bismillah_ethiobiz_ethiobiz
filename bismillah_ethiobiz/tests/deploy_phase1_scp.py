#!/usr/bin/env python3
"""Bismillah — ANFRG-26-00063 Phase 1 deploy (scp path, no GitHub creds needed).

Local commit already exists (1974844). This pushes files straight into the
container, commits them inside the server clone, deploys settings fields,
runs the integration suite, clears cache and restarts.
"""
import os
import subprocess
import sys
from datetime import datetime

SERVER = "root@128.140.82.215"
PASSWORD = "bizTECHNOLOGY@123"
CONTAINER = "bismallah_ethiobiz_inshaallah-backend-1"
SITE = "ethiobiz.et"
PLINK = r"C:\Program Files\PuTTY\plink.exe"
PSCP = r"C:\Program Files\PuTTY\pscp.exe"
APP = "/home/frappe/frappe-bench/apps/bizmarketing"
WS = r"C:\BISMALLAH ETHIOBIZ.ET CLOUD SYSTEMS INSHA'ALLAH"

FILES = [
    r"bizmarketing\bizmarketing\api\dobiz_manual_activation.py",
    r"bizmarketing\bizmarketing\deploy_manual_activation.py",
    r"bizmarketing\bizmarketing\api\dobiz_signup_api.py",
    r"bizmarketing\bizmarketing\api\dobiz_trial.py",
    r"bizmarketing\bizmarketing\api\subscription_cron.py",
    r"bizmarketing\bizmarketing\api\addispay.py",
]
SUITE = WS + r"\bismillah_ethiobiz_ethiobiz\tests\server\phase1_integration.py"


def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", flush=True)


def ssh(cmd, timeout=300):
    log(f"SSH> {cmd[:160]}")
    r = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PASSWORD, SERVER, cmd],
                       capture_output=True, text=True, timeout=timeout)
    if r.stdout.strip():
        print(r.stdout.strip()[:4000])
    if r.returncode != 0 and r.stderr.strip():
        print(f"STDERR: {r.stderr.strip()[:600]}")
    return r.returncode


def main():
    # 1. upload files to /tmp on host
    for f in FILES + [SUITE]:
        name = f.split("\\")[-1]
        local = f if os.path.isabs(f) else f"{WS}\\{f}"
        r = subprocess.run([PSCP, "-batch", "-pw", PASSWORD, local,
                            f"{SERVER}:/tmp/{name}"],
                           capture_output=True, text=True, timeout=120)
        log(("OK  " if r.returncode == 0 else "FAIL ") + name)
        if r.returncode != 0:
            print(r.stderr[:300])
            return 1

    # 2. map into container paths
    pairs = {
        "dobiz_manual_activation.py": f"{APP}/bizmarketing/api/dobiz_manual_activation.py",
        "deploy_manual_activation.py": f"{APP}/deploy_manual_activation.py",
        "dobiz_signup_api.py": f"{APP}/bizmarketing/api/dobiz_signup_api.py",
        "dobiz_trial.py": f"{APP}/bizmarketing/api/dobiz_trial.py",
        "subscription_cron.py": f"{APP}/bizmarketing/api/subscription_cron.py",
        "addispay.py": f"{APP}/bizmarketing/api/addispay.py",
        "phase1_integration.py": f"{APP}/anfrg_phase1_server_tests.py",
    }
    for src, dst in pairs.items():
        code = ssh(f"docker cp /tmp/{src} {CONTAINER}:{dst}")
        if code != 0:
            return 1
    ssh(f"docker exec {CONTAINER} chown frappe:frappe "
        + " ".join(pairs.values()))

    # 3. nuke pycache for changed modules
    ssh(f"docker exec {CONTAINER} bash -c "
        f"'find {APP}/bizmarketing -name __pycache__ -type d -exec rm -rf {{}} + 2>/dev/null; true'")

    # 4. deploy custom fields + client script
    ssh(f"docker exec -u frappe -w {APP} {CONTAINER} "
        f"bench --site {SITE} execute bizmarketing.deploy_manual_activation.execute",
        timeout=300)

    # 5. run integration suite
    ssh(f"docker exec -u frappe -w {APP} {CONTAINER} "
        f"bench --site {SITE} execute anfrg_phase1_server_tests.run",
        timeout=600)

    # 6. commit inside server clone (history stays truthful)
    ssh(f"docker exec {CONTAINER} bash -c \"cd {APP} && git add -A && "
        f"git -c user.email=deploy@ethiobiz.et -c user.name='Deploy Bot' "
        f"commit -m 'ANFRG-26-00063 P0: manual activation gate (scp deploy)' || true\"")

    # 7. clear cache + restart
    ssh(f"docker exec {CONTAINER} bench --site {SITE} clear-cache", timeout=300)
    ssh(f"docker restart {CONTAINER}", timeout=300)
    log("Alhamdulillah — Phase 1 deployed. Site health check in ~60s.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
