import os
import re
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, text/html, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_shead1_birds_count():
    """Fetches total active live birds for Shead 1 from batch_json_to_web.php."""
    live_birds = 15783  # Fallback default if web request fails
    session = requests.Session()
    login_url = "https://sunfra.com/farm/sunfra/login/login.php"
    login_data = {"username": "sunfra", "password": "Sunfra#321", "remember_me": "1"}

    try:
        session.post(login_url, data=login_data, headers=REQUEST_HEADERS, timeout=15)
        batch_url = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
        resp = session.get(batch_url, headers=REQUEST_HEADERS, timeout=15)

        if resp.status_code == 200:
            html = resp.text
            labels_m = re.search(r'const\s+shedLabels\s*=\s*(\[.*?\]);', html)
            birds_m = re.search(r'const\s+liveBirdsData\s*=\s*(\[.*?\]);', html)

            if labels_m and birds_m:
                labels = json.loads(labels_m.group(1))
                birds = json.loads(birds_m.group(1))
                for lbl, count in zip(labels, birds):
                    clean_lbl = str(lbl).strip().lower()
                    if "shead 1" in clean_lbl or "shed 1" in clean_lbl:
                        if count and count > 0:
                            live_birds = int(count)
                            break
    except Exception as e:
        logger.error(f"Error fetching live birds for Shead 1: {e}")

    return live_birds


def calculate_water_consumption_status(water_litres: float, live_birds: int):
    """
    Evaluates water consumption status based on live birds count:
    Target Daily Water = live_birds * 1.0 Litre (e.g. 15,783 birds -> 15,783 L target).
    Range: 95% to 105% of target -> Moderate 🟡
    < 95% -> Low 🔵
    > 105% -> High 🔴
    """
    if live_birds <= 0:
        return "Moderate 🟡"

    target_litres = float(live_birds)
    min_target = 0.95 * target_litres
    max_target = 1.05 * target_litres

    if min_target <= water_litres <= max_target:
        return "Moderate 🟡"
    elif water_litres < min_target:
        return "Low 🔵"
    else:
        return "High 🔴"


def fetch_silo_and_water_data():
    """Fetches Feed Consumed (Silo) and Water Consumed for Shead 1 from sunfra.com APIs."""
    feed_tons = 0.0
    water_litres = 0.0

    session = requests.Session()
    login_url = "https://sunfra.com/farm/sunfra/login/login.php"
    login_data = {"username": "sunfra", "password": "Sunfra#321", "remember_me": "1"}

    try:
        session.post(login_url, data=login_data, headers=REQUEST_HEADERS, timeout=15)

        # 1. Silo Feed Data for Shead 1
        silo_url = "https://sunfra.com/farm/sunfra/sensor/indicator_last_value_json.php?client_id=1"
        resp_silo = session.get(silo_url, headers=REQUEST_HEADERS, timeout=15)
        if resp_silo.status_code == 200:
            s_data = resp_silo.json()
            if s_data and s_data.get("data"):
                for shed_name, shed_obj in s_data["data"].items():
                    if "shead-1" in shed_name.lower() or "shed-1" in shed_name.lower() or "shead 1" in shed_name.lower():
                        ind_val = shed_obj.get("indicator_data", {}).get("value", "0")
                        val_kg = float(ind_val) if ind_val else 0.0
                        feed_tons = round(val_kg / 1000.0, 2)
                        break
                if feed_tons == 0.0 and s_data["data"]:
                    first_item = list(s_data["data"].values())[0]
                    ind_val = first_item.get("indicator_data", {}).get("value", "0")
                    feed_tons = round(float(ind_val) / 1000.0, 2)

        # 2. Water Flow Data for Shead 1
        water_url = "https://sunfra.com/farm/sunfra/sensor/water_flow_last_value_json.php?client_id=1"
        resp_water = session.get(water_url, headers=REQUEST_HEADERS, timeout=15)
        if resp_water.status_code == 200:
            w_data = resp_water.json()
            if w_data and w_data.get("data"):
                for shed_name, shed_obj in w_data["data"].items():
                    if "shead-1" in shed_name.lower() or "shed-1" in shed_name.lower() or "shead 1" in shed_name.lower():
                        water_litres = round(float(shed_obj.get("water_used_liters", 0.0)), 2)
                        break
                if water_litres == 0.0 and w_data.get("grand_total_liters"):
                    water_litres = round(float(w_data["grand_total_liters"]), 2)

    except Exception as e:
        logger.error(f"Error fetching IoT sensor data from sunfra.com: {e}")

    return feed_tons, water_litres


