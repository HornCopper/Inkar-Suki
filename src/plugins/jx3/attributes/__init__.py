from concurrent.futures import ThreadPoolExecutor
from typing import Any, cast
from nonebot import on_command
from nonebot.exception import ActionFailed
from nonebot.log import logger
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
from src.utils.database import db, logs_db
from src.utils.database.classes import EquipReplacementLog, RoleData
from src.utils.database.attributes import JX3PlayerAttribute, parse_conditions
from src.utils.database.operation import get_group_settings
from src.utils.database.player import search_player, get_uid_data

from src.plugins.preferences.app import Preference
from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import get_equip_list, get_enchant_list, EquipInfo, EnchantInfo
from src.plugins.jx3.calculator.equipment_rating import get_equipment_rating_support_status

import asyncio
import hashlib

from .v2_remake import get_attr_v2_remake, get_attr_v2_remake_build, get_attr_v2_remake_global
from .v4 import get_attr_v4
from .equip_replace import EQUIP_LOCATION

attribute_matcher = on_command("jx3_attribute", aliases={"属性", "查装"}, force_whitespace=True, priority=5)

ATTRIBUTE_IMAGE_SEND_FAILED = (
    "属性图已生成，但 QQ 富媒体上传失败。"
    "这不是属性数据解析错误，请稍后重试；如果持续失败，需要检查 QQ/NapCat 的图片上传状态。"
)

async def finish_attribute_response(matcher: type[Matcher], data: Any) -> None:
    try:
        await matcher.finish(data)
    except ActionFailed as exc:
        logger.warning(f"属性查询结果发送失败，已尝试文本降级：{exc}")
        try:
            await matcher.finish(ATTRIBUTE_IMAGE_SEND_FAILED)
        except ActionFailed as fallback_exc:
            logger.warning(f"属性查询文本降级发送失败，已忽略本次发送错误：{fallback_exc}")

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
    await finish_attribute_response(attribute_matcher, data)

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
    await finish_attribute_response(attribute_v2remake_matcher, data)

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
    await finish_attribute_response(attribute_v4_matcher, data)

attribute_repo = on_command("jx3_attribute_repo", aliases={"属性库"}, priority=5, force_whitespace=True)

@attribute_repo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() == "":
        return
    num = args.extract_plain_text().strip()
    if not check_number(num):
        await attribute_repo.finish("属性库仅支持使用全服ID进行查看！")
    image = await get_attr_v2_remake_global(int(num))
    await finish_attribute_response(attribute_repo, image)

attribute_build = on_command("jx3_attribute_build", aliases={"配装器"}, priority=5, force_whitespace=True)

@attribute_build.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() == "":
        return
    jcl_line = args.extract_plain_text().strip()
    image = await get_attr_v2_remake_build(jcl_line)
    await finish_attribute_response(attribute_build, image)

ATTRIBUTE_SUBMIT_USAGE = (
    "提交属性 可接受以下格式：\n"
    "1. 提交属性 <服务器> <角色名/ID> <心法> <茗伊装备导出码>\n"
    "2. 提交属性 <角色名/ID> <心法> <茗伊装备导出码>（使用本群绑定服务器）\n"
    "3. 提交属性 <服务器> <角色名/ID> <心法>\n"
    "4. 提交属性 <角色名/ID> <心法>（使用本群绑定服务器）"
)

async def get_attribute_submit_player(role: str, server: str):
    if check_number(role):
        player_info = await search_player(role_name=role, role_id=role, server_name=server, local_lookup=True)
        if player_info.roleId == "":
            player_info = await get_uid_data(role_id=role, server=server, msg=False)
    else:
        player_info = await search_player(role_name=role, server_name=server)
    return player_info

LOCAL_GLOBAL_ROLE_ID_BASE = 8_000_000_000_000_000_000

def build_local_global_role_id(role: str, server: str) -> str:
    digest = hashlib.sha1(f"{server}:{role}".encode("utf-8")).hexdigest()
    return str(LOCAL_GLOBAL_ROLE_ID_BASE + int(digest[:15], 16))

