import os
import re
import pandas as pd
from datetime import datetime, date, timedelta, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from database import SessionLocal
from models import ProcessedData

IST = timezone(timedelta(hours=5, minutes=30))

REVENUE_CATS = {'sales'}
EXPENSE_CATS = {'feed', 'raw_material', 'medicine', 'expense', 'purchase'}


def get_date_range(range_type: str):
    # Always evaluate today in Indian Standard Time (IST)
    now_ist = datetime.now(IST)
    today = now_ist.date()
    
    if range_type == 'weekly':
        return today - timedelta(days=7), today
    elif range_type == 'monthly':
        return today - timedelta(days=30), today
    elif range_type == 'yearly':
        return today - timedelta(days=365), today
    else:
        # Try custom date formats like DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(range_type, fmt).date()
                return parsed, parsed
            except ValueError:
                continue
        return today, today


def _natural_sort_key(name: str):
    parts = re.split(r'(\d+)', str(name))
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def _get_item_label(row) -> str:
    """Extract a meaningful item label from notes or processed_text."""
    notes = str(row.get('notes', '') or '')
    processed = str(row.get('processed_text', '') or '')

    # Try extracting "Item: X" or "Activity: X" from notes
    for prefix in ('Item:', 'Activity:', 'Medicine:', 'Material:'):
        if prefix in notes:
            val = notes.split(prefix, 1)[1].split('\n')[0].strip()
            if val:
                return val

    # Fall back to processed_text (remove shead prefix like "Shead 1 - ")
    if processed:
        cleaned = re.sub(r'^Shead\s*\d+\s*[-–]\s*', '', processed, flags=re.IGNORECASE).strip()
        if cleaned:
            return cleaned

    return ''


def _sorted_sheads(df: pd.DataFrame):
    return sorted(
        [s for s in df['shead_name'].dropna().unique() if str(s).strip()],
        key=_natural_sort_key
    )


