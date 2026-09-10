#!/usr/bin/env python
"""
Deployment script for Phase D vertical fixes
BISMALLAH - Copies updated API files to cloud container
"""

import os
import subprocess
import sys

# Files to deploy
FILES_TO_DEPLOY = [
    "bizbooking_api.py",
    "bizhealth_api.py",
    "bizhome_api.py",
    "bizride_api.py",
    "ethiobiz_identity.py",
    "jobs.py",
    "magala_shop_api.py",
]

# Cloud configuration
CLOUD_HOST = "128.140.82.215"
CLOUD_USER = "root"
BACKEND_CONTAINER = "bismallah_ethiobiz_inshaallah-backend-1"
FRONTEND_CONTAINER = "bismallah_ethiobiz_inshaallah-frontend-1"
APP_PATH = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz"

def run_command(cmd, check=True):
    """Run a shell command and return output"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    print("BISMALLAH - Deploying Phase D vertical fixes to cloud")
    print("=" * 60)
    
    # Check if files exist
    for f in FILES_TO_DEPLOY:
        if not os.path.exists(f):
            print(f"Error: File not found: {f}")
            sys.exit(1)
    
    print("Step 1: Copying files to cloud host...")
    for f in FILES_TO_DEPLOY:
        print(f"  Copying {f}...")
        # Using scp - assuming scp is available
        cmd = f'scp -o StrictHostKeyChecking=no {f} {CLOUD_USER}@{CLOUD_HOST}:/tmp/'
        try:
            run_command(cmd)
        except Exception as e:
            print(f"  SCP failed: {e}")
            print("  Manual copy required. Please manually copy these files to /tmp/ on the cloud host:")
            for f2 in FILES_TO_DEPLOY:
                print(f"    - {f2}")
            sys.exit(1)
    
    print("\nStep 2: Copying files into backend container...")
    for f in FILES_TO_DEPLOY:
        print(f"  Copying {f} into container...")
        cmd = f'ssh {CLOUD_USER}@{CLOUD_HOST} "docker cp /tmp/{f} {BACKEND_CONTAINER}:{APP_PATH}/"'
        run_command(cmd)
    
    print("\nStep 3: Running migration...")
    migration_cmd = f'ssh {CLOUD_USER}@{CLOUD_HOST} "docker exec {BACKEND_CONTAINER} python -c \\"from frappe.migrate import SiteMigration; SiteMigration().run(\\'ethiobiz.et\\')\\""'
    run_command(migration_cmd)
    
    print("\nStep 4: Restarting backend...")
    restart_cmd = f'ssh {CLOUD_USER}@{CLOUD_HOST} "docker restart {BACKEND_CONTAINER}"'
    run_command(restart_cmd)
    
    print("\nStep 5: Reloading frontend nginx...")
    nginx_cmd = f'ssh {CLOUD_USER}@{CLOUD_HOST} "docker exec {FRONTEND_CONTAINER} nginx -s reload"'
    run_command(nginx_cmd)
    
    print("\n" + "=" * 60)
    print("BISMALLAH - Deployment complete!")
    print("Vertical fixes deployed to cloud:")
    for f in FILES_TO_DEPLOY:
        print(f"  ✓ {f}")
    print("\nPlease verify the live site at https://ethiobiz.et")

if __name__ == "__main__":
    main()
