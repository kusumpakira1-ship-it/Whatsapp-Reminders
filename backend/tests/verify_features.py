import sys
import os
import pymysql
from datetime import datetime, date

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
from models import Flock, BookStandard, ProcessedData
from report_generator import generate_daily_reports

def test_flocks():
    print("=== Testing Flocks Database & Calculations ===")
    db = SessionLocal()
    try:
        flocks = db.query(Flock).all()
        print(f"Total Flocks Found: {len(flocks)}")
        today = date(2026, 7, 27)
        for f in flocks:
            days = (today - f.hatch_date).days
            running_weeks = max(0, days // 7)
            print(f"[{f.shed_name}] Hatch: {f.hatch_date} | Initial Chicks: {f.initial_chicks:,} | Batch: {f.batch_id} | Running Weeks: {running_weeks}")
        assert len(flocks) >= 11, "Expected at least 11 pre-seeded flocks"
        print("✅ Flocks verification passed.")
    finally:
        db.close()

def test_standards():
    print("\n=== Testing Book Standards Lookups ===")
    db = SessionLocal()
    try:
        w52 = db.query(BookStandard).filter(BookStandard.week == 52).first()
        if w52:
            print(f"Week 52 Standards -> BP: {w52.expected_production_pct}% | BW: {w52.expected_body_weight_g}g | Feed: {w52.expected_feed_g}g")
            
        w24 = db.query(BookStandard).filter(BookStandard.week == 24).first()
        if w24:
            print(f"Week 24 Standards -> BP: {w24.expected_production_pct}% | BW: {w24.expected_body_weight_g}g | Feed: {w24.expected_feed_g}g")
            
        w3 = db.query(BookStandard).filter(BookStandard.week == 3).first()
        if w3:
            print(f"Week 3 Standards  -> BP: {w3.expected_production_pct}% | BW: {w3.expected_body_weight_g}g | Feed: {w3.expected_feed_g}g")
            
        assert w52 is not None and w24 is not None, "Book standards missing expected weeks"
        print("✅ Standards verification passed.")
    finally:
        db.close()

def test_daily_report_generation():
    print("\n=== Testing Daily Summary Report Output ===")
    from models import RawMessage
    db = SessionLocal()
    msg_id = f"test_msg_{int(datetime.now().timestamp())}"
    try:
        # Create raw message first
        raw_msg = RawMessage(message_id=msg_id, sender="919999999999", timestamp=datetime.now(), message_type="text", full_webhook_json={})
        db.add(raw_msg)
        db.commit()
        
        # Add mock processed data records
        mock1 = ProcessedData(message_id=msg_id, shead_name='Shead 1', category='egg_collection_1', quantity=18126, unit='eggs', processed_time=datetime.now())
        mock2 = ProcessedData(message_id=msg_id, shead_name='Shead 1', category='mortality', quantity=8, unit='', processed_time=datetime.now())
        mock3 = ProcessedData(message_id=msg_id, shead_name='Chick Whites', category='mortality', quantity=2, unit='', processed_time=datetime.now())
        mock4 = ProcessedData(message_id=msg_id, shead_name='Chick Brownie', category='mortality', quantity=1, unit='', processed_time=datetime.now())
        mock5 = ProcessedData(message_id=msg_id, shead_name='Shead 1', category='hen_weight', quantity=1.516, unit='kg', processed_time=datetime.now())
        mock6 = ProcessedData(message_id=msg_id, shead_name='Shead 1', category='feed', quantity=45, unit='bags', processed_time=datetime.now())
        
        db.add_all([mock1, mock2, mock3, mock4, mock5, mock6])
        db.commit()
    finally:
        db.close()


    try:
        pdf_path, summary_text = generate_daily_reports()
        print("Report Summary Output Preview:")
        print("="*60)
        print(summary_text)
        print("="*60)
        assert "DAILY FARM SUMMARY" in summary_text, "Daily Farm Summary header missing"
        assert "Shed-wise mortality:" in summary_text, "Shed-wise mortality missing"
        assert "SED_AGE_PRODUCTION-AP-BP" in summary_text, "Production comparison missing"
        assert "Birds Weight Comparison:" in summary_text, "Weight comparison missing"
        print("✅ Daily report generation & comparative sections verification passed.")
    finally:
        db = SessionLocal()
        db.query(ProcessedData).filter(ProcessedData.message_id == msg_id).delete()
        db.query(RawMessage).filter(RawMessage.message_id == msg_id).delete()
        db.commit()
        db.close()



if __name__ == "__main__":
    test_flocks()
    test_standards()
    test_daily_report_generation()
