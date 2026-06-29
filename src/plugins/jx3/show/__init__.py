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
from src.const.path import SHOW
from src.utils.network import Request
from src.utils.file import write
from src.utils.permission import check_group_permission
from src.utils.database.player import search_player

from .api import get_role_card_url

def cache_show(image_bytes: bytes, name: str, server: str) -> None:
    path = SHOW + f"/{name}·{server}.png"
    write(path, image_bytes, "wb")

show_matcher = on_command("jx3_show", aliases={"名片", "qq秀", "QQ秀", "名片秀"}, force_whitespace=True, priority=5)

@show_matcher.handle()
async def _(event: GroupMessageEvent, full_argument: Message = CommandArg()):
    if full_argument.extract_plain_text() == "":
        return
    args = full_argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await show_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：名片 <服务器> <角色名>")
    if len(args) == 1:
        server = None
        name = args[0]
    elif len(args) == 2:
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await show_matcher.finish(PROMPT.ServerNotExist)
    role_data = await search_player(role_name=name, server_name=server)
    if not role_data.roleId:
        await show_matcher.finish(PROMPT.PlayerNotExist)
    image_url = await get_role_card_url(role_data)
    if not image_url:
        await show_matcher.finish(PROMPT.PlayerNotExist)
    image_bytes = (await Request(image_url).get()).content
    cache_show(image_bytes, name, server)
    image = ms.image(
        image_bytes
    )
    msg = ms.at(event.user_id) + f" 查询成功！来自：{name}·{server}" + image
    await show_matcher.finish(msg)
