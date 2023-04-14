import sys
import nonebot
import json
import os

from nonebot import get_driver
from nonebot import on, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"
ASSETS = TOOLS[:-5] + "assets"

from utils import checknumber, get_api
from file import read, write

from .jx3 import *
from .skilldatalib import getAllSkillsInfo, getSingleSkill, getSingleTalent, aliases as als
from .adventure import getAdventure, getAchievementsIcon
from .pet import get_pet, get_cd
from .task import getTask, getTaskChain
from .jx3apiws import ws_client
from .jx3_event import RecvEvent
from .buff import get_buff
from .trade import search_item_info, getItemPriceById
from .top100 import get_top100
from .dh import get_dh
from .macro import get_macro
from .chitu import get_chitu, get_horse_reporter
from .wanbaolou import get_wanbaolou

news = on_command("jx3_news", aliases={"新闻"}, priority=5)
@news.handle()
async def _():
    '''
    获取剑网3近期新闻：

    Example：-新闻
    '''
    await news.finish(await news_())

server = on_command("jx3_server", aliases={"服务器","开服"}, priority=5)
@server.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取服务器开服状态：

    Example：-服务器 幽月轮
    Example：-开服 幽月轮
    '''
    if args.extract_plain_text():
        await server.finish(await server_status(server=args.extract_plain_text(), group=str(event.group_id)))
    else:
        await server.finish("没有输入任何服务器名称哦，没办法帮你找啦。")

daily = on_command("jx3_daily", aliases={"日常","周常"}, priority=5)
@daily.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    Example：-日常 幽月轮
    '''
    if args.extract_plain_text():
        img = await daily_(args.extract_plain_text(), str(event.group_id))
    else:
        img = await daily_("长安城", str(event.group_id))
    await daily.finish(ms.image(img))
        
exam = on_command("jx3_exam", aliases={"科举"}, priority=5)
@exam.handle()
async def _(args: Message = CommandArg()):
    '''
    查询科举答案：

    Example：-科举 古琴有几根弦
    '''
    if args.extract_plain_text():
        await exam.finish(await exam_(args.extract_plain_text()))
    else:
        await exam.finish("没有提供科举的问题，没办法解答啦。")
        
matrix = on_command("jx3_matrix", aliases={"阵眼"}, priority=5)
@matrix.handle()
async def _(args: Message = CommandArg()):
    '''
    查询阵眼效果：

    Example：-阵眼 紫霞功
    '''
    if args.extract_plain_text():
        await matrix.finish(await matrix_(args.extract_plain_text()))
    else:
        await matrix.finish("没有输入任何心法名称哦，没办法帮你找啦。")

random_ = on_command("jx3_random", aliases={"骚话"}, priority=5)
@random_.handle()
async def _():
    '''
    召唤一条骚话：

    Example：-骚话
    '''
    await random_.finish("来自“万花谷”频道：\n"+await random__())

