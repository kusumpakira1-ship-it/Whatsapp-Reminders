import os
import re
import pandas as pd
from datetime import datetime, date, timedelta, timezone
from database import SessionLocal
from models import ProcessedData, Flock, BookStandard
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from report_formatter import build_whatsapp_summary, generate_pdf

IST = timezone(timedelta(hours=5, minutes=30))

def get_date_range(range_type: str):
    now_ist = datetime.now(IST)
    today = now_ist.date()
    
    if range_type == 'weekly':
        return today - timedelta(days=7), today
    elif range_type == 'monthly':
        return today - timedelta(days=30), today
    elif range_type == 'yearly':
        return today - timedelta(days=365), today
    else:
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(range_type, fmt).date()
                return parsed, parsed
            except ValueError:
                continue
        return today, today


def _generate_empty_pdf(pdf_path: str, message: str):
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('EmptyTitle', parent=styles['Heading1'], alignment=1, fontSize=16, textColor=colors.HexColor('#1b4332'), spaceAfter=20)
    msg_style = ParagraphStyle('EmptyMsg', parent=styles['Normal'], alignment=1, fontSize=12, textColor=colors.darkgrey)
    
    story = [
        Paragraph("<b>Daily Farm Summary</b>", title_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2d6a4f'), spaceBefore=5, spaceAfter=20),
        Paragraph(message.replace('📭 ', ''), msg_style)
    ]
    doc.build(story)


def generate_custom_report(range_type: str = 'daily'):
    db = SessionLocal()
    start_date, end_date = get_date_range(range_type)

    data = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{start_date} 00:00:00",
        ProcessedData.processed_time <= f"{end_date} 23:59:59"
    ).all()

    os.makedirs("/app/media/reports", exist_ok=True)
    import glob
    for old_file in glob.glob(f"/app/media/reports/{range_type.capitalize()}_Report_*"):
        try:
            os.remove(old_file)
        except Exception:
            pass

    timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M")
    pdf_path = f"/app/media/reports/{range_type.capitalize()}_Report_{timestamp}.pdf"

    if not data:
        db.close()
        msg = f"📭 No farm data collected for {start_date.strftime('%d %b %Y')}."
        _generate_empty_pdf(pdf_path, msg)
        return pdf_path, msg

    df = pd.DataFrame([{
        'shead_name':    d.shead_name or '',
        'category':      d.category or 'unknown',
        'quantity':      float(d.quantity) if d.quantity else 0,
        'unit':          d.unit or '',
        'amount':        float(d.amount) if d.amount else 0.0,
        'notes':         d.notes or '',
        'processed_text': '',
        'sender':        d.sender or '',
        'group_name':    d.group_name or '',
        'time':          d.processed_time.strftime("%H:%M") if d.processed_time else '',
    } for d in data])

    df = df[df['category'] != 'unknown']
    if df.empty:
        db.close()
        msg = f"📭 No classifiable farm data found for {start_date.strftime('%d %b %Y')}."
        _generate_empty_pdf(pdf_path, msg)
        return pdf_path, msg
        
    # Dynamically fetch historical configuration (birds, egg rate, feed cost) up to end_date
    birds_map = {}
    latest_birds = db.query(ProcessedData.shead_name, ProcessedData.quantity).filter(
        ProcessedData.category == 'production',
        ProcessedData.quantity > 1000,
        ProcessedData.processed_time <= f"{end_date} 23:59:59"
    ).order_by(ProcessedData.processed_time.desc()).all()
    
    for shed, qty in latest_birds:
        if shed:
            shed_str = str(shed).replace('Shead', 'Shed').strip()
            if shed_str not in birds_map:
                birds_map[shed_str] = int(qty)

    default_egg_rate = 5.20
    latest_sale = db.query(ProcessedData).filter(
        ProcessedData.category == 'sales',
        ProcessedData.quantity > 0,
        ProcessedData.amount > 0,
        ProcessedData.processed_time <= f"{end_date} 23:59:59"
    ).order_by(ProcessedData.processed_time.desc()).first()
    
    if latest_sale:
        qty = float(latest_sale.quantity)
        amt = float(latest_sale.amount)
        unit = str(latest_sale.unit).lower()
        eggs = qty * 30 if 'tray' in unit else qty
        if eggs > 0:
            default_egg_rate = amt / eggs

    default_feed_cost_ton = 35000.0
    latest_feed = db.query(ProcessedData).filter(
        ProcessedData.category.in_(['feed', 'raw_material']),
        ProcessedData.quantity > 0,
        ProcessedData.amount > 0,
        ProcessedData.processed_time <= f"{end_date} 23:59:59"
    ).order_by(ProcessedData.processed_time.desc()).first()
    
    if latest_feed:
        qty = float(latest_feed.quantity)
        amt = float(latest_feed.amount)
        unit = str(latest_feed.unit).lower()
        feed_mt = 0
        if 'kg' in unit: feed_mt = qty / 1000.0
        elif 'bag' in unit: feed_mt = qty * 0.05
        elif 'mt' in unit or 'ton' in unit: feed_mt = qty
        else: feed_mt = qty * 0.05 if qty < 500 else qty / 1000.0
        if feed_mt > 0:
            default_feed_cost_ton = amt / feed_mt

    # -------------------------------------------------------------
    # Generate Comparative Insights for Daily Report
    # -------------------------------------------------------------
    comparative_insights = ""
    if range_type == 'daily' or start_date == end_date:
        try:
            from sqlalchemy import func
            
            flocks = db.query(Flock).filter(Flock.status == 'active').all()
            
            # 1. Shed-Wise Mortality
            mort_lines = ["💀 *Shed-Wise Mortality*", "```"]
            total_mort = 0
            
            ordered_sheds = [f"Shead {i}" for i in range(1, 10)]
            m_map = {}
            for sname in ordered_sheds:
                shed_norm = sname.replace('Shead', 'Shed').strip()
                shed_alt = sname.replace('Shed', 'Shead').strip()
                
                mort_qty = float(db.query(func.sum(ProcessedData.quantity)).filter(
                    ProcessedData.category == 'mortality',
                    ProcessedData.shead_name.in_([shed_norm, shed_alt]),
                    func.date(ProcessedData.processed_time) == start_date
                ).scalar() or 0)
                
                short_name = sname.replace('Shead ', '')
                m_map[short_name] = int(mort_qty)
                total_mort += int(mort_qty)
                
            chick_whites_mort = float(db.query(func.sum(ProcessedData.quantity)).filter(
                ProcessedData.category == 'mortality',
                ProcessedData.shead_name == 'Chick Whites',
                func.date(ProcessedData.processed_time) == start_date
            ).scalar() or 0)
            
            chick_brownie_mort = float(db.query(func.sum(ProcessedData.quantity)).filter(
                ProcessedData.category == 'mortality',
                ProcessedData.shead_name == 'Chick Brownie',
                func.date(ProcessedData.processed_time) == start_date
            ).scalar() or 0)
            
            for i in range(1, 10):
                mort_lines.append(f"{i}-{m_map.get(str(i), 0)}")
                
            mort_lines.append("Chick")
            mort_lines.append(f"Whites; {int(chick_whites_mort)}")
            mort_lines.append(f"Brownie; {int(chick_brownie_mort)}")
            total_mort += int(chick_whites_mort) + int(chick_brownie_mort)
            mort_lines.append(f"Totall mortality; {total_mort}")
            mort_lines.append("```")
            
            comparative_insights += "\n".join(mort_lines) + "\n\n"
            
            # 2. Production (AP-BP)
            prod_lines = ["🥚 *SED_AGE_PRODUCTION-AP-BP*", "```"]
            for f in flocks:
                if not f.shed_name.lower().startswith('shead') and not f.shed_name.lower().startswith('shed'):
                    continue
                    
                days = (start_date - f.hatch_date).days
                running_weeks = max(1, days // 7)
                
                shed_norm = f.shed_name.replace('Shead', 'Shed').strip()
                shed_alt = f.shed_name.replace('Shed', 'Shead').strip()
                
                eggs_collected = float(db.query(func.sum(ProcessedData.quantity)).filter(
                    ProcessedData.category.in_(['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']),
                    ProcessedData.shead_name.in_([shed_norm, shed_alt]),
                    func.date(ProcessedData.processed_time) == start_date
                ).scalar() or 0)
                
                trays = eggs_collected / 30.0
                
                mort_cum = float(db.query(func.sum(ProcessedData.quantity)).filter(
                    ProcessedData.category == 'mortality',
                    ProcessedData.shead_name.in_([shed_norm, shed_alt]),
                    ProcessedData.processed_time >= f.hatch_date,
                    ProcessedData.processed_time <= f"{start_date} 23:59:59"
                ).scalar() or 0)
                live_birds = max(0, f.initial_chicks - int(mort_cum))
                
                ap = (eggs_collected / live_birds * 100.0) if live_birds > 0 else 0.0
                
                standard = db.query(BookStandard).filter(BookStandard.week == running_weeks).first()
                bp = float(standard.expected_production_pct) if standard else 0.0
                
                short_name = f.shed_name.replace('Shead ', '').replace('Shed ', '')
                if trays > 0 or live_birds > 0:
                    prod_lines.append(f"{short_name}._ {running_weeks}._ {trays:.2f}_{ap:.0f}%-{bp:.0f}%")
                else:
                    prod_lines.append(f"{short_name}_0")
                    
            prod_lines.append("```")
            comparative_insights += "\n".join(prod_lines) + "\n\n"
            
            # 3. Birds Weight
            weight_lines = ["⚖️ *Birds Weight Comparison*", "```"]
            for f in flocks:
                is_laying = f.shed_name.lower().startswith('shead') or f.shed_name.lower().startswith('shed')
                is_chick = f.shed_name.lower().startswith('chick')
                
                if not is_laying and not is_chick:
                    continue
                    
                days = (start_date - f.hatch_date).days
                running_weeks = max(1, days // 7)
                
                shed_norm = f.shed_name.replace('Shead', 'Shed').strip()
                shed_alt = f.shed_name.replace('Shed', 'Shead').strip()
                
                actual_wt = db.query(ProcessedData.quantity).filter(
                    ProcessedData.category == 'hen_weight',
                    ProcessedData.shead_name.in_([shed_norm, shed_alt]),
                    func.date(ProcessedData.processed_time) == start_date
                ).order_by(ProcessedData.processed_time.desc()).first()
                
                actual_wt_val = float(actual_wt[0]) if actual_wt else 0.0
                
                standard = db.query(BookStandard).filter(BookStandard.week == running_weeks).first()
                book_wt_g = standard.expected_body_weight_g if standard else 0
                
                if actual_wt_val > 0 and book_wt_g > 0:
                    actual_wt_g = actual_wt_val * 1000.0 if actual_wt_val < 10 else actual_wt_val
                    diff = int(actual_wt_g - book_wt_g)
                    sign = "🟢" if diff >= 0 else "🔴"
                    
                    weight_lines.append(
                        f"{f.shed_name}: Actual: {actual_wt_g/1000.0:.3f}, Book: {book_wt_g/1000.0:.3f}, {abs(diff)} Gms {sign}"
                    )
                else:
                    weight_lines.append(f"{f.shed_name}: No Weight Data")
                    
            weight_lines.append("```")
            comparative_insights += "\n".join(weight_lines) + "\n"
            
        except Exception as comp_err:
            print(f"Error compiling comparative insights: {comp_err}")

    db.close()
    summary_text = build_whatsapp_summary(df, range_type, start_date, end_date, birds_map, default_egg_rate, default_feed_cost_ton)
    
    if comparative_insights:
        summary_text += comparative_insights

    generate_pdf(pdf_path, df, range_type, start_date, end_date, birds_map, default_egg_rate, default_feed_cost_ton)

    return pdf_path, summary_text



def generate_daily_reports():
    return generate_custom_report('daily')
