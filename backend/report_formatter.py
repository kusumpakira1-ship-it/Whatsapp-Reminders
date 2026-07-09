import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

FIXED_SHEDS = [
    "Shed 1", "Shed 2", "Shed 3", "Shed 4",
    "Shed 5", "Shed 6", "Shed 7", "Shed 8",
    "Shed 9", "Grower", "Chick"
]

def _calculate_tables(df, birds_map, default_egg_rate, default_feed_cost_ton):
    if not df.empty:
        df['shead_name'] = df['shead_name'].astype(str).str.replace('Shead', 'Shed').str.strip()
    
    sales_df = df[df['category'] == 'sales'] if not df.empty else pd.DataFrame()
    rates_by_shed = {}
    for _, row in sales_df.iterrows():
        s = row['shead_name']
        qty = float(row['quantity']) if row['quantity'] else 0
        amt = float(row['amount']) if row['amount'] else 0.0
        if qty > 0 and amt > 0:
            unit = str(row['unit']).lower()
            eggs = qty * 30 if 'tray' in unit else qty
            rates_by_shed[s] = amt / eggs

    prod_rows = []
    total_birds = 0
    total_eggs = 0
    total_prod_value = 0.0
    total_mortality = 0

    for shed in FIXED_SHEDS:
        is_grower_chick = shed in ["Grower", "Chick"]
        
        shed_prod = df[(df['shead_name'] == shed) & (df['category'] == 'production')] if not df.empty else pd.DataFrame()
        birds = birds_map.get(shed, 0)
        for _, row in shed_prod.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            if qty > 1000:
                birds = int(qty)
                break
                
        mort_df = df[(df['shead_name'] == shed) & (df['category'] == 'mortality')] if not df.empty else pd.DataFrame()
        mortality = sum(float(row['quantity'] or 0) for _, row in mort_df.iterrows())

        if is_grower_chick:
            prod_rows.append([
                shed, f"{birds:,}" if birds > 0 else "-", "N/A", "N/A", "N/A",
                f"{int(mortality)}" if mortality > 0 else "-",
                "N/A", "N/A", "N/A", "N/A"
            ])
            continue

        c1 = 0
        c2 = 0
        gen_eggs = 0
        
        shed_eggs_df = df[(df['shead_name'] == shed) & (df['category'].isin(['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']))] if not df.empty else pd.DataFrame()
        for _, row in shed_eggs_df.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            unit = str(row['unit']).lower()
            eggs = qty * 30 if 'tray' in unit else qty
            cat = row['category']
            if cat == 'egg_collection_1': c1 += eggs
            elif cat == 'egg_collection_2': c2 += eggs
            else: gen_eggs += eggs

        total_shed_eggs = c1 + c2 + gen_eggs
        
        if total_shed_eggs > 0 or mortality > 0:
            total_birds += birds
            total_eggs += total_shed_eggs
            total_mortality += mortality
            
            rate = rates_by_shed.get(shed, default_egg_rate)
            prod_val = total_shed_eggs * rate
            total_prod_value += prod_val
            
            actual_pct = (total_shed_eggs / birds * 100) if birds > 0 else 0.0
            
            prod_rows.append([
                shed, f"{birds:,}" if birds > 0 else "-",
                f"{c1:,.0f}" if c1 > 0 else "-", f"{c2:,.0f}" if c2 > 0 else "-",
                f"{total_shed_eggs:,.0f}" if total_shed_eggs > 0 else "-",
                f"{int(mortality)}" if mortality > 0 else "-",
                "95.0%", f"{actual_pct:.1f}%", f"Rs. {rate:.2f}", f"Rs. {prod_val:,.2f}"
            ])
        else:
            prod_rows.append([shed, "-", "-", "-", "-", "-", "-", "-", "-", "-"])

    if total_eggs > 0 or total_mortality > 0:
        avg_total_rate = (total_prod_value / total_eggs) if total_eggs > 0 else default_egg_rate
        total_actual_pct = (total_eggs / total_birds * 100) if total_birds > 0 else 0.0
        prod_rows.append([
            "**Total**", f"{total_birds:,}", "-", "-", f"{total_eggs:,.0f}", f"{int(total_mortality)}",
            "95.0%", f"{total_actual_pct:.1f}%", f"Rs. {avg_total_rate:.2f}", f"Rs. {total_prod_value:,.2f}"
        ])
    else:
        prod_rows.append(["**Total**", "-", "-", "-", "-", "-", "-", "-", "-", "-"])

    feed_rows = []
    total_feed_mt = 0.0
    total_feed_cost = 0.0

    for shed in FIXED_SHEDS:
        shed_feed_df = df[(df['shead_name'] == shed) & (df['category'].isin(['feed', 'raw_material']))] if not df.empty else pd.DataFrame()
        feed_mt = 0.0
        db_feed_cost = 0.0
        for _, row in shed_feed_df.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            unit = str(row['unit']).lower()
            amt = float(row['amount']) if row['amount'] else 0.0
            if 'kg' in unit: feed_mt += qty / 1000.0
            elif 'bag' in unit: feed_mt += qty * 0.05
            elif 'mt' in unit or 'ton' in unit: feed_mt += qty
            else: feed_mt += qty * 0.05 if qty < 500 else qty / 1000.0
            db_feed_cost += amt

        if feed_mt > 0:
            birds = birds_map.get(shed, 0)
            feed_g_bird = (feed_mt * 1000000.0 / birds) if birds > 0 else 0.0
            feed_cost_ton = default_feed_cost_ton
            cost = db_feed_cost if db_feed_cost > 0 else (feed_mt * feed_cost_ton)
            total_feed_mt += feed_mt
            total_feed_cost += cost
            feed_rows.append([shed, f"{feed_mt:.3f}", f"{feed_g_bird:.1f}", f"Rs. {feed_cost_ton:,.2f}", f"Rs. {cost:,.2f}"])
        else:
            feed_rows.append([shed, "-", "-", "-", "-"])

    if total_feed_mt > 0:
        avg_feed_g_bird = (total_feed_mt * 1000000.0 / total_birds) if total_birds > 0 else 0.0
        feed_rows.append(["**Total**", f"{total_feed_mt:.3f}", f"{avg_feed_g_bird:.1f}", "-", f"Rs. {total_feed_cost:,.2f}"])
    else:
        feed_rows.append(["**Total**", "-", "-", "-", "-"])

    exp_rows = []
    total_labourers = 0
    total_med_used = 0
    total_shed_exp = 0.0

    for shed in FIXED_SHEDS:
        shed_exp_df = df[(df['shead_name'] == shed) & (df['category'].isin(['expense', 'medicine', 'purchase']))] if not df.empty else pd.DataFrame()
        labourers = 0
        med_used = 0
        cost = 0.0
        payender = "-"
        
        for _, row in shed_exp_df.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            amt = float(row['amount']) if row['amount'] else 0.0
            cat = row['category']
            notes = str(row['notes'] or '').lower()

            if 'labour' in notes or 'labor' in notes or 'worker' in notes or 'wages' in notes:
                labourers += int(qty) if qty > 0 else 1
            if cat == 'medicine':
                med_used += int(qty) if qty > 0 else 1
            cost += amt

            for prefix in ["paid to:", "payee:", "paid by:"]:
                if prefix in notes:
                    extracted = str(row['notes']).lower().split(prefix)[1].split('\n')[0].strip().title()
                    if extracted: payender = extracted

        if cost > 0 or labourers > 0 or med_used > 0:
            total_labourers += labourers
            total_med_used += med_used
            total_shed_exp += cost
            exp_rows.append([shed, f"{labourers}", f"{med_used}", f"Rs. {cost:,.2f}", payender])
        else:
            exp_rows.append([shed, "-", "-", "-", "-"])

    if total_shed_exp > 0 or total_labourers > 0 or total_med_used > 0:
        exp_rows.append(["**Total Shed-Related Expenditure**", f"{total_labourers}", f"{total_med_used}", f"Rs. {total_shed_exp:,.2f}", "-"])
    else:
        exp_rows.append(["**Total Shed-Related Expenditure**", "-", "-", "-", "-"])

    fuel_amt = 0.0; fuel_qty = 0.0; elec_amt = 0.0; elec_qty = 0.0; repair_amt = 0.0; other_amt = 0.0
    common_df = df[df['shead_name'].isin(['', 'nan', 'unknown', 'Common', 'None', None])] if not df.empty else pd.DataFrame()
    for _, row in common_df.iterrows():
        cat = row['category']
        notes = str(row['notes'] or '').lower()
        amt = float(row['amount']) if row['amount'] else 0.0
        qty = float(row['quantity']) if row['quantity'] else 0
        if 'fuel' in notes or 'diesel' in notes or 'petrol' in notes:
            fuel_amt += amt; fuel_qty += qty
        elif 'electricity' in notes or 'current' in notes or 'power' in notes or 'eb bill' in notes:
            elec_amt += amt; elec_qty += qty
        elif 'repair' in notes or 'maintenance' in notes or 'servicing' in notes or 'mechanic' in notes:
            repair_amt += amt
        elif cat in ['expense', 'purchase']:
            other_amt += amt

    total_common_exp = fuel_amt + elec_amt + repair_amt + other_amt
    common_rows = [
        ["Fuel", f"{fuel_qty:.1f} L" if fuel_qty > 0 else "-", f"Rs. {fuel_amt:,.2f}" if fuel_amt > 0 else "-"],
        ["Electricity", f"{elec_qty:.1f} Units" if elec_qty > 0 else "-", f"Rs. {elec_amt:,.2f}" if elec_amt > 0 else "-"],
        ["Repairs & Maintenance", "-", f"Rs. {repair_amt:,.2f}" if repair_amt > 0 else "-"],
        ["Other Common Expenses", "-", f"Rs. {other_amt:,.2f}" if other_amt > 0 else "-"],
        ["**Total Common Expenditure**", "-", f"Rs. {total_common_exp:,.2f}" if total_common_exp > 0 else "-"]
    ]

    total_expenses = total_feed_cost + total_shed_exp + total_common_exp
    net_profit = total_prod_value - total_expenses
    pl_rows = [
        ["Total Production Value", f"Rs. {total_prod_value:,.2f}" if total_prod_value > 0 else "-"],
        ["Total Feed Cost", f"Rs. {total_feed_cost:,.2f}" if total_feed_cost > 0 else "-"],
        ["Total Shed-Related Expenditure", f"Rs. {total_shed_exp:,.2f}" if total_shed_exp > 0 else "-"],
        ["Total Common Expenditure", f"Rs. {total_common_exp:,.2f}" if total_common_exp > 0 else "-"],
        ["**Total Expenses**", f"Rs. {total_expenses:,.2f}" if total_expenses > 0 else "-"],
        ["**Net Profit / Loss**", f"Rs. {net_profit:,.2f}" if (total_prod_value > 0 or total_expenses > 0) else "-"]
    ]
    
    return prod_rows, feed_rows, exp_rows, common_rows, pl_rows