kungfu = on_command("jx3_kungfu", aliases={"心法"}, priority=5)
@kungfu.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询心法下所有技能：

    Example：-心法 莫问
    '''
    kungfu_ = args.extract_plain_text()
    node = await getAllSkillsInfo(kungfu_)
    if node == False:
        await kungfu.finish("此心法不存在哦，请检查后重试~")
    await bot.call_api("send_group_forward_msg", group_id = event.group_id, messages = node)

skill = on_command("jx3_skill", aliases={"技能"}, priority=5)
@skill.handle()
async def _(args: Message = CommandArg()):
    '''
    查询心法下某技能：

    Example：-技能 莫问 徵
    '''
    info = args.extract_plain_text().split(" ")
    if len(info) != 2:
        await skill.finish("信息不正确哦，只能有2个参数，请检查后重试~")
    else:
        kungfu = info[0]
        skill_ = info[1]
    msg = await getSingleSkill(kungfu, skill_)
    if msg == False:
        await skill.finish("此心法不存在哦，请检查后重试~")
    await skill.finish(msg)

talent = on_command("_jx3_talent", aliases={"_奇穴"}, priority=5)
@talent.handle()
async def _(args: Message = CommandArg()):
    '''
    查询心法下某奇穴：

    Example：-_奇穴 莫问 流照

    Notice：此功能会显示秘籍，而另外一个不会（参考事件响应器为`_talent`的函数）
    '''
    data = args.extract_plain_text()
    data = data.split(" ")
    if len(data) != 2:
        await talent.finish("信息不正确哦，只能有2个参数，请检查后重试~")
    else:
        kungfu = data[0]
        talent_ = data[1]
        msg = await getSingleTalent(kungfu, talent_)
        await talent.finish(msg)

pet_ = on_command("jx3_pet", aliases={"宠物"}, priority=5)
@pet_.handle()
async def _(state: T_State, args: Message = CommandArg()):
    '''
    查询宠物信息：

    Example：-宠物 静静
    '''
    data = args.extract_plain_text()
    info = await get_pet(data)
    if info["status"] == 404:
        await pet_.finish("唔……没有找到你要的宠物，请检查后重试~")
    elif info["status"] == 201:
        from nonebot.log import logger
        logger.info(info)
        result = info["result"]
        state["result"] = result
        desc = info["desc"]
        state["desc"] = desc
        clue = info["clue"]
        state["clue"] = clue
        url = info["url"]
        state["url"] = url
        msg = ""
        for i in range(len(result)):
            msg = msg + f"\n{i}.{result[i]}"
        msg = msg[1:]
        await pet_.send(msg)

@pet_.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
async def __(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num):
        result = state["result"]
        desc = state["desc"]
        clue = state["clue"]
        url = state["url"]
        name = result[int(num)]
        desc = desc[int(num)] 
        clue = clue[int(num)]
        url = url[int(num)]
        msg = f"查询到「{name}」：\n{url}\n{clue}\n{desc}"
        await pet_.finish(msg)
    else:
        await pet_.finish("唔……输入的不是数字哦，取消搜索。")

adventure_ = on_command("jx3_adventure", aliases={"成就"}, priority=5)# 别骂了，想不出其他变量名了
@adventure_.handle()
async def _(state: T_State, args: Message = CommandArg()):
    '''
    查询成就信息：

    Example：-成就 好久不见

    Notice：还有一个会发送聊天记录的功能，可以查询自身是否完成该成就，同时也会提供成就信息。
    '''
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

@adventure_.got("num", prompt = "发送序号以搜索，发送其他内容则取消搜索。")
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

task_ = on_command("jx3_task", aliases={"任务"}, priority=5)
@task_.handle()
async def _(state: T_State, args: Message = CommandArg()):
    '''
    查询任务及任务链：

    Example：-任务 十万火急
    '''
    task__ = args.extract_plain_text()
    data = await getTask(task__)
    if data["status"] == 404:
        await task_.finish("未找到该任务，请检查后重试~")
    map = data["map"]
    id = data["id"]
    task___ = data["task"]
    target = data["target"]
    level = data["level"]
    state["map"] = map
    state["id"] = id
    state["task"] = task___
    state["target"] = target
    state["level"] = level
    msg = ""
    for i in range(len(map)):
        msg = msg + f"{i}.{map[i]}：{task___[i]}\n"
    msg = msg[:-1]
    await task_.send(msg)
    return

@task_.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
async def _(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num):
        num = int(num)
        map = state["map"][num]
        id = state["id"][num]
        task__ = state["task"][num]
        target = state["target"][num]
        level = state["level"][num]
        msg = f"查询到「{task__}」：\nhttps://www.jx3box.com/quest/view/{id}\n开始等级：{level}\n地图：{map}\n任务目标：{target}"
        chain = await getTaskChain(id)
        msg = msg + f"\n任务链：{chain}"
        await task_.finish(msg)
    else:
        await task_.finish("唔……输入的不是数字哦，取消搜索。")

subscribe = on_command("jx3_subscribe", aliases={"订阅"}, priority=5)
@subscribe.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    订阅内容，可选择订阅的内容：

    目前支持：玄晶、新闻、开服。

    Example：-订阅 玄晶

    Notice：一次只可订阅一个。
    '''
    path = DATA + "/" + str(event.group_id) + "/subscribe.json"
    now = json.loads(read(path))
    obj = args.extract_plain_text()
    if obj not in ["玄晶","公告","开服"]:
        await subscribe.finish("请不要订阅一些很奇怪的东西，我可是无法理解的哦~")
    if obj in now:
        await subscribe.finish("已经订阅了哦，请不要重复订阅~")
    now.append(obj)
    write(path, json.dumps(now, ensure_ascii=False))
    await subscribe.finish(f"已开启本群的{obj}订阅！当收到事件时会自动推送，如需取消推送，请发送：-退订 {obj}")

