import requests
import base64
import os

url = 'http://waha:3000/api/sendFile'
headers = {'Accept': 'application/json', 'X-Api-Key': '123'}

def send_file_b64(file_path: str, caption: str, mimetype: str):
    with open(file_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        'chatId': '917259510983@c.us',
        'file': {
            'mimetype': mimetype,
            'filename': os.path.basename(file_path),
            'url': f'data:{mimetype};base64,{b64}'
        },
        'caption': caption,
        'session': 'default'
    }
    
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    print(f"Sending {os.path.basename(file_path)} ({len(b64)} b64 bytes) -> Status: {resp.status_code}")
    print("Response:", resp.text)
    return resp.status_code in (200, 201)

if __name__ == "__main__":
    png_ok = send_file_b64('/app/test_table.png', '📊 Sunfra Farms P&L Table Image', 'image/png')
    pdf_ok = send_file_b64('/app/Sunfra_PL_Report_2026-08-05.pdf', '📄 Sunfra Farms P&L Report PDF', 'application/pdf')
    print(f"PNG Dispatch: {png_ok} | PDF Dispatch: {pdf_ok}")
