from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent
from nonebot.params import CommandArg

from src.utils.analyze import check_number

from .api import get_daren_count, get_tieba_records

LookupPersonMatcher = on_command("jx3_cheater", aliases={"查人", "骗子"}, force_whitespace=True, priority=5)

@LookupPersonMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    uin = args.extract_plain_text()
    if not check_number(uin):
        await LookupPersonMatcher.finish("唔……查人请给出纯数字的QQ号！")
    if int(uin) > 9999999999 or int(uin) < 100000:
        await LookupPersonMatcher.finish("唔……该QQ号无效！")
    data = await bot.call_api("get_cookies", domain="vip.qq.com")
    pskey = data["cookies"]
    count = await get_daren_count(event.self_id, int(uin), pskey)
    info = await bot.call_api("get_stranger_info", user_id=int(uin))
    nickname = info["nickname"]
    tieba = await get_tieba_records(int(uin))
    msg = f"查询到以下信息：\nQQ号：{uin}\n昵称：{nickname}\n达人：{count}天\n强制打开主页：https://ti.qq.com/friends/recall?uin={uin}\n\n贴吧：{tieba}\n\n线下交易需谨慎，交易请至万宝楼！"
    await LookupPersonMatcher.finish(msg)