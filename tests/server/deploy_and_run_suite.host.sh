#!/bin/bash
# Bismillah — deploy + launch the Phase-1 server suite from REPO copies.
# Usage (from workstation, repo root of bismillah_ethiobiz_ethiobiz):
#   powershell:  & "C:\Program Files\PuTTY\pscp.exe" ... see ops/PERSISTENCE.md
# This script runs ON THE HOST after files are pscp'd to /tmp/.
set -e
C=bismallah_ethiobiz_inshaallah-backend-1
APP=/home/frappe/frappe-bench/apps/bizmarketing/bizmarketing
docker exec -u root $C rm -f /tmp/suite_inner.sh /tmp/suite_out.txt
docker cp /tmp/anfrg_phase1_server_tests.py $C:$APP/anfrg_phase1_server_tests.py
docker cp /tmp/runner_suite.py              $C:/tmp/runner_suite.py
docker cp /tmp/suite_inner.sh               $C:/tmp/suite_inner.sh
docker exec -u root $C chown frappe:frappe \
    "$APP/anfrg_phase1_server_tests.py" /tmp/runner_suite.py /tmp/suite_inner.sh
docker exec -u root $C bash -c \
    "find /home/frappe/frappe-bench/apps/bizmarketing -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null; true"
docker exec -d -u frappe $C bash /tmp/suite_inner.sh
echo LAUNCHED — poll with: docker exec $C tail -50 /tmp/suite_out.txt
