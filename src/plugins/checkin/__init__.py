from typing import Literal

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, ArgPlainText

from src.accounts.manage import AccountManage, CheckinRewards
from src.utils.permission import check_permission, denied
from src.utils.analyze import check_number

from ._message import message_sign

import random

LotMatcher = on_command("抽签", force_whitespace=True, priority=5)

@LotMatcher.handle()
async def lq_(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    await LotMatcher.send("确定要抽取吗")

@LotMatcher.got("pb")
async def pq_(reply: str = ArgPlainText("pb")):
    if reply == "确定" or "yes" or "抽取" or "嗯":
        for i in range(3):
            a = random.randint(0,100)
            if a >= 5 :
                pd=True
                await LotMatcher.send(
                    message="抽到了正签"
                )
                break
            else:
                await LotMatcher.send(
                    message="是空签呢",
                    at_sender=True,
                )
                pd=False
                break

        if pd is True:
            await LotMatcher.finish(message=f"\n{random.choice(message_sign)}",at_sender=True)
        else:
           await LotMatcher.finish()
    else:
        await LotMatcher.finish("\n放弃了抽取",at_sender=True,)

CheckinMatcher = on_command("签到", aliases={"打卡"}, force_whitespace=True, priority=5)


@CheckinMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    status: CheckinRewards | Literal[False] = AccountManage(event.user_id).checkin()
    if not status:
        await CheckinMatcher.finish("您已经签到过了哦，请等待次日7点后重试！")
    msg = ms.at(event.user_id) + f" 签到成功！\n本日幸运值：{status.lucky_value}\n金币：+{status.coin}\n累计签到：{status.total_days}天"
    if status.is_lucky:
        msg += "\n触发额外奖励！获得 10000 金币！"
    await CheckinMatcher.finish(msg)

CoinMatcher = on_command("金币", aliases={"余额"}, force_whitespace=True, priority=5)


@CoinMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    coin: int = AccountManage(event.user_id).coins
    await CoinMatcher.finish(ms.at(event.user_id) + f"\n您的金币余额为：\n{coin}枚")


AddCoinMatcher = on_command("增加金币", force_whitespace=True, priority=5)

@AddCoinMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 10):
        await AddCoinMatcher.finish(denied(10))
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await AddCoinMatcher.finish("唔……参数数量不正确哦~")
    if not check_number(arg[0]) or not check_number(arg[1]):
        await AddCoinMatcher.finish("唔……参数需要是数字哦~")
    AccountManage(int(arg[0])).add_coin(int(arg[1]))
    await AddCoinMatcher.finish("已向该账户添加了" + arg[1] + "枚金币！")

ReduceCoinMatcher = on_command("减少金币", force_whitespace=True, priority=5)

@ReduceCoinMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 10):
        await ReduceCoinMatcher.finish(denied(10))
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await ReduceCoinMatcher.finish("唔……参数数量不正确哦~")
    if not check_number(arg[0]) or not check_number(arg[1]):
        await ReduceCoinMatcher.finish("唔……参数需要是数字哦~")
    AccountManage(int(arg[0])).reduce_coin(int(arg[1]))
    await ReduceCoinMatcher.finish("已向该账户扣除了" + arg[1] + "枚金币！")

TradeCoinMatcher = on_command("交易金币", force_whitespace=True, priority=5)

@TradeCoinMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await TradeCoinMatcher.finish("唔……参数数量不正确哦~")
    if not check_number(arg[0]) or not check_number(arg[1]):
        await TradeCoinMatcher.finish("唔……参数需要是数字哦~")
    if AccountManage(event.user_id).coins < int(arg[1]):
        await TradeCoinMatcher.finish("唔……你没有那么多的金币！")
    else:
        AccountManage(event.user_id).reduce_coin(int(arg[1]))
        AccountManage(int(arg[0])).add_coin(int(arg[1]))
        await TradeCoinMatcher.finish("已成功将" + arg[1] + "枚金币从您的账户转到" + str(arg[0]) + "的账户！")