# ─────────────────────────────────────────────────────────────────────────────
#  WHATSAPP SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def _build_whatsapp_summary(df: pd.DataFrame, range_type: str, start_date, end_date) -> str:
    # Format the header based on the date range
    if range_type == 'daily' or start_date == end_date:
        today_str = start_date.strftime("%d/%m/%Y")
        title = f"📊 Daily Farm Summary – {today_str}"
    elif range_type == 'weekly':
        title = f"📊 Weekly Farm Summary – {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
    else:
        title = f"📊 Monthly Farm Summary – {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"

    # Normalize shed names to standard Shed 1, Shed 2, Shed 3
    df['shead_name'] = df['shead_name'].astype(str).str.replace('Shead', 'Shed').str.strip()

    # Define standard configuration maps
    birds_map = {"Shed 1": 15000, "Shed 2": 12000, "Shed 3": 13000}
    expected_prod_pct = 95.0
    default_egg_rate = 5.20
    default_feed_cost_ton = 35000.0

    # Extract all unique sheds from dataframe and order them
    raw_sheds = df['shead_name'].dropna().unique()
    sheds = ["Shed 1", "Shed 2", "Shed 3"]
    for s in raw_sheds:
        s_str = str(s).strip()
        if s_str and s_str not in sheds and s_str.lower() not in ('nan', 'none', 'unknown', 'common'):
            sheds.append(s_str)

    sheds = [s for s in sheds if s and s.lower() not in ('nan', 'none', 'unknown', 'common')]

    # ── 1. PRODUCTION ──
    # Columns: Shed| Birds| Eggs Produced| Expected Production (%)| Actual Production (%)| Avg. Egg Selling Price (₹/Egg)| Production Value (₹)
    prod_lines = []
    total_birds = 0
    total_eggs = 0
    total_prod_value = 0.0

    # Extract sales rates if available today
    sales_df = df[df['category'] == 'sales']
    rates_by_shed = {}
    for _, row in sales_df.iterrows():
        s = row['shead_name']
        qty = float(row['quantity']) if row['quantity'] else 0
        amt = float(row['amount']) if row['amount'] else 0.0
        if qty > 0 and amt > 0:
            unit = str(row['unit']).lower()
            eggs = qty * 30 if 'tray' in unit else qty
            rates_by_shed[s] = amt / eggs

    for shed in sheds:
        # Check if there is an explicit bird count in the production entries
        shed_prod = df[(df['shead_name'] == shed) & (df['category'] == 'production')]
        birds = birds_map.get(shed, 10000)
        for _, row in shed_prod.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            if qty > 1000:
                birds = int(qty)
                break

        # Get eggs produced
        egg_cats = ['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']
        shed_eggs_df = df[(df['shead_name'] == shed) & (df['category'].isin(egg_cats))]
        eggs_produced = 0
        for _, row in shed_eggs_df.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            unit = str(row['unit']).lower()
            eggs_produced += qty * 30 if 'tray' in unit else qty

        if eggs_produced > 0:
            actual_pct = (eggs_produced / birds * 100) if birds > 0 else 0.0
            rate = rates_by_shed.get(shed, default_egg_rate)
            prod_val = eggs_produced * rate

            total_birds += birds
            total_eggs += eggs_produced
            total_prod_value += prod_val

            prod_lines.append(f"{shed}| {birds:,}| {eggs_produced:,.0f}| {expected_prod_pct}%| {actual_pct:.1f}%| ₹{rate:.2f}| ₹{prod_val:,.2f}")
        else:
            prod_lines.append(f"{shed}| -| -| -| -| -| -")

    if total_eggs > 0:
        avg_total_rate = (total_prod_value / total_eggs) if total_eggs > 0 else default_egg_rate
        total_actual_pct = (total_eggs / total_birds * 100) if total_birds > 0 else 0.0
        prod_lines.append(f"Total| {total_birds:,}| {total_eggs:,.0f}| {expected_prod_pct}%| {total_actual_pct:.1f}%| ₹{avg_total_rate:.2f}| ₹{total_prod_value:,.2f}")
    else:
        prod_lines.append(f"Total| -| -| -| -| -| -")

    # ── 2. FEED CONSUMPTION ──
    # Columns: Shed| Feed Consumed (MT)| Feed per Bird (g/Bird/Day)| Feed Cost/Ton (₹)| Total Feed Cost (₹)
    feed_lines = []
    total_feed_mt = 0.0
    total_feed_cost = 0.0

    for shed in sheds:
        # Get birds count
        shed_prod = df[(df['shead_name'] == shed) & (df['category'] == 'production')]
        birds = birds_map.get(shed, 10000)
        for _, row in shed_prod.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            if qty > 1000:
                birds = int(qty)
                break

        # Get feed consumed
        shed_feed_df = df[(df['shead_name'] == shed) & (df['category'].isin(['feed', 'raw_material']))]
        feed_mt = 0.0
        db_feed_cost = 0.0
        for _, row in shed_feed_df.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            unit = str(row['unit']).lower()
            amt = float(row['amount']) if row['amount'] else 0.0
            
            if 'kg' in unit:
                feed_mt += qty / 1000.0
            elif 'bag' in unit:
                feed_mt += qty * 0.05
            elif 'mt' in unit or 'ton' in unit:
                feed_mt += qty
            else:
                feed_mt += qty * 0.05 if qty < 500 else qty / 1000.0
            db_feed_cost += amt

        if feed_mt > 0:
            feed_g_bird = (feed_mt * 1000000.0 / birds) if birds > 0 else 0.0
            feed_cost_ton = default_feed_cost_ton
            cost = db_feed_cost if db_feed_cost > 0 else (feed_mt * feed_cost_ton)

            total_feed_mt += feed_mt
            total_feed_cost += cost

            feed_lines.append(f"{shed}| {feed_mt:.3f}| {feed_g_bird:.1f}| ₹{feed_cost_ton:,.2f}| ₹{cost:,.2f}")
        else:
            feed_lines.append(f"{shed}| -| -| -| -")

    if total_feed_mt > 0:
        avg_feed_g_bird = (total_feed_mt * 1000000.0 / total_birds) if total_birds > 0 else 0.0
        feed_lines.append(f"Total| {total_feed_mt:.3f}| {avg_feed_g_bird:.1f}| -| ₹{total_feed_cost:,.2f}")
    else:
        feed_lines.append(f"Total| -| -| -| -")

    # ── 3. SHED-RELATED EXPENDITURE ──
    # Columns: Shed| No. of Labourers Used| No. of Medicines Used| Final Cost (₹)| Daily Payender
    shed_exp_lines = []
    total_labourers = 0
    total_med_used = 0
    total_shed_exp = 0.0

    for shed in sheds:
        shed_exp_df = df[(df['shead_name'] == shed) & (df['category'].isin(['expense', 'medicine', 'purchase']))]
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
                    if extracted:
                        payender = extracted
                        break

        if cost > 0 or labourers > 0 or med_used > 0:
            total_labourers += labourers
            total_med_used += med_used
            total_shed_exp += cost
            shed_exp_lines.append(f"{shed}| {labourers}| {med_used}| ₹{cost:,.2f}| {payender}")
        else:
            shed_exp_lines.append(f"{shed}| -| -| -| -")

    if total_shed_exp > 0 or total_labourers > 0 or total_med_used > 0:
        shed_exp_lines.append(f"Total Shed-Related Expenditure| {total_labourers}| {total_med_used}| ₹{total_shed_exp:,.2f}| -")
    else:
        shed_exp_lines.append(f"Total Shed-Related Expenditure| -| -| -| -")

    # ── 4. COMMON EXPENDITURES ──
    # Particular| Quantity| Amount (₹)
    fuel_amt = 0.0
    fuel_qty = 0.0
    elec_amt = 0.0
    elec_qty = 0.0
    repair_amt = 0.0
    other_amt = 0.0

    common_df = df[df['shead_name'].isin(['', 'nan', 'unknown', 'Common', 'None', None])]
    for _, row in common_df.iterrows():
        cat = row['category']
        notes = str(row['notes'] or '').lower()
        amt = float(row['amount']) if row['amount'] else 0.0
        qty = float(row['quantity']) if row['quantity'] else 0

        if 'fuel' in notes or 'diesel' in notes or 'petrol' in notes:
            fuel_amt += amt
            fuel_qty += qty
        elif 'electricity' in notes or 'current' in notes or 'power' in notes or 'eb bill' in notes:
            elec_amt += amt
            elec_qty += qty
        elif 'repair' in notes or 'maintenance' in notes or 'servicing' in notes or 'mechanic' in notes:
            repair_amt += amt
        elif cat in ['expense', 'purchase']:
            other_amt += amt

    total_common_exp = fuel_amt + elec_amt + repair_amt + other_amt

    common_lines = []
    common_lines.append(f"Fuel| {f'{fuel_qty:.1f} L' if fuel_qty > 0 else '-'}| {f'₹{fuel_amt:,.2f}' if fuel_amt > 0 else '-'}")
    common_lines.append(f"Electricity| {f'{elec_qty:.1f} Units' if elec_qty > 0 else '-'}| {f'₹{elec_amt:,.2f}' if elec_amt > 0 else '-'}")
    common_lines.append(f"Repairs & Maintenance| -| {f'₹{repair_amt:,.2f}' if repair_amt > 0 else '-'}")
    common_lines.append(f"Other Common Expenses| -| {f'₹{other_amt:,.2f}' if other_amt > 0 else '-'}")
    common_lines.append(f"Total Common Expenditure| -| {f'₹{total_common_exp:,.2f}' if total_common_exp > 0 else '-'}")

    # ── 5. DAILY P&L SUMMARY ──
    total_expenses = total_feed_cost + total_shed_exp + total_common_exp
    net_profit = total_prod_value - total_expenses

    pl_lines = []
    pl_lines.append(f"Total Production Value| {f'₹{total_prod_value:,.2f}' if total_prod_value > 0 else '-'}")
    pl_lines.append(f"Total Feed Cost| {f'₹{total_feed_cost:,.2f}' if total_feed_cost > 0 else '-'}")
    pl_lines.append(f"Total Shed-Related Expenditure| {f'₹{total_shed_exp:,.2f}' if total_shed_exp > 0 else '-'}")
    pl_lines.append(f"Total Common Expenditure| {f'₹{total_common_exp:,.2f}' if total_common_exp > 0 else '-'}")
    pl_lines.append(f"Total Expenses| {f'₹{total_expenses:,.2f}' if total_expenses > 0 else '-'}")
    pl_lines.append(f"Net Profit / Loss| {f'₹{net_profit:,.2f}' if (total_prod_value > 0 or total_expenses > 0) else '-'}")

    # Compile the final markdown text
    lines = []
    lines.append(title)
    lines.append("")
    lines.append("1. Production")
    lines.append("")
    lines.append("Shed| Birds| Eggs Produced| Expected Production (%)| Actual Production (%)| Avg. Egg Selling Price (₹/Egg)| Production Value (₹)")
    lines.extend(prod_lines)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("2. Feed Consumption")
    lines.append("")
    lines.append("Shed| Feed Consumed (MT)| Feed per Bird (g/Bird/Day)| Feed Cost/Ton (₹)| Total Feed Cost (₹)")
    lines.extend(feed_lines)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("3. Shed-Related Expenditure")
    lines.append("")
    lines.append("Shed| No. of Labourers Used| No. of Medicines Used| Final Cost (₹)| Daily Payender")
    lines.extend(shed_exp_lines)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("4. Common Fuel and Common Expenditures")
    lines.append("")
    lines.append("Particular| Quantity| Amount (₹)")
    lines.extend(common_lines)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("5. Daily P&L Summary")
    lines.append("")
    lines.append("Particular| Amount (₹)")
    lines.extend(pl_lines)

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  EXCEL EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def _generate_excel(excel_path: str, df: pd.DataFrame, range_type: str, start_date, end_date):
    """Generate a structured Excel with one sheet per category group."""
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:

        # Sheet 1: All Data
        export = df[['time', 'shead_name', 'category', 'quantity', 'unit',
                      'amount', 'notes', 'sender', 'group_name']].copy()
        export.columns = ['Time', 'Shead', 'Category', 'Qty', 'Unit',
                          'Amount (Rs.)', 'Notes', 'Sender', 'Group']
        export['Category'] = export['Category'].str.replace('_', ' ').str.title()
        export.to_excel(writer, sheet_name='All Data', index=False)

        # Sheet 2: Egg Collections
        egg_df = df[df['category'].isin(['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg'])].copy()
        if not egg_df.empty:
            egg_df['Round'] = egg_df['category'].map({
                'egg_collection_1': '1st Collection (Morning)',
                'egg_collection_2': '2nd Collection (Evening)',
                'egg_collection': 'General Collection',
                'egg': 'General Collection',
            })
            egg_exp = egg_df[['time', 'shead_name', 'Round', 'quantity', 'unit']].copy()
            egg_exp.columns = ['Time', 'Shead', 'Round', 'Qty', 'Unit']
            egg_exp.to_excel(writer, sheet_name='Egg Collections', index=False)

        # Sheet 3: Feed & Raw Materials (individual items)
        feed_df = df[df['category'].isin(['feed', 'raw_material'])].copy()
        if not feed_df.empty:
            feed_df['Item'] = feed_df.apply(_get_item_label, axis=1)
            feed_exp = feed_df[['time', 'shead_name', 'Item', 'quantity', 'unit', 'amount']].copy()
            feed_exp.columns = ['Time', 'Shead', 'Item', 'Qty', 'Unit', 'Amount (Rs.)']
            feed_exp.to_excel(writer, sheet_name='Feed & Raw Materials', index=False)

        # Sheet 4: Medicine (individual items)
        med_df = df[df['category'] == 'medicine'].copy()
        if not med_df.empty:
            med_df['Item'] = med_df.apply(_get_item_label, axis=1)
            med_exp = med_df[['time', 'shead_name', 'Item', 'quantity', 'unit', 'amount']].copy()
            med_exp.columns = ['Time', 'Shead', 'Item', 'Qty', 'Unit', 'Amount (Rs.)']
            med_exp.to_excel(writer, sheet_name='Medicine', index=False)

        # Sheet 5: Sales
        sales_df = df[df['category'] == 'sales'].copy()
        if not sales_df.empty:
            sales_exp = sales_df[['time', 'shead_name', 'quantity', 'unit', 'amount', 'notes']].copy()
            sales_exp.columns = ['Time', 'Shead', 'Qty', 'Unit', 'Amount (Rs.)', 'Notes']
            sales_exp.to_excel(writer, sheet_name='Sales', index=False)

        # Sheet 6: Mortality
        mort_df = df[df['category'] == 'mortality'].copy()
        if not mort_df.empty:
            mort_exp = mort_df[['time', 'shead_name', 'quantity', 'notes']].copy()
            mort_exp.columns = ['Time', 'Shead', 'Deaths', 'Notes']
            mort_exp.to_excel(writer, sheet_name='Mortality', index=False)

        # Sheet 7: P&L Summary
        total_revenue = float(df[df['category'].isin(REVENUE_CATS)]['amount'].sum())
        feed_amt  = float(df[df['category'].isin(['feed', 'raw_material'])]['amount'].sum())
        med_amt   = float(df[df['category'] == 'medicine']['amount'].sum())
        purch_amt = float(df[df['category'] == 'purchase']['amount'].sum())
        exp_amt   = float(df[df['category'] == 'expense']['amount'].sum())
        total_expense = feed_amt + med_amt + purch_amt + exp_amt
        net = total_revenue - total_expense

        pl_data = pd.DataFrame([
            {'Category': 'Revenue (Sales)',        'Amount (Rs.)': total_revenue},
            {'Category': 'Feed & Raw Materials',   'Amount (Rs.)': feed_amt},
            {'Category': 'Medicine',               'Amount (Rs.)': med_amt},
            {'Category': 'Purchases',              'Amount (Rs.)': purch_amt},
            {'Category': 'Other Expenses',         'Amount (Rs.)': exp_amt},
            {'Category': 'TOTAL EXPENSES',         'Amount (Rs.)': total_expense},
            {'Category': 'NET PROFIT / LOSS',      'Amount (Rs.)': net},
        ])
        pl_data.to_excel(writer, sheet_name='P&L Summary', index=False)


