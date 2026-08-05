import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from database import SessionLocal
from models import BookStandard, Flock

FIXED_SHEDS = [
    "Shed 1", "Shed 2", "Shed 3", "Shed 4",
    "Shed 5", "Shed 6", "Shed 7", "Shed 8",
    "Shed 9", "Grower", "Chick"
]

def _calculate_tables(df, birds_map, default_egg_rate, default_feed_cost_ton):
    if not df.empty:
        import re
        expanded_rows = []
        for _, row in df.iterrows():
            name = str(row['shead_name']).strip()
            
            # 1. Expand multiple sheds separated by commas or 'and'
            if (',' in name or ' and ' in name.lower()) and re.search(r'\d', name):
                numbers = re.findall(r'\d+', name)
                if len(numbers) > 1:
                    num_sheds = len(numbers)
                    for n in numbers:
                        new_row = row.copy()
                        new_row['shead_name'] = f"Shed {n}"
                        if new_row['quantity']: new_row['quantity'] = float(new_row['quantity']) / num_sheds
                        if new_row['amount']: new_row['amount'] = float(new_row['amount']) / num_sheds
                        expanded_rows.append(new_row)
                    continue
            
            name_lower = name.lower()
            if 'chick' in name_lower:
                row['shead_name'] = 'Chick'
            elif 'grower' in name_lower:
                row['shead_name'] = 'Grower'
            else:
                # 2. Extract digits for single sheds
                numbers = re.findall(r'\d+', name)
                if numbers:
                    row['shead_name'] = f"Shed {numbers[0]}"
                elif name_lower in ['nan', 'unknown', 'none', 'null', '']:
                    row['shead_name'] = ''
                
            expanded_rows.append(row)
            
        df = pd.DataFrame(expanded_rows)
    
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
            
            # Look up expected production % from BookStandard (uses flock age from birds_map or flock DB)
            expected_pct_str = "N/A"
            if birds > 0 and birds_map.get(shed + "_age_days"):
                age_days = birds_map.get(shed + "_age_days", 0)
                try:
                    _db = SessionLocal()
                    std = _db.query(BookStandard).filter(BookStandard.day == age_days).first()
                    if std and std.expected_production_pct is not None:
                        expected_pct_str = f"{float(std.expected_production_pct):.1f}%"
                    _db.close()
                except Exception:
                    pass
            
            prod_rows.append([
                shed, f"{birds:,}" if birds > 0 else "-",
                f"{c1:,.0f}" if c1 > 0 else "-", f"{c2:,.0f}" if c2 > 0 else "-",
                f"{total_shed_eggs:,.0f}" if total_shed_eggs > 0 else "-",
                f"{int(mortality)}" if mortality > 0 else "-",
                expected_pct_str, f"{actual_pct:.1f}%", f"Rs. {rate:.2f}", f"Rs. {prod_val:,.2f}"
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

    common_feed_df = df[(df['shead_name'] == '') & (df['category'].isin(['feed', 'raw_material']))] if not df.empty else pd.DataFrame()
    c_feed_mt = 0.0
    c_feed_cost = 0.0
    for _, row in common_feed_df.iterrows():
        qty = float(row['quantity']) if row['quantity'] else 0
        unit = str(row['unit']).lower()
        amt = float(row['amount']) if row['amount'] else 0.0
        if 'kg' in unit: c_feed_mt += qty / 1000.0
        elif 'bag' in unit: c_feed_mt += qty * 0.05
        elif 'mt' in unit or 'ton' in unit: c_feed_mt += qty
        else: c_feed_mt += qty * 0.05 if qty < 500 else qty / 1000.0
        c_feed_cost += amt if amt > 0 else (c_feed_mt * default_feed_cost_ton)

    if c_feed_mt > 0:
        total_feed_mt += c_feed_mt
        total_feed_cost += c_feed_cost
        feed_rows.append(["Common/Bulk", f"{c_feed_mt:.3f}", "-", "-", f"Rs. {c_feed_cost:,.2f}"])

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
        elif cat in ['expense', 'purchase', 'medicine']:
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
    import re
    def _norm_shead(name):
        n = str(name or '').strip().lower()
        if 'chick' in n: return 'Chick'
        if 'grower' in n: return 'Grower'
        nums = re.findall(r'\d+', n)
        if nums: return f"Shed {nums[0]}"
        return name

    if not df.empty:
        df = df.copy()
        df['shead_name'] = df['shead_name'].apply(_norm_shead)

    today_str = start_date.strftime("%d/%m/%Y")
    lines = [f"📋 *DAILY FARM SUMMARY ({today_str})*", ""]

    book_map = _get_book_standards_map(birds_map)
    FIXED_SHEDS = ["Shed 1", "Shed 2", "Shed 3", "Shed 4", "Shed 5", "Shed 6", "Shed 7", "Shed 8", "Shed 9", "Grower", "Chick"]

    # 1. Shed-Wise Mortality Section
    lines.append("💀 *Shed-Wise Mortality*")
    lines.append("```")
    tot_mort = 0
    for s in ["Shed 1", "Shed 2", "Shed 3", "Shed 4", "Shed 5", "Shed 6", "Shed 7", "Shed 8", "Shed 9"]:
        mort_df = df[(df['shead_name'] == s) & (df['category'] == 'mortality')] if not df.empty else pd.DataFrame()
        m = int(max([float(r['quantity'] or 0) for _, r in mort_df.iterrows()], default=0))
        tot_mort += m
        num = re.findall(r'\d+', s)[0]
        lines.append(f"{num}-{m}")

    chick_w_df = df[(df['shead_name'].str.lower().str.contains('whites', na=False)) & (df['category'] == 'mortality')] if not df.empty else pd.DataFrame()
    chick_w_m = int(max([float(r['quantity'] or 0) for _, r in chick_w_df.iterrows()], default=0))
    chick_b_df = df[(df['shead_name'].str.lower().str.contains('brownie', na=False)) & (df['category'] == 'mortality')] if not df.empty else pd.DataFrame()
    chick_b_m = int(max([float(r['quantity'] or 0) for _, r in chick_b_df.iterrows()], default=0))
    tot_mort += (chick_w_m + chick_b_m)

    lines.append("Chick")
    lines.append(f"Whites; {chick_w_m}")
    lines.append(f"Brownie; {chick_b_m}")
    lines.append(f"Totall mortality; {tot_mort}")
    lines.append("```")
    lines.append("")

    # 2. Production Section: SED_AGE_PRODUCTION-AP-BP
    lines.append("🥚 *SED_AGE_PRODUCTION-AP-BP*")
    lines.append("```")
    for s in ["Shed 1", "Shed 2", "Shed 3", "Shed 4", "Shed 5", "Shed 6", "Shed 7", "Shed 8"]:
        num = re.findall(r'\d+', s)[0]
        info = book_map.get(s, {})
        age_weeks = info.get('book_week', 0)
        expected_pct = info.get('expected_pct')
        birds = birds_map.get(s, 0)
        shed_eggs_df = df[(df['shead_name'] == s) & (df['category'].isin(
            ['egg_collection_1', 'egg_collection_2', 'egg_collection_3', 'egg_collection', 'egg']))] if not df.empty else pd.DataFrame()
        total_eggs = 0
        for _, row in shed_eggs_df.iterrows():
            qty = float(row['quantity'] or 0)
            unit = str(row['unit'] or '').lower()
            total_eggs += qty * 30 if 'tray' in unit else qty
        trays = total_eggs / 30.0
        actual_pct = (total_eggs / birds * 100.0) if birds > 0 and total_eggs > 0 else 0.0
        exp_str = f"{int(expected_pct)}%" if expected_pct is not None else "0%"
        act_str = f"{int(actual_pct)}%"
        lines.append(f"{num}._ {age_weeks}._ {trays:.2f}_{act_str}-{exp_str}")
    lines.append("```")
    lines.append("")

    # 3. Birds Weight Comparison Section
    lines.append("⚖️ *Birds Weight Comparison*")
    lines.append("```")
    for s in FIXED_SHEDS:
        info = book_map.get(s, {})
        book_wt_g = info.get('book_weight_g')
        wt_df = df[(df['shead_name'] == s) & (df['category'].isin(
            ['weight', 'body_weight', 'bird_weight', 'avg_weight', 'hen_weight']))] if not df.empty else pd.DataFrame()
        actual_wt_kg = None
        for _, row in wt_df.iterrows():
            qty = float(row['quantity'] or 0)
            if qty > 0:
                unit = str(row['unit'] or '').lower()
                actual_wt_kg = qty / 1000.0 if (qty > 50 or ('g' in unit and 'kg' not in unit)) else qty
                break
        if actual_wt_kg is not None and book_wt_g is not None:
            actual_g = actual_wt_kg * 1000.0
            diff_g = actual_g - book_wt_g
            symbol = "🟢" if diff_g >= 0 else "🔴"
            sign = "+" if diff_g >= 0 else ""
            lines.append(f"{s}: {actual_wt_kg:.3f} kg (Book: {book_wt_g/1000.0:.3f} kg) {symbol} {sign}{diff_g:.0f}g")
        elif actual_wt_kg is not None:
            lines.append(f"{s}: {actual_wt_kg:.3f} kg (No Book Standard)")
        else:
            lines.append(f"{s}: No Weight Data")
    lines.append("```")

    return "\n".join(lines)




def _get_book_standards_map(birds_map):
    """Returns {shed_name: {'age_days': int, 'expected_pct': float|None, 'book_weight_g': float|None}}"""
    result = {}
    try:
        db = SessionLocal()
        flocks = db.query(Flock).filter(Flock.status == 'active').all()
        from datetime import date, timedelta
        today = date.today()
        for flock in flocks:
            shed_key = flock.shed_name.strip() if flock.shed_name else ''
            # Normalize shed name to match FIXED_SHEDS format
            shed_key_lower = shed_key.lower()
            if 'chick' in shed_key_lower:
                normalized = 'Chick'
            elif 'grower' in shed_key_lower:
                normalized = 'Grower'
            else:
                import re as _re
                nums = _re.findall(r'\d+', shed_key)
                if nums:
                    normalized = f"Shed {nums[0]}"
                else:
                    normalized = shed_key

            if flock.hatch_date:
                age_days = (today - flock.hatch_date).days + 1
            else:
                age_days = 0

            std = db.query(BookStandard).filter(BookStandard.day == age_days).first()
            expected_pct = float(std.expected_production_pct) if std and std.expected_production_pct is not None else None
            book_weight_g = float(std.expected_body_weight_g) if std and std.expected_body_weight_g is not None else None
            book_week = int(std.week) if std and std.week is not None else (age_days // 7 if age_days else 0)

            result[normalized] = {
                'age_days': age_days,
                'book_week': book_week,
                'expected_pct': expected_pct,
                'book_weight_g': book_weight_g,
                'flock_name': shed_key
            }
        db.close()
    except Exception as e:
        pass
    return result


def _make_doc_and_helpers(pdf_path, title_str):
    """Creates a ReportLab doc + shared styles + draw_table helper. Returns (doc, story, draw_table)."""
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=0.35*inch, leftMargin=0.35*inch,
                            topMargin=0.35*inch, bottomMargin=0.35*inch)
    styles = getSampleStyleSheet()
    story = []
    GREEN_DARK  = colors.HexColor('#1b4332')
    GREEN_MID   = colors.HexColor('#2d6a4f')
    GREEN_LIGHT = colors.HexColor('#d8f3dc')
    GREY_ROW    = colors.HexColor('#f8f9fa')

    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=15, spaceAfter=6,
                         textColor=GREEN_DARK, alignment=1, fontName='Helvetica-Bold')
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, spaceAfter=3,
                         textColor=GREEN_MID, spaceBefore=10, fontName='Helvetica-Bold')

    story.append(Paragraph(title_str, h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GREEN_MID, spaceAfter=8))

    def draw_table(title, headers, rows, col_widths=None, highlight_last=True):
        story.append(Paragraph(title, h2))
        def strip_md(s):
            if isinstance(s, Paragraph):
                return s
            return str(s).replace("**", "")
        data = [headers] + [[strip_md(c) for c in row] for row in rows]
        tbl_style = [
            ('BACKGROUND', (0, 0), (-1, 0), GREEN_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GREY_ROW]),
        ]
        if highlight_last and len(data) > 1:
            tbl_style += [
                ('BACKGROUND', (0, -1), (-1, -1), GREEN_LIGHT),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]
        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)
        story.append(Spacer(1, 0.12*inch))

    return doc, story, draw_table