def build_whatsapp_summary(df: pd.DataFrame, range_type: str, start_date, end_date, birds_map, default_egg_rate, default_feed_cost_ton) -> str:
    if range_type == 'daily' or start_date == end_date:
        today_str = start_date.strftime("%d/%m/%Y")
        title = f"📊 DAILY FARM SUMMARY – {today_str}"
    elif range_type == 'weekly':
        title = f"📊 WEEKLY FARM SUMMARY – {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
    else:
        title = f"📊 MONTHLY FARM SUMMARY – {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"

    prod, feed, exp, common, pl = _calculate_tables(df, birds_map, default_egg_rate, default_feed_cost_ton)

    lines = [title, "", "1. Production", ""]
    lines.append("Shed| Birds| 1st Collection (Eggs)| 2nd Collection (Eggs)| Total Eggs Produced| Mortality| Expected Production (%)| Actual Production (%)| Avg. Egg Selling Price (Rs./Egg)| Production Value (Rs.)")
    for r in prod: lines.append("| ".join(r).replace("**", ""))
    
    lines.extend(["", "-"*100, "", "2. Feed Consumption", ""])
    lines.append("Shed| Feed Consumed (MT)| Feed per Bird (g/Bird/Day)| Feed Cost/Ton (Rs.)| Total Feed Cost (Rs.)")
    for r in feed: lines.append("| ".join(r).replace("**", ""))
    
    lines.extend(["", "-"*100, "", "3. Shed-Related Expenditure", ""])
    lines.append("Shed| No. of Labourers Used| No. of Medicines Used| Final Cost (Rs.)| Daily Payender")
    for r in exp: lines.append("| ".join(r).replace("**", ""))
    
    lines.extend(["", "-"*100, "", "4. Common Fuel and Common Expenditures", ""])
    lines.append("Particular| Quantity| Amount (Rs.)")
    for r in common: lines.append("| ".join(r).replace("**", ""))
    
    lines.extend(["", "-"*100, "", "5. Daily P&L Summary", ""])
    lines.append("Particular| Amount (Rs.)")
    for r in pl: lines.append("| ".join(r).replace("**", ""))
    
    return "\n".join(lines)


