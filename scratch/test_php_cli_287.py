"""
Test PHP API output for Reminder ID 287 (Balaji) directly
"""

import sys, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8')

# Run PHP CLI script locally to execute index.php for route=reminders
import subprocess

cmd = ['php', '-r', '''
$_GET["route"] = "reminders";
$_SERVER["REQUEST_METHOD"] = "GET";
chdir(r"c:\\Users\\sunfra\\Desktop\\Whatsapp New Reminders");
require "index.php";
''']

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
stdout, stderr = p.communicate()

print("PHP CLI Execution Output:")
try:
    data = json.loads(stdout)
    print(f"Total Reminders returned: {len(data)}")
    for r in data:
        if r.get('id') == 287 or 'balaji' in str(r.get('person_name')).lower():
            print("\n=== BALAJI REMINDER (ID 287) LIVE RESULT ===")
            print(f"ID: {r.get('id')}")
            print(f"Person: {r.get('person_name')}")
            print(f"Status: {r.get('status')}")
            print(f"is_submitted: {r.get('is_submitted')}")
            print(f"submitted_reports: {r.get('submitted_reports')}")
            print(f"missing_reports: {r.get('missing_reports')}")
            print(f"verification_details: {r.get('verification_details')}")
except Exception as e:
    print("Error parsing JSON:", e)
    print("Stdout:", stdout[:500])
    print("Stderr:", stderr[:500])