def generate_operations_pdf(pdf_path: str, df: pd.DataFrame, range_type: str, start_date, end_date, birds_map):
    """PDF 1: Shed-Wise Mortality | Age & Production (Trays, Actual% vs Expected%) | Weight Comparison"""
    if range_type == 'daily' or start_date == end_date:
        title_str = f"DAILY FARM OPERATIONS REPORT - {start_date.strftime('%d/%m/%Y')}"
    else:
        title_str = f"FARM OPERATIONS REPORT - {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"

    doc, story, draw_table = _make_doc_and_helpers(pdf_path, title_str)
    book_map = _get_book_standards_map(birds_map)
    
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        'TableCellStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        alignment=1, # Center
        textColor=colors.black,
        leading=9
    )

    if not df.empty:
        import re
        def _norm_shead(name):
            n = str(name or '').strip().lower()
            if 'chick' in n: return 'Chick'
            if 'grower' in n: return 'Grower'
            nums = re.findall(r'\d+', n)
            if nums: return f"Shed {nums[0]}"
            return name
        df = df.copy()
        df['shead_name'] = df['shead_name'].apply(_norm_shead)

    # ─── SECTION 1: Shed-Wise Mortality ─────────────────────────────────────────
    mort_headers = ["Shed", "Age (Days)", "Age (Weeks)", "Mortality Today"]
    mort_rows = []
    for shed in FIXED_SHEDS:
        mort_df = df[(df['shead_name'] == shed) & (df['category'] == 'mortality')] if not df.empty else pd.DataFrame()
        mortality = int(max([float(r['quantity'] or 0) for _, r in mort_df.iterrows()], default=0))
        info = book_map.get(shed, {})
        age_days = info.get('age_days', 0)
        age_weeks = info.get('book_week', 0)
        mort_rows.append([shed,
            str(age_days) if age_days else "-",
            str(age_weeks) if age_weeks else "-",
            str(mortality) if mortality else "0"])
    total_mort = sum(int(r[3]) for r in mort_rows if r[3].isdigit())
    mort_rows.append(["Total", "-", "-", str(total_mort)])
    draw_table("1. Shed-Wise Mortality", mort_headers, mort_rows,
               col_widths=[1.6*inch, 1.6*inch, 1.6*inch, 2.2*inch])

    # ─── SECTION 2: Age & Production ────────────────────────────────────────────
    prod_headers = ["Shed", "Age\n(Days)", "Age\n(Weeks)", "Eggs\n(Nos.)",
                    "Trays\n(30 eggs)", "Actual\nProd %", "Expected\nProd %", "Diff\n(%pts)"]
    prod2_rows = []
    for shed in FIXED_SHEDS:
        is_grower_chick = shed in ["Grower", "Chick"]
        birds = birds_map.get(shed, 0)
        info = book_map.get(shed, {})
        age_days = info.get('age_days', 0)
        age_weeks = info.get('book_week', 0)
        expected_pct = info.get('expected_pct')
        for _, row in (df[(df['shead_name'] == shed) & (df['category'] == 'production')] if not df.empty else pd.DataFrame()).iterrows():
            qty = float(row['quantity'] or 0)
            if qty > 1000:
                birds = int(qty)
                break
        shed_eggs_df = df[(df['shead_name'] == shed) & (df['category'].isin(
            ['egg_collection_1', 'egg_collection_2', 'egg_collection_3', 'egg_collection', 'egg']))] if not df.empty else pd.DataFrame()
        total_eggs = 0
        for _, row in shed_eggs_df.iterrows():
            qty = float(row['quantity'] or 0)
            unit = str(row['unit'] or '').lower()
            total_eggs += qty * 30 if 'tray' in unit else qty
        trays = total_eggs / 30 if total_eggs > 0 else 0
        actual_pct = (total_eggs / birds * 100) if birds > 0 and total_eggs > 0 else 0.0
        if is_grower_chick:
            prod2_rows.append([shed, str(age_days) if age_days else "-", str(age_weeks) if age_weeks else "-",
                                "N/A", "N/A", "N/A", "N/A", "N/A"])
            continue
        exp_str = f"{expected_pct:.1f}%" if expected_pct is not None else "N/A"
        if expected_pct is not None and actual_pct > 0:
            diff = actual_pct - expected_pct
            if diff >= 0:
                diff_str = Paragraph(f'<font color="#2d6a4f"><b>+{diff:.1f}%</b></font>', cell_style)
            else:
                diff_str = Paragraph(f'<font color="#b7094c"><b>{diff:.1f}%</b></font>', cell_style)
        else:
            diff_str = "N/A"
        prod2_rows.append([
            shed, str(age_days) if age_days else "-", str(age_weeks) if age_weeks else "-",
            f"{int(total_eggs):,}" if total_eggs else "0",
            f"{trays:.1f}" if trays else "0",
            f"{actual_pct:.1f}%" if actual_pct else "0.0%",
            exp_str, diff_str
        ])
    draw_table("2. Age & Production (Eggs / Trays vs Book Standard)",
               prod_headers, prod2_rows,
               col_widths=[1.0*inch, 0.85*inch, 0.85*inch, 1.05*inch, 0.95*inch,
                           0.95*inch, 0.95*inch, 0.85*inch])

    # ─── SECTION 3: Birds Weight Comparison ─────────────────────────────────────
    wt_headers = ["Shed", "Age\n(Days)", "Age\n(Weeks)", "Actual Weight\n(Kg)",
                  "Book Weight\n(g)", "Book Weight\n(Kg)", "Difference\n(g)", "Status"]
    wt_rows = []
    for shed in FIXED_SHEDS:
        birds = birds_map.get(shed, 0)
        info = book_map.get(shed, {})
        age_days = info.get('age_days', 0)
        age_weeks = info.get('book_week', 0)
        book_wt_g = info.get('book_weight_g')
        wt_df = df[(df['shead_name'] == shed) & (df['category'].isin(
            ['weight', 'body_weight', 'bird_weight', 'avg_weight', 'hen_weight']))] if not df.empty else pd.DataFrame()
        actual_wt_kg = None
        for _, row in wt_df.iterrows():
            qty = float(row['quantity'] or 0)
            if qty > 0:
                unit = str(row['unit'] or '').lower()
                if qty > 50 or ('g' in unit and 'kg' not in unit):
                    actual_wt_kg = qty / 1000.0
                else:
                    actual_wt_kg = qty
                break
        for _, row in (df[(df['shead_name'] == shed) & (df['category'] == 'production')] if not df.empty else pd.DataFrame()).iterrows():
            qty = float(row['quantity'] or 0)
            if qty > 1000:
                birds = int(qty)
                break
        if actual_wt_kg is None and book_wt_g is None:
            wt_rows.append([shed, str(age_days) if age_days else "-", str(age_weeks) if age_weeks else "-",
                            "No Data", "No Data", "No Data", "No Data", "-"])
            continue
        actual_str = f"{actual_wt_kg:.3f}" if actual_wt_kg is not None else "No Data"
        book_g_str = f"{int(book_wt_g)}" if book_wt_g is not None else "No Data"
        book_kg_str = f"{book_wt_g/1000:.3f}" if book_wt_g is not None else "No Data"
        if actual_wt_kg is not None and book_wt_g is not None:
            actual_g = actual_wt_kg * 1000.0
            diff_g = actual_g - book_wt_g
            if diff_g >= 0:
                diff_str = Paragraph(f'<font color="#2d6a4f"><b>+{diff_g:.0f} g</b></font>', cell_style)
                status = Paragraph('<font color="#2d6a4f"><b>Above 🟢</b></font>', cell_style)
            else:
                diff_str = Paragraph(f'<font color="#b7094c"><b>{diff_g:.0f} g</b></font>', cell_style)
                status = Paragraph('<font color="#b7094c"><b>Below 🔴</b></font>', cell_style)
        else:
            diff_str = "N/A"
            status = "N/A"
        wt_rows.append([shed, str(age_days) if age_days else "-", str(age_weeks) if age_weeks else "-",
                        actual_str, book_g_str, book_kg_str, diff_str, status])
    draw_table("3. Birds Weight Comparison (Actual vs Book Standard)",
               wt_headers, wt_rows,
               col_widths=[0.9*inch, 0.75*inch, 0.75*inch, 1.0*inch, 0.9*inch,
                           0.9*inch, 0.95*inch, 0.8*inch])

    doc.build(story)


