import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = ["docker", "logs", "--timestamps", "--since", "2026-11-05T12:00:00Z", "--until", "2026-11-06T06:00:00Z", "fastapi_backend"]
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

lines = [l for l in (res.stdout.split('\n') + res.stderr.split('\n')) if l.strip()]
print(f"Total lines between 2026-11-05 12:00 UTC and 2026-11-06 06:00 UTC: {len(lines)}")
if lines:
    print("First 10 lines:")
    for l in lines[:10]:
        print(l)
    print("\nLast 10 lines:")
    for l in lines[-10:]:
        print(l)
