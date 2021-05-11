import time
import os
from datetime import datetime

import requests
from lxml import etree

APP_CODE = os.getenv('APP_CODE', 'abc')



def get_weather(app_code):
    headers = {
        'Authorization': f'APPCODE {app_code}'
    }
    url = 'https://jisutqybmf.market.alicloudapi.com/weather/query?city=深圳'
    data = requests.get(url, headers=headers).json()
    resp = {
        'temp': data['result']['temp'],
        'templow': data['result']['templow'],
        'temphigh': data['result']['temphigh'],
    }
    return resp


def get_data(index_date):
    url = 'https://richuriluo.xuenb.com/1985.html'
    text = requests.get(url).text
    tree = etree.HTML(text)
    node_list = tree.xpath('//*[@id="main_content"]/*//tr[position()>1]')
    map = {}
    for node in node_list:
        date = node.xpath('./td[1]/text()')[0].split(" ")[0]
        sun_rise = node.xpath('./td[2]/text()')[0]
        sun_set = node.xpath('./td[4]/text()')[0]
        map[date] = {
            'sun_rise': sun_rise,
            'sun_set': sun_set
        }
    return map[index_date]


def update_readme(data):
    with open("README.md", 'w') as f:
        with open('index.html', 'r') as f1:
            html = f1.read().format(**data)
        f.write(html)


def run():
    now = datetime.now()
    data = {}
    weather_data = get_weather(APP_CODE)
    sun_date = get_data(str(now.date()))
    data.update(weather_data)
    data.update(sun_date)
    data['refresh_date'] = '{}, {}'.format(now.strftime('%a %b %d %H:%M'), time.strftime('%Z', time.localtime()))
    update_readme(data)
    print('README file updated')
    return 'successful'


if __name__ == '__main__':
    run()
