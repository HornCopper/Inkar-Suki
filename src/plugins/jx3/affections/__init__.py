from datetime import datetime

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.const.prompts import PROMPT
from src.utils.database.operation import get_group_settings
from src.utils.network import Request
from src.utils.analyze import check_number
from src.utils.time import Time

from .affections_system import (
    bind_affection,
    delete_affection,
    generate_affection_image
)

from .everyday_affection import (
    get_affection,
    set_affection,
    get_random_affection
)



bind_affection_matcher = on_command("jx3_affbind", aliases={"绑定情缘"}, force_whitespace=True, priority=5)

@bind_affection_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [3, 4]:
        await bind_affection_matcher.finish("绑定失败！请参考下面的命令格式：\n绑定情缘 自己ID 对方ID 对方QQ 时间(可不填)")
    self_name = arg[0]
    self_qq = event.user_id
    other_name = arg[1]
    other_qq = int(arg[2])
    custom_time = arg[3] if len(arg) == 4 else Time().format("%Y-%m-%d")
    if not isinstance(custom_time, str):
        return
    timestamp = 0
    try:
        timestamp = int(datetime.strptime(custom_time, "%Y年%m月%d日").timestamp())
    except ValueError:
        try:
            timestamp = int(datetime.strptime(custom_time, "%Y-%m-%d").timestamp())
        except ValueError:
            await bind_affection_matcher.finish(PROMPT.AffectionFormatInvalid)
    if not check_number(other_qq):
        await bind_affection_matcher.finish(PROMPT.AffectionUINInvalid)
    ans = await bind_affection(self_qq, self_name, other_qq, other_name, event.group_id, timestamp)
    await bind_affection_matcher.finish(ans[0])

delete_affection_matcher = on_command("jx3_affdl", aliases={"解除情缘"}, force_whitespace=True, priority=5)

@delete_affection_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    self_id = event.user_id
    ans = await delete_affection(self_id)
    if not isinstance(ans, list):
        return
    await delete_affection_matcher.finish(ans[0])

affection_crt_matcher = on_command("jx3_affcrt", aliases={"查看情缘证书"}, force_whitespace=True, priority=5)

@affection_crt_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() != "":
        return
    img = await generate_affection_image(event.user_id)
    await affection_crt_matcher.finish(img)

random_affection_matcher = on_command("jx3_rdaff", aliases={"随机情缘", "抽情缘"}, priority=5, force_whitespace=True)

@random_affection_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() != "":
        return
    if "抽情缘" not in get_group_settings(event.group_id, "additions"):
        return
    basic_msg = ms.at(event.user_id)
    if get_affection(event.user_id):
        await random_affection_matcher.finish(basic_msg + " 您今日已经抽过情缘了，请明日再试！")
    else:
        random_affection_id = await get_random_affection(bot, event.group_id, event.user_id)
        random_affection_info = await bot.get_group_member_info(group_id=event.group_id, user_id=random_affection_id)
        display_name = random_affection_info["card"] or str(random_affection_info["nickname"])
        avatar = (await Request(f"https://q.qlogo.cn/headimg_dl?dst_uin={random_affection_id}&spec=100&img_type=jpg").get()).content
        status = set_affection(event.user_id, event.group_id, random_affection_id)
        if status:
            await random_affection_matcher.finish(basic_msg + " 您今天抽到的情缘是：\n" + ms.image(avatar) + f"{display_name}（{random_affection_id}）")
        else:
            await random_affection_matcher.finish(basic_msg + " 您今日已经抽过情缘了，请明日再试！")