import json
import random
import time
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

LATITUDE = 22.5431
LONGITUDE = 114.0579
TIMEZONE = "Asia/Shanghai"

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
SUNRISE_SUNSET_URL = "https://api.sunrise-sunset.org/json"

WMO_WEATHER = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _day_of_month(lt):
    """与 /bin/date 的 %e 一致：1–9 日为前导空格而非 0。"""
    return f"{lt.tm_mday:2d}"


def _timezone_abbr(lt):
    tz = time.strftime("%Z", lt)
    if tz:
        return tz
    if lt.tm_isdst:
        return time.tzname[1] or time.tzname[0] or "UTC"
    return time.tzname[0] or "UTC"


def format_bin_date(lt=None):
    """与 macOS / Linux 默认 `date` 输出一致（C locale）。"""
    if lt is None:
        lt = time.localtime()
    return (
        f"{time.strftime('%a %b', lt)} {_day_of_month(lt)} "
        f"{time.strftime('%H:%M:%S', lt)} {_timezone_abbr(lt)} {lt.tm_year}"
    )


def _today_refresh_markers(lt=None):
    """README 中可能出现的“今日”日期片段（兼容旧格式）。"""
    if lt is None:
        lt = time.localtime()
    month = time.strftime("%b", lt)
    year = lt.tm_year
    day = lt.tm_mday
    return (
        f"{month} {_day_of_month(lt)} {year}",
        f"{month} {day:02d} {year}",
    )


def weather_code_desc(code):
    return WMO_WEATHER.get(code, f"Weather code {code}")


def fetch_json(url, params=None, timeout=30):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "DukeNan/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def format_utc_iso_to_local_hm(iso_time):
    dt = datetime.fromisoformat(iso_time)
    local = dt.astimezone(ZoneInfo(TIMEZONE))
    return local.strftime("%H:%M")


def get_weather():
    data = fetch_json(
        OPEN_METEO_URL,
        params={
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset",
            "timezone": TIMEZONE,
        },
    )
    current = data["current"]
    daily = data["daily"]

    return {
        "max_temp": str(int(round(daily["temperature_2m_max"][0]))),
        "min_temp": str(int(round(daily["temperature_2m_min"][0]))),
        "current_temp": str(int(round(current["temperature_2m"]))),
        "weatherDesc": weather_code_desc(current["weather_code"]),
    }


def get_sunrise_daily(date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    elif len(date) == 8:
        date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"

    payload = fetch_json(
        SUNRISE_SUNSET_URL,
        params={
            "lat": LATITUDE,
            "lng": LONGITUDE,
            "date": date,
            "formatted": 0,
        },
    )
    results = payload["results"]

    return {
        "sun_rise": format_utc_iso_to_local_hm(results["sunrise"]),
        "sun_set": format_utc_iso_to_local_hm(results["sunset"]),
    }


def update_readme(data):
    with open("README.md", "w") as f:
        with open("index.html", "r") as f1:
            html = f1.read().format(**data)
        f.write(html)


def log_format(data, cost_time):
    print("\n=====================log==================================")
    print("\033[0;36m{}\033[0m".format(json.dumps(data, ensure_ascii=False, indent=4)))
    print("\n响应时间: {} ms".format(cost_time))
    print("=====================log==================================\n")


def _already_updated_today():
    """检查 README 今天是否已经更新过"""
    try:
        with open("README.md", "r") as f:
            content = f.read()
        return any(marker in content for marker in _today_refresh_markers())
    except FileNotFoundError:
        return False


def run():
    skip = random.randint(0, 1)
    if skip and _already_updated_today():
        return "Skip update"
    now = datetime.now()
    data = {}
    data.update(get_weather())
    data.update(get_sunrise_daily(now.strftime("%Y%m%d")))
    data["refresh_date"] = format_bin_date()
    update_readme(data)
    log_format(data, (datetime.now() - now).microseconds / 1000)

    print("README file updated")
    return "successful"


if __name__ == "__main__":
    run()
