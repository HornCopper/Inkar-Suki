from pathlib import Path

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment as ms, MessageEvent, Bot, Message, GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.helpers import extract_image_urls
from nonebot.exception import ActionFailed
from nonebot.matcher import Matcher
from nonebot.params import Arg
from nonebot.typing import T_State

from src.tools.config import Config
from src.tools.permission import checker, error
from src.plugins.sign import Sign

import requests
import random
import base64
import os

from .check_pass import check_cd, check_max
from .rdimg import *
from .joke import *
from .bmi import *
from .help import *
from .poke import *

what_eat = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?吃(什么|啥|点啥)$", priority=5)
what_drink = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?喝(什么|啥|点啥)$", priority=5)
view_all_dishes = on_regex(r"^(/)?查[看|询]?全部(菜[单|品]|饮[料|品])$", priority=5)
view_dish = on_regex(r"^(/)?查[看|询]?(菜[单|品]|饮[料|品])[\s]?(.*)?", priority=5)
add_dish = on_regex(r"^(/)?添[加]?(菜[品|单]|饮[品|料])[\s]?(.*)?", priority=99,
                    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)
del_dish = on_regex(r"^(/)?删[除]?(菜[品|单]|饮[品|料])[\s]?(.*)?", priority=5,
                    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)

# 今天吃什么路径
img_eat_path = Path(os.path.join(os.path.dirname(__file__), "eat_pic"))
all_file_eat_name = os.listdir(str(img_eat_path))

# 今天喝什么路径
img_drink_path = Path(os.path.join(os.path.dirname(__file__), "drink_pic"))
all_file_drink_name = os.listdir(str(img_drink_path))

# 载入bot名字
Bot_NICKNAME = Config.bot_basic.bot_name

@del_dish.handle()
async def _(matcher: Matcher, state: T_State):
    args = list(state["_matched_groups"])
    state["type"] = args[1]
    if args[2]:
        matcher.set_arg("name", args[2])


@del_dish.got("name", prompt="请告诉我你要删除哪个菜品或饮料,发送“取消”可取消操作")
async def _(state: T_State, name: Message = Arg()):
    if str(name) == "取消":
        await del_dish.finish("已取消")
    if state["type"] in ["菜单", "菜品"]:
        img = img_eat_path / (str(name)+".jpg")
    elif state["type"] in ["饮料", "饮品"]:
        img = img_drink_path / (str(name)+".jpg")
    try:
        os.remove(img)
    except OSError:
        msg = state["type"]
        await del_dish.finish(f"不存在该{msg}，请检查下菜单再重试吧")
    msg = state["type"]
    await del_dish.send(f"已成功删除{msg}:{name}", at_sender=True)


@add_dish.handle()
async def got_dish_name(matcher: Matcher, state: T_State):
    args = list(state["_matched_groups"])
    state["type"] = args[1]
    if args[2]:
        matcher.set_arg("dish_name", args[2])


@add_dish.got("dish_name", prompt="⭐请发送名字\n发送“取消”可取消添加")
async def _(state: T_State, dish_name: Message = Arg()):
    state["name"] = str(dish_name)
    if str(dish_name) == "取消":
        await add_dish.finish("已取消")


@add_dish.got("img", prompt="⭐图片也发给我吧\n发送“取消”可取消添加")
async def _(state: T_State, img: Message = Arg()):
    if str(img) == "取消":
        await add_dish.finish("已取消")
    img_url = extract_image_urls(img) # type: ignore
    if not img_url:
        await add_dish.finish("没有找到图片(╯▔皿▔)╯，请稍后重试", at_sender=True)

    if state["type"] in ["菜品", "菜单"]:
        path = img_eat_path
    elif state["type"] in ["饮料", "饮品"]:
        path = img_drink_path

    dish_img = requests.get(url=img_url[0])
    with open(path / str(state["name"]+".jpg"), "wb") as f: # type: ignore
        f.write(dish_img.content)
    name = state["name"]
    type_ = state["type"]
    await add_dish.finish(f"成功添加{type_}:{name}\n" + ms.image(img_url)) # type: ignore


@view_dish.handle()
async def _(matcher: Matcher, state: T_State, event: MessageEvent):
    # 正则匹配组
    args = list(state["_matched_groups"])
    if args[1] in ["菜单", "菜品"]:
        state["type"] = "吃的"
    elif args[1] in ["饮料", "饮品"]:
        state["type"] = "喝的"
    # 设置下一步got的arg
    if args[2]:
        matcher.set_arg("name", args[2])


