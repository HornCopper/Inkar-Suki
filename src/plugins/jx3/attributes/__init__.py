from concurrent.futures import ThreadPoolExecutor
from typing import cast
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    GroupUploadNoticeEvent
)
from nonebot.params import CommandArg, Arg
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request
from src.utils.analyze import check_number
from src.utils.database import logs_db
from src.utils.database.classes import EquipReplacementLog
from src.utils.database.attributes import JX3PlayerAttribute, parse_conditions
from src.utils.database.operation import get_group_settings
from src.utils.database.player import search_player

from src.plugins.preferences.app import Preference
from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import get_equip_list, get_enchant_list, EquipInfo, EnchantInfo

import asyncio

from .v2_remake import get_attr_v2_remake, get_attr_v2_remake_build, get_attr_v2_remake_global
from .v4 import get_attr_v4
from .equip_replace import EQUIP_LOCATION

attribute_matcher = on_command("jx3_attribute", aliases={"属性", "查装"}, force_whitespace=True, priority=5)

@attribute_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2, 3]:
        await attribute_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：属性 <服务器> <角色名>\n参考格式：属性 [角色名·服务器]\n参加格式：属性 角色名·服务器")
    if len(arg) == 1:
        server = None
        role_name = arg[0]
        tags = ""
    elif len(arg) == 2:
        if parse_conditions(arg[-1]):
            server = None
            role_name = arg[0]
            tags = arg[1]
        else:
            server = arg[0]
            role_name = arg[1]
            tags = ""
    elif len(arg) == 3:
        server = arg[0]
        role_name = arg[1]
        tags = arg[-1]
    server = Server(server, event.group_id).server
    if not server:
        await attribute_matcher.finish(PROMPT.ServerNotExist)
    ver = Preference(event.user_id, "", "").setting("属性")
    if ver == "v2r":
        data = await get_attr_v2_remake(server, role_name, segment=True)
    elif ver == "v4":
        data = await get_attr_v4(server, role_name, tags)
    await attribute_matcher.finish(data)

attribute_v2remake_matcher = on_command("jx3_addritube_v2_remake", aliases={"属性v2r", "查装v2r"}, force_whitespace=True, priority=5)

@attribute_v2remake_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2]:
        await attribute_v2remake_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：属性v2r <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        role = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        role = arg[1]
    server = Server(server, event.group_id).server
    if not server:
        await attribute_v2remake_matcher.finish(PROMPT.ServerNotExist)
    data = await get_attr_v2_remake(server, role, segment=True)
    await attribute_v2remake_matcher.finish(data)

attribute_v4_matcher = on_command("jx3_addritube_v4", aliases={"属性v4", "查装v4"}, force_whitespace=True, priority=5)

@attribute_v4_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2, 3]:
        await attribute_v4_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：属性v4 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        role_name = arg[0]
        tags = ""
    elif len(arg) == 2:
        if parse_conditions(arg[-1]):
            server = None
            role_name = arg[0]
            tags = arg[1]
        else:
            server = arg[0]
            role_name = arg[1]
            tags = ""
    elif len(arg) == 3:
        server = arg[0]
        role_name = arg[1]
        tags = arg[-1]
    server = Server(server, event.group_id).server
    if not server:
        await attribute_v4_matcher.finish(PROMPT.ServerNotExist)
    data = await get_attr_v4(server, role_name, tags)
    await attribute_v4_matcher.finish(data)

attribute_repo = on_command("jx3_attribute_repo", aliases={"属性库"}, priority=5, force_whitespace=True)

@attribute_repo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() == "":
        return
    num = args.extract_plain_text().strip()
    if not check_number(num):
        await attribute_repo.finish("属性库仅支持使用全服ID进行查看！")
    image = await get_attr_v2_remake_global(int(num))
    await attribute_repo.finish(image)

attribute_build = on_command("jx3_attribute_build", aliases={"配装器"}, priority=5, force_whitespace=True)

@attribute_build.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() == "":
        return
    jcl_line = args.extract_plain_text().strip()
    image = await get_attr_v2_remake_build(jcl_line)
    await attribute_build.finish(image)

attribute_submit = on_command("jx3_attribute_submit", aliases={"提交属性"}, priority=5, force_whitespace=True)

