from pathlib import Path

from nonebot import on_regex, on_command
from nonebot.params import CommandArg, RawCommand
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment as ms
)

from src.config import Config
from src.const.path import (
    ASSETS,
    build_path
)
from src.utils.network import Request
from src.utils.analyze import check_number
from src.utils.database.operation import get_group_settings

import random
import os

from ._message import answers as a

What2EatMatcher = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?吃(什么|啥|点啥)$", priority=5)
What2DrinkMatcher = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?喝(什么|啥|点啥)$", priority=5)

@What2DrinkMatcher.handle()
async def _(event: MessageEvent):
    image_name = random.choice(os.listdir(
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "drink"
            ]
        )
    ))
    image_path = Path( 
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "drink"
            ],
            end_with_slash=True
        ) + image_name
    )
    msg = (f"{Config.bot_basic.bot_name}建议你喝: \n⭐{image_path.stem}⭐\n" + ms.image(Request(image_path.as_uri()).local_content))
    await What2DrinkMatcher.send("正在为你找好喝的……")
    await What2DrinkMatcher.send(msg, at_sender=True)

@What2EatMatcher.handle()
async def _(event: MessageEvent):
    image_name = random.choice(os.listdir(
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "eat"
            ]
        )
    ))
    image_path = Path( 
        build_path(
            ASSETS,
            [
                "image",
                "what2eat",
                "eat"
            ],
            end_with_slash=True
        ) + image_name
    )
    msg = (f"{Config.bot_basic.bot_name}建议你吃: \n⭐{image_path.stem}⭐\n" + ms.image(Request(image_path.as_uri()).local_content))
    await What2EatMatcher.send("正在为你找好吃的……")
    await What2EatMatcher.send(msg, at_sender=True)

BMIMatcher = on_command("bmi", aliases={"BMI", "身体质量指数"}, force_whitespace=True, priority=5)

@BMIMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await BMIMatcher.finish("唔……参数数量不正确哦，请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
    for i in arg:
        if not check_number(i):
            await BMIMatcher.finish("唔……请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
    height = float(arg[0])
    weight = float(arg[1])
    bmi_value = weight / (height*height)
    final_result = round(bmi_value, 1)
    if final_result <= 18.4:
        msg = f"您的BMI计算结果是：{final_result}，属于偏瘦（0~18.4）哦~"
    elif 18.5 <= final_result <= 23.9:
        msg = f"您的BMI计算结果是：{final_result}，属于正常（18.5~23.9）哦~"
    elif 24.0 <= final_result <= 27.9:
        msg = f"您的BMI计算结果是：{final_result}，属于偏胖（24.0~27.9）哦~"
    elif final_result >= 28.0:
        msg = f"您的BMI计算结果是：{final_result}，属于肥胖（28.0+）哦~\n音卡建议您少吃高热量食物，多多运动保持健康身体哦！"
    await BMIMatcher.finish(msg)

HelpMatcher = on_command("help", aliases={"帮助", "功能", "查看", "文档", "使用说明"}, force_whitespace=True, priority=5)

@HelpMatcher.handle()
async def help_(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    await HelpMatcher.finish("Inkar Suki · 音卡使用文档：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/usage")

RandomColdJokeMatcher = on_command("冷笑话", priority=5, force_whitespace=True)

@RandomColdJokeMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    resp = (await Request("https://api.qicaiyun.top/joke/api.php").get())
    resp.encoding = "gbk"
    msg = resp.text.split("、")[1:]
    await RandomColdJokeMatcher.finish(str(msg))

RandomDogImageMatcher = on_command("随机狗图", aliases={"随机lwx"}, priority=5)

@RandomDogImageMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    rdint = random.randint(1, 100)
    if event.user_id in [1649157526, 1925648680]:
        if rdint >= 31:
            img = Request(
                Path(
                    build_path(
                        ASSETS,
                        [
                            "image",
                            "lwx"
                        ]
                        ,
                        end_with_slash=True
                    ) + str(random.randint(1,4)) + ".jpg"
                ).as_uri()
            ).local_content
            await RandomDogImageMatcher.finish(ms.image(img))
    if rdint <= 10:
        img = Request(
            Path(
                build_path(
                    ASSETS,
                    [
                        "image",
                        "lwx"
                    ]
                    ,
                    end_with_slash=True
                ) + str(random.randint(1,4)) + ".jpg"
            ).as_uri()
        ).local_content
        await RandomDogImageMatcher.finish(ms.image(img))
    data = (await Request("https://api.thedogapi.com/v1/images/search?size=full").get()).json()
    image = (await Request(data[0]["url"]).get()).content
    await RandomDogImageMatcher.finish(ms.image(image))

RandomDragonImageMatcher = on_command("随机龙图", priority=5)

@RandomDragonImageMatcher.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    batch_choice = random.choice(["batch1/", "batch2/", "batch3/"])
    base_url = "https://git.acwing.com/Est/dragon/-/raw/main/"
    rdnum = random.randint(
        (
            int(batch_choice[-2])
            -1
        )*500+1,
        (
            int(batch_choice[-2])
            *500
        )
            )
    for ext in [".jpg", ".png", ".gif"]:
        image_url = f"{base_url}{batch_choice}dragon_{rdnum}_{ext}"
        resp = await Request(image_url).get()
        if resp.status_code == 200:
            image = resp.content
            await RandomDragonImageMatcher.finish(ms.image(image))

AnswerBookMatcher = on_command("答案之书", priority=5, force_whitespace=True)

@AnswerBookMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    else:
        answer = random.choice(a)
        await AnswerBookMatcher.finish("答案之书给出的建议是：\n" + answer)

LiftMatcher = on_command("抽奖", aliases={"抽大奖", "十连抽", "百连抽", "抽巨奖"}, priority=5)

@LiftMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, cmd: str = RawCommand()):
    additions = get_group_settings(event.group_id, "additions")
    self_role = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self_id)
    terminal_role = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
    if "抽奖" not in additions:
        await LiftMatcher.finish("本群尚未启用抽奖！\n发送“订阅 抽奖”即可启用。包含以下命令：\n抽奖、抽大奖、十连抽、百连抽")
    if self_role["role"] not in ["owner", "admin"] or terminal_role["role"] in ["owner", "admin"]:
        await LiftMatcher.finish("音卡的权限似乎不对？请检查音卡是否为管理员，自身是否为非管理员？")
    max_time = {
        "抽奖": 15,
        "抽大奖": 60,
        "十连抽": 150,
        "百连抽": 1500,
        "抽巨奖": 43200
    }
    reward_time = random.randint(0, max_time[cmd])
    await bot.send_group_msg(group_id=event.group_id, message=f"恭喜你{cmd}的奖励时长：{reward_time}分钟！")
    await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=reward_time*60)