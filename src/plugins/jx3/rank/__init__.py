from typing import Any
from jinja2 import Template
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.dungeon import Dungeon
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.jx3.school import School
from src.utils.database import rank_db as db
from src.utils.database.classes import CQCRank
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.permission import check_permission

from .api import get_zlrank
from .rank import get_rank, get_slrank

from ._template import cqcrank_template_body, cqcrank_table_head

exp_rank_matcher = on_command("jx3_zlrank", aliases={"资历排行", "资历榜单"}, priority=5, force_whitespace=True)

@exp_rank_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [0, 1, 2]:
        await exp_rank_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：资历排行 [服务器] [门派]")
    if args[0] == "":
        """
        CMD
        """
        server = ""
        school = ""
        if server is None:
            await exp_rank_matcher.finish(PROMPT.ServerNotExist)
    elif len(args) == 1:
        """
        CMD SCH/SRV
        """
        if Server(args[0], None).server is None:
            """
            CMD SCH
            """
            school = School(args[0]).name or ""
            server = ""
        else:
            """
            CMD SRV
            """
            school = ""
            server = Server(args[0], None).server or ""
    elif len(args) == 2:
        server = Server(args[0], event.group_id).server or ""
        school = School(args[1]).name or ""
    image = await get_zlrank(server, school)
    await exp_rank_matcher.finish(image)

rdps_rank_matcher = on_command("jx3_rdps_rank", aliases={"RD天梯"}, priority=5)

rhps_rank_matcher = on_command("jx3_rhps_rank", aliases={"RH天梯"}, priority=5)

@rdps_rank_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if msg.extract_plain_text() == "":
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) != 4:
        await rdps_rank_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：RD天梯 <副本名> <副本难度> <首领名> <心法名>")
    _dungeon_name = args[0]
    _dungeon_mode = args[1]
    boss_name = args[2]
    _kungfu_name = args[3]
    dungeon = Dungeon(_dungeon_name, _dungeon_mode)
    dungeon_name, dungeon_mode = dungeon.name, dungeon.mode
    kungfu_name = Kungfu(_kungfu_name).name
    inject_msg = ""
    if not dungeon_name or not dungeon_mode:
        inject_msg = PROMPT.DungeonInvalid
    if not kungfu_name:
        inject_msg = PROMPT.KungfuNotExist
    if inject_msg:
        await rdps_rank_matcher.finish(inject_msg)
    reply_msg = await get_rank(str(dungeon_mode) + str(dungeon_name), boss_name, str(kungfu_name), "rdps")
    await rdps_rank_matcher.finish(reply_msg)

@rhps_rank_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if msg.extract_plain_text() == "":
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) != 4:
        await rhps_rank_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：RH天梯 <副本名> <副本难度> <首领名> <心法名>")
    _dungeon_name = args[0]
    _dungeon_mode = args[1]
    boss_name = args[2]
    _kungfu_name = args[3]
    dungeon = Dungeon(_dungeon_name, _dungeon_mode)
    dungeon_name, dungeon_mode = dungeon.name, dungeon.mode
    kungfu_name = Kungfu(_kungfu_name).name
    inject_msg = ""
    if not dungeon_name or not dungeon_mode:
        inject_msg = PROMPT.DungeonInvalid
    if not kungfu_name:
        inject_msg = PROMPT.KungfuNotExist
    if inject_msg:
        await rhps_rank_matcher.finish(inject_msg)
    reply_msg = await get_rank(str(dungeon_mode) + str(dungeon_name), boss_name, str(kungfu_name), "rhps")
    await rhps_rank_matcher.finish(reply_msg)

slrank_matcher = on_command("jx3_slrank", aliases={"试炼之地", "试炼"}, priority=5, force_whitespace=True)

@slrank_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if msg.extract_plain_text() == "":
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) not in [1, 2]:
        await slrank_matcher.finish(PROMPT.ArgumentCountInvalid)
    if len(args) == 1:
        server = Server(None, event.group_id).server
        school = args[0]
    if len(args) == 2:
        if args[0] != "全服":
            server = Server(args[0], event.group_id).server
        else:
            server = "全服"
        school = args[1]
    school = School(school).name
    if school is None:
        await slrank_matcher.finish(PROMPT.SchoolInvalid)
    if server is None:
        await slrank_matcher.finish(PROMPT.ServerNotExist)
    reply_msg = await get_slrank(school, server)
    await slrank_matcher.finish(reply_msg)