@view_dish.got("name", prompt=f"请告诉{Bot_NICKNAME}具体菜名或者饮品名吧")
async def _(state: T_State, name: Message = Arg()):
    if state["type"] == "吃的":
        img = img_eat_path / (str(name)+".jpg")
    elif state["type"] == "喝的":
        img = img_drink_path / (str(name)+".jpg")
    try:
        await view_dish.send(ms.image(img))
    except ActionFailed:
        await view_dish.finish("没有找到你所说的，请检查一下菜单吧", at_sender=True)

# 初始化内置时间的last_time
time = 0
# 用户数据
user_count = {}


@what_drink.handle()
async def _(msg: MessageEvent):
    global time, user_count
    check_result, remain_time, new_last_time = check_cd(time)
    if not check_result:
        time = new_last_time
        await what_drink.finish(f"cd冷却中,还有{remain_time}秒", at_sender=True)
    else:
        is_max, user_count = check_max(msg, user_count)
        if is_max:
            await what_drink.finish(random.choice(max_msg), at_sender=True)
        time = new_last_time
        img_name = random.choice(all_file_drink_name)
        img = img_drink_path / img_name
        with open(img, "rb") as im:
            img_bytes = im.read()
        base64_str = "base64://" + base64.b64encode(img_bytes).decode()
        msg = (f"{Bot_NICKNAME}建议你喝: \n⭐{img.stem}⭐\n" + ms.image(base64_str)) # type: ignore
        try:
            await what_drink.send("正在为你找好喝的……")
            await what_drink.send(msg, at_sender=True) # type: ignore
        except ActionFailed:
            await what_drink.finish("出错啦！没有找到好喝的~")


@what_eat.handle()
async def _(msg: MessageEvent):
    global time, user_count
    check_result, remain_time, new_last_time = check_cd(time)
    if not check_result:
        time = new_last_time
        await what_eat.finish(f"cd冷却中,还有{remain_time}秒", at_sender=True)
    else:
        is_max, user_count = check_max(msg, user_count)
        if is_max:
            await what_eat.finish(random.choice(max_msg), at_sender=True)
        time = new_last_time
        img_name = random.choice(all_file_eat_name)
        img = img_eat_path / img_name
        with open(img, "rb") as im:
            img_bytes = im.read()
        base64_str = "base64://" + base64.b64encode(img_bytes).decode()
        msg = (f"{Bot_NICKNAME}建议你吃: \n⭐{img.stem}⭐\n" + ms.image(base64_str)) # type: ignore
        try:
            await what_eat.send("正在为你找好吃的……")
            await what_eat.send(msg, at_sender=True) # type: ignore
        except ActionFailed:
            await what_eat.finish("出错啦！没有找到好吃的~")

max_msg = ("你今天吃的够多了！不许再吃了(´-ωก`)", "吃吃吃，就知道吃，你都吃饱了！明天再来(▼皿▼#)", "(*｀へ´*)你猜我会不会再给你发好吃的图片",
           f"没得吃的了，{Bot_NICKNAME}的食物都被你这坏蛋吃光了！", "你在等我给你发好吃的？做梦哦！你都吃那么多了，不许再吃了！ヽ(≧Д≦)ノ")

self_ban = on_command("禁言我", aliases={"抽奖"}, force_whitespace=True, priority=5)

@self_ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    num = random.randint(1, 720)
    await bot.call_api("set_group_ban", user_id=event.user_id, group_id=event.group_id, duration=num*60)
    await self_ban.finish(f"自助禁言成功！音卡送您{num}分钟的红茶~")

# ai = on_command("chat", aliases={"AI"}, priority=5, force_whitespace=True)

# @ai.handle()
# async def _(event: GroupMessageEvent, args: Message = CommandArg()):
#     if args.extract_plain_text() == "":
#         return
#     if not checker(str(event.user_id), 9):
#         coin = Sign.get_coin(str(event.user_id))
#         if len(args.extract_plain_text())*5 > coin:
#             await ai.finish(error(9) + "\n或者您也可以通过5金币/字进行使用，签到或与音卡玩游戏即可获得，但您当前金币余额不足。")
#         else:
#             Sign.reduce(str(event.user_id), len(args.extract_plain_text())*5)
#     msg = args.extract_plain_text()
#     resp = await chat_spark(msg)
#     await ai.finish(resp)