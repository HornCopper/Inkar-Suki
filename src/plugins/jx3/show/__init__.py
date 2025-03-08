from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent,
    MessageSegment as ms
)

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request
from src.utils.database.operation import get_group_settings
from src.utils.database.player import search_player
from src.plugins.jx3.server.api import get_server_status

ShowMatcher = on_command("jx3_show", aliases={"名片", "qq秀", "QQ秀", "名片秀"}, force_whitespace=True, priority=5)

@ShowMatcher.handle()
async def _(event: GroupMessageEvent, full_argument: Message = CommandArg()):
    additions = get_group_settings(str(event.group_id), "additions")
    if not Config.jx3.api.enable or "Preview" not in additions:
        return
    if full_argument.extract_plain_text() == "":
        return
    args = full_argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await ShowMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(args) == 1:
        server = None
        name = args[0]
    elif len(args) == 2:
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await ShowMatcher.finish(PROMPT.ServerNotExist)
    status = "开服" in (await get_server_status(server))
    if not status:
        await ShowMatcher.finish("尚未开服，无法查询名片！")
    role_exist = (await search_player(role_name=name, server_name=server)).format_jx3api()["code"] == 200
    if not role_exist:
        await ShowMatcher.finish("未找到该玩家，请检查后重试！")
    data = (await Request(f"{Config.jx3.api.url}/data/show/card?server={server}&name={name}&token={Config.jx3.api.token_v2}").get()).json()
    if data["code"] != 200:
        await ShowMatcher.finish("查询名片失败，请检查玩家是否存在？名片是否过审？")
    image_url = data["data"]["showAvatar"]
    image = ms.image(
        (await Request(image_url).get()).content
    )
    msg = ms.at(event.user_id) + f" 查询成功！来自：{name}·{server}" + image
    await ShowMatcher.finish(msg)