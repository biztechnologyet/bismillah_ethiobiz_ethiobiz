# Cloud Deployment Instructions - Phase D Vertical Fixes
## BISMALLAH - Deploying to ethiobiz.et

### Files to Deploy
Copy these 7 Python API files from the local repository to the cloud host:

**Source Location:**
`C:\BISMALLAH ETHIOBIZ.ET CLOUD SYSTEMS INSHA'ALLAH\bismillah_ethiobiz_ethiobiz\bismillah_ethiobiz\`

**Files:**
1. `bizbooking_api.py`
2. `bizhealth_api.py`
3. `bizhome_api.py`
4. `bizride_api.py`
5. `ethiobiz_identity.py`
6. `jobs.py`
7. `magala_shop_api.py`

---

### Step 1: Copy Files to Cloud Host

**Option A: Using SCP (if SSH key is configured)**
```bash
cd "C:\BISMALLAH ETHIOBIZ.ET CLOUD SYSTEMS INSHA'ALLAH\bismillah_ethiobiz_ethiobiz\bismillah_ethiobiz"
scp bizbooking_api.py root@128.140.82.215:/tmp/
scp bizhealth_api.py root@128.140.82.215:/tmp/
scp bizhome_api.py root@128.140.82.215:/tmp/
scp bizride_api.py root@128.140.82.215:/tmp/
scp ethiobiz_identity.py root@128.140.82.215:/tmp/
scp jobs.py root@128.140.82.215:/tmp/
scp magala_shop_api.py root@128.140.82.215:/tmp/
```

**Option B: Using WinSCP or FileZilla**
- Connect to: `128.140.82.215` as `root`
- Upload the 7 files to `/tmp/` directory on the server

---

### Step 2: SSH into Cloud Host and Copy to Container

```bash
ssh root@128.140.82.215
```

Then run these commands:

```bash
# Copy files into backend container
docker cp /tmp/bizbooking_api.py bismallah_ethiobiz_inshaallah-backend-1:/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/
docker cp /tmp/bizhealth_api.py bismallah_ethiobiz_inshaallah-backend-1:/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/
docker cp /tmp/bizhome_api.py bismallah_ethiobiz_inshaallah-backend-1:/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/
docker cp /tmp/bizride_api.py bismallah_ethiobiz_inshaallah-backend-1:/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/
docker cp /tmp/ethiobiz_identity.py bismallah_ethiobiz_inshaallah-backend-1:/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/
docker cp /tmp/jobs.py bismallah_ethiobiz_inshaallah-backend-1:/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/
docker cp /tmp/magala_shop_api.py bismallah_ethiobiz_inshaallah-backend-1:/home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/
```

---

### Step 3: Run Migration

```bash
docker exec bismallah_ethiobiz_inshaallah-backend-1 python -c "from frappe.migrate import SiteMigration; SiteMigration().run('ethiobiz.et')"
```

Expected output should show:
- Migration completed successfully
- No errors (some telephony warnings are OK)

---

### Step 4: Restart Backend

```bash
docker restart bismallah_ethiobiz_inshaallah-backend-1
```

Wait for the container to restart (usually 10-20 seconds).

---

### Step 5: Reload Frontend Nginx

```bash
docker exec bismallah_ethiobiz_inshaallah-frontend-1 nginx -s reload
```

---

### Step 6: Verify Deployment

Test the following endpoints on `https://ethiobiz.et`:

1. **Jobs (`/jobs`)** - Try submitting a job application (should require login)
2. **BizHealth (`/bizhealth`)** - Check for Practo branding (should be removed)
3. **BizHome (`/bizhome`)** - Try requesting a lease (should require login)
4. **Shop (`/shop`)** - Check categories (should load dynamically)
5. **BizFix (`/bizfix`)** - Check categories (should load dynamically)

---

### Rollback Instructions (if needed)

If something goes wrong, you can restore the previous versions:

```bash
# The files are already in the container, but you may want to backup first
docker exec bismallah_ethiobiz_inshaallah-backend-1 cp /home/frappe/frappe-bench/apps/bismillah_ethiobiz/bismillah_ethiobiz/bizbooking_api.py /tmp/bizbooking_api.py.backup
# Repeat for other files...

# Then copy the old versions back and restart
```

---

### What Was Deployed

This deployment includes the following Phase D vertical fixes:

- **BizFix**: Dynamic categories, customer binding, removed fake IDs
- **BizHealth**: Patient/customer binding, company validation
- **BizRide**: Customer binding, company validation, removed hardcoded values
- **BizHome**: Login enforcement, company validation
- **Shop**: Dynamic categories, customer binding for reviews
- **Jobs**: Login enforcement, company/job/user storage
- **Shared Identity Helper**: Enhanced with session_contact_defaults

All changes are committed in Git:
- `b10117d` - BizFix fixes
- `623307e` - Shop fixes
- `e1acfbb` - BizRide and BizHome fixes
- `9c91e03` - BizHealth and Jobs fixes
- `67df325` - Practo/OYO branding removal

---

BISMALLAH - Deployment ready. Please execute the steps above to deploy to production.
