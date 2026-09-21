import requests, json

url = 'http://localhost:3000/api/default/chats/120363410545216320@g.us/messages?limit=200'
resp = requests.get(url, headers={'X-Api-Key': '123'})
msgs = resp.json()

senders = {}
for m in msgs:
    participant = m.get('participant') or m.get('author') or m.get('_data', {}).get('author') or m.get('_data', {}).get('key', {}).get('participant') or m.get('from') or ''
    body = (m.get('body') or '').replace('\n', ' ')
    ts = m.get('timestamp')
    if participant not in senders:
        senders[participant] = []
    senders[participant].append((ts, body))

print(f"Total unique senders in Sunfra Mudah chat: {len(senders)}")
for s, history in senders.items():
    print(f"Sender: {s:<30} | Last msg: {history[0]}")
