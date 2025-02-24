from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent
)

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.permission import check_permission
from src.utils.database.operation import get_group_settings

from .api import get_recruit_image

RecruitMatcher = on_command("jx3_recruit", aliases={"招募"}, force_whitespace=True, priority=5)


@RecruitMatcher.handle()
async def _(event: GroupMessageEvent, full_argument: Message = CommandArg()):
    additions = get_group_settings(str(event.group_id), "additions")
    if not Config.jx3.api.enable and not "Preview" in additions:
        return
    filter = False
    additions = get_group_settings(str(event.group_id), "additions")
    if not isinstance(additions, list):
        return
    if "招募过滤" in additions:
        filter = True
    args = full_argument.extract_plain_text().split(" ")
    if len(args) == 0:
        """
        招募
        """
        server = Server(None, event.group_id).server
        if server is None:
            await RecruitMatcher.finish(PROMPT.ServerNotExist)
        data = await get_recruit_image(server, "", False, filter)
    elif len(args) == 1:
        """
        招募 KW
        招募 SRV
        """
        server = Server(args[0]).server
        if server is None:
            """
            招募 KW
            """
            group_server = Server(None, event.group_id).server
            if group_server is None:
                await RecruitMatcher.finish(PROMPT.ServerNotExist)
            data = await get_recruit_image(group_server, args[0], False, filter)
        else:
            """
            招募 SRV
            """
            data = await get_recruit_image(server, "", False, filter)
    elif len(args) == 2:
        """
        招募 SRV KW
        """
        server = Server(args[0], event.group_id).server
        if server is None:
            await RecruitMatcher.finish(PROMPT.ServerNotExist)
        data = await get_recruit_image(server, args[1], False, filter)
    else:
        await RecruitMatcher.finish(PROMPT.ArgumentCountInvalid)
    await RecruitMatcher.finish(data)