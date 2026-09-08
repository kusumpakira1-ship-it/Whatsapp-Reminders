import re

def check_task_match(tn, msg_text):
    tn = tn.lower()
    msg = msg_text.lower().strip()
    
    if 'tank a' in tn:
        has_clean_kw = any(w in msg for w in ['clean', 'cleaned', 'done', 'completed', 'finish', 'finished', 'complete'])
        has_tank_a = 'tank a' in msg or 'tanka' in msg or 'tank-a' in msg
        return has_clean_kw and has_tank_a
    elif 'tank b' in tn:
        has_clean_kw = any(w in msg for w in ['clean', 'cleaned', 'done', 'completed', 'finish', 'finished', 'complete'])
        has_tank_b = 'tank b' in msg or 'tankb' in msg or 'tank-b' in msg
        return has_clean_kw and has_tank_b
    return False

test_msgs = [
    'cleaned',
    'done',
    'surrounding cleaned',
    'tank a cleaned',
    'tank a done',
    'tank b cleaned',
    'tanka completed',
    'tankb done'
]

print('=== Tank A Matching ===')
for m in test_msgs:
    print(f'Msg: "{m}" -> {check_task_match("Tank A Cleaning Reminder", m)}')

print('\n=== Tank B Matching ===')
for m in test_msgs:
    print(f'Msg: "{m}" -> {check_task_match("Tank B Cleaning Reminder", m)}')
