from typing import Literal
from nonebot import on_command
from nonebot.params import CommandArg, RawCommand
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, MessageSegment as ms

from src.accounts.manage import AccountManage
from src.const.jx3.school import School
from src.const.jx3.server import Server
from src.config import Config
from src.const.prompts import PROMPT
from src.utils.analyze import check_number
from src.utils.network import Request
from src.plugins.preferences.app import Preference

from .random_serendipity import get_serendipity, get_serendipity_image
from .random_loot import RandomLoot
from .random_shilian import generate_shilian_box
from .random_equip import get_equip_info_image, get_equip_info
from .random_5gimage import (
    generate_random_5gimage,
    get_random_5gimage_rank_image,
    get_random_5gimage_record_image,
    normalize_image_index,
)

RANDOM_5GIMAGE_COST = 10

saohua_matcher = on_command("jx3_random", aliases={"骚话", "烧话"}, force_whitespace=True, priority=5)

@saohua_matcher.handle()
async def jx3_saohua_random(args: Message = CommandArg()):
    """
    召唤一条骚话：

    Example：-骚话
    """
    if args.extract_plain_text() != "":
        return
    url = f"{Config.jx3.api.url}/data/saohua/random"
    info = (await Request(url).get()).json()
    msg = info["data"]["text"]
    await saohua_matcher.finish(msg)

tiangou_matcher = on_command("jx3_tiangou", aliases={"舔狗", "舔狗日记"}, force_whitespace=True, priority=5)

@tiangou_matcher.handle()
async def jx3_saohua_tiangou(args: Message = CommandArg()):
    """
    获取一条舔狗日志：

    Example：-舔狗
    """
    if args.extract_plain_text() != "":
        return
    url = f"{Config.jx3.api.url}/data/saohua/content"
    info = (await Request(url).get()).json()
    msg = info["data"]["text"]
    await tiangou_matcher.finish(msg)

random_loot_matcher = on_command("jx3_rdloot", aliases={"黑本", "模拟掉落", "红本"}, force_whitespace=True, priority=5)

@random_loot_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg == "":
        await random_loot_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：黑本 <副本名> <难度>")
    msg = msg.split(" ")
    if len(msg) != 2:
        await random_loot_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：黑本 <副本名> <难度>")
    name = msg[0]
    mode = msg[1]
    instance = await RandomLoot.with_map_name(name, mode)
    if instance is None:
        await random_loot_matcher.finish(PROMPT.DungeonInvalid)
    else:
        display_mode = Preference(event.user_id, "", "").setting("黑本显示")
        image = await instance.generate(display_mode=display_mode)
        await random_loot_matcher.finish(ms.at(event.user_id) + image)

random_5gimage_matcher = on_command("jx3_random_5gimage", aliases={"随机5G图", "随机5g图", "随机武技图"}, priority=5, force_whitespace=True)

@random_5gimage_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    raw_args = args.extract_plain_text().strip().split()
    if len(raw_args) == 1:
        server = Server(None, event.group_id).server
        image_index = normalize_image_index(raw_args[0])
    elif len(raw_args) == 2:
        server = Server(raw_args[0], event.group_id).server
        image_index = normalize_image_index(raw_args[1])
    else:
        await random_5gimage_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：随机武技图 <服务器> <1-8/2N>")
    if server is None:
        await random_5gimage_matcher.finish(PROMPT.ServerNotExist)
    if image_index is None:
        await random_5gimage_matcher.finish("请输入 1-8，或 2N（贰·新编）。")
    account = AccountManage(event.user_id)
    if account.coins < RANDOM_5GIMAGE_COST:
        await random_5gimage_matcher.finish(f"金币不足，本次开图需要 {RANDOM_5GIMAGE_COST} 枚金币。\n金币可通过签到、对诗、玩 24 点、或直接与别人交易等途径获得。")
    image_result = await generate_random_5gimage(
        server,
        image_index,
        int(event.user_id),
        int(event.group_id),
    )
    if image_result is None:
        await random_5gimage_matcher.finish("无法确定输入的武技殊影图代码！\n请给出数字 1-8、2N 其中的一个。")
    image, is_profit_calculable = image_result
    account.reduce_coin(RANDOM_5GIMAGE_COST)
    if not is_profit_calculable:
        account.add_coin(RANDOM_5GIMAGE_COST)
    await random_5gimage_matcher.finish(ms.at(event.user_id) + image)

