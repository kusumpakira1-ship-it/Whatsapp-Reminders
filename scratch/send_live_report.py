import sys, requests, json, time
sys.path.insert(0, 'backend')
from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message

# Check WAHA session status
try:
    r_status = requests.get('http://localhost:3000/api/sessions/default', headers={'X-Api-Key': '123'}, timeout=5)
    print("WAHA Session Status:", r_status.status_code, r_status.json().get('status'))
    if r_status.json().get('status') != 'WORKING':
        print("Restarting WAHA session...")
        requests.post('http://localhost:3000/api/sessions/default/restart', headers={'X-Api-Key': '123'}, timeout=10)
        time.sleep(5)
except Exception as e:
    print("Session check exception:", e)

# Evaluate and send report
data = evaluate_attendance_for_date('2026-09-17')
report_text = generate_attendance_summary_message(data)

print("Report to send:")
print(report_text)

payload = {
    'chatId': '917259510983@c.us',
    'text': report_text,
    'session': 'default'
}

resp = requests.post('http://localhost:3000/api/sendText', json=payload, headers={'X-Api-Key': '123'}, timeout=15)
print("WAHA Send Status Code:", resp.status_code)
print("WAHA Send Response:", resp.text)
