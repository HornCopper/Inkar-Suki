from pathlib import Path

from nonebot import on_regex, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
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

import random
import os

what_eat = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?吃(什么|啥|点啥)$", priority=5)
what_drink = on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)?喝(什么|啥|点啥)$", priority=5)

@what_drink.handle()
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
    msg = (f"{Config.bot_basic.bot_name}建议你喝: \n⭐{image_path.stem}⭐\n" + ms.image(Request(image_path.as_uri()).local_content))
    await what_drink.send("正在为你找好喝的……")
    await what_drink.send(msg, at_sender=True)

@what_eat.handle()
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
    await what_eat.send("正在为你找好喝的……")
    await what_eat.send(msg, at_sender=True)

bmi = on_command("bmi", aliases={"BMI", "身体质量指数"}, force_whitespace=True, priority=5)

@bmi.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await bmi.finish("唔……参数数量不正确哦，请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
    for i in arg:
        if not check_number(i):
            await bmi.finish("唔……请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
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
    await bmi.finish(msg)

help = on_command("help", aliases={"帮助", "功能", "查看", "文档", "使用说明"}, force_whitespace=True, priority=5)

@help.handle()
async def help_(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    await help.finish(f"Inkar Suki · 音卡使用文档：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/\n点击下面的链接直达剑网3模块简化版文档：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/jx3_easy")

rdcoldjoke = on_command("冷笑话", priority=5, force_whitespace=True)

@rdcoldjoke.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    resp = (await Request("https://api.qicaiyun.top/joke/api.php").get())
    resp.encoding = "gbk"
    msg = resp.text.split("、")[1:]
    await rdcoldjoke.finish(str(msg))

rdci = on_command("随机猫图", priority=5)

rddi = on_command("随机狗图", aliases={"随机lwx"}, priority=5)

@rdci.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    data = (await Request("https://api.thecatapi.com/v1/images/search?size=full").get()).json()
    image = (await Request(data[0]["url"]).get()).content
    await rdci.finish(ms.image(image))

@rddi.handle()
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
                            "lwx"
                        ]
                        ,
                        end_with_slash=True
                    ) + str(random.randint(1,4)) + ".jpg"
                ).as_uri()
            ).local_content
            await rddi.finish(ms.image(img))
    if rdint <= 10:
        img = Request(
            Path(
                build_path(
                    ASSETS,
                    [
                        "lwx"
                    ]
                    ,
                    end_with_slash=True
                ) + str(random.randint(1,4)) + ".jpg"
            ).as_uri()
        ).local_content
        await rddi.finish(ms.image(img))
    data = (await Request("https://api.thedogapi.com/v1/images/search?size=full").get()).json()
    image = (await Request(data[0]["url"]).get()).content
    await rddi.finish(ms.image(image))

rdli = on_command("随机龙图", priority=5)

@rdli.handle()
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
            await rdli.finish(ms.image(image))