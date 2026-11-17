import sys, os
backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from daily_feed_rates_summary import scheduled_daily_feed_rates_summary_job

if __name__ == "__main__":
    scheduled_daily_feed_rates_summary_job()

