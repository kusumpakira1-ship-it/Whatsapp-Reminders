import requests
import base64
import os

url = 'http://waha:3000/api/sendFile'
headers = {'Accept': 'application/json', 'X-Api-Key': '123'}

with open('/app/test_table.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

payload = {
    'chatId': '917259510983@c.us',
    'file': {
        'mimetype': 'image/png',
        'filename': 'test_table.png',
        'url': f'data:image/png;base64,{b64}'
    },
    'caption': 'Table Image Test',
    'session': 'default'
}

resp = requests.post(url, json=payload, headers=headers, timeout=30)
print("STATUS CODE:", resp.status_code)
print("RESPONSE TEXT:\n", resp.text)
