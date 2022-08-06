import sys
from urllib.error import HTTPError
import nonebot
from nonebot.log import logger
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from utils import get_api
async def getWeatherByCity(city: str) -> str:
    final_link = f"https://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&needMoreData=true&city={city}"
    try:
        information = await get_api(final_link)
    except:
        raise HTTPError("Can't connect to " + final_link)
    if information["code"] == 105:
        return "您要查询的城市不存在哦，请检查后重试~"
    elif information["code"] == 0:
        more_info = information["data"]["list"]
        weather_warn = more_info[0]["moreData"]["alert"]
        now_temp = more_info[0]["temp"]
        msg = f"查询到地区「{city}」（当前温度{now_temp}℃）的信息啦："
        if type(weather_warn) == type([]):
            for i in weather_warn:
                warn_info = i["content"]
                msg = msg + "\n" + warn_info
        else:
            pass
        try:
            for i in more_info:
                weather = i["weather"] # 天气
                humidity = i["humidity"] # 湿度
                wind = i["wind"] # 风向
                pm25 = i["pm25"] # PM 2.5
                lowest_temp = i["low"] # 最低气温
                highest_temp = i["high"] # 最高气温
                airData = i["airData"] # 空气指数
                airQuality = i["airQuality"] # 空气质量
                windLevel = i["windLevel"] # 风力等级
                date = i["date"] # 预报日期
                if wind[-1] == "风":
                    wind = wind + str(windLevel) + "级"
                daily_weather = f"日期：{date}，{weather}（{lowest_temp}℃~{highest_temp}℃）；\n空气指数{airData}，{airQuality}，大气PM2.5含量为{pm25}；\n{wind}，湿度{humidity}。"
                msg = msg + "\n" + daily_weather
        except:
            msg = "唔……不支持查询国外城市哦"
        return msg
    else:
        return "唔……未知错误。"