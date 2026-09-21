import json
import os

if os.path.exists('messages.json'):
    with open('messages.json', 'r', encoding='utf-8') as f:
        try:
            msgs = json.load(f)
            print(f"Total messages in messages.json: {len(msgs)}")
            msgs_today = [m for m in msgs if m.get('timestamp', '').startswith('2026-09-17')]
            print(f"Total messages today (17 Sep) in messages.json: {len(msgs_today)}")
            for m in msgs_today:
                print(f"[{m.get('timestamp')}] Group: [{m.get('group_name')}] | Sender: {m.get('sender')} | Text: '{m.get('raw_text')}'")
        except Exception as e:
            print("JSON parse error:", e)
else:
    print("messages.json does not exist.")