unsubscribe = on_command("jx3_unsubscribe", aliases={"退订"}, priority=5)
@unsubscribe.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    退订某内容，可选择：

    同上。

    Example：-退订 开服
    '''
    path = DATA + "/" + str(event.group_id) + "/subscribe.json"
    now = json.loads(read(path))
    obj = args.extract_plain_text()
    if obj not in ["玄晶","公告","开服"]:
        await subscribe.finish("请不要取消订阅一些很奇怪的东西，我可是无法理解的哦~")
    if obj not in now:
        await subscribe.finish("尚未订阅，无法取消订阅哦~")
    now.remove(obj)
    write(path, json.dumps(now, ensure_ascii=False))
    await subscribe.finish(f"已关闭本群的{obj}订阅！如需再次开启，请发送：\n-订阅 {obj}")

tiangou = on_command("jx3_tiangou", aliases={"舔狗"}, priority=5)
@tiangou.handle()
async def _(event: GroupMessageEvent):
    '''
    获取一条舔狗日志：

    Example：-舔狗
    '''
    data = await tiangou_()
    await tiangou.finish(f"舔狗日志：\n{data}")

buff_ = on_command("jx3_buff", aliases={"debuff","buff"}, priority=5)
@buff_.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    '''
    获取Buff信息：

    Example：-buff 躺在冰冷的地上
    Example：-debuff 耐力受损
    '''
    buff = args.extract_plain_text()
    data = await get_buff(buff)
    if type(data) != type("sb"):
        state["icon"] = data["icon"]
        state["remark"] = data["remark"]
        state["desc"] = data["desc"]
        state["name"] = data["name"]
        state["id"] = data["id"]
        msg = ""
        for i in range(len(data["icon"])):
            msg = msg + "\n" + str(i) + "." + data["name"][i] + "（技能ID：" + data["id"][i] + "）"
        await buff_.send(msg[1:])
        return
    else:
        await buff_.finish(data)

@buff_.got("num", prompt="输入数字搜索状态效果，输入其他内容则无视。")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num):
        icon = state["icon"]
        remark = state["remark"]
        desc = state["desc"]
        name = state["name"]
        id = state["id"]
        if int(num) not in list(range(len(icon))):
            await buff_.finish("唔，输入的数字不对哦，取消搜索~")
        else:
            num = int(num)
            msg = ms.image(icon[num]) + f"\nBUFF名称：{name[num]}\n{desc[num]}\n特殊描述：{remark[num]}"
            await buff_.finish(msg)
    else:
        return

_talent = on_command("jx3_talent", aliases={"奇穴"}, priority=5)
@_talent.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2,3]:
        await _talent.finish("唔……参数不正确哦~")
    if len(arg) == 2:
        kf = arg[0]
        tl = arg[1]
        ver = "20221027"
    else:
        kf = arg[0]
        tl = arg[1]
        ver = arg[2]
        if ver == "怒海争锋":
            ver = "20190926"
        elif ver == "凌雪藏锋":
            ver = "20191128"
        elif ver == "结庐在江湖":
            ver = "20200522"
        elif ver == "同筑山水居":
            ver = "20200805"
        elif ver == "奉天证道":
            ver = "20201030"
        elif ver == "月满归乡":
            ver = "20201130"
        elif ver == "白帝风云":
            ver = "20210830"
        elif ver == "北天药宗":
            ver = "20220118"
        elif ver == "江湖无限":
            ver = "20220706"
        elif ver == "横刀断浪":
            ver = "20230206"
        elif ver == "群侠万变一改":
            ver = "20230328"
        elif ver == "群侠万变二改" or ver == "群侠万变":
            ver = "20230411"
        else:
            await _talent.finish("唔……这是什么赛季呢？")
    name = aliases(kf)
    if name == False:
        await _talent.finish("未找到该心法，请检查后重试~")
    if os.path.exists(ASSETS + "/jx3" + f"v{ver}.json") == False:
        final_url = f"https://oss.jx3box.com/data/qixue/v{ver}.json"
        data = await get_api(final_url)
        write(ASSETS + "/jx3/" + f"v{ver}.json", json.dumps(data, ensure_ascii=False))
    else:
        data = json.loads(read(ASSETS + "/jx3" + f"v{ver}.json"))
    try:
        real_data = data[name]
    except:
        await _talent.finish("唔……该赛季没有此心法~")
    for i in range(1,13):
        for x in range(1,6):
            try:
                each = real_data[str(i)][str(x)]
            except:
                continue
            if each["name"] == tl:
                if each["is_skill"] == 1:
                    special_desc = each["meta"]
                    desc = each["desc"]
                    extend = each["extend"]
                    icon = "https://icon.jx3box.com/icon/" + str(each["icon"]) + ".png"
                    msg = f"第{i}重·第{x}层：{tl}\n" + ms.image(icon) + f"\n{special_desc}\n{desc}\n{extend}"
                else:
                    desc = each["desc"]
                    icon = "https://icon.jx3box.com/icon/" + str(each["icon"]) + ".png"
                    msg = f"第{i}重·第{x}层：{tl}\n" + ms.image(icon) + f"\n{desc}"
                await _talent.finish(msg)
    await _talent.finish("唔……未找到该奇穴哦~")

recruit = on_command("jx3_recruit", aliases={"招募"}, priority=5)
@recruit.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取招募：

    Example：-招募 幽月轮
    '''
    arg = args.extract_plain_text()
    if arg == "":
        await recruit.finish("缺少服务器名称哦~")
    arg = arg.split(" ")
    group = str(event.group_id)
    if len(arg) not in [1,2]:
        await recruit.finish("参数不正确哦，只能有1或2个参数~")
    if len(arg) == 1:
        server = arg[0]
        data = await recruit_(server, group=group)
    else:
        server = arg[0]
        copy = arg[1]
        data = await recruit_(server, copy = copy, group = group)
    if type(data) == type([]):
        await recruit.finish(data[0])
    await recruit.finish(ms.image(data))