# ─────────────────────────────────────────────────────────────────────────────
#  PDF EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def _generate_pdf(pdf_path: str, df: pd.DataFrame, range_type: str, start_date, end_date):
    """Generate a structured, section-based PDF report."""
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []

    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, spaceAfter=4, textColor=colors.HexColor('#1b4332'))
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, textColor=colors.HexColor('#2d6a4f'), spaceBefore=12)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9)
    bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')

    period_label = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
    story.append(Paragraph(f"🐔 Farm Report — {range_type.capitalize()}", h1))
    story.append(Paragraph(f"Period: {period_label}", normal))
    story.append(Spacer(1, 0.1*inch))

    def _section_table(headers, rows, col_widths, header_color='#2d6a4f'):
        data = [headers] + rows
        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return tbl

    # ── EGG COLLECTIONS ──
    egg_cats = ['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']
    egg_df = df[df['category'].isin(egg_cats)]
    if not egg_df.empty:
        story.append(Paragraph("🥚 Egg Collections", h2))
        round_map = {
            'egg_collection_1': '1st (Morning)',
            'egg_collection_2': '2nd (Evening)',
            'egg_collection': 'General',
            'egg': 'General',
        }
        egg_rows = []
        for _, row in egg_df.sort_values(['category', 'shead_name']).iterrows():
            egg_rows.append([
                round_map.get(row['category'], row['category']),
                row['shead_name'] or '—',
                f"{row['quantity']:,.0f} {row['unit']}".strip(),
                row['time'],
            ])
        story.append(_section_table(['Round', 'Shead', 'Quantity', 'Time'], egg_rows,
                                    [1.5*inch, 1.2*inch, 1.5*inch, 1.0*inch]))

    # ── MORTALITY ──
    mort_df = df[df['category'] == 'mortality']
    if not mort_df.empty:
        story.append(Paragraph("💀 Mortality", h2))
        rows = [[row['shead_name'] or '—', f"{row['quantity']:,.0f} birds", row['time']]
                for _, row in mort_df.iterrows()]
        rows.append(['TOTAL', f"{mort_df['quantity'].sum():,.0f} birds", ''])
        story.append(_section_table(['Shead', 'Deaths', 'Time'], rows, [2*inch, 2*inch, 1.5*inch]))

    # ── DISPATCH & LOADING ──
    loaded_df = df[df['category'] == 'egg_loaded']
    unloaded_df = df[df['category'] == 'egg_unloaded']
    if not loaded_df.empty or not unloaded_df.empty:
        story.append(Paragraph("📦 Dispatch & Loading", h2))
        rows = []
        for _, row in loaded_df.iterrows():
            rows.append(['Loaded Out', f"{row['quantity']:,.0f} {row['unit']}".strip(), row['time']])
        for _, row in unloaded_df.iterrows():
            rows.append(['Received Back', f"{row['quantity']:,.0f} {row['unit']}".strip(), row['time']])
        story.append(_section_table(['Type', 'Quantity', 'Time'], rows, [2*inch, 2*inch, 1.5*inch]))

    # ── PRODUCTION ──
    prod_df = df[df['category'] == 'production']
    if not prod_df.empty:
        story.append(Paragraph("🏭 Production", h2))
        rows = [[row['shead_name'] or '—', row['notes'] or row['processed_text'] or '', row['time']]
                for _, row in prod_df.iterrows()]
        story.append(_section_table(['Shead', 'Details', 'Time'], rows, [1.5*inch, 3.5*inch, 1.0*inch]))

    # ── HEN WEIGHT ──
    wt_df = df[df['category'] == 'hen_weight']
    if not wt_df.empty:
        story.append(Paragraph("⚖️ Hen Weights", h2))
        rows = [[row['shead_name'] or '—', f"{row['quantity']:.2f} kg", row['time']]
                for _, row in wt_df.iterrows()]
        story.append(_section_table(['Shead', 'Weight', 'Time'], rows, [2*inch, 2*inch, 1.5*inch]))

    # ── FEED & RAW MATERIALS ──
    feed_df = df[df['category'].isin(['feed', 'raw_material'])]
    if not feed_df.empty:
        story.append(Paragraph("🌾 Feed & Raw Materials", h2))
        rows = []
        for _, row in feed_df.iterrows():
            item = _get_item_label(row) or row['notes'] or '—'
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else '—'
            amt_str = f"₹{row['amount']:,.2f}" if row['amount'] > 0 else '—'
            rows.append([row['shead_name'] or '—', item, qty_str, amt_str, row['time']])
        total_f = feed_df['amount'].sum()
        rows.append(['', 'TOTAL', '', f"₹{total_f:,.2f}", ''])
        story.append(_section_table(['Shead', 'Item', 'Qty', 'Amount', 'Time'], rows,
                                    [1.0*inch, 2.0*inch, 1.0*inch, 1.2*inch, 0.8*inch]))

    # ── MEDICINE ──
    med_df = df[df['category'] == 'medicine']
    if not med_df.empty:
        story.append(Paragraph("💊 Medicine", h2))
        rows = []
        for _, row in med_df.iterrows():
            item = _get_item_label(row) or row['notes'] or '—'
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else '—'
            amt_str = f"₹{row['amount']:,.2f}" if row['amount'] > 0 else '—'
            rows.append([row['shead_name'] or '—', item, qty_str, amt_str, row['time']])
        total_m = med_df['amount'].sum()
        rows.append(['', 'TOTAL', '', f"₹{total_m:,.2f}", ''])
        story.append(_section_table(['Shead', 'Medicine', 'Qty', 'Amount', 'Time'], rows,
                                    [1.0*inch, 2.0*inch, 1.0*inch, 1.2*inch, 0.8*inch]))

    # ── PURCHASES ──
    purch_df = df[df['category'] == 'purchase']
    if not purch_df.empty:
        story.append(Paragraph("🛒 Purchases", h2))
        rows = []
        for _, row in purch_df.iterrows():
            item = _get_item_label(row) or row['notes'] or '—'
            amt_str = f"₹{row['amount']:,.2f}" if row['amount'] > 0 else '—'
            rows.append([row['shead_name'] or '—', item, amt_str, row['time']])
        story.append(_section_table(['Shead', 'Item', 'Amount', 'Time'], rows,
                                    [1.2*inch, 2.5*inch, 1.2*inch, 1.1*inch]))

    # ── SALES ──
    sales_df = df[df['category'] == 'sales']
    if not sales_df.empty:
        story.append(Paragraph("💵 Sales", h2))
        rows = []
        for _, row in sales_df.iterrows():
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else '—'
            rows.append([row['shead_name'] or '—', qty_str, f"₹{row['amount']:,.2f}", row['time']])
        rows.append(['TOTAL', '', f"₹{sales_df['amount'].sum():,.2f}", ''])
        story.append(_section_table(['Shead', 'Qty', 'Revenue', 'Time'], rows,
                                    [1.5*inch, 1.5*inch, 1.5*inch, 1.0*inch]))

    # ── P&L SUMMARY ──
    story.append(Paragraph("📊 Profit & Loss", h2))
    
    # Calculate values matching the whatsapp text report exactly
    df_copy = df.copy()
    df_copy['shead_name'] = df_copy['shead_name'].astype(str).str.replace('Shead', 'Shed').str.strip()

    birds_map = {"Shed 1": 15000, "Shed 2": 12000, "Shed 3": 13000}
    expected_prod_pct = 95.0
    default_egg_rate = 5.20
    default_feed_cost_ton = 35000.0

    raw_sheds = df_copy['shead_name'].dropna().unique()
    sheds = ["Shed 1", "Shed 2", "Shed 3"]
    for s in raw_sheds:
        s_str = str(s).strip()
        if s_str and s_str not in sheds and s_str.lower() not in ('nan', 'none', 'unknown', 'common'):
            sheds.append(s_str)
    sheds = [s for s in sheds if s and s.lower() not in ('nan', 'none', 'unknown', 'common')]

    # Calculate production value
    total_birds = 0
    total_eggs = 0
    total_prod_value = 0.0
    sales_df = df_copy[df_copy['category'] == 'sales']
    rates_by_shed = {}
    for _, row in sales_df.iterrows():
        s = row['shead_name']
        qty = float(row['quantity']) if row['quantity'] else 0
        amt = float(row['amount']) if row['amount'] else 0.0
        if qty > 0 and amt > 0:
            unit = str(row['unit']).lower()
            eggs = qty * 30 if 'tray' in unit else qty
            rates_by_shed[s] = amt / eggs

    for shed in sheds:
        shed_prod = df_copy[(df_copy['shead_name'] == shed) & (df_copy['category'] == 'production')]
        birds = birds_map.get(shed, 10000)
        for _, row in shed_prod.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            if qty > 1000:
                birds = int(qty)
                break
        egg_cats = ['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']
        shed_eggs_df = df_copy[(df_copy['shead_name'] == shed) & (df_copy['category'].isin(egg_cats))]
        eggs_produced = 0
        for _, row in shed_eggs_df.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            unit = str(row['unit']).lower()
            eggs_produced += qty * 30 if 'tray' in unit else qty
        if eggs_produced > 0:
            rate = rates_by_shed.get(shed, default_egg_rate)
            prod_val = eggs_produced * rate
            total_birds += birds
            total_eggs += eggs_produced
            total_prod_value += prod_val

    # Calculate feed cost
    total_feed_mt = 0.0
    total_feed_cost = 0.0
    for shed in sheds:
        shed_feed_df = df_copy[(df_copy['shead_name'] == shed) & (df_copy['category'].isin(['feed', 'raw_material']))]
        feed_mt = 0.0
        db_feed_cost = 0.0
        for _, row in shed_feed_df.iterrows():
            qty = float(row['quantity']) if row['quantity'] else 0
            unit = str(row['unit']).lower()
            amt = float(row['amount']) if row['amount'] else 0.0
            if 'kg' in unit:
                feed_mt += qty / 1000.0
            elif 'bag' in unit:
                feed_mt += qty * 0.05
            elif 'mt' in unit or 'ton' in unit:
                feed_mt += qty
            else:
                feed_mt += qty * 0.05 if qty < 500 else qty / 1000.0
            db_feed_cost += amt
        if feed_mt > 0:
            cost = db_feed_cost if db_feed_cost > 0 else (feed_mt * default_feed_cost_ton)
            total_feed_mt += feed_mt
            total_feed_cost += cost

    # Calculate shed expenditure
    total_shed_exp = 0.0
    for shed in sheds:
        shed_exp_df = df_copy[(df_copy['shead_name'] == shed) & (df_copy['category'].isin(['expense', 'medicine', 'purchase']))]
        cost = 0.0
        for _, row in shed_exp_df.iterrows():
            amt = float(row['amount']) if row['amount'] else 0.0
            cost += amt
        total_shed_exp += cost

    # Calculate common expenditure
    fuel_amt = 0.0
    elec_amt = 0.0
    repair_amt = 0.0
    other_amt = 0.0
    common_df = df_copy[df_copy['shead_name'].isin(['', 'nan', 'unknown', 'Common', 'None', None])]
    for _, row in common_df.iterrows():
        cat = row['category']
        notes = str(row['notes'] or '').lower()
        amt = float(row['amount']) if row['amount'] else 0.0
        if 'fuel' in notes or 'diesel' in notes or 'petrol' in notes:
            fuel_amt += amt
        elif 'electricity' in notes or 'current' in notes or 'power' in notes or 'eb bill' in notes:
            elec_amt += amt
        elif 'repair' in notes or 'maintenance' in notes or 'servicing' in notes or 'mechanic' in notes:
            repair_amt += amt
        elif cat in ['expense', 'purchase']:
            other_amt += amt
    total_common_exp = fuel_amt + elec_amt + repair_amt + other_amt

    total_expenses = total_feed_cost + total_shed_exp + total_common_exp
    net_profit = total_prod_value - total_expenses

    pl_rows = [
        ['Total Production Value',          f"₹{total_prod_value:,.2f}" if total_prod_value > 0 else '—'],
        ['Total Feed Cost',                 f"₹{total_feed_cost:,.2f}" if total_feed_cost > 0 else '—'],
        ['Total Shed-Related Expenditure',  f"₹{total_shed_exp:,.2f}" if total_shed_exp > 0 else '—'],
        ['Total Common Expenditure',        f"₹{total_common_exp:,.2f}" if total_common_exp > 0 else '—'],
        ['Total Expenses',                  f"₹{total_expenses:,.2f}" if total_expenses > 0 else '—'],
        ['Net Profit / Loss',               f"₹{net_profit:,.2f}" if (total_prod_value > 0 or total_expenses > 0) else '—']
    ]

    pl_table = Table([['Particular', 'Amount']] + pl_rows, colWidths=[3.2*inch, 2.3*inch])
    pl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b4332')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0fff4')]),
        ('BACKGROUND', (0, -1), (-1, -1),
         colors.HexColor('#d8f3dc') if net_profit >= 0 else colors.HexColor('#ffe0e0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(pl_table)

    doc.build(story)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def generate_custom_report(range_type: str = 'daily'):
    db = SessionLocal()
    start_date, end_date = get_date_range(range_type)

    data = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{start_date} 00:00:00",
        ProcessedData.processed_time <= f"{end_date} 23:59:59"
    ).all()
    db.close()

    if not data:
        return None, None, f"📭 No farm data collected for {start_date.strftime('%d %b %Y')}."

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
        return None, None, f"📭 No classifiable farm data found for {start_date.strftime('%d %b %Y')}."

    os.makedirs("/app/media/reports", exist_ok=True)
    
    # Delete old reports of the same range type to keep directory clean
    import glob
    for old_file in glob.glob(f"/app/media/reports/{range_type.capitalize()}_Report_*"):
        try:
            os.remove(old_file)
        except Exception:
            pass

    timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M")
    excel_path = f"/app/media/reports/{range_type.capitalize()}_Report_{timestamp}.xlsx"
    pdf_path   = f"/app/media/reports/{range_type.capitalize()}_Report_{timestamp}.pdf"

    summary_text = _build_whatsapp_summary(df, range_type, start_date, end_date)
    _generate_excel(excel_path, df, range_type, start_date, end_date)
    _generate_pdf(pdf_path, df, range_type, start_date, end_date)

    return pdf_path, excel_path, summary_text


def generate_daily_reports():
    return generate_custom_report('daily')
