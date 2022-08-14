import sys, nonebot
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from .weather import getWeatherByCity

weather = on_command("weather",aliases={"天气"},priority=5)
@weather.handle()
async def _(args: Message = CommandArg()):
    city = args.extract_plain_text()
    msg = await getWeatherByCity(city)
    await weather.finish(msg)