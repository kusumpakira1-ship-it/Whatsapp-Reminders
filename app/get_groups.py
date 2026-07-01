import requests

try:
    res = requests.get('http://waha:3000/api/default/groups', headers={'X-Api-Key': '123'})
    data = res.json()
    print("Found Groups:")
    if isinstance(data, list):
        for g in data:
            print(f"ID: {g.get('id')}, Name: {g.get('subject') or g.get('name')}")
    elif isinstance(data, dict):
        for k, v in data.items():
            print(f"ID: {k}, Name: {v.get('subject') or v.get('name')}")
except Exception as e:
    print(f"Error: {e}")