demon = on_command("jx3_demon", aliases={"金价"}, priority=5)
@demon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取各服金价：

    Example：-金价 幽月轮
    '''
    arg = args.extract_plain_text()
    if arg == "":
        arg = None
    data = await demon_(arg, group=str(event.group_id))
    if type(data) == type([]):
        await demon.finish(data[0])
    else:
        await demon.finish(ms.image(data))

item_price = on_command("jx3_price", aliases={"物价"}, priority=5)
@item_price.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取外观物价：
    
    Example：-物价 山神盒子
    Example：-物价 大橙武券
    '''
    arg = args.extract_plain_text()
    if arg == "":
        await item_price.finish("缺少物品名称，没办法找哦~")
    data = await item_(arg)
    if type(data) == type([]):
        await item_price.finish(data[0])
    else:
        await item_price.finish(ms.image(data))

serendipity = on_command("jx3_serendipity", aliases={"奇遇"}, priority=5)
@serendipity.handle()  
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取个人奇遇记录：

    Example：-奇遇 幽月轮 哭包猫@唯我独尊
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await serendipity.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    id = arg[1]
    data = await serendipity_(server, id, group=str(event.group_id))
    if type(data) == type([]):
        await serendipity.finish(data[0])
    else:
        await serendipity.finish(ms.image(data))

statistical = on_command("jx3_statistical", aliases={"近期奇遇"}, priority=5)
@statistical.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取某服务器最近出奇遇的人的列表：

    Example：-近期奇遇 幽月轮 阴阳两界
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await statistical.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = arg[0]
        name = None
    else:
        server = arg[0]
        name = arg[1]
    data = await statistical_(server, name, group=str(event.group_id))
    if type(data) == type([]):
        await statistical.finish(data[0])
    else:
        await statistical.finish(ms.image(data))

