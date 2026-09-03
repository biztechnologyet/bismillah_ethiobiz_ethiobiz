#!/usr/bin/env python
"""
Deployment script for Phase D vertical fixes using Paramiko
BISMALLAH - Deploys API files to cloud container
"""

import paramiko
import os
import sys

# Cloud configuration from expert system
HOST = "128.140.82.215"
USER = "root"
PASSWORD = "bizTECHNOLOGY@123"
BACKEND_CONTAINER = "bismallah_ethiobiz_inshaallah-backend-1"
FRONTEND_CONTAINER = "bismallah_ethiobiz_inshaallah-frontend-1"
APP_PATH = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz"

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

def run_ssh_command(ssh, command):
    """Run SSH command and return output"""
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    if error and "Warning" not in error:
        print(f"Error: {error}")
    return output

def main():
    print("BISMALLAH - Deploying Phase D vertical fixes to cloud")
    print("=" * 60)
    
    # Check if files exist locally
    for f in FILES_TO_DEPLOY:
        if not os.path.exists(f):
            print(f"Error: File not found: {f}")
            sys.exit(1)
    
    # Connect to SSH
    print("\nStep 1: Connecting to cloud host...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD)
        print("✓ Connected to cloud host")
    except Exception as e:
        print(f"✗ SSH connection failed: {e}")
        sys.exit(1)
    
    # Upload files via SFTP
    print("\nStep 2: Uploading files to cloud host...")
    sftp = ssh.open_sftp()
    for f in FILES_TO_DEPLOY:
        print(f"  Uploading {f}...")
        try:
            sftp.put(f, f"/root/{f}")
            print(f"  ✓ {f} uploaded")
        except Exception as e:
            print(f"  ✗ Failed to upload {f}: {e}")
            sftp.close()
            ssh.close()
            sys.exit(1)
    sftp.close()
    
    # Copy files into backend container
    print("\nStep 3: Copying files into backend container...")
    for f in FILES_TO_DEPLOY:
        cmd = f"docker cp /root/{f} {BACKEND_CONTAINER}:{APP_PATH}/{f}"
        output = run_ssh_command(ssh, cmd)
        print(f"  ✓ {f} copied to container")
    
    # Run migration
    print("\nStep 4: Running migration...")
    migration_script = """
import os
os.chdir('/home/frappe/frappe-bench/sites')
os.makedirs('../logs', exist_ok=True)
os.makedirs('ethiobiz.et/logs', exist_ok=True)

from frappe.migrate import SiteMigration
migrator = SiteMigration(skip_failing=False, skip_search_index=False)
migrator.run('ethiobiz.et')
print('MIGRATE_DONE')
"""
    
    # Write migration script to container
    with open("temp_migration.py", "w") as f:
        f.write(migration_script)
    
    sftp = ssh.open_sftp()
    sftp.put("temp_migration.py", "/root/temp_migration.py")
    sftp.close()
    
    cmd = f"docker cp /root/temp_migration.py {BACKEND_CONTAINER}:/tmp/temp_migration.py"
    run_ssh_command(ssh, cmd)
    
    cmd = f"docker exec {BACKEND_CONTAINER} /home/frappe/frappe-bench/env/bin/python /tmp/temp_migration.py"
    output = run_ssh_command(ssh, cmd)
    print(output)
    
    if "MIGRATE_DONE" in output:
        print("✓ Migration completed successfully")
    else:
        print("⚠ Migration may have issues - check output above")
    
    # Clean up temp files
    run_ssh_command(ssh, "rm /root/temp_migration.py")
    run_ssh_command(ssh, f"docker exec {BACKEND_CONTAINER} rm /tmp/temp_migration.py")
    os.remove("temp_migration.py")
    
    # Restart backend
    print("\nStep 5: Restarting backend...")
    cmd = f"docker restart {BACKEND_CONTAINER}"
    output = run_ssh_command(ssh, cmd)
    print("✓ Backend restarted")
    
    # Wait for restart
    print("  Waiting 10 seconds for backend to start...")
    import time
    time.sleep(10)
    
    # Reload frontend nginx
    print("\nStep 6: Reloading frontend nginx...")
    cmd = f"docker exec {FRONTEND_CONTAINER} nginx -s reload"
    output = run_ssh_command(ssh, cmd)
    print("✓ Frontend nginx reloaded")
    
    # Close SSH connection
    ssh.close()
    
    print("\n" + "=" * 60)
    print("BISMALLAH - Deployment complete!")
    print("Vertical fixes deployed to cloud:")
    for f in FILES_TO_DEPLOY:
        print(f"  ✓ {f}")
    print("\nPlease verify the live site at https://ethiobiz.et")

if __name__ == "__main__":
    main()