def build_attribute_submit_role(role: str, server: str, player_info: RoleData) -> RoleData:
    role_name = player_info.roleName or role
    global_role_id = player_info.globalRoleId or build_local_global_role_id(role_name, server)
    role_id = player_info.roleId or (role if check_number(role) else global_role_id)
    return RoleData(
        bodyName=player_info.bodyName,
        campName=player_info.campName,
        forceName=player_info.forceName,
        globalRoleId=global_role_id,
        roleName=role_name,
        roleId=role_id,
        serverName=server,
    )

def save_attribute_submit_role(role_info: RoleData) -> None:
    db.delete(RoleData(), "roleName = ? AND serverName = ?", role_info.roleName, role_info.serverName)
    db.delete(RoleData(), "roleId = ? AND serverName = ?", role_info.roleId, role_info.serverName)
    db.delete(RoleData(), "globalRoleId = ?", role_info.globalRoleId)
    db.save(role_info)

def validate_attribute_instance(instance: JX3PlayerAttribute) -> None:
    instance.validate()

def save_attribute_instance(instance: JX3PlayerAttribute) -> None:
    validate_attribute_instance(instance)
    instance.save()

def format_attribute_save_error(instance: JX3PlayerAttribute, exc: BaseException) -> str:
    kungfu = Kungfu.with_internel_id(instance.kungfu_id).name or str(instance.kungfu_id)
    role = instance.name or str(instance.global_role_id)
    error = str(exc).strip() or type(exc).__name__
    return f"{role}（{instance.global_role_id}，{kungfu}）：{error}"

async def save_plugin_attribute(role: str, server: str, kungfu_name: str, equip_data: str) -> tuple[RoleData, int]:
    kungfu_id = Kungfu(kungfu_name).id
    if kungfu_id is None:
        await attribute_submit.finish(PROMPT.KungfuNotExist)
    kungfu_id_pc = cast(int, Kungfu.with_internel_id(kungfu_id, True).id)
    player_info = await get_attribute_submit_player(role, server)
    role_info = build_attribute_submit_role(role, server, player_info)
    try:
        instance = await JX3PlayerAttribute.from_plugin(equip_data, kungfu_id_pc, int(role_info.globalRoleId))
        save_attribute_instance(instance)
        save_attribute_submit_role(role_info)
    except Exception as e:
        await attribute_submit.finish(f"导入的装备数据不可用，已拒绝入库：\n{e}")
    return role_info, kungfu_id_pc

def _attribute_submit_role_name(role_info: RoleData) -> str:
    return role_info.roleName or role_info.roleId or str(role_info.globalRoleId)

async def format_attribute_submit_success(role_info: RoleData, kungfu_id: int) -> str:
    role_name = _attribute_submit_role_name(role_info)
    message = f"已导入装备数据，请尝试使用指令：属性 {role_info.serverName} {role_name}"
    kungfu_name = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True).name or str(kungfu_id)
    support_status = await get_equipment_rating_support_status(kungfu_id)
    if support_status is True:
        message += f"\n该心法支持装备评级，使用指令：装备评级 {role_info.serverName} {role_name} {kungfu_name}"
    elif support_status is False:
        message += f"\n该心法暂不支持装备评级：{kungfu_name}"
    else:
        message += "\n暂时无法确认该心法是否支持装备评级，请稍后使用 装备评级支持 查询。"
    return message

attribute_submit = on_command("jx3_attribute_submit", aliases={"提交属性"}, priority=5, force_whitespace=True)