@attribute_submit.handle()
async def _(event: GroupMessageEvent, state: T_State, matcher: Matcher, msg: Message = CommandArg()):
    if msg.extract_plain_text().strip() == "":
        matcher.stop_propagation()
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) not in [2, 3]:
        await attribute_submit.finish(PROMPT.ArgumentCountInvalid)
    if len(args) == 2:
        server = Server(None, event.group_id).server
        name = args[0]
        kungfu_name = args[1]
    else:
        server = Server(args[0], event.group_id).server
        name = args[1]
        kungfu_name = args[2]
    if server is None:
        await attribute_submit.finish(PROMPT.ServerInvalid)
    player_info = await search_player(role_name=name, server_name=server)
    global_role_id = player_info.globalRoleId
    if global_role_id == "":
        await attribute_submit.finish(PROMPT.PlayerNotExist)
    kungfu_id = Kungfu(kungfu_name).id
    if kungfu_id is None:
        await attribute_submit.finish(PROMPT.KungfuNotExist)
    kungfu_id_pc = cast(int, Kungfu.with_internel_id(kungfu_id, True).id)
    state["kungfu_id"] = kungfu_id_pc
    state["global_role_id"] = int(global_role_id)
    await attribute_submit.send("请发送从茗伊插件-角色统计-装备统计中导出的装备数据，请从文本编辑器中复制后直接发送，不要修改任何内容：")

@attribute_submit.got("equip_data")
async def _(event: GroupMessageEvent, state: T_State, equip_data: Message = Arg()):
    data = equip_data.extract_plain_text()
    try:
        instance = await JX3PlayerAttribute.from_plugin(data, state["kungfu_id"], state["global_role_id"])
        instance.save()
    except Exception as e:
        await attribute_submit.finish(f"导入装备数据时发生错误，请检查数据中是否有错误：\n{e}")
    await attribute_submit.finish("已导入装备数据，请尝试使用 属性 命令查询！")

replace_equip_matcher = on_command("jx3_attribute_replace_equip", aliases={"替换装备"}, priority=5, force_whitespace=True)

@replace_equip_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, matcher: Matcher, msg: Message = CommandArg()):
    if msg.extract_plain_text().strip() == "":
        matcher.stop_propagation()
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) != 5:
        await replace_equip_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：替换装备 <服务器> <角色名> <标签> <装备部位> <装备关键词>")
    server = Server(args[0], event.group_id).server
    role_name = args[1]
    tag = args[2]
    equip_location = args[3]
    equip_keyword = args[4]
    if server is None:
        await replace_equip_matcher.finish(PROMPT.ServerInvalid)
    role_info = await search_player(role_name=role_name, server_name=server)
    if role_info.globalRoleId == "":
        await replace_equip_matcher.finish(PROMPT.PlayerNotExist)
    if equip_location not in EQUIP_LOCATION:
        await replace_equip_matcher.finish("装备部位输入错误，当前接受的装备部位如下：\n" + "、".join(EQUIP_LOCATION.keys()))
    to_replace_location_code = EQUIP_LOCATION[equip_location]
    equips = await get_equip_list(equip_keyword)
    match_equips = []
    for each_equip in equips:
        if each_equip.location_code == to_replace_location_code or (each_equip.location_code == 6 and to_replace_location_code == 7):
            match_equips.append(each_equip)
    if not match_equips:
        await replace_equip_matcher.finish("未找到符合条件的装备，请尝试更换关键词！")
    state["equips"] = match_equips
    state["location"] = to_replace_location_code
    state["global_role_id"] = int(role_info.globalRoleId)
    state["tag"] = tag
    reply_msg = "请从下面选择装备进行替换！"
    num = 1
    for equip in equips:
        reply_msg += f"\n{num}. ({equip.subkind}) {equip.name}\n{equip.quality} {' '.join(equip.attr)}"
        num += 1
    await replace_equip_matcher.send(reply_msg)

@replace_equip_matcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_text = num.extract_plain_text().strip()
    if not check_number(num_text):
        await replace_equip_matcher.finish("序号输入有误，请重新发起命令！")
    num_int = int(num_text)
    equips: list[EquipInfo] = state["equips"]
    replace_location_code: int = state["location"]
    tag: str = state["tag"]
    global_role_id: int = state["global_role_id"]
    if num_int < 1 or num_int > len(equips):
        await replace_equip_matcher.finish("选择的序号有误，请重新发起命令！")
    equip = equips[num_int - 1]
    new_log = EquipReplacementLog(
        user_id = event.user_id,
        message = f"替换了 {equip.name}（{equip.item_id}） 作为 {tag} 的装备",
        global_role_id = global_role_id
    )
    logs_db.save(new_log)
    current_data = await JX3PlayerAttribute.from_database(global_role_id, tag)
    if current_data is None:
        await replace_equip_matcher.finish(PROMPT.EquipNotFound)
    for each_equip_line in current_data.equip_lines:
        if each_equip_line[0] == replace_location_code:
            each_equip_line[2] = equip.item_id
    current_data.save()
    await replace_equip_matcher.finish(f"已替换为 {equip.name}，请尝试使用 属性 命令查询效果！")

replace_enchant_matcher = on_command("jx3_attribute_replace_enchant", aliases={"替换附魔"}, priority=5, force_whitespace=True)

