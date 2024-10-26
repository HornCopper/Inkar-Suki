from pathlib import Path

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.const.jx3.school import School
from src.utils.network import Request

from .api import get_zlrank

ZiliRankMatcher = on_command("jx3_zlrank", aliases={"资历排行", "资历榜单"}, priority=5, force_whitespace=True)

@ZiliRankMatcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [0, 1, 2]:
        await ZiliRankMatcher.finish(PROMPT.ArgumentCountInvalid)
    if args[0] == "":
        """
        CMD
        """
        server = ""
        school = ""
        if server is None:
            await ZiliRankMatcher.finish(PROMPT.ServerNotExist)
    elif len(args) == 1:
        """
        CMD SCH/SRV
        """
        if Server(args[0], None).server is None:
            """
            CMD SCH
            """
            school = School(args[0]).name or ""
            server = ""
        else:
            """
            CMD SRV
            """
            school = ""
            server = Server(args[0], None).server or ""
    elif len(args) == 2:
        server = Server(args[0], event.group_id).server or ""
        school = School(args[1]).name or ""
    image = Request(
        Path(
            await get_zlrank(server, school)
        ).as_uri()
    ).local_content
    await ZiliRankMatcher.finish(ms.image(image))