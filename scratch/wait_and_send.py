import sys, requests, json, time
sys.path.insert(0, 'backend')
from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message

print("Waiting for WAHA session to reach WORKING status...")
for i in range(30):
    try:
        r = requests.get('http://localhost:3000/api/sessions/default', headers={'X-Api-Key': '123'}, timeout=5)
        st = r.json().get('status')
        print(f"Attempt {i+1}: Status = {st}")
        if st == 'WORKING':
            break
        elif st == 'STOPPED' or st == 'FAILED':
            print("Session stopped/failed. Triggering start...")
            requests.post('http://localhost:3000/api/sessions/default/start', headers={'X-Api-Key': '123'}, timeout=5)
    except Exception as e:
        print(f"Attempt {i+1} exception:", e)
    time.sleep(3)

data = evaluate_attendance_for_date('2026-09-17')
report_text = generate_attendance_summary_message(data)

payload = {
    'chatId': '917259510983@c.us',
    'text': report_text,
    'session': 'default'
}

resp = requests.post('http://localhost:3000/api/sendText', json=payload, headers={'X-Api-Key': '123'}, timeout=15)
print("WAHA Send Status Code:", resp.status_code)
print("WAHA Send Response:", resp.text)