cqcrank_carry = on_command("jx3_cqc_uncarry", aliases={"池清川大C榜"}, priority=5, force_whitespace=True)

@cqcrank_carry.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    kungfu_id = 0
    if len(arg) == 1:
        value_type = "damage" if arg[0].upper() in ["DPS", "D", "伤害", "dps", "Dps"] else "health"
    elif len(arg) == 2:
        kungfu_id = Kungfu(arg[0]).id
        value_type = "damage" if arg[1].upper() in ["DPS", "D", "伤害", "dps", "Dps"] else "health"
    all_record: list[CQCRank] | Any = db.where_all(CQCRank(), f"total_{value_type} != 0", default=[])
    effective_records: list[CQCRank] = []
    for each_record in all_record:
        if Kungfu.with_internel_id(each_record.kungfu_id).abbr in (["N", "T"] if value_type != "health" else ["D", "T"]):
            continue
        if each_record.damage_per_second < 0 or each_record.health_per_second < 0:
            continue
        if kungfu_id != 0 and each_record.kungfu_id != kungfu_id:
            continue
        effective_records.append(each_record)
    effective_records = sorted(effective_records, key=lambda x: (x.damage_per_second if value_type == "damage" else x.health_per_second), reverse=True)
    if len(effective_records) > 20:
        effective_records = effective_records[:20]
    results = []
    num = 0
    for each_record in effective_records:
        num += 1
        results.append(
            Template(
                cqcrank_template_body
            ).render(
                rank = str(num),
                kungfu_icon = Kungfu.with_internel_id(each_record.kungfu_id).icon,
                name = each_record.role_name,
                server = each_record.server_name,
                value = "{:,}".format(each_record.total_damage if value_type == "damage" else each_record.total_health),
                value_per_second = "{:,}".format(each_record.damage_per_second if value_type == "damage" else each_record.health_per_second)
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = "池清川排行榜",
            table_head = cqcrank_table_head,
            table_body = "\n".join(results)
        )
    )
    image = await generate(html, ".container", segment=True)
    await cqcrank_carry.finish(image)

cqcrank_uncarry = on_command("jx3_cqc_carry", aliases={"池清川大吸榜"}, priority=5, force_whitespace=True)

@cqcrank_uncarry.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(event.user_id, 10):
        await cqcrank_uncarry.finish("暂无权限查看大吸榜！")
    value_type = "damage" if args.extract_plain_text().strip().upper() in ["DPS", "D", "伤害", "dps", "Dps"] else "health"
    all_record: list[CQCRank] | Any = db.where_all(CQCRank(), f"total_{value_type} != 0", default=[])
    effective_records: list[CQCRank] = []
    for each_record in all_record:
        if Kungfu.with_internel_id(each_record.kungfu_id).abbr in (["N", "T"] if value_type != "health" else ["D", "T"]):
            continue
        if each_record.total_damage >= 500000000:
            continue
        if each_record.damage_per_second < 0 or each_record.health_per_second < 0:
            continue
        effective_records.append(each_record)
    effective_records = sorted(effective_records, key=lambda x: (x.damage_per_second if value_type == "damage" else x.health_per_second))
    if len(effective_records) > 20:
        effective_records = effective_records[:20]
    results = []
    num = 0
    for each_record in effective_records:
        num += 1
        results.append(
            Template(
                cqcrank_template_body
            ).render(
                rank = str(num),
                kungfu_icon = Kungfu.with_internel_id(each_record.kungfu_id).icon,
                name = each_record.role_name,
                server = each_record.server_name,
                value = "{:,}".format(each_record.total_damage if value_type == "damage" else each_record.total_health),
                value_per_second = "{:,}".format(each_record.damage_per_second if value_type == "damage" else each_record.health_per_second)
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = "池清川排行榜",
            table_head = cqcrank_table_head,
            table_body = "\n".join(results)
        )
    )
    image = await generate(html, ".container", segment=True)
    await cqcrank_uncarry.finish(image)