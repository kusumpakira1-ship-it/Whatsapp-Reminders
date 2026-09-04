import sys
from datetime import datetime, timedelta

def get_next_occurrence(base_time, frequency):
    next_time = base_time
    freq = str(frequency or '').lower().strip()
    # Simulate step advance
    if freq == 'weekly':
        next_time += timedelta(days=7)
    elif freq in ('mon-sat', 'mon_to_sat', 'mon_sat'):
        next_time += timedelta(days=1)
        if next_time.weekday() == 6:  # Sunday -> jump to Monday
            next_time += timedelta(days=1)
    elif freq in ('mon-fri', 'mon_to_fri', 'weekdays', 'weekday'):
        next_time += timedelta(days=1)
        while next_time.weekday() in (5, 6):  # Sat & Sun -> jump to Monday
            next_time += timedelta(days=1)
    else:
        next_time += timedelta(days=1)
    return next_time

def check_should_skip(dt, freq):
    weekday = dt.weekday() # 0=Mon, 5=Sat, 6=Sun
    f = str(freq or '').lower().strip()
    if f in ('mon-sat', 'mon_to_sat', 'mon_sat') and weekday == 6:
        return True, "Sunday (Weekly Off)"
    if f in ('mon-fri', 'mon_to_fri', 'weekdays', 'weekday') and weekday in (5, 6):
        return True, f"Weekend ({dt.strftime('%A')})"
    return False, "Active Day"

print("--- TESTING MON-SAT LOGIC ---")
# Test Mon-Sat for Fri, Sat, Sun
base_fri = datetime(2026, 9, 4, 10, 0, 0) # Friday
base_sat = datetime(2026, 9, 5, 10, 0, 0) # Saturday
base_sun = datetime(2026, 9, 6, 10, 0, 0) # Sunday

skip_fri, msg = check_should_skip(base_fri, 'mon-sat')
print(f"Fri {base_fri.strftime('%Y-%m-%d (%A)')}: Skip={skip_fri} ({msg})")
skip_sat, msg = check_should_skip(base_sat, 'mon-sat')
print(f"Sat {base_sat.strftime('%Y-%m-%d (%A)')}: Skip={skip_sat} ({msg})")
skip_sun, msg = check_should_skip(base_sun, 'mon-sat')
print(f"Sun {base_sun.strftime('%Y-%m-%d (%A)')}: Skip={skip_sun} ({msg})")

next_from_sat = get_next_occurrence(base_sat, 'mon-sat')
print(f"Mon-Sat Next after Sat {base_sat.strftime('%A')}: {next_from_sat.strftime('%Y-%m-%d (%A)')}")
assert next_from_sat.weekday() == 0 # Should be Monday!
print("[OK] Mon-Sat assertions passed!")

print("\n--- TESTING MON-FRI LOGIC ---")
skip_fri, msg = check_should_skip(base_fri, 'mon-fri')
print(f"Fri {base_fri.strftime('%Y-%m-%d (%A)')}: Skip={skip_fri} ({msg})")
skip_sat, msg = check_should_skip(base_sat, 'mon-fri')
print(f"Sat {base_sat.strftime('%Y-%m-%d (%A)')}: Skip={skip_sat} ({msg})")
skip_sun, msg = check_should_skip(base_sun, 'mon-fri')
print(f"Sun {base_sun.strftime('%Y-%m-%d (%A)')}: Skip={skip_sun} ({msg})")

next_from_fri = get_next_occurrence(base_fri, 'mon-fri')
print(f"Mon-Fri Next after Fri {base_fri.strftime('%A')}: {next_from_fri.strftime('%Y-%m-%d (%A)')}")
assert next_from_fri.weekday() == 0 # Should be Monday!
print("[OK] Mon-Fri assertions passed!")