@attribute_submit.handle()
async def _(event: GroupMessageEvent, state: T_State, matcher: Matcher, msg: Message = CommandArg()):
    plain_text = msg.extract_plain_text().strip()
    if plain_text == "":
        matcher.stop_propagation()
        return
    if plain_text.lower() in {"help", "帮助", "参数", "示例"}:
        await attribute_submit.finish(ATTRIBUTE_SUBMIT_USAGE)
    args = plain_text.split(maxsplit=3)
    if len(args) == 4:
        server = Server(args[0], event.group_id).server
        role = args[1]
        kungfu_name = args[2]
        equip_data = args[3]
        if server is None:
            await attribute_submit.finish(PROMPT.ServerInvalid  + "\n参考格式：提交属性 <服务器> <ID> <心法>")
        role_info, kungfu_id_pc = await save_plugin_attribute(role, server, kungfu_name, equip_data)
        await attribute_submit.finish(await format_attribute_submit_success(role_info, kungfu_id_pc))

    args = plain_text.split(maxsplit=2)
    if len(args) == 3 and Kungfu(args[1]).id is not None and Kungfu(args[2]).id is None:
        server = Server(None, event.group_id).server
        role = args[0]
        kungfu_name = args[1]
        equip_data = args[2]
        if server is None:
            await attribute_submit.finish(PROMPT.ServerInvalid + "\n参考格式：提交属性 <服务器> <ID> <心法>")
        role_info, kungfu_id_pc = await save_plugin_attribute(role, server, kungfu_name, equip_data)
        await attribute_submit.finish(await format_attribute_submit_success(role_info, kungfu_id_pc))

    args = plain_text.split()
    if len(args) not in [2, 3]:
        await attribute_submit.finish(PROMPT.ArgumentCountInvalid + "\n" + ATTRIBUTE_SUBMIT_USAGE)
    if len(args) == 2:
        server = Server(None, event.group_id).server
        name = args[0]
        kungfu_name = args[1]
    else:
        server = Server(args[0], event.group_id).server
        name = args[1]
        kungfu_name = args[2]
    if server is None:
        await attribute_submit.finish(PROMPT.ServerInvalid + "\n参考格式：提交属性 <服务器> <ID> <心法>")
    player_info = await get_attribute_submit_player(name, server)
    role_info = build_attribute_submit_role(name, server, player_info)
    kungfu_id = Kungfu(kungfu_name).id
    if kungfu_id is None:
        await attribute_submit.finish(PROMPT.KungfuNotExist + "\n参考格式：提交属性 <服务器> <ID> <心法>")
    kungfu_id_pc = cast(int, Kungfu.with_internel_id(kungfu_id, True).id)
    state["kungfu_id"] = kungfu_id_pc
    state["global_role_id"] = int(role_info.globalRoleId)
    state["role_info"] = role_info
    await attribute_submit.send("请发送从茗伊插件-角色统计-装备统计中导出的装备数据，请从文本编辑器中复制后直接发送，不要修改任何内容：")

@attribute_submit.got("equip_data")
async def _(event: GroupMessageEvent, state: T_State, equip_data: Message = Arg()):
    data = equip_data.extract_plain_text()
    try:
        instance = await JX3PlayerAttribute.from_plugin(data, state["kungfu_id"], state["global_role_id"])
        save_attribute_instance(instance)
        save_attribute_submit_role(state["role_info"])
    except Exception as e:
        await attribute_submit.finish(f"导入的装备数据不可用，已拒绝入库：\n{e}")
    await attribute_submit.finish(await format_attribute_submit_success(state["role_info"], state["kungfu_id"]))

replace_equip_matcher = on_command("jx3_attribute_replace_equip", aliases={"替换装备", "装备替换"}, priority=5, force_whitespace=True)

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
    for equip in match_equips:
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
    for enchant in match_enchants:
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
        if not attributes_data:
            await bot.send_group_msg(group_id=event.group_id, message="未识别到可入库的属性数据。")
            return
        loop = asyncio.get_running_loop()
        results = await asyncio.gather(*[
            loop.run_in_executor(attribute_db_executor, save_attribute_instance, each_data)
            for each_data in attributes_data
        ], return_exceptions=True)
        saved_data = [
            each_data
            for each_data, result in zip(attributes_data, results)
            if not isinstance(result, BaseException)
        ]
        failed_data = [
            format_attribute_save_error(each_data, cast(BaseException, result))
            for each_data, result in zip(attributes_data, results)
            if isinstance(result, BaseException)
        ]
        if not saved_data:
            msg = "未发现可用装备数据，已跳过不可用数据。"
        else:
            msg = "以下全局玩家ID完成入库："
        for each_data in saved_data:
            msg += f"\n{each_data.name}（{each_data.global_role_id}）"
        if failed_data:
            msg += "\n以下装备数据不可用，已跳过："
            for line in failed_data[:10]:
                msg += f"\n{line[:160]}"
            if len(failed_data) > 10:
                msg += f"\n另有 {len(failed_data) - 10} 条不可用数据已跳过。"
        await bot.send_group_msg(group_id=event.group_id, message=msg)