def fetch_chittoor_weather_data():
    """Fetches real-time weather and tomorrow forecast (including rain %) for Chittoor, AP, India."""
    weather_info = {
        "today_temp": "32°C",
        "today_feels": "34°C",
        "today_wind": "13 km/h",
        "tomorrow_temp": "21°C - 33°C",
        "tomorrow_feels": "25°C - 35°C",
        "tomorrow_wind": "14 km/h",
        "rain_forecast": "0% (No rain expected)"
    }

    try:
        resp = requests.get("https://wttr.in/Chittoor?format=j1", timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            curr = data['current_condition'][0]
            today = data['weather'][0]
            tomorrow = data['weather'][1]

            t_temp = f"{curr.get('temp_C', '32')}°C"
            t_feels = f"{curr.get('FeelsLikeC', '34')}°C"
            t_wind = f"{curr.get('windspeedKmph', '13')} km/h"

            tom_min_t = tomorrow.get('mintempC', '21')
            tom_max_t = tomorrow.get('maxtempC', '33')
            tom_temp = f"{tom_min_t}°C - {tom_max_t}°C"

            tom_hourly = tomorrow.get('hourly', [])
            feels_list = [int(h.get('FeelsLikeC', 25)) for h in tom_hourly] if tom_hourly else [25, 35]
            tom_feels = f"{min(feels_list)}°C - {max(feels_list)}°C" if feels_list else "25°C - 35°C"
            tom_wind = f"{tomorrow.get('hourly', [{}])[0].get('windspeedKmph', '14')} km/h"

            max_rain_chance = 0
            rain_timings = []
            for h in tom_hourly:
                chance = int(h.get('chanceofrain', 0))
                time_raw = h.get('time', '0')
                if chance > max_rain_chance:
                    max_rain_chance = chance
                if chance >= 20:
                    t_int = int(time_raw) // 100
                    period = 'AM' if t_int < 12 else 'PM'
                    t_12 = t_int if t_int <= 12 else t_int - 12
                    if t_12 == 0:
                        t_12 = 12
                    rain_timings.append(f"{t_12}:00 {period}")

            if max_rain_chance > 0 and rain_timings:
                unique_times = list(dict.fromkeys(rain_timings))
                times_str = ", ".join(unique_times[:3])
                rain_forecast_str = f"{max_rain_chance}% (Expected around {times_str})"
            elif max_rain_chance > 0:
                rain_forecast_str = f"{max_rain_chance}% (Possibility of rain)"
            else:
                rain_forecast_str = "0% (No rain expected)"

            weather_info = {
                "today_temp": t_temp,
                "today_feels": t_feels,
                "today_wind": t_wind,
                "tomorrow_temp": tom_temp,
                "tomorrow_feels": tom_feels,
                "tomorrow_wind": tom_wind,
                "rain_forecast": rain_forecast_str
            }
    except Exception as e:
        logger.error(f"Error fetching weather data for Chittoor: {e}")

    return weather_info


def generate_sunfra_farms_summary_report(target_date=None) -> str:
    """Generates the formatted Sunfra Farms Summary Report."""
    now_ist = datetime.now(IST)
    if not target_date:
        target_date = now_ist.date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    date_str = target_date.strftime("%d %b %Y")

    feed_tons, water_litres = fetch_silo_and_water_data()
    live_birds = fetch_shead1_birds_count()
    water_avg_status = calculate_water_consumption_status(water_litres, live_birds)
    weather = fetch_chittoor_weather_data()

    report_lines = [
        "🌾*Sunfra Farms Summary Report*",
        f"*Date:* {date_str}",
        "",
        "*Shead 1:*",
        f"Feed Consumed: {feed_tons:.2f} Tons",
        f"Water Consumed: {water_litres:.2f} Litres",
        f"Avg Water Consumed: {water_avg_status}",
        "",
        "*Shead 2:* 🔴 Not Installed",
        "*Shead 3:* 🔴 Not Installed",
        "*Shead 4:* 🔴 Not Installed",
        "*Shead 5:* 🔴 Not Installed",
        "*Shead 6:* 🔴 Not Installed",
        "*Shead 7:* 🔴 Not Installed",
        "*Shead 8:* 🔴 Not Installed",
        "*Shead Chick:* 🔴 Not Connected",
        "*Shead Grower:* 🔴 Not Installed",
        "",
        "*Today Weather Report:*",
        f"Temperature: {weather['today_temp']}",
        f"Feels Like: {weather['today_feels']}",
        f"Wind Speed: {weather['today_wind']}",
        "",
        "*Tomorrow Weather Forecast:*",
        f"Temperature: {weather['tomorrow_temp']}",
        f"Feels Like: {weather['tomorrow_feels']}",
        f"Wind Speed: {weather['tomorrow_wind']}",
        f"Rain Expected %: {weather['rain_forecast']}"
    ]

    return "\n".join(report_lines)


def send_daily_sunfra_farms_summary_report(target_phone: str = "917259510983@c.us"):
    """Generates and dispatches the Sunfra Farms Summary Report to target recipient."""
    logger.info("Executing Sunfra Farms Summary Report Dispatcher...")
    try:
        report_msg = generate_sunfra_farms_summary_report()
        if report_msg:
            if not target_phone.endswith("@c.us") and not target_phone.endswith("@g.us"):
                target_phone = f"{target_phone}@c.us"

            logger.info(f"Sending Sunfra Farms Summary Report to {target_phone}...")
            ok = send_waha_message(target_phone, report_msg)
            logger.info(f"Sunfra Farms Summary Report send result: {ok}")
            return ok
    except Exception as e:
        logger.error(f"Error in send_daily_sunfra_farms_summary_report: {e}")
        return False


if __name__ == "__main__":
    msg = generate_sunfra_farms_summary_report()
    print("--- SAMPLE REPORT ---")
    print(msg.encode('utf-8').decode('utf-8', errors='ignore'))