gserendipity = on_command("jx3_gserendipity", aliases={"全服奇遇"}, priority=5)
@gserendipity.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取全服最近某奇遇的触发列表，按触发顺序：

    Example：-全服奇遇 阴阳两界
    '''
    arg = args.extract_plain_text()
    if arg == "":
        await gserendipity.finish("唔，缺少奇遇名称，没有办法找哦~")
    data = await global_serendipity(arg)
    if type(data) == type([]):
        await gserendipity.finish(data[0])
    else:
        await gserendipity.finish(ms.image(data))

gstatistical = on_command("jx3_gstatistical", aliases={"全服统计"}, priority=5)
@gstatistical.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取各服奇遇的触发者，统计图表：

    Example：-全服统计 阴阳两界
    '''
    arg = args.extract_plain_text()
    if arg == "":
        await gstatistical.finish("唔，缺少奇遇名称，没有办法找哦~")
    data = await global_statistical(arg)
    if type(data) == type([]):
        await gstatistical.finish(data[0])
    else:
        await gstatistical.finish(ms.image(data))

addritube = on_command("jx3_addritube", aliases={"属性","查装"}, priority=5)
@addritube.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await addritube.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    id = arg[1]
    data = await addritube_(server, id, group=str(event.group_id))
    if type(data) == type([]):
        await addritube.finish(data[0])
    else:
        await addritube.finish(ms.image(data))

sandbox = on_command("jx3_sandbox", aliases={"沙盘"}, priority=5)
@sandbox.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取服务器沙盘：

    Example：-沙盘 幽月轮
    '''
    arg = args.extract_plain_text()
    if arg == "":
        await sandbox.finish("缺少服务器名称，没办法帮你找哦~")
    data = await sandbox_(arg, group=str(event.group_id))
    if type(data) == type([]):
        await sandbox.finish(data[0])
    else:
        await sandbox.finish(ms.image(data))

trade_ = on_command("jx3_trade", aliases={"交易行"}, priority=5)
@trade_.handle()
async def _(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取交易行物品价格：

    Example：-交易行 幽月轮 帝骖龙翔
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await trade_.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    check_url = f"https://api.jx3api.com/data/server/status?server={server}"
    check_data = await get_api(check_url, proxy = proxies)
    if check_data["code"] == 401:
        await trade_.finish("唔……服务器不存在，请检查后重试~")
    item = arg[1]
    state["server"] = server
    data = await search_item_info(item)
    if data == []:
        await trade_.finish("唔……没有找到该物品哦~")
    else:
        state["data"] = data
        msg = ""
        for i in range(len(data)):
            msg = msg + "\n" + str(i) + "." + f"{data[i][1]}（ID：{data[i][0]}）"
        await trade_.send(msg[1:] + "\n小提示：按住Ctrl并将鼠标放在物品上，即可查看该物品的ID。")

@trade_.got("num", prompt="输入序号以搜索，其他内容则无视。")
async def _(state: T_State, event: GroupMessageEvent, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num):
        data = state["data"]
        server = state["server"]
        id = data[int(num)][0]
        try:
            final_data = await getItemPriceById(id, server, group=str(event.group_id))
        except:
            await trade_.finish("暂未找到该区服报价，请查看其他区服~")
        if type(final_data) == type({}):
            await trade_.finish(final_data["msg"])
        msg = f"查到{server}的该物品交易行价格：\n最低价格：{final_data[0]}\n平均价格：{final_data[1]}\n最高价格：{final_data[2]}"
        await trade_.finish(msg)
    else:
        return
    
achievements = on_command("jx3_machi", aliases={"进度"}, priority=5)
@achievements.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询玩家成就完成进度以及成就信息：

    Example：-进度 幽月轮 哭包猫@唯我独尊 好久不见
    Example：-进度 幽月轮 哭包猫@唯我独尊 25人英雄范阳夜变
    Example：-进度 幽月轮 哭包猫@唯我独尊 扶摇九天
    '''
    achievement = args.extract_plain_text().split(" ")
    if len(achievement) != 3:
        await achievements.finish("唔……缺少参数哦~")
    server = achievement[0]
    id = achievement[1]
    achi = achievement[2]
    data = await achievements_(server, id, achi, group = str(event.group_id))
    if type(data) == type([]):
        await achievements.finish(data[0])
    else:
        await achievements.finish(ms.image(data))