random_5gimage_record_matcher = on_command("jx3_5gimage_record", aliases={"开图记录", "开图战绩"}, priority=5, force_whitespace=True)

@random_5gimage_record_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip():
        return
    image = await get_random_5gimage_record_image(
        int(event.user_id),
        int(event.group_id),
    )
    await random_5gimage_record_matcher.finish(ms.at(event.user_id) + image)

random_5gimage_rank_matcher = on_command("jx3_5gimage_rank", aliases={"开图排行"}, priority=5, force_whitespace=True)

@random_5gimage_rank_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    rank_type = args.extract_plain_text().strip() or "赢取"
    if rank_type not in {"赢取", "亏损"}:
        await random_5gimage_rank_matcher.finish("请输入 赢取 或 亏损。")
    image = await get_random_5gimage_rank_image(bot, int(event.group_id), rank_type)
    await random_5gimage_rank_matcher.finish(ms.at(event.user_id) + image)

random_shilian_matcher = on_command("jx3_rdsl", aliases={"翻牌", "模拟试炼"}, priority=5, force_whitespace=True)

@random_shilian_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text().strip()
    if msg == "":
        return
    msg = msg.split(" ")
    if len(msg) != 2:
        await random_shilian_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：翻牌 <层数> <序号>")
    level = msg[0]
    order = msg[1]
    image = await generate_shilian_box(int(level), int(order), event.group_id, bot)
    await random_loot_matcher.finish(ms.at(event.user_id) + image)

random_serendipity_matcher = on_command("jx3_rdsp", aliases={"抽奇遇", "模拟奇遇"}, priority=5, force_whitespace=True)

@random_serendipity_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text().strip()
    cw_serendipity: str | Literal[False] = False
    if msg == "":
        pass
    else:
        school = School(msg).name
        if school is None:
            await random_serendipity_matcher.finish("无法识别该门派，请检查名称！")
        cw_serendipity = school
    serendipity_path = get_serendipity(cw_serendipity)
    if serendipity_path is None:
        await random_serendipity_matcher.finish(ms.at(event.user_id) + " 本次抽取没有中奇遇呢，可以再试一次？")
    image = get_serendipity_image(serendipity_path)
    await random_serendipity_matcher.finish(ms.at(event.user_id) + image)

random_equip_matcher = on_command("jx3_randomequip", aliases={"抽防具", "抽首饰", "抽武器", "抽装备"}, priority=5)

@random_equip_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg(), cmd: str = RawCommand()):
    raw_arg = args.extract_plain_text().strip()
    params = {
        "random": 1
    }
    if raw_arg:
        arg = raw_arg.split(" ")
        if len(arg) == 1:
            params["min_level"] = int(arg[0])
        elif len(arg) == 2:
            params["min_level"] = int(arg[0])
            params["max_level"] = int(arg[1])
        else:
            await random_equip_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：抽防具 最低品级 最高品级\n无参数时按当前主流装备品级；单参数时为最低品级，双参数时前者为最低品级；后者为最高品级。")
    if cmd == "抽防具":
        params["category"] = 7
    elif cmd == "抽首饰":
        params["category"] = 8
    elif cmd == "抽武器":
        params["category"] = 6
    else:
        await random_equip_matcher.finish("请选择【抽武器】【抽防具】【抽首饰】其中一个命令进行！")
    equip_data = await get_equip_info_image(
        await get_equip_info(params)
    )
    await random_equip_matcher.finish(
        ms.at(event.user_id) + equip_data
    )
