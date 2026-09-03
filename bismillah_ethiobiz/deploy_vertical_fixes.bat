@echo off
REM Deployment script for Phase D vertical fixes using Windows OpenSSH
REM BISMALLAH - Deploys API files to cloud container

set HOST=128.140.82.215
set USER=root
set PASSWORD=bizTECHNOLOGY@123
set BACKEND_CONTAINER=bismallah_ethiobiz_inshaallah-backend-1
set FRONTEND_CONTAINER=bismallah_ethiobiz_inshaallah-frontend-1
set APP_PATH=/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz

echo BISMALLAH - Deploying Phase D vertical fixes to cloud
echo ========================================================

echo.
echo Step 1: Connecting to cloud host and uploading files...
echo.

REM Use plink if available, otherwise manual instructions
where plink >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using plink for SSH operations...
    
    REM Upload files
    plink -batch -pw %PASSWORD% %USER%@%HOST% "mkdir -p /root/deploy"
    
    for %%f in (bizbooking_api.py bizhealth_api.py bizhome_api.py bizride_api.py ethiobiz_identity.py jobs.py magala_shop_api.py) do (
        echo Uploading %%f...
        pscp -batch -pw %PASSWORD% %%f %USER%@%HOST%:/root/deploy/
    )
    
    echo.
    echo Step 2: Copying files into backend container...
    echo.
    
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/deploy/bizbooking_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizbooking_api.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/deploy/bizhealth_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizhealth_api.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/deploy/bizhome_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizhome_api.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/deploy/bizride_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizride_api.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/deploy/ethiobiz_identity.py %BACKEND_CONTAINER%:%APP_PATH%/ethiobiz_identity.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/deploy/jobs.py %BACKEND_CONTAINER%:%APP_PATH%/jobs.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/deploy/magala_shop_api.py %BACKEND_CONTAINER%:%APP_PATH%/magala_shop_api.py"
    
    echo.
    echo Step 3: Running migration...
    echo.
    
    pscp -batch -pw %PASSWORD% migrate_script.py %USER%@%HOST%:/root/
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker cp /root/migrate_script.py %BACKEND_CONTAINER%:/tmp/migrate_script.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker exec %BACKEND_CONTAINER% /home/frappe/frappe-bench/env/bin/python /tmp/migrate_script.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "rm /root/migrate_script.py"
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker exec %BACKEND_CONTAINER% rm /tmp/migrate_script.py"
    
    echo.
    echo Step 4: Restarting backend...
    echo.
    
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker restart %BACKEND_CONTAINER%"
    
    echo Waiting 10 seconds for backend to start...
    timeout /t 10 /nobreak
    
    echo.
    echo Step 5: Reloading frontend nginx...
    echo.
    
    plink -batch -pw %PASSWORD% %USER%@%HOST% "docker exec %FRONTEND_CONTAINER% nginx -s reload"
    
    echo.
    echo ========================================================
    echo BISMALLAH - Deployment complete!
    echo Please verify the live site at https://ethiobiz.et
    
) else (
    echo plink.exe not found. Please install PuTTY or use manual deployment.
    echo.
    echo MANUAL DEPLOYMENT INSTRUCTIONS:
    echo 1. Use WinSCP to upload these files to /root/deploy/ on %HOST%:
    echo    - bizbooking_api.py
    echo    - bizhealth_api.py
    echo    - bizhome_api.py
    echo    - bizride_api.py
    echo    - ethiobiz_identity.py
    echo    - jobs.py
    echo    - magala_shop_api.py
    echo.
    echo 2. SSH into the server and run:
    echo    docker cp /root/deploy/bizbooking_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizbooking_api.py
    echo    docker cp /root/deploy/bizhealth_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizhealth_api.py
    echo    docker cp /root/deploy/bizhome_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizhome_api.py
    echo    docker cp /root/deploy/bizride_api.py %BACKEND_CONTAINER%:%APP_PATH%/bizride_api.py
    echo    docker cp /root/deploy/ethiobiz_identity.py %BACKEND_CONTAINER%:%APP_PATH%/ethiobiz_identity.py
    echo    docker cp /root/deploy/jobs.py %BACKEND_CONTAINER%:%APP_PATH%/jobs.py
    echo    docker cp /root/deploy/magala_shop_api.py %BACKEND_CONTAINER%:%APP_PATH%/magala_shop_api.py
    echo.
    echo 3. Run migration:
    echo    docker exec %BACKEND_CONTAINER% /home/frappe/frappe-bench/env/bin/python /tmp/migrate_script.py
    echo.
    echo 4. Restart backend:
    echo    docker restart %BACKEND_CONTAINER%
    echo.
    echo 5. Reload nginx:
    echo    docker exec %FRONTEND_CONTAINER% nginx -s reload
)

pause
