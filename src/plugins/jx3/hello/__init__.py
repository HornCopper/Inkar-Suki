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

from .hello import *

from nonebot import require, get_bots

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

dailyv2 = on_command("jx3_hello", aliases={"看世界"}, force_whitespace=True, priority=5)

@dailyv2.handle()
async def jx3_dailyv2(args: Message = CommandArg()):
    about_img = await world_()
    await dailyv2.finish(ms.image(about_img))


@scheduler.scheduled_job("cron", hour="07", minute="10")
async def run_at_07_10():
    image_data = await world_()
    bots = get_bots()
    groups = os.listdir(DATA)
    group = {}
    for i in list(bots):
        single_groups = await bots[i].call_api("get_group_list")
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s
    for group_id in groups:
        for x in list(group):
            if int(group_id) in group[x]:
                if "日常" in getGroupData(str(group_id), "subscribe"):
                    await bots[x].call_api("send_group_msg", group_id=int(group_id), message=MessageSegment.image(image_data))