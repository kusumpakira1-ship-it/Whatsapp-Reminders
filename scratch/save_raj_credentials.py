import os
import sys
import json
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from zoho_service import save_setting, get_setting

settings_to_save = {
    "raj_farms_client_id": "1000.B9KFRFFVSCJ0SN1DJ0PCZEFK4P5ANE",
    "raj_farms_client_secret": "67726abb28b0e5b870d2996106d02c8047f7610f4e",
    "raj_farms_refresh_token": "1000.7c59fea5714f993ac878b37d256e3783.aa78348ecdeb3f906d825cbc130f0d6b",
    "raj_farms_org_id": "904503869",
    "raj_farms_access_token": "1000.8d220264e57b0769d33d563af8ad6e60.00c8c5adc99a673bed450fe928460800",
    "raj_farms_access_expiry": str(time.time() + 3500)
}

for k, v in settings_to_save.items():
    save_setting(k, v)
    print(f"Saved {k} successfully!", flush=True)