@replace_enchant_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, matcher: Matcher, msg: Message = CommandArg()):
    if msg.extract_plain_text().strip() == "":
        matcher.stop_propagation()
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) != 5:
        await replace_enchant_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：替换附魔 <服务器> <角色名> <标签> <装备部位> <附魔关键词>")
    server = Server(args[0], event.group_id).server
    role_name = args[1]
    tag = args[2]
    equip_location = args[3]
    enchant_keyword = args[4]
    if server is None:
        await replace_enchant_matcher.finish(PROMPT.ServerInvalid)
    role_info = await search_player(role_name=role_name, server_name=server)
    if role_info.globalRoleId == "":
        await replace_enchant_matcher.finish(PROMPT.PlayerNotExist)
    if equip_location not in EQUIP_LOCATION:
        await replace_enchant_matcher.finish("装备部位输入错误，当前接受的装备部位如下：\n" + "、".join(EQUIP_LOCATION.keys()))
    to_replace_location_code = EQUIP_LOCATION[equip_location]
    enchants = await get_enchant_list(enchant_keyword)
    match_enchants = []
    for each_enchant in enchants:
        if each_enchant.location_code == to_replace_location_code or (each_enchant.location_code == 6 and to_replace_location_code == 7):
            match_enchants.append(each_enchant)
    if not match_enchants:
        await replace_enchant_matcher.finish("未找到符合条件的附魔，请尝试更换关键词！")
    state["enchants"] = match_enchants
    state["location"] = to_replace_location_code
    state["global_role_id"] = int(role_info.globalRoleId)
    state["tag"] = tag
    reply_msg = "请从下面选择附魔进行替换！"
    num = 1
    for enchant in enchants:
        reply_msg += f"\n{num}. {enchant.name} \n描述：{enchant.desc or '无'}"
        num += 1
    await replace_enchant_matcher.send(reply_msg)

@replace_enchant_matcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_text = num.extract_plain_text().strip()
    if not check_number(num_text):
        await replace_enchant_matcher.finish("序号输入有误，请重新发起命令！")
    num_int = int(num_text)
    enchants: list[EnchantInfo] = state["enchants"]
    replace_location_code: int = state["location"]
    tag: str = state["tag"]
    global_role_id: int = state["global_role_id"]
    if num_int < 1 or num_int > len(enchants):
        await replace_enchant_matcher.finish("选择的序号有误，请重新发起命令！")
    enchant = enchants[num_int - 1]
    current_data = await JX3PlayerAttribute.from_database(global_role_id, tag)
    if current_data is None:
        await replace_enchant_matcher.finish(PROMPT.EquipNotFound)
    new_log = EquipReplacementLog(
        user_id = event.user_id,
        message = f"替换了 {enchant.name}（{enchant.enchant_id}） 作为 {tag} 的附魔",
        global_role_id = global_role_id
    )
    logs_db.save(new_log)
    for each_enchant_line in current_data.equip_lines:
        if each_enchant_line[0] == replace_location_code:
            if enchant.name.startswith("彩·"):
                # 五彩石
                each_enchant_line[4][3][1] = enchant.enchant_id
            elif enchant.is_common:
                # 大附魔
                each_enchant_line[6] = enchant.enchant_id
            else:
                # 小附魔
                each_enchant_line[5] = enchant.enchant_id
    current_data.save()
    await replace_enchant_matcher.finish(f"已替换为 {enchant.name}，请尝试使用 属性 命令查询效果！")

attribute_db_executor = ThreadPoolExecutor(max_workers=1)

@notice.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent):
    if event.file.name.endswith(".jcl"):
        if event.file.name[:4] not in ["ATTR"]:
            return
        msg = "以下全局玩家ID完成入库："
        try:
            url = event.model_dump()["file"]["url"]
        except KeyError:
            file_id = event.model_dump()["file"]["id"]
            bus_id = event.model_dump()["file"]["busid"]
            file_data = await bot.call_api("get_group_file_url", group_id=event.group_id, file_id=file_id, bus_id=bus_id)
            url = file_data["url"]
        response = await Request(url).get()
        response.encoding = "gbk"
        jcl_text = response.text
        if len(response.content) > 2 * 1024 * 1024 and "Preview" not in get_group_settings(event.group_id, "additions"):
            return
        attributes_data = await JX3PlayerAttribute.from_jcl(jcl_text)
        loop = asyncio.get_running_loop()
        await asyncio.gather(*[
            loop.run_in_executor(attribute_db_executor, each_data.save)
            for each_data in attributes_data
        ])
        for each_data in attributes_data:
            msg += f"\n{each_data.name}（{each_data.global_role_id}）"
        await bot.send_group_msg(group_id=event.group_id, message=msg)