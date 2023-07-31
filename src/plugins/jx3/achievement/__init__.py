from src.plugins.jx3.dungeon.api import mode_mapping

from .api import *

adventure_ = on_command("jx3_adventure", aliases={"成就"}, priority=5)

@adventure_.handle()
async def _(state: T_State, args: Message = CommandArg()):
    """
    查询成就信息：

    Example：-成就 好久不见
    """
    achievement_name = args.extract_plain_text()
    data = await getAdventure(achievement_name)
    if data["status"] == 404:
        await adventure_.finish("没有找到任何相关成就哦，请检查后重试~")
    elif data["status"] == 200:
        achievement_list = data["achievements"]
        icon_list = data["icon"]
        subAchievements = data["subAchievements"]
        id_list = data["id"]
        simpleDesc = data["simpDesc"]
        fullDesc = data["Desc"]
        point = data["point"]
        map = data["map"]
        state["map"] = map
        state["point"] = point
        state["achievement_list"] = achievement_list
        state["icon_list"] = icon_list
        state["id_list"] = id_list
        state["simpleDesc"] = simpleDesc
        state["fullDesc"] = fullDesc
        state["subAchievements"] = subAchievements
        msg = ""
        for i in range(len(achievement_list)):
            msg = msg + f"{i}." + achievement_list[i] + "\n"
        msg = msg[:-1]
        await adventure_.send(msg)
        return

@adventure_.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
async def _(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num):
        num = int(num)
        map = state["map"][num]
        achievement = state["achievement_list"][num]
        icon = state["icon_list"][num]
        id = state["id_list"][num]
        simpleDesc = state["simpleDesc"][num]
        point = state["point"][num]
        fullDesc = state["fullDesc"][num]
        subAchievement = state["subAchievements"][num]
        msg = f"查询到「{achievement}」：\n" + await getAchievementsIcon(icon) + f"\nhttps://www.jx3box.com/cj/view/{id}\n{simpleDesc}\n{fullDesc}\n地图：{map}\n资历：{point}点\n附属成就：{subAchievement}"
        await adventure_.finish(msg)
    else:
        await adventure_.finish("唔……输入的不是数字哦，取消搜索。")

achievements = on_command("jx3_machi", aliases={"进度"}, priority=5)

@achievements.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询玩家成就完成进度以及成就信息：

    Example：-进度 幽月轮 哭包猫@唯我独尊 好久不见
    Example：-进度 幽月轮 哭包猫@唯我独尊 25人英雄范阳夜变
    Example：-进度 幽月轮 哭包猫@唯我独尊 扶摇九天
    Example：-进度 哭包猫@唯我独尊 扶摇九天
    """
    achievement = args.extract_plain_text().split(" ")
    if len(achievement) not in [2, 3]:
        await achievements.finish(PROMPT_ArgumentInvalid)
    if len(achievement) == 2:
        server = None
        id = achievement[0]
        achi = achievement[1]
    elif len(achievement) == 3:
        server = achievement[0]
        id = achievement[1]
        achi = achievement[2]
    data = await achievements_(server, id, achi, event.group_id)
    if type(data) == type([]):
        await achievements.finish(data[0])
    else:
        await achievements.finish(ms.image(data))

achievement_v2 = on_command("jx3_achievement_v2", aliases={"进度v2"}, priority=5)

@achievement_v2.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    achievement = args.extract_plain_text().split(" ")
    if len(achievement) not in [2, 3]:
        await achievement_v2.finish(PROMPT_ArgumentInvalid)
    if len(achievement) == 2:
        server = None
        id = achievement[0]
        achi = achievement[1]
    elif len(achievement) == 3:
        server = achievement[0]
        id = achievement[1]
        achi = achievement[2]
    data = await achi_v2(server, id, achi, str(event.group_id))
    if type(data) == type([]):
        await achievement_v2.finish(data[0])
    else:
        await achievement_v2.finish(ms.image(data))

zone_achievement = on_command("jx3_zoneachi", aliases={"团本成就"}, priority=5)

@zone_achievement.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2,3,4]:
        await zone_achievement.finish(PROMPT_ArgumentInvalid)
    group = str(event.group_id)
    if len(arg) == 2:
        server = None
        id = arg[0]
        zone = arg[1]
        mode = "10人普通"
    elif len(arg) == 3:
        server = arg[0] if server_mapping(arg[0], group) != None else ""
        if server != "":
            id = arg[1]
            zone = arg[2]
            mode = "10人普通"
        else:
            id = arg[0]
            zone = arg[1]
            mode = mode_mapping(arg[2])
    elif len(arg) == 4:
        server = arg[0]
        id = arg[1]
        zone = arg[2]
        mode = mode_mapping(arg[3])
    data = await zone_achi(server ,id, zone, mode, group)
    if type(data) == type([]):
        await zone_achievement.finish(data[0])
    else:
        await zone_achievement.finish(ms.image(data))