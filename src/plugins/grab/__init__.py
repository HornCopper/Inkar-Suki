import os
import re
import nonebot
import requests
import random
import base64
import sys

from nonebot.adapters.onebot.v11 import MessageSegment as ms, MessageEvent, Bot, Message, GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.helpers import extract_image_urls
from nonebot.exception import ActionFailed
from nonebot.plugin import on_regex, on_command
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot import require
from pathlib import Path

try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception:
    scheduler = None
    logger.warning("未安装定时插件依赖")

from src.tools.utils import checknumber

from .check_pass import check_cd, check_max
from .gettor import get_tieba
from .cheater import verify_cheater

what_eat = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)吃(什么|啥|点啥)$", priority=5)
what_drink = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)喝(什么|啥|点啥)$", priority=5)
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
Bot_NICKNAME = "音卡"

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

tieba = on_command("-tieba", aliases={"-帖子"}, priority=5)


@tieba.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    贴吧内容查询，具体实现参考`gettor.py`的`get_tieba`函数。
    """
    tid = args.extract_plain_text()
    if checknumber(tid) == False:
        await tieba.finish("请给出纯数字的帖子ID哦~")
    msg = await get_tieba(int(tid))
    await tieba.finish(msg)

cheater_ = on_command("jx3_cheater", aliases={"-骗子", "-查人"}, priority=5)


@cheater_.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    content = args.extract_plain_text()
    if not checknumber(content):
        await cheater_.finish("请输入纯数字的QQ哦~")
    else:
        personal_data = await bot.call_api("get_stranger_info", user_id=int(content))
        if personal_data["user_id"] == 0:
            await cheater_.finish("唔……该QQ号似乎不存在哦~")
        else:
            level = personal_data["level"]
            login = personal_data["login_days"]
            nickname = personal_data["nickname"]
            basic_info = f"QQ等级：{level}\n登录天数：{login}\n昵称：{nickname}"
        data = await verify_cheater(str(content))
        if data == False:
            msg = f"此人应该不是骗子？音卡在贴吧没有找到哦~\n{basic_info}"
        else:
            url = data
            msg = f"此人可能是骗子？在贴吧已有记录！\n{url}\n{basic_info}\n仅供参考！请以实际内容为准！"
        await cheater_.finish(msg)


@del_dish.handle()
async def got_dish_name(matcher: Matcher, state: T_State):
    args = list(state["_matched_groups"])
    state["type"] = args[1]
    if args[2]:
        matcher.set_arg("name", args[2])


@del_dish.got("name", prompt="请告诉我你要删除哪个菜品或饮料,发送“取消”可取消操作")
async def del_(state: T_State, name: Message = Arg()):
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
async def got(state: T_State, dish_name: Message = Arg()):
    state["name"] = str(dish_name)
    if str(dish_name) == "取消":
        await add_dish.finish("已取消")


@add_dish.got("img", prompt="⭐图片也发给我吧\n发送“取消”可取消添加")
async def handle(state: T_State, img: Message = Arg()):
    if str(img) == "取消":
        await add_dish.finish("已取消")
    img_url = extract_image_urls(img)
    if not img_url:
        await add_dish.finish("没有找到图片(╯▔皿▔)╯，请稍后重试", at_sender=True)

    if state["type"] in ["菜品", "菜单"]:
        path = img_eat_path
    elif state["type"] in ["饮料", "饮品"]:
        path = img_drink_path

    dish_img = requests.get(url=img_url[0])
    with open(path / str(state["name"]+".jpg"), "wb") as f:
        f.write(dish_img.content)
    name = state["name"]
    type_ = state["type"]
    await add_dish.finish(f"成功添加{type_}:{name}\n" + ms.image(img_url))


@view_dish.handle()
async def got_name(matcher: Matcher, state: T_State, event: MessageEvent):
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
async def handle(state: T_State, name: Message = Arg()):
    if state["type"] == "吃的":
        img = img_eat_path / (str(name)+".jpg")
    elif state["type"] == "喝的":
        img = img_drink_path / (str(name)+".jpg")
    try:
        await view_dish.send(ms.image(img))
    except ActionFailed:
        await view_dish.finish("没有找到你所说的，请检查一下菜单吧", at_sender=True)


@view_all_dishes.handle()
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    # 正则匹配组
    args = list(state["_matched_groups"])
    if args[1] in ["菜单", "菜品"]:
        path = img_eat_path
        all_name = all_file_eat_name
    elif args[1] in ["饮料", "饮品"]:
        path = img_drink_path
        all_name = all_file_drink_name
    # 合并转发
    msg_list = [f"{Bot_NICKNAME}查询到的{args[1]}如下"]
    N = 0
    for name in all_name:
        N += 1
        img = path / name
        with open(img, "rb") as im:
            img_bytes = im.read()
        base64_str = "base64://" + base64.b64encode(img_bytes).decode()
        name = re.sub(".jpg", "", name)
        msg_list.append(f"{N}.{name}\n{ms.image(base64_str)}")
    await send_forward_msg(bot, event, Bot_NICKNAME, bot.self_id, msg_list)

# 初始化内置时间的last_time
time = 0
# 用户数据
user_count = {}


@what_drink.handle()
async def wtd(msg: MessageEvent):
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
        msg = (f"{Bot_NICKNAME}建议你喝: \n⭐{img.stem}⭐\n" + ms.image(base64_str))
        try:
            await what_drink.send("正在为你找好喝的……")
            await what_drink.send(msg, at_sender=True)
        except ActionFailed:
            await what_drink.finish("出错啦！没有找到好喝的~")


@what_eat.handle()
async def wte(msg: MessageEvent):
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
        msg = (f"{Bot_NICKNAME}建议你吃: \n⭐{img.stem}⭐\n" + ms.image(base64_str))
        try:
            await what_eat.send("正在为你找好吃的……")
            await what_eat.send(msg, at_sender=True)
        except ActionFailed:
            await what_eat.finish("出错啦！没有找到好吃的~")

# 每日0点重置用户数据


def reset_user_count():
    global user_count
    user_count = {}


try:
    scheduler.add_job(reset_user_count, "cron", hour="0", id="delete_date")
except ActionFailed as e:
    logger.warning(f"定时任务添加失败，{repr(e)}")

# 上限回复消息
max_msg = ("你今天吃的够多了！不许再吃了(´-ωก`)", "吃吃吃，就知道吃，你都吃饱了！明天再来(▼皿▼#)", "(*｀へ´*)你猜我会不会再给你发好吃的图片",
           f"没得吃的了，{Bot_NICKNAME}的食物都被你这坏蛋吃光了！", "你在等我给你发好吃的？做梦哦！你都吃那么多了，不许再吃了！ヽ(≧Д≦)ノ")

# 调用合并转发api函数


async def send_forward_msg(bot: Bot, event: MessageEvent, name: str, uin: str, msgs: list) -> dict:
    def to_json(msg: Message):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        return await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=messages)
    else:
        return await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=messages)
