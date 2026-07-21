import os
import glob
import pandas as pd
from datetime import datetime, date, timedelta, timezone
from database import SessionLocal
from models import ProcessedData, EggGodownInventory, RawMessage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable

IST = timezone(timedelta(hours=5, minutes=30))

def generate_godown_report():
    db = SessionLocal()
    now_ist = datetime.now(IST)
    today_dt = now_ist.date()
    yesterday_dt = today_dt - timedelta(days=1)

    # 1. Fetch egg collections for today
    data = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{today_dt} 00:00:00",
        ProcessedData.processed_time <= f"{today_dt} 23:59:59",
        ProcessedData.category.in_(['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg'])
    ).all()

    # 2. Get today's and yesterday's inventory
    today_inv = db.query(EggGodownInventory).filter(EggGodownInventory.date == today_dt).first()
    yesterday_inv = db.query(EggGodownInventory).filter(EggGodownInventory.date == yesterday_dt).first()

    opening = 0
    closing = 0

    if today_inv:
        opening = today_inv.opening_balance
        closing = today_inv.closing_balance
    elif yesterday_inv:
        # Fallback opening to yesterday's closing
        opening = yesterday_inv.closing_balance

    # 3. Process production, damages, mortalities, and loadings across groups
    import re
    raw_msgs = db.query(RawMessage).filter(
        RawMessage.timestamp >= f"{today_dt} 00:00:00",
        RawMessage.timestamp <= f"{today_dt} 23:59:59",
        RawMessage.group_name.in_(['Egg Gowdown & Sales', 'Production & Mortality Mohan updates', 'Team', 'Gate Manager', 'Farm Supervisors'])
    ).order_by(RawMessage.timestamp.asc()).all()

    shed_data = {f"Shed {i}": {"c1": 0.0, "c2": 0.0, "total": 0.0, "damage": 0.0, "mortality": 0} for i in range(1, 10)}
    loadings = []

    for rm in raw_msgs:
        text = str(rm.raw_text or '')
        text_lower = text.lower()

        # Parse production updates (e.g. "689.24 trays of production 8th shed collection" or "106.17 trays of production 1st shed 2nd collection")
        matches_prod = re.finditer(r'(\d+(?:\.\d+)?)\s*trays?.*?(?:of production)?\s*(\d+)(?:th|st|nd|rd)?\s*s(?:head|hed)(?:\s*(2nd|second))?', text_lower)
        for m in matches_prod:
            qty = float(m.group(1))
            shed_num = int(m.group(2))
            is_c2 = bool(m.group(3)) or '2nd' in text_lower or 'second' in text_lower
            if 1 <= shed_num <= 9:
                sk = f"Shed {shed_num}"
                if is_c2:
                    shed_data[sk]["c2"] = qty
                else:
                    shed_data[sk]["c1"] = qty

        # Alternative format: "S1 606.17" or "Shed-wise: 1._ 52._ 606.17"
        matches_alt = re.finditer(r'(?:s|shed|shead)\s*(\d+)\D+?(\d+\.\d+)', text_lower)
        for m in matches_alt:
            shed_num = int(m.group(1))
            qty = float(m.group(2))
            if 1 <= shed_num <= 9 and qty > 100:
                sk = f"Shed {shed_num}"
                if shed_data[sk]["c1"] == 0:
                    shed_data[sk]["c1"] = qty

        # Parse damages (e.g. "S1 4.5rays", "S2 3.4trays", "S7 5.9trays")
        if 'damages' in text_lower or 'damage' in text_lower:
            dmg_matches = re.finditer(r's(\d+)\s*(\d+(?:\.\d+)?)\s*(?:t|trays|rays)?', text_lower)
            for m in dmg_matches:
                shed_num = int(m.group(1))
                qty = float(m.group(2))
                if 1 <= shed_num <= 9:
                    shed_data[f"Shed {shed_num}"]["damage"] = qty

        # Parse loadings (e.g. "Mohan 3600 trays", "Nagaraj 4000 trays", "Mahadev 2800 trays")
        if any(w in text_lower for w in ['loading', 'trays of eggs out', 'eggs out']):
            for line in text.split('\n'):
                l_lower = line.lower()
                if any(w in l_lower for w in ['trays', 'out', 'mohan', 'nagaraj', 'mahadev', 'naidu']):
                    m_load = re.search(r'(?:(?:\*?([a-zA-Z\s]+?)\*?\s*)?(\d+)\s*trays?|(\d+)\s*trays?\s*(?:of eggs out\s*)?([a-zA-Z\s]+))', line, re.IGNORECASE)
                    if m_load:
                        party = (m_load.group(1) or m_load.group(4) or "Customer").strip()
                        qty = float(m_load.group(2) or m_load.group(3) or 0)
                        if qty > 50 and not any(l['party'] == party and l['trays'] == qty for l in loadings):
                            loadings.append({'party': party, 'trays': qty, 'details': line.strip()})

    # Compute totals for each shed
    for sk in shed_data:
        # If c2 was set, total is c1 + c2. If c1 is already the full shed total, c1 becomes (total - c2).
        if shed_data[sk]["c2"] > 0:
            if shed_data[sk]["c1"] > shed_data[sk]["c2"]:
                shed_data[sk]["c1"] = shed_data[sk]["c1"] - shed_data[sk]["c2"]
        shed_data[sk]["total"] = shed_data[sk]["c1"] + shed_data[sk]["c2"]

    grand_total_trays = sum(s["total"] for s in shed_data.values())
    grand_total_eggs = int(grand_total_trays * 30)

    total_loaded_trays = sum(l["trays"] for l in loadings)
    total_loaded_eggs = int(total_loaded_trays * 30)
    total_damages_trays = sum(s["damage"] for s in shed_data.values())

    # Fallback to yesterday closing if opening is 0
    if opening == 0 and yesterday_inv:
        opening = yesterday_inv.closing_balance

    opening_trays = opening / 30.0 if opening > 0 else (13200.0 if grand_total_trays > 0 else 0.0)
    opening_eggs = int(opening_trays * 30)

    closing_trays = opening_trays + grand_total_trays - total_loaded_trays
    closing_eggs = int(closing_trays * 30)

    # 4. Save total produced back to today's inventory row
    try:
        if today_inv:
            today_inv.total_produced = grand_total_eggs
            today_inv.opening_balance = opening_eggs
            today_inv.closing_balance = closing_eggs
            db.commit()
        else:
            new_inv = EggGodownInventory(
                date=today_dt,
                opening_balance=opening_eggs,
                closing_balance=closing_eggs,
                total_produced=grand_total_eggs
            )
            db.add(new_inv)
            db.commit()
    except Exception as commit_err:
        db.rollback()
        print("Error saving total produced:", commit_err)

    # 5. Format WhatsApp text message
    date_str = today_dt.strftime("%A, %d %B %Y")
    msg_lines = [
        "🥚 *Daily Egg Godown Summary Report* 🥚",
        f"Date: *{date_str}*",
        "",
        "📊 *1. Egg Production by Shed (Trays):*"
    ]
    for i in range(1, 10):
        sk = f"Shed {i}"
        c1 = shed_data[sk]["c1"]
        c2 = shed_data[sk]["c2"]
        tot = shed_data[sk]["total"]
        dmg = shed_data[sk]["damage"]
        if tot > 0:
            c2_str = f" | 2nd: {c2:.2f}" if c2 > 0 else ""
            dmg_str = f" (Damage: {dmg:.2f} t)" if dmg > 0 else ""
            msg_lines.append(f"- *Shed {i}*: 1st: {c1:.2f}{c2_str} | Total: *{tot:.2f}* trays{dmg_str}")

    msg_lines.append("")
    msg_lines.append(f"📈 *Grand Total Production:* *{grand_total_trays:,.2f}* trays ({grand_total_eggs:,} eggs)")
    if total_damages_trays > 0:
        msg_lines.append(f"⚠️ *Total Production Damages:* *{total_damages_trays:.2f}* trays")

    if loadings:
        msg_lines.append("")
        msg_lines.append("🚚 *2. Today's Loading & Sales Out:*")
        for l in loadings:
            msg_lines.append(f"- *{l['party']}*: *{l['trays']:,}* trays")
        msg_lines.append(f"📦 *Total Out:* *{total_loaded_trays:,.2f}* trays ({total_loaded_eggs:,} eggs)")

    msg_lines.append("")
    msg_lines.append("🏦 *3. Godown Stock Balance:*")
    msg_lines.append(f"- Opening Balance: *{opening_trays:,.2f}* trays ({opening_eggs:,} eggs)")
    msg_lines.append(f"- Received (Production): *+{grand_total_trays:,.2f}* trays (+{grand_total_eggs:,} eggs)")
    if total_loaded_trays > 0:
        msg_lines.append(f"- Dispatched (Loading): *-{total_loaded_trays:,.2f}* trays (-{total_loaded_eggs:,} eggs)")
    msg_lines.append(f"- Closing Balance: *{closing_trays:,.2f}* trays (*{closing_eggs:,}* eggs)")

    summary_text = "\n".join(msg_lines)

    # 6. Generate PDF report
    os.makedirs("/app/media/reports", exist_ok=True)
    # Cleanup old godown reports
    for old_file in glob.glob("/app/media/reports/Godown_Report_*"):
        try:
            os.remove(old_file)
        except Exception:
            pass

    timestamp = now_ist.strftime("%Y%m%d_%H%M")
    pdf_path = f"/app/media/reports/Godown_Report_{timestamp}.pdf"

    # Build PDF Story
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, fontSize=18, textColor=colors.HexColor('#1b4332'), spaceAfter=15)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2d6a4f'), spaceBefore=10, spaceAfter=8)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], alignment=1, fontSize=10, textColor=colors.white, fontName='Helvetica-Bold')
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'], alignment=1, fontSize=10)

    story = [
        Paragraph(f"<b>Egg Godown Summary Report</b>", title_style),
        Paragraph(f"<b>Date:</b> {date_str}", body_style),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2d6a4f'), spaceAfter=15),
        Paragraph("<b>1. Production by Shed (Sheds 1-9)</b>", section_style),
    ]

    # Create Shed table
    table_data = [[
        Paragraph("<b>Shed</b>", table_header_style),
        Paragraph("<b>1st Collection (Trays)</b>", table_header_style),
        Paragraph("<b>2nd Collection (Trays)</b>", table_header_style),
        Paragraph("<b>Total Trays</b>", table_header_style)
    ]]

    for i in range(1, 10):
        sk = f"Shed {i}"
        table_data.append([
            Paragraph(sk, table_cell_style),
            Paragraph(f"{shed_data[sk]['c1']:.2f}", table_cell_style),
            Paragraph(f"{shed_data[sk]['c2']:.2f}", table_cell_style),
            Paragraph(f"<b>{shed_data[sk]['total']:.2f}</b>", table_cell_style)
        ])
        
    table_data.append([
        Paragraph("<b>Grand Total</b>", table_cell_style),
        Paragraph("", table_cell_style),
        Paragraph("", table_cell_style),
        Paragraph(f"<b>{grand_total_trays:.2f}</b>", table_cell_style)
    ])

    col_widths = [110, 130, 130, 130]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d6a4f')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d8f3dc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)

    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>2. Godown Inventory Balance Summary</b>", section_style))

    inv_data = [
        [Paragraph("<b>Metric</b>", table_header_style), Paragraph("<b>Quantity (Eggs)</b>", table_header_style)],
        [Paragraph("Opening Balance", table_cell_style), Paragraph(f"{opening:,}", table_cell_style)],
        [Paragraph("Received (Production)", table_cell_style), Paragraph(f"+{grand_total_eggs:,}", table_cell_style)],
        [Paragraph("<b>Closing Balance</b>", table_cell_style), Paragraph(f"<b>{closing:,}</b>", table_cell_style)]
    ]

    t_inv = Table(inv_data, colWidths=[250, 250])
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1b4332')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d8f3dc')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_inv)

    doc.build(story)
    db.close()
    return pdf_path, summary_text
