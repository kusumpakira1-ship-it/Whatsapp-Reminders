import re

def parse_mortality_text(text: str):
    records = []
    lines = text.splitlines()
    for line in lines:
        line_str = line.strip()
        if not line_str or 'totall' in line_str.lower() or 'wisemortality' in line_str.lower():
            continue
            
        # Match Shed mortality e.g. "1-5", "1- 5", "1 - 5", "Shed 1: 5"
        m_shed = re.match(r'^(?:shed|shead)?\s*(\d{1,2})[\s:\-_]+(\d+)\s*$', line_str, re.IGNORECASE)
        if m_shed:
            shed_num = m_shed.group(1)
            qty = int(m_shed.group(2))
            records.append({
                'shead_name': f'Shed {shed_num}',
                'category': 'mortality',
                'quantity': qty,
                'unit': 'birds',
                'notes': line_str
            })
            continue

        # Match Chick Whites e.g. "Whites:2", "Whites - 2", "Chick Whites: 2"
        m_whites = re.search(r'(?:chick\s+)?whites?[\s:\-_]+(\d+)', line_str, re.IGNORECASE)
        if m_whites:
            qty = int(m_whites.group(1))
            records.append({
                'shead_name': 'Chick Whites',
                'category': 'mortality',
                'quantity': qty,
                'unit': 'birds',
                'notes': line_str
            })
            continue

        # Match Chick Brownie e.g. "Brownie: 0", "Chick Brownie: 0"
        m_brownie = re.search(r'(?:chick\s+)?brownies?[\s:\-_]+(\d+)', line_str, re.IGNORECASE)
        if m_brownie:
            qty = int(m_brownie.group(1))
            records.append({
                'shead_name': 'Chick Brownie',
                'category': 'mortality',
                'quantity': qty,
                'unit': 'birds',
                'notes': line_str
            })
            continue

    return records


def parse_production_text(text: str):
    records = []
    lines = text.splitlines()
    for line in lines:
        line_str = line.strip()
        if not line_str or 'sed_age_production' in line_str.lower():
            continue
            
        # Pattern e.g. "1._ 53._ 599.10_92%-94%" or "2._53_628.7_94%_94%" or "5_16th week."
        # Parts: shed_num, age, trays.eggs, actual_pct, book_pct
        m = re.match(r'^(?:shed|shead)?\s*(\d+)[\._\s]+(?:(\d+)(?:th\s*week)?)?[\._\s]*(\d+\.?\d*)?', line_str, re.IGNORECASE)
        if m:
            shed_num = m.group(1)
            trays_val_str = m.group(3)
            if trays_val_str:
                try:
                    if '.' in trays_val_str:
                        trays_part, eggs_part = trays_val_str.split('.', 1)
                        trays = int(trays_part)
                        eggs = int(eggs_part) if eggs_part.isdigit() else 0
                    else:
                        trays = int(trays_val_str)
                        eggs = 0
                    total_eggs = trays * 30 + eggs
                    records.append({
                        'shead_name': f'Shed {shed_num}',
                        'category': 'egg_collection_1',
                        'quantity': total_eggs,
                        'unit': 'eggs',
                        'notes': f'{trays} trays {eggs} eggs ({line_str})'
                    })
                except ValueError:
                    pass

        # Match individual collection e.g. "100 Trays of Production 8th Shead first Collection"
        m_single = re.search(r'(\d+)\s*trays?.*?(?:(\d+)(?:st|nd|rd|th)?\s*(?:shed|shead))', line_str, re.IGNORECASE)
        if not m_single:
            m_single = re.search(r'(?:(\d+)(?:st|nd|rd|th)?\s*(?:shed|shead)).*?(\d+)\s*trays?', line_str, re.IGNORECASE)
            if m_single:
                shed_num = m_single.group(1)
                trays = int(m_single.group(2))
                records.append({
                    'shead_name': f'Shed {shed_num}',
                    'category': 'egg_collection_1',
                    'quantity': trays * 30,
                    'unit': 'eggs',
                    'notes': line_str
                })
        else:
            trays = int(m_single.group(1))
            shed_num = m_single.group(2)
            records.append({
                'shead_name': f'Shed {shed_num}',
                'category': 'egg_collection_1',
                'quantity': trays * 30,
                'unit': 'eggs',
                'notes': line_str
            })

    return records


def parse_weight_text(text: str):
    records = []
    # Match blocks like:
    # Shead 1:
    # Actual: 1.516
    # Book: 1.541
    # OR Shead Chick: Whites \n Actual: 141
    blocks = re.split(r'\n(?=(?:shead|shed)\b)', text, flags=re.IGNORECASE)
    for block in blocks:
        block_str = block.strip()
        if not block_str:
            continue
        m_shed = re.search(r'(?:shead|shed)\s*(?:chick\s*:\s*|chick\s+)?([a-z0-9\s]+)[:;\n]', block_str, re.IGNORECASE)
        m_act = re.search(r'actual[:;\s]+(\d+\.?\d*)', block_str, re.IGNORECASE)
        if m_shed and m_act:
            raw_shed = m_shed.group(1).strip()
            if raw_shed.isdigit():
                shed_name = f"Shed {raw_shed}"
            elif 'white' in raw_shed.lower():
                shed_name = "Chick Whites"
            elif 'brown' in raw_shed.lower():
                shed_name = "Chick Brownie"
            elif 'grower' in raw_shed.lower():
                shed_name = "Grower"
            else:
                shed_name = f"Shed {raw_shed}"

            act_wt = float(m_act.group(1))
            # Convert grams to kg if > 50
            if act_wt > 50:
                act_wt_kg = act_wt / 1000.0
            else:
                act_wt_kg = act_wt

            records.append({
                'shead_name': shed_name,
                'category': 'hen_weight',
                'quantity': act_wt_kg,
                'unit': 'kg',
                'notes': block_str.replace('\n', ' ')
            })
    return records


# Test sample text from user
sample_mort = """Shed wisemortality 
1-5
2-5
3-4
4-6
5-4
6-8
7-3
8-4
Chick
Whites:2
Brownie: 0
Totall  36 mortality"""

sample_prod = """SED_AGE_PRODUCTION-AP-BP
     1._ 53._ 599.10_92%-94%
      2._53_628.7_94%_94%
      3._23_653.1_91%_93%
      4._65_631.12_93%_90%
      5_16th week.
      6_71_599.2_89%_88%
      7_79_571.10_87%_84%
      8_35_690.2_95%_97%"""

sample_wt = """Birds Weight:
Shead 1:
Actual: 1.516
Book: 1.541
25 Gms 🔴

Shead 2: h
Actual: 1.485
Book: 1.541
56Gms 🔴

Shead Chick: Whites 
Actual: 141
Book: 165
24🔴

Shed Chick Brownie;
Actual;172
Book; 165
7🟢

Shead Grower
Actual: 0
Book: 0"""

print("=== MORTALITY PARSED ===")
for r in parse_mortality_text(sample_mort):
    print(r)

print("\n=== PRODUCTION PARSED ===")
for r in parse_production_text(sample_prod):
    print(r)

print("\n=== WEIGHT PARSED ===")
for r in parse_weight_text(sample_wt):
    r_copy = dict(r)
    r_copy['notes'] = r_copy['notes'].encode('ascii', 'ignore').decode('ascii')
    print(r_copy)
