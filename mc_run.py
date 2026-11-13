import subprocess, os
os.chdir('/home/frappe/frappe-bench')
result = subprocess.run(
    ['/home/frappe/frappe-bench/env/bin/python', '-m', 'frappe.utils.bench_helper', 'migrate', '--site', 'ethiobiz.et'],
    capture_output=True, text=True, timeout=300
)
print(result.stdout)
if result.returncode != 0:
    print('STDERR:', result.stderr)
print('EXIT_CODE:', result.returncode)
print('MIGRATE_DONE')
