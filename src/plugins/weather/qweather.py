from typing import Literal
from jinja2 import Template
from pathlib import Path

from src.config import Config
from src.const.path import ASSETS, TEMPLATES
from src.utils.file import read
from src.utils.network import Request
from src.utils.generate import generate

from ._template import template_weather

class QWeather:
    def __init__(self, city_name: str):
        self.city = city_name
        self.location_id: str = ""
        self.actual_name: tuple[str, str, str] = ("", "", "")
        self.real_time_weather: dict = {}
        self._7d_weather: list[dict] = []
        self.cloth_advice: str = ""
    
    async def get_location(self) -> Literal[False] | None:
        url = "https://geoapi.qweather.com/v2/city/lookup"
        params = {
            "location": self.city,
            "key": Config.weather.token
        }
        response = (await Request(url, params=params).get())
        if response.status_code != 200:
            return False
        self.location_id = response.json()["location"][0]["id"]
        self.actual_name = (
            response.json()["location"][0]["adm1"],
            response.json()["location"][0]["adm2"],
            response.json()["location"][0]["name"]
        )
        
    async def get_real_time_weather(self) -> Literal[False] | None:
        if not self.location_id:
            return False
        url = f"{Config.weather.url}/v7/weather/now"
        params = {
            "location": self.location_id,
            "key": Config.weather.token
        }
        response = (await Request(url, params=params).get())
        if response.status_code != 200:
            return False
        self.real_time_weather = response.json()["now"]

    async def get_7d_weather(self) -> Literal[False] | None:
        if not self.location_id:
            return False
        url = f"{Config.weather.url}/v7/weather/7d"
        params = {
            "location": self.location_id,
            "key": Config.weather.token
        }
        response = (await Request(url, params=params).get())
        if response.status_code != 200:
            return False
        self._7d_weather = response.json()["daily"]
    
    async def get_cloth_advice(self) -> Literal[False] | None:
        if not self.location_id:
            return False
        url = f"{Config.weather.url}/v7/indices/1d"
        params = {
            "location": self.location_id,
            "key": Config.weather.token,
            "type": 3
        }
        response = (await Request(url, params=params).get())
        if response.status_code != 200:
            return False
        self.cloth_advice = response.json()["daily"][0]["text"]
    
    async def generate_image(self):
        await self.get_location()
        if not self.location_id:
            return "未找到该城市，请检查城市名称！"
        await self.get_7d_weather()
        await self.get_real_time_weather()
        await self.get_cloth_advice()
        name = " ".join(list(self.actual_name))
        unit = "°C"
        current_temp = self.real_time_weather["temp"] + unit
        humidity = self.real_time_weather["humidity"] + "%"
        wind_speed = self.real_time_weather["windSpeed"] + "km/h"
        pressure = self.real_time_weather["pressure"] + "hPa"
        current_icon = self.real_time_weather["icon"]
        current_weather = self.real_time_weather["text"]
        today_weather = self._7d_weather[0]
        today_max = today_weather["tempMax"] + unit
        today_min = today_weather["tempMin"] + unit
        future_weather = []
        for each_weather in self._7d_weather:
            date = each_weather["fxDate"]
            day_icon = each_weather["iconDay"]
            night_icon = each_weather["iconNight"]
            day_weather = each_weather["textDay"]
            night_weather = each_weather["textNight"]
            temp = each_weather["tempMin"] + unit + " / " + each_weather["tempMax"] + unit
            future_weather.append(
                Template(template_weather).render(
                    date = date,
                    day_icon = day_icon,
                    day_weather = day_weather,
                    night_icon = night_icon,
                    night_weather = night_weather,
                    temp = temp
                )
            )
        html = Template(
            read(TEMPLATES + "/weather/weather.html")
        ).render(
            css = Path(TEMPLATES + "/weather/qweather-icons.css").as_uri(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            name = name,
            current_temp = current_temp,
            today_min_temp = today_min,
            today_max_temp = today_max,
            current_weather_icon = current_icon,
            current_weather = current_weather,
            humidity = humidity,
            wind_speed = wind_speed,
            pressure = pressure,
            cloth_advice = self.cloth_advice,
            future_weather = "\n".join(future_weather)
        )
        return await generate(html, ".weather-container", segment=True)