def generate_pdf(pdf_path: str, df: pd.DataFrame, range_type: str, start_date, end_date, birds_map, default_egg_rate, default_feed_cost_ton):
    if range_type == 'daily' or start_date == end_date:
        title_str = f"DAILY FARM FINANCIAL REPORT - {start_date.strftime('%d/%m/%Y')}"
    else:
        title_str = f"FARM FINANCIAL REPORT - {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"

    doc, story, draw_table = _make_doc_and_helpers(pdf_path, title_str)
    prod, feed, exp, common, pl = _calculate_tables(df, birds_map, default_egg_rate, default_feed_cost_ton)

    draw_table("1. Full Production & Financial Overview",
               ["Shed", "Birds", "1st Coll.", "2nd Coll.", "Total Eggs", "Mortality",
                "Expected %", "Actual %", "Egg Price", "Prod. Value"],
               prod)
    draw_table("2. Feed Consumption",
               ["Shed", "Feed Consumed (MT)", "Feed/Bird (g/Day)", "Feed Cost/Ton", "Total Feed Cost"],
               feed)
    draw_table("3. Shed-Related Expenditure",
               ["Shed", "Labourers", "Medicines", "Final Cost", "Daily Payender"],
               exp)
    draw_table("4. Common Expenditures",
               ["Particular", "Quantity", "Amount"],
               common)
    draw_table("5. Daily P&L Summary",
               ["Particular", "Amount"],
               pl, col_widths=[3.5*inch, 2.5*inch])

    doc.build(story)