arena = on_command("jx3_arena", aliases={"名剑"}, priority=5)
@arena.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2,3]:
        await arena.finish("唔……参数数量有误，请检查后重试~")
    if arg[0] == "战绩":
        if len(arg) != 3:
            await arena.finish("唔……参数数量有误，请检查后重试~")
        data = await arena_(object = "战绩", server = arg[1], name = arg[2], group = str(event.group_id))
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            await arena.finish(ms.image(data))
    elif arg[0] == "排行":
        if len(arg) != 2:
            await arena.finish("唔……参数数量有误，请检查后重试~")
        data = await arena_(object = "排行", mode = arg[1])
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            await arena.finish(ms.image(data))
    elif arg[0] == "统计":
        if len(arg) != 2:
            await arena.finish("唔……参数数量有误，请检查后重试~")
        data = await arena_(object = "统计", mode = arg[1])
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            await arena.finish(ms.image(data))

top100_ = on_command("jx3_top100", aliases={"百强"}, priority=5)
@top100_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取魔盒百强列表：

    Example：-百强 幽月轮 李重茂
    Example：-百强 幽月轮 李重茂 风波渡
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2,3]:
        await top100_.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 2:
        server = arg[0]
        boss = arg[1]
        team = None
    else:
        server = arg[0]
        boss = arg[1]
        team = arg[2]
    data = await get_top100(server, boss, group=str(event.group_id), team=team)
    await top100_.finish(data)

rank = on_command("jx3_rank", aliases={"榜单"}, priority=5)
@rank.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取风云榜单：

    Example：-榜单 个人 幽月轮 名士五十强
    Example：-榜单 帮会 幽月轮 恶人神兵宝甲五十强
    Example：-榜单 阵营 幽月轮 赛季恶人五十强
    Example：-榜单 试炼 幽月轮 明教
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await rank.finish("唔……参数不正确哦，请检查后重试~")
    type1 = arg[0]
    server = arg[1]
    type2 = arg[2]
    data = await rank_(type_1=type1, server=server, type_2=type2, group=str(event.group_id))
    if type(data) == type([]):
        await rank.finish(data[0])
    else:
        await rank.finish(ms.image(data))

announce = on_command("jx3_announce", aliases={"维护公告"}, priority=5)
@announce.handle()
async def _(event: GroupMessageEvent):
    '''
    获取维护公告的图片：

    Example：-维护公告
    '''
    url = await announce_()
    await announce.finish(ms.image(url))

roleInfo = on_command("jx3_player", aliases={"玩家信息"}, priority=5)
@roleInfo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取玩家信息：

    Example：-玩家信息 幽月轮 哭包猫@唯我独尊
    '''
    text = args.extract_plain_text().split(" ")
    if len(text) != 2:
        await roleInfo.finish("唔……参数数量不正确哦~")
    srv = text[0]
    id = text[1]
    msg = await roleInfo_(server = srv, player = id, group=str(event.group_id))
    await roleInfo.finish(msg)

dh_ = on_command("jx3_dh", aliases={"蹲号"}, priority=5)
@dh_.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取盆栽蹲号信息：

    Example：-蹲号 蝶金
    '''
    details = args.extract_plain_text()
    if details == "":
        await dh_.finish("您没有输入条件哦，请检查后重试~\n条件以英文分号(;)分割哦~")
    details = details.split(";")
    if len(details) < 1:
        await dh_.finish("您没有输入条件哦，请检查后重试~\n条件以英文分号(;)分割哦~")
    final_details = ",".join(details)
    data = await get_dh(final_details)
    if type(data) != type([]):
        await dh_.finish(data)
    else:
        await bot.call_api("send_group_forward_msg", group_id = event.group_id, messages = data)

