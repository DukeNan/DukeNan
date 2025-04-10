import json
import random
import time
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

CITY = "Shenzhen"


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
    res = requests.get(url)
    table = pd.read_html(StringIO(res.text), header=2)[1]
    month_df = table.iloc[:-1,]
    day_df = month_df[month_df.iloc[:, 0].astype(str).str.zfill(2) == date[6:]]
    day_df.index = pd.to_datetime([date] * len(day_df), format="%Y%m%d")

    ser = day_df.iloc[-1]
    sun_rise = ser["Sunrise"]
    sun_set = ser["Sunset"]
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


def run():
    if random.randint(0, 1):
        return "Skip update"
    now = datetime.now()
    data = {}
    weather_data = get_weather(CITY)
    sun_date = get_sunrise_daily(now.strftime("%Y%m%d"), CITY)
    data.update(weather_data)
    data.update(sun_date)
    data["refresh_date"] = "{} {}".format(
        now.strftime("%a %b %d %H:%M"), time.strftime("%Z", time.localtime())
    )
    update_readme(data)
    log_format(data, (datetime.now() - now).microseconds / 1000)

    print("README file updated")
    return "successful"


if __name__ == "__main__":
    run()
