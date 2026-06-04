import json
import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

CITY = "Shenzhen"


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


def get_weather(city):
    # https://wttr.in/Shenzhen?format=j1&lang=zh-cn
    url = f"https://wttr.in/{city}?format=j1&lang=zh-cn"
    data = requests.get(url).json()
    current_condition = data["current_condition"][0]
    weather = data["weather"][0]
    weatherDesc = current_condition["weatherDesc"][0]["value"].split(",")[0]
    current_temp = current_condition["temp_C"]
    max_temp = weather["maxtempC"]
    min_temp = weather["mintempC"]

    resp = {
        "max_temp": max_temp,
        "min_temp": min_temp,
        "current_temp": current_temp,
        "weatherDesc": weatherDesc,
    }
    return resp


def get_sunrise_daily(date="20190801", city="shenzhen"):
    year = date[:4]
    month = date[4:6]
    url = f"https://www.timeanddate.com/sun/china/{city}?month={month}&year={year}"
    res = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; DukeNan/1.0)"},
    )
    soup = BeautifulSoup(res.text, "lxml")
    table = soup.find("table", id="as-monthsun") or soup.find_all("table")[1]
    rows = table.find_all("tr")
    headers = [c.get_text(strip=True) for c in rows[1].find_all(["th", "td"])]

    day = date[6:].zfill(2)
    matched = None
    for row in rows[3:-1]:
        cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
        if cells and str(cells[0]).zfill(2) == day:
            matched = dict(zip(headers, cells[: len(headers)]))

    sun_rise = matched["Sunrise"]
    sun_set = matched["Sunset"]
    resp = {
        "sun_rise": format_time_string(sun_rise),
        "sun_set": format_time_string(sun_set),
    }
    return resp


def format_time_string(time_str: str):
    time_str = time_str.lower()
    temp_str = time_str.split(" ")[0]
    hour, minute = temp_str.split(":")
    if "am" in time_str:
        hour = hour.zfill(2)
    elif "pm" in time_str:
        hour = str(int(hour) + 12)
    else:
        pass
    return f"{hour}:{minute}"


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
    weather_data = get_weather(CITY)
    sun_date = get_sunrise_daily(now.strftime("%Y%m%d"), CITY)
    data.update(weather_data)
    data.update(sun_date)
    data["refresh_date"] = format_bin_date()
    update_readme(data)
    log_format(data, (datetime.now() - now).microseconds / 1000)

    print("README file updated")
    return "successful"


if __name__ == "__main__":
    run()