ct = on_command("jx3_ct", aliases={"-赤兔"}, priority=5)
@ct.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取赤兔刷新信息：

    Example：-赤兔 幽月轮
    '''
    server = args.extract_plain_text()
    if server == "":
        await ct.finish("您没有输入服务器名称哦，请检查后重试~")
    msg = await get_chitu(server, str(event.group_id))
    await ct.finish(msg)

mc_helper = on_command("jx3_cd", aliases={"-cd"}, priority=5)
@mc_helper.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取部分特殊物品的上次记录：

    Notice：数据来源@茗伊插件集 https://www.j3cx.com

    Example：-cd 幽月轮 归墟玄晶
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await mc_helper.finish("唔……参数数量有误，请检查后重试~")
    server = arg[0]
    sep = arg[1]
    msg = await get_cd(server, sep, str(event.group_id))
    await mc_helper.finish(msg)

zones = on_command("jx3_zones", aliases={"副本"}, priority=5)
@zones.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取玩家副本通关记录：

    Example：-副本 幽月轮 哭包猫@唯我独尊
    '''
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await zones.finish("唔……参数数量有误，请检查后重试~")
    server = arg[0]
    id = arg[1]
    data = await zone(server, id, str(event.group_id))
    if type(data) == type([]):
        await zones.finish(data[0])
    else:
        await zones.finish(ms.image(data))

xuanjing = on_command("jx3_xuanjing", aliases={"-玄晶"}, priority=5)
@xuanjing.handle()
async def _(event: GroupMessageEvent):
    dt = json.loads(read("./xuanjing.json"))
    dt = list(reversed(dt))
    if len(dt) == 0:
        await xuanjing.finish("尚未检测到玄晶哦~")
    msg = ""
    num = 0
    for i in dt:
        x = i.split(";")
        map = x[1]
        id = x[2]
        time = x[3]
        msg = msg + f"{map}：{id} {time}\n"
        num = num + 1
        if num == 6:
            break
    await xuanjing.finish(msg[:-1])

macro_ = on_command("jx3_macro", aliases={"宏"}, priority=5)
@macro_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    xf = args.extract_plain_text()
    xf = als(xf)
    if xf == False:
        await macro_.finish("唔……心法输入有误，请检查后重试~")
    data = await get_macro(xf)
    await macro_.finish(data)

horse = on_command("jx3_horse", aliases={"抓马","马场"}, priority=5)
@horse.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    if server == "":
        await horse.finish("没有输入服务器信息哦，暂时没有办法帮您获取呢~")
    group = str(event.group_id)
    msg = await get_horse_reporter(server, group)
    await horse.finish(msg)

wbl = on_command("jx3_wbl", aliases={"万宝楼"}, priority=5)
@wbl.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await wbl.finish("唔……参数有误，请检查后重试~")
    product = arg[0]
    product_num = arg[1]
    if checknumber(product_num) == False:
        await wbl.finish("唔……检测到商品编号出现了非数字的内容！\n请检查后重试~")
    if product not in ["外观","角色"]:
        await wbl.finish("唔……第二个参数请填写「外观」或「角色」。")
    if product == "外观":
        product_flag = True
    else:
        product_flag = False
    msg = await get_wanbaolou(product_num, product_flag)
    await wbl.finish(msg)

driver = get_driver()

@driver.on_startup
async def _():
    logger.info("Connecting to JX3API...Please wait.")
    await ws_client.init()
    logger.info("Connected to JX3API successfully.")

ws_recev = on(type="WsRecv", priority=5, block=False)

@ws_recev.handle()
async def _(bot: Bot, event: RecvEvent):
    message = event.get_message()
    if message == "False":
        return
    groups = os.listdir(DATA)
    for i in groups:
        subscribe = json.loads(read(DATA + "/" + i + "/subscribe.json"))
        if message["type"] in subscribe:
            try:
                await bot.call_api("send_group_msg", group_id = int(i), message = message["msg"])
            except:
                logger.info(f"向群({i})推送失败，可能是因为风控、禁言或者未加入该群。")
