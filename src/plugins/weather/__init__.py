from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from .qweather import QWeather

WeatherMatcher = on_command("天气", priority=5, force_whitespace=True)

@WeatherMatcher.handle()
async def  _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    reply = await QWeather(args.extract_plain_text()).generate_image()
    await WeatherMatcher.finish(reply)