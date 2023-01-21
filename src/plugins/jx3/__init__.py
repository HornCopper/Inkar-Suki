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

from utils import checknumber, get_status, get_api
from file import read, write

from .jx3 import *
from .skilldatalib import getAllSkillsInfo, getSingleSkill, getSingleTalent
from .adventure import getAdventure, getAchievementsIcon
from .pet import get_pet
from .task import getTask, getTaskChain
from .jx3apiws import ws_client
from .jx3_event import RecvEvent
from .buff import get_buff
from .trade import search_item_info, getItemPriceById
from .top100 import get_top100

horse = on_command("jx3_horse",aliases={"马"},priority=5)
@horse.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await horse.finish(await horse_flush_place(args.extract_plain_text()))
    else:
        await horse.finish("没有输入任何马的名称哦，没办法帮你找啦。")

server = on_command("jx3_server",aliases={"服务器","开服"},priority=5)
@server.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await server.finish(await server_status(args.extract_plain_text()))
    else:
        await server.finish("没有输入任何服务器名称哦，没办法帮你找啦。")

macro = on_command("jx3_macro",aliases={"宏"},priority=5)
@macro.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await macro.finish(await macro_(args.extract_plain_text()))
    else:
        await macro.finish("没有输入任何心法名称哦，没办法帮你找啦。")

daily = on_command("jx3_daily",aliases={"日常","周常"},priority=5)
@daily.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await daily.finish(await daily_(args.extract_plain_text()))
    else:
        await daily.finish("没有输入任何服务器名称哦，自动切换至电信一区-长安城。\n"+await daily_("长安城"))
        
exam = on_command("jx3_exam",aliases={"科举"},priority=5)
@exam.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await exam.finish(await exam_(args.extract_plain_text()))
    else:
        await exam.finish("没有提供科举的问题，没办法解答啦。")
        
matrix = on_command("jx3_matrix",aliases={"阵眼"},priority=5)
@matrix.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await matrix.finish(await matrix_(args.extract_plain_text()))
    else:
        await matrix.finish("没有输入任何心法名称哦，没办法帮你找啦。")
        
equip = on_command("jx3_equip",aliases={"装备"},priority=5)
@equip.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await equip.finish(await equip_(args.extract_plain_text()))
    else:
        await equip.finish("没有输入任何心法名称哦，没办法帮你找啦。")
        
require = on_command("jx3_require",aliases={"奇遇信息"},priority=5)
@require.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await require.finish(await require_(args.extract_plain_text()))
    else:
        await require.finish("没有输入任何奇遇名称，没办法帮你找啦，输入时也请不要输入宠物奇遇哦~")
        
news = on_command("jx3_news",aliases={"新闻"},priority=5)
@news.handle()
async def _():
    await require.finish(await news_())
    
random_ = on_command("jx3_random",aliases={"骚话"},priority=5)
@random_.handle()
async def _():
    await random_.finish("来自“万花谷”频道：\n"+await random__())
    
heighten = on_command("jx3_heighten",aliases={"小药"},priority=5)
@heighten.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        await heighten.finish(await heighten_(args.extract_plain_text()))
    else:
        await heighten.finish("没有输入任何心法名称哦，没办法帮你找啦。")

kungfu = on_command("jx3_kungfu",aliases={"心法"},priority=5)
@kungfu.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    kungfu_ = args.extract_plain_text()
    node = await getAllSkillsInfo(kungfu_)
    if node == False:
        await kungfu.finish("此心法不存在哦，请检查后重试~")
    await bot.call_api("send_group_forward_msg", group_id = event.group_id, messages = node)

skill = on_command("jx3_skill",aliases={"技能"},priority=5)
@skill.handle()
async def _(args: Message = CommandArg()):
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

talent = on_command("_jx3_talent",aliases={"_奇穴"},priority=5)
@talent.handle()
async def _(args: Message = CommandArg()):
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
async def _(event: GroupMessageEvent):
    now = json.loads(read(TOOLS + "/subscribe.json"))
    if str(event.group_id) not in now:
        now.append(str(event.group_id))
        write(TOOLS + "/subscribe.json", json.dumps(now))
        await subscribe.finish("已开启本群的订阅！当收到事件时会自动推送。")
    else:
        await subscribe.finish("已经订阅了，不能重复订阅哦~")

unsubscribe = on_command("jx3_unsubscribe", aliases={"退订"}, priority=5)
@unsubscribe.handle()
async def _(event: GroupMessageEvent):
    now = json.loads(read(TOOLS + "/subscribe.json"))
    if str(event.group_id) not in now:
        await unsubscribe.finish("尚未订阅，无法退订哦~")
    else:
        now.remove(str(event.group_id))
        write(TOOLS + "/subscribe.json", json.dumps(now))
        await unsubscribe.finish("退订成功！不会再收到订阅了，需要的话请使用命令重新订阅~")

tiangou = on_command("jx3_tiangou", aliases={"舔狗"}, priority=5)
@tiangou.handle()
async def _(event: GroupMessageEvent):
    data = await tiangou_()
    await tiangou.finish(f"舔狗日志：\n{data}")

buff_ = on_command("jx3_buff", aliases={"debuff","buff"}, priority=5)
@buff_.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
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
            ver = "20221027"
        else:
            await _talent.finish("唔……这是什么赛季呢？")
    name = aliases(kf)
    if name == False:
        await _talent.finish("未找到该心法，请检查后重试~")
    if os.path.exists(ASSETS + "/jx3" + f"v{ver}.json") == False:
        final_url = f"https://oss.jx3box.com/data/qixue/v{ver}.json"
        data = await get_api(final_url)
        write(ASSETS + "/jx3" + f"v{ver}.json", json.dumps(data, ensure_ascii=False))
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
    arg = args.extract_plain_text()
    if arg == "":
        await recruit.finish("缺少服务器名称哦~")
    arg = arg.split(" ")
    if len(arg) not in [1,2]:
        await recruit.finish("参数不正确哦，只能有1或2个参数~")
    if len(arg) == 1:
        server = arg[0]
        data = await recruit_(server)
    else:
        server = arg[0]
        copy = arg[1]
        data = await recruit_(server, copy)
    if type(data) == type([]):
        await recruit.finish(data[0])
    await recruit.finish(ms.image(data))

calculate = on_command("jx3_calculate", aliases={"日历"}, priority=5)
@calculate.handle()
async def _(event: GroupMessageEvent):
    data = await calculate_()
    if type(data) == type([]):
        await calculate.finish(data[0])
    else:
        await calculate.finish(ms.image(data))

flower = on_command("jx3_flower", aliases={"花价"}, priority=5)
@flower.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await flower.finish("唔……参数数量不对哦，请检查后重试~")
    if len(arg) == 1:
        server = arg[0]
        flower__ = None
    else:
        server = arg[0]
        flower__ = arg[1]
    data = await flower_(flower__, server)
    if type(data) == type([]):
        await flower.finish(data[0])
    else:
        await flower.finish(ms.image(data))

demon = on_command("jx3_demon", aliases={"金价"}, priority=5)
@demon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if arg == "":
        arg = None
    data = await demon_(arg)
    if type(data) == type([]):
        await demon.finish(data[0])
    else:
        await demon.finish(ms.image(data))

item_price = on_command("jx3_price", aliases={"物价"}, priority=5)
@item_price.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
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
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await serendipity.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    id = arg[1]
    data = await serendipity_(server, id)
    if type(data) == type([]):
        await serendipity.finish(data[0])
    else:
        await serendipity.finish(ms.image(data))

statistical = on_command("jx3_statistical", aliases={"近期奇遇"}, priority=5)
@statistical.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await statistical.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = arg[0]
        name = None
    else:
        server = arg[0]
        name = arg[1]
    data = await statistical_(server, name)
    if type(data) == type([]):
        await statistical.finish(data[0])
    else:
        await statistical.finish(ms.image(data))

gserendipity = on_command("jx3_gserendipity", aliases={"全服奇遇"}, priority=5)
@gserendipity.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
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
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await addritube.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    id = arg[1]
    data = await addritube_(server, id)
    if type(data) == type([]):
        await addritube.finish(data[0])
    else:
        await addritube.finish(ms.image(data))

firework = on_command("jx3_firework", aliases={"烟花"}, priority=5)
@firework.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await firework.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    id = arg[1]
    data = await firework_(server, id)
    if type(data) == type([]):
        await firework.finish(data[0])
    else:
        await firework.finish(ms.image(data))

sandbox = on_command("jx3_sandbox", aliases={"沙盘"}, priority=5)
@sandbox.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if arg == "":
        await sandbox.finish("缺少服务器名称，没办法帮你找哦~")
    data = await sandbox_(arg)
    if type(data) == type([]):
        await sandbox.finish(data[0])
    else:
        await sandbox.finish(ms.image(data))

trade_ = on_command("jx3_trade", aliases={"交易行"}, priority=5)
@trade_.handle()
async def _(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await trade_.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    check_url = f"https://www.jx3api.com/data/server/status?server={server}"
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
            final_data = await getItemPriceById(id, server)
        except:
            await trade_.finish("暂未找到该区服报价，请查看其他区服~")
        if type(final_data) == type({}):
            await trade_.finish(final_data["msg"])
        msg = f"查到{server}的该物品交易行价格：\n最低价格：{final_data[0]}\n平均价格：{final_data[1]}\n最高价格：{final_data[2]}"
        await trade_.finish(msg)
    else:
        return
    
achievements = on_command("jx3_machi",aliases={"进度"},priority=5)
@achievements.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    achievement = args.extract_plain_text().split(" ")
    if len(achievement) != 3:
        await achievements.finish("唔……缺少参数哦~")
    server = achievement[0]
    id = achievement[1]
    achi = achievement[2]
    data = await achievements_(server, id, achi)
    if type(data) == type([]):
        await achievements.finish(data[0])
    else:
        await bot.call_api("send_group_forward_msg",group_id = event.group_id, messages = data["result"])

special = on_command("jx3_special",aliases={"掉落"},priority=5)
@special.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await special.finish("唔……参数数量有误，请检查后重试~")
    if len(arg) == 1:
        data = await special_(server = arg[0])
    else:
        data = await special_(server = arg[0], item = arg[1])
    if type(data) == type([]):
        await special.finish(data[0])
    else:
        await special.finish(ms.image(data))

arena = on_command("jx3_arena",aliases={"名剑"}, priority=5)
@arena.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2,3]:
        await arena.finish("唔……参数数量有误，请检查后重试~")
    if arg[0] == "战绩":
        if len(arg) != 3:
            await arena.finish("唔……参数数量有误，请检查后重试~")
        data = await arena_(object = "战绩", server = arg[1], name = arg[2])
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

trials = on_command("jx3_trials", aliases={"试炼"}, priority=5)
@trials.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await trials.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    school = arg[1]
    data = await trials_(server, school)
    if type(data) == type([]):
        await trials.finish(data[0])
    else:
        await trials.finish(ms.image(data))

top100_ = on_command("jx3_top100",aliases={"百强"},priority=5)
@top100_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await top100_.finish("唔……参数不正确哦，请检查后重试~")
    server = arg[0]
    boss = arg[1]
    team = arg[2]
    data = await get_top100(server, team, boss)
    await top100_.finish(data)

rank = on_command("jx3_rank", aliases={"榜单"}, priority=5)
@rank.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await rank.finish("唔……参数不正确哦，请检查后重试~")
    type1 = arg[0]
    server = arg[1]
    type2 = arg[2]
    data = await rank_(type_1=type1, server=server, type_2=type2)
    if type(data) == type([]):
        await rank.finish(data[0])
    else:
        await rank.finish(ms.image(data))

announce = on_command("jx3_announce",aliases={"维护公告"},priority=5)
@announce.handle()
async def _(event: GroupMessageEvent):
    url = await announce_()
    await announce.finish(ms.image(url))

driver = get_driver()

@driver.on_startup
async def _():
    logger.info("Connecting to JX3API...Please wait.")
    await ws_client.init()
    logger.info("Connected to JX3API successfully.")

ws_recev = on(type="WsRecv", priority=5, block=False)

@ws_recev.handle()
async def _(bot: Bot, event: RecvEvent):
    message = str(event.get_message())
    if message == "False":
        return
    groups = json.loads(read(TOOLS + "/subscribe.json"))
    for i in groups:
        try:
            await bot.call_api("send_group_msg", group_id = int(i), message = message)
        except:
            logger.info(f"向群({i})推送失败，可能是因为风控、禁言或者未加入该群。")
