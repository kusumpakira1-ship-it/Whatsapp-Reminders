import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(repo_root, 'backend')
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

os.environ["WAHA_URL"] = "http://localhost:3000"
from backend.config import settings
settings.WAHA_URL = "http://localhost:3000"

from report_generator_godown import generate_godown_report
from sunfra_pandl_report import generate_and_send_sunfra_pandl_report
from egg_market_analyzer import send_daily_egg_market_pdf_job
from report_generator import generate_custom_report
from waha_service import send_waha_file

TARGET_PHONE = "917259510983@c.us"

print(f"=== DISPATCHING EGG MARKET ANALYSIS PDF TO {TARGET_PHONE} ===")

# 3. Daily Egg Price & Market Analysis PDF Report
print("\n[3/4] Sending Egg Price & Market Analysis PDF Report...")
try:
    send_daily_egg_market_pdf_job()
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

print(f"\n=== COMPLETE ===")
