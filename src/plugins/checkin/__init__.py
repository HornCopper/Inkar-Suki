from typing import Literal, Any
from jinja2 import Template

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent,
    MessageEvent,
    MessageSegment as ms
)
from nonebot.params import CommandArg, ArgPlainText

from src.accounts.manage import AccountManage, CheckinRewards
from src.utils.analyze import sort_dict_list
from src.utils.database.classes import Account
from src.utils.database import db
from src.utils.permission import check_permission, denied
from src.utils.analyze import check_number
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._message import message_sign
from ._template import template_body, table_head

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
    if int(arg[1]) <= 0:
        await AddCoinMatcher.finish("金币数量需要是正整数！")
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
    if int(arg[1]) <= 0:
        await ReduceCoinMatcher.finish("金币数量需要是正整数！")
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

CoinRankMatcher = on_command("金币排行", force_whitespace=True, priority=5)

@CoinRankMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    accounts: list[Account] | Any = db.where_all(Account(), default=[])
    accounts_data: list[dict[str, Any]] = sort_dict_list([a.dump() for a in accounts], "coins")[::-1]
    table = []
    num = 0
    in_forward_30 = False
    for account in accounts_data:
        num += 1
        if num == 31:
            break
        if account["user_id"] == event.user_id:
            in_forward_30 = True
        table.append(
            Template(template_body).render(
                rank = str(num),
                avatar = "https://q.qlogo.cn/headimg_dl?dst_uin=" + str(account["user_id"]) + "&spec=100&img_type=jpg",
                user_id = str(account["user_id"])[:2] + "*" * (len(str(account["user_id"])) - 4) + str(account["user_id"])[-2:],
                coins = account["coins"],
                count = account["checkin_counts"]
            )
        )
    if not in_forward_30:
        rank = next((i for i, d in enumerate(accounts_data) if d["user_id"] == event.user_id), False)
        if isinstance(rank, int):
            account = accounts_data[rank]
            table.append(
                Template(template_body).render(
                    rank = rank + 1,
                    avatar = "https://q.qlogo.cn/headimg_dl?dst_uin=" + str(account["user_id"]) + "&spec=100&img_type=jpg",
                    user_id = account["user_id"],
                    coins = account["coins"],
                    count = account["checkin_counts"]
                )
            )
        else:
            table.append(
                Template(template_body).render(
                    rank = "未上榜",
                    avatar = "https://q.qlogo.cn/headimg_dl?dst_uin=" + str(event.user_id) + "&spec=100&img_type=jpg",
                    user_id = str(event.user_id),
                    coins = "0",
                    count = "0"
                )
            )
    html = str(
        HTMLSourceCode(
            application_name = " · 金币统计",
            table_head = table_head,
            table_body = "\n".join(table)
        )
    )
    image = await generate(html, "table", segment=True)
    await CoinRankMatcher.finish(image)