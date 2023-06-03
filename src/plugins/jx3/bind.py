import sys
import nonebot
import json
import os

from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot import on_command

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
DATA = TOOLS[:-5] + "data"

from .jx3 import server_mapping

from src.tools.file import read, write

bind = on_command("jx3_bind", aliases={"绑定"}, priority=5)
@bind.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    personal_data = await bot.call_api("get_group_member_info", group_id = event.group_id, user_id = event.user_id, no_cache = True)
    if personal_data["role"] not in ["owner", "admin"]:
        await bind.finish("唔……只有群主或管理员才可以修改哦！")
    server = args.extract_plain_text()
    group = str(event.group_id)
    exact_server = server_mapping(server)
    if exact_server == False and server != "":
        await bind.finish("唔……服务器名称输入有误，绑定失败！")
    if server != "":
        server = exact_server
    path = DATA + "/" + group + "/jx3group.json"
    now = json.loads(read(path))
    now["server"] = server
    write(path, json.dumps(now, ensure_ascii=False))
    if server == "":
        await bind.finish("已清除本群的绑定信息！\n注意：推送将推送全服内容！")
    await bind.finish("绑定成功！\n当前区服为：" + server)