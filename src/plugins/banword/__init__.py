from typing import Union, Any

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import CommandArg

from src.tools.permission import checker, error
from src.tools.database import group_db, BannedWordList


banword = on_command("banword", force_whitespace=True, priority=5)


@banword.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):  # 违禁词封锁
    if args.extract_plain_text() == "":
        return
    bw = args.extract_plain_text()
    if not checker(str(event.user_id), 10):
        await banword.finish(error(5))
    if bw:
        current_data: Union[BannedWordList, Any] = group_db.where_one(BannedWordList(), default=BannedWordList())
        current_list = current_data.banned_word_list
        if bw in current_list:
            await banword.finish("唔……封禁失败，已经封禁过了。")
        current_list.append(bw)
        current_data.banned_word_list = current_list
        group_db.save(current_data)
        await banword.finish("已成功封禁词语！")
    else:
        await banword.finish("您封禁了什么？")

unbanword = on_command("unbanword", force_whitespace=True, priority=5)  # 违禁词解封


@unbanword.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await unbanword.finish(error(5))
    bw = args.extract_plain_text()
    if bw:
        current_data: Union[BannedWordList, Any] = group_db.where_one(BannedWordList(), default=BannedWordList())
        current_list = current_data.banned_word_list
        if bw in current_list:
            current_list.remove(bw)
            current_data.banned_word_list = current_list
            group_db.save(current_data)
            await unbanword.finish("成功解封词语！")
        else:
            await unbanword.finish("您解封了什么？")
    else:
        await unbanword.finish("您解封了什么？")