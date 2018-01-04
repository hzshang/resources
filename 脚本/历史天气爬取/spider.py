#!/usr/bin/env python
# coding=utf8
import urllib2
import time
from lxml import etree
import urllib
import csv
import traceback

BASE = "https://www.wunderground.com/history/airport/ZSSS/%s/DailyHistory.html"
BEGIN = "2017-10-01"
END = "2017-12-25"
CITY = "Shanghai"
STATE = "China"
DIR = "./"
DAILY_CSV = DIR+"daily.csv"
HOUR_CSV = DIR+"hour.csv"


# 获取天数
def getDay():
    begin = int(time.mktime(time.strptime(BEGIN, "%Y-%m-%d")))
    end = int(time.mktime(time.strptime(END, "%Y-%m-%d")))
    for i in range(begin, end, 3600 * 24):
        yield time.strftime("%Y/%m/%d", time.localtime(i))
    return


def average(list):
    if None in list:
        list.remove(None)
    return sum(list) / len(list)


def parase_dom(date, dom):
    def getVisibility(i):
        if len(i) == 0:
            ret = None
        else:
            ret = float(i[0][0].text)
        return ret

    def getEvent(i):
        if i.text == u'\n\t\xa0\n':
            ret = None
        else:
            ret = i.text.replace("\n", "")
        return ret

    def getWindSpeed(i):
        if len(i) == 0:
            ret = 0
        else:
            ret = float(i[1][0].text)
        return ret

    def getTemp(i):
        if len(i) == 0:
            ret = None
        else:
            ret = float(i[0][0].text)
        return ret

    def getHumidity(i):
        try:
            ret = float(i.text.strip("%")) / 100
        except Exception as e:
            ret = None
        return ret

    def getDewPoint(i):
        if len(i) == 0:
            ret = None
        else:
            ret = float(i[0][0].text)
        return ret

    def getPressure(i):
        if len(i) == 0:
            ret = None
        else:
            ret = float(i[0][0].text)
        return ret

    html = etree.HTML(dom.decode("utf8"))
    table = html.xpath("""//*[@id="obsTable"]/tbody""")[0]
    header = html.xpath("""//*[@id="obsTable"]/thead/tr""")[0]

    if len(header) == 13:
        for i in range(len(table)):
            table[i].remove(table[i].findall("""td[3]""")[0])

    tables = []
    for i in table:
        tmp_dic = {
            "Date": date,
            "Time": i[0].text,
            "Temp": getTemp(i[1]),
            "DewPoint": getDewPoint(i[2]),
            "Humidity": getHumidity(i[3]),
            "Pressure": getPressure(i[4]),
            "Visibility": getVisibility(i[5]),
            "WindDir": i[6].text,
            "WindSpeed": getWindSpeed(i[7]),
            "Precip": i[9].text,
            "Event": getEvent(i[10]),
            "Conditions": i[11].text,
        }
        tables.append(tmp_dic)

    ave_temp = average([x["Temp"] for x in tables]);
    ave_humidity = average([x["Humidity"] for x in tables]);
    ave_pressure = average([x["Pressure"] for x in tables]);
    ave_windSpeed = average([x["WindSpeed"] for x in tables]);
    daily = {
        "Date":date,
        "Temp": ave_temp,
        "Humidity": ave_humidity,
        "Pressure": ave_pressure,
        "WindSpeed": ave_windSpeed
    }
    return [daily, tables]


def main():
    values = {
        "req_city": CITY,
        "req_state": "",
        "req_statename": STATE,
        "reqdb.zip": "",
        "reqdb.magic": "",
        "reqdb.wmo": ""
    }
    daily_file = open(DAILY_CSV, "w+")
    hourly_file = open(HOUR_CSV, "w+")
    first=True
    data = urllib.urlencode(values)
    try:
        for i in getDay():
            url = BASE % i
            try:
                request = urllib2.Request(url, data)
                response = urllib2.urlopen(request)
                print i, "page download success"
            except Exception as e:
                print i, "page download fail"
                continue
            else:
                daily_table, hourly_table = parase_dom(i, response.read())
                if first:
                    first=False
                    hourly_header=["Date","Time","Temp","DewPoint","Humidity","Pressure","Visibility","WindDir","WindSpeed","Precip","Event","Conditions"]
                    daily_header=["Date","Temp","Humidity","Pressure","WindSpeed"]
                    hourly_writer = csv.DictWriter(hourly_file, fieldnames=hourly_header)
                    daily_writer = csv.DictWriter(daily_file, fieldnames=daily_header)
                    hourly_writer.writeheader()
                    daily_writer.writeheader()

                hourly_writer.writerows(hourly_table)
                daily_writer.writerows([daily_table])

    except Exception as e:
        traceback.print_exc()
    finally:
        daily_file.close()
        hourly_file.close()


if __name__ == '__main__':
    main()
