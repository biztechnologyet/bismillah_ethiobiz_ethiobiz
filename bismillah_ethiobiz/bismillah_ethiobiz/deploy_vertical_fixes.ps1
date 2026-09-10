# Deployment script for Phase D vertical fixes using PowerShell
# BISMALLAH - Deploys API files to cloud container

$CloudHost = "128.140.82.215"
$USER = "root"
$PASSWORD = "bizTECHNOLOGY@123"
$BACKEND_CONTAINER = "bismallah_ethiobiz_inshaallah-backend-1"
$FRONTEND_CONTAINER = "bismallah_ethiobiz_inshaallah-frontend-1"
$APP_PATH = "/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz"

$FILES = @(
    "bizbooking_api.py",
    "bizhealth_api.py",
    "bizhome_api.py",
    "bizride_api.py",
    "ethiobiz_identity.py",
    "jobs.py",
    "magala_shop_api.py"
)

Write-Host "BISMALLAH - Deploying Phase D vertical fixes to cloud"
Write-Host "======================================================"
Write-Host ""

# Check if plink and pscp are available
$plinkExists = Get-Command plink -ErrorAction SilentlyContinue
$pscpExists = Get-Command pscp -ErrorAction SilentlyContinue

if (-not $plinkExists -or -not $pscpExists) {
    Write-Host "ERROR: plink.exe or pscp.exe not found."
    Write-Host "Please install PuTTY from: https://www.putty.org/"
    Write-Host ""
    Write-Host "MANUAL DEPLOYMENT INSTRUCTIONS:"
    Write-Host "1. Use WinSCP to upload these files to /root/deploy/ on ${CloudHost}:"
    foreach ($f in $FILES) {
        Write-Host "   - $f"
    }
    Write-Host ""
    Write-Host "2. SSH into the server and run:"
    foreach ($f in $FILES) {
        Write-Host "   docker cp /root/deploy/$f $BACKEND_CONTAINER`:$APP_PATH/$f"
    }
    Write-Host ""
    Write-Host "3. Run migration:"
    Write-Host "   docker exec $BACKEND_CONTAINER /home/frappe/frappe-bench/env/bin/python -c 'from frappe.migrate import SiteMigration; SiteMigration().run(`"ethiobiz.et`")'"
    Write-Host ""
    Write-Host "4. Restart backend:"
    Write-Host "   docker restart $BACKEND_CONTAINER"
    Write-Host ""
    Write-Host "5. Reload nginx:"
    Write-Host "   docker exec $FRONTEND_CONTAINER nginx -s reload"
    exit 1
}

Write-Host "Step 1: Uploading files to cloud host..."
Write-Host ""

# Create deploy directory
plink -batch -pw $PASSWORD $USER@$CloudHost "mkdir -p /root/deploy"

# Upload files
foreach ($f in $FILES) {
    if (Test-Path $f) {
        Write-Host "  Uploading $f..."
        pscp -batch -pw $PASSWORD $f "$USER@$CloudHost:/root/deploy/"
    } else {
        Write-Host "  ERROR: File not found: $f"
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Copying files into backend container..."
Write-Host ""

foreach ($f in $FILES) {
    $cmd = "docker cp /root/deploy/$f $BACKEND_CONTAINER`:$APP_PATH/$f"
    Write-Host "  Copying $f..."
    plink -batch -pw $PASSWORD $USER@$CloudHost $cmd
}

Write-Host ""
Write-Host "Step 3: Running migration..."
Write-Host ""

# Upload migration script
$migrationScript = @"
import os
os.chdir('/home/frappe/frappe-bench/sites')
os.makedirs('../logs', exist_ok=True)
os.makedirs('ethiobiz.et/logs', exist_ok=True)

from frappe.migrate import SiteMigration
migrator = SiteMigration(skip_failing=False, skip_search_index=False)
migrator.run('ethiobiz.et')
print('MIGRATE_DONE')
"@

$migrationScript | Out-File -FilePath "temp_migration.py" -Encoding UTF8
pscp -batch -pw $PASSWORD temp_migration.py "$USER@$CloudHost:/root/"
plink -batch -pw $PASSWORD $USER@$CloudHost "docker cp /root/temp_migration.py $BACKEND_CONTAINER`:/tmp/temp_migration.py"
$output = plink -batch -pw $PASSWORD $USER@$CloudHost "docker exec $BACKEND_CONTAINER /home/frappe/frappe-bench/env/bin/python /tmp/temp_migration.py"
Write-Host $output
plink -batch -pw $PASSWORD $USER@$CloudHost "rm /root/temp_migration.py"
plink -batch -pw $PASSWORD $USER@$CloudHost "docker exec $BACKEND_CONTAINER rm /tmp/temp_migration.py"
Remove-Item temp_migration.py

if ($output -match "MIGRATE_DONE") {
    Write-Host "  Migration completed successfully"
} else {
    Write-Host "  WARNING: Migration may have issues - check output above"
}

Write-Host ""
Write-Host "Step 4: Restarting backend..."
Write-Host ""

plink -batch -pw $PASSWORD $USER@$CloudHost "docker restart $BACKEND_CONTAINER"
Write-Host "  Backend restarted"

Write-Host "  Waiting 10 seconds for backend to start..."
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Step 5: Reloading frontend nginx..."
Write-Host ""

plink -batch -pw $PASSWORD $USER@$CloudHost "docker exec $FRONTEND_CONTAINER nginx -s reload"
Write-Host "  Frontend nginx reloaded"

Write-Host ""
Write-Host "======================================================"
Write-Host "BISMALLAH - Deployment complete!"
Write-Host "Vertical fixes deployed to cloud:"
foreach ($f in $FILES) {
    Write-Host "  ✓ $f"
}
Write-Host ""
Write-Host "Please verify the live site at https://ethiobiz.et"
