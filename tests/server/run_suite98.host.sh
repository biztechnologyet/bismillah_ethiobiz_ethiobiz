#!/bin/bash
# Bismillah — install and run the feed-engagement suite (98) from the REPO copy.
#
# Why this exists: /home/frappe/frappe-bench/tests/ lives INSIDE the container only.
# It is not a bind mount, so `docker compose up -d --force-recreate` (or a new image)
# wipes every suite. The durable source of truth is the version-controlled copy at
#   apps/bismillah_ethiobiz/tests/server/suite_98_feed_engagement.py
# Run this script after any container recreation to restore and execute it.
#
# Usage ON THE HOST (from the app dir, or pass the repo path):
#   bash tests/server/run_suite98.host.sh
set -e

C=bismallah_ethiobiz_inshaallah-backend-1
APP=/home/frappe/frappe-bench/apps/bismillah_ethiobiz
PY=/home/frappe/frappe-bench/env/bin/python
SUITE=suite_98_feed_engagement.py
SRC="${1:-$APP/tests/server/$SUITE}"
DST=/home/frappe/frappe-bench/tests/suites/$SUITE

if [ ! -f "$SRC" ]; then
    echo "FATAL: suite source not found: $SRC"
    echo "       expected the version-controlled copy under $APP/tests/server/"
    exit 1
fi

echo "=== installing $SUITE into the container ==="
docker exec -u root "$C" mkdir -p /home/frappe/frappe-bench/tests/suites
docker cp "$SRC" "$C:$DST"
docker exec -u root "$C" chown frappe:frappe "$DST"
echo "installed: $DST"

echo
echo "=== confirming the runner discovers suite 98 ==="
docker exec "$C" bash -c "cd /home/frappe/frappe-bench/tests && $PY run_all_suites.py --list | grep -E '^ *98'"

echo
echo "=== running suite 98 ==="
# Exits non-zero if any check fails, so this script fails with it (set -e).
docker exec "$C" bash -c "cd /home/frappe/frappe-bench/tests && $PY run_all_suites.py --suite 98"

echo
echo "=== JSON report ==="
docker exec "$C" cat /home/frappe/frappe-bench/tests/results/suite_98_report.json
