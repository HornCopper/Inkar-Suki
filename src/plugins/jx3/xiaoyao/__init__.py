#from nonebot.adapters.onebot.v11 import MessageSegment as ms, MessageEvent, Bot, Message, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.helpers import extract_image_urls
from nonebot.exception import ActionFailed
from nonebot import require
from nonebot.matcher import Matcher
from src.tools.basic import *
import requests
import base64
import json
import os



from nonebot import require, get_bots
from src.tools.basic import *

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

xiaoyao = on_command("jx3_xiaoyao", aliases={"全部小药"}, force_whitespace=True, priority=5)

@xiaoyao.handle()
async def jx3_xiaoyao(args: Message = CommandArg()):
    about_img = await get_content('https://s21.ax1x.com/2024/06/19/pkBZytO.jpg')
    await xiaoyao.finish(ms.image(about_img))