def generate_pdf(pdf_path: str, df: pd.DataFrame, range_type: str, start_date, end_date, birds_map, default_egg_rate, default_feed_cost_ton):
    if range_type == 'daily' or start_date == end_date:
        today_str = start_date.strftime("%d/%m/%Y")
        title_str = f"📊 DAILY FARM SUMMARY – {today_str}"
    else:
        title_str = f"📊 FARM SUMMARY – {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=0.3*inch, leftMargin=0.3*inch, topMargin=0.3*inch, bottomMargin=0.3*inch)
    styles = getSampleStyleSheet()
    story = []
    
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=14, spaceAfter=8, textColor=colors.HexColor('#1b4332'), alignment=1)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11, spaceAfter=4, textColor=colors.HexColor('#2d6a4f'), spaceBefore=8)
    
    story.append(Paragraph(title_str, h1))
    
    prod, feed, exp, common, pl = _calculate_tables(df, birds_map, default_egg_rate, default_feed_cost_ton)
    
    def strip_markdown(s): return s.replace("**", "")

    def _draw_table(title, headers, rows, col_widths=None):
        story.append(Paragraph(title, h2))
        data = [headers] + [[strip_markdown(str(c)) for c in row] for row in rows]
        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6.5 if len(headers) > 6 else 8),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.1*inch))

    _draw_table("1. Production", ["Shed", "Birds", "1st Coll.", "2nd Coll.", "Total Eggs", "Mortality", "Expected %", "Actual %", "Egg Price", "Prod. Value"], prod)
    _draw_table("2. Feed Consumption", ["Shed", "Feed Consumed (MT)", "Feed/Bird (g/Day)", "Feed Cost/Ton", "Total Feed Cost"], feed)
    _draw_table("3. Shed-Related Expenditure", ["Shed", "Labourers", "Medicines", "Final Cost", "Daily Payender"], exp)
    _draw_table("4. Common Expenditures", ["Particular", "Quantity", "Amount"], common)
    _draw_table("5. Daily P&L Summary", ["Particular", "Amount"], pl, col_widths=[3*inch, 2*inch])

    doc.build(story)
