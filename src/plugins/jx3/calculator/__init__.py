from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, GroupUploadNoticeEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.plugins.notice import notice

from .lxg import LingxueCalculator
from .rdps import RDPSCalculator

import re
import json

yinlongjue_calc_matcher = on_command("jx3_calculator_lyj", aliases={"凌雪计算器"}, priority=5, force_whitespace=True)

@yinlongjue_calc_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await yinlongjue_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：凌雪计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await yinlongjue_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await LingxueCalculator.with_name(name, server)
    if isinstance(instance, str):
        await yinlongjue_calc_matcher.finish(instance)
    data = await instance.image(len(raw_arg) > len(arg))
    await yinlongjue_calc_matcher.finish(data)

def check_jcl_name(filename: str) -> bool:
    if not filename.startswith("IKS-"):
        return False
    pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-[\u4e00-\u9fff\d]+(?:\(\d+\))?-[\u4e00-\u9fff\d]+(?:\(\d+\))?\.jcl$"
    )
    return bool(pattern.match(filename[4:]))

@notice.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent):
    if not check_jcl_name(event.file.name):
        return
    else:
        try:
            image = await RDPSCalculator(event.file.name[4:], event.model_dump()["file"]["url"])
        except json.decoder.JSONDecodeError:
            await bot.send_group_msg(group_id=event.group_id, message="啊哦，警长的服务器目前似乎暂时有些小问题，请稍后再使用JCL分析？")
        await bot.send_group_msg(group_id=event.group_id, message=Message(image))