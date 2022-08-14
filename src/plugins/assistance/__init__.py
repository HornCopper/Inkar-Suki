import nonebot
import json
import sys
import time
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.adapters import Message
from nonebot.params import CommandArg
import numpy as np
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"
from file import read, write
from utils import convert_time, checknumber

open_ = on_command("open_group", aliases = {"开团"}, priority = 5)
@open_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    useful_info = data[0]
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    now = json.loads(read(final_path))
    for i in now:
        if i["desc"] == useful_info:
            await open_.finish("要不换一个描述？这个描述已经有人用了哦~")
    time_ = int(round(time.time() * 1000))
    from nonebot.log import logger
    logger.info(time_)
    new = {"desc":useful_info, "leader": str(event.user_id), "book":[], "gkp":["0","0"], "special":["无"], "time": time_}
    now.append(new)
    write(final_path, json.dumps(now, ensure_ascii = False))
    await open_.finish(f"已开启预定！\n使用以下命令即可预定：\n+预定 <团队描述> <T/奶/dps/老板> <ID> [备注(可不写)]\n此团的团队描述为：\n{useful_info}")

book = on_command("book", aliases = {"预定"}, priority = 5)
@book.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    now = json.loads(read(final_path))
    if len(data) not in [3,4]:
        await book.finish("参数不对哦！应该有3个或者4个参数，具体请看帮助文件。")
    else:
        if len(data) == 3:
            type_ = data[1]
            if type_ not in ["t","T","dps","DPS","奶","治疗","输出","Dps","老板"]:
                await book.finish("唔……您的预定类型是什么呀，可以说得再明白些吗？")
            id = data[2]
            group = data[0]
            for i in now:
                for a in i["book"]:
                    if a["id"] == id:
                        await book.finish("已经预定过了哦，请不要重复预定！")
            for i in now:
                if i["desc"] == group:
                    time_ = int(round(time.time() * 1000))
                    new = {"type":type_, "id": id, "info": "无", "time": time_}
                    i["book"].append(new)
                    write(final_path, json.dumps(now, ensure_ascii = False))
                    await book.finish("预定成功！")
            await book.finish("唔……目前还没有这个团，检查一下是不是完全一致哦~")
        else:
            type_ = data[1]
            if type_ not in ["t","T","dps","DPS","奶","治疗","输出","Dps","老板"]:
                await book.finish("唔……您的预定类型是什么呀，可以说得再明白些吗？")
            id = data[2]
            group = data[0]
            info = data[3]
            for i in now:
                for a in i["book"]:
                    if a["id"] == id:
                        await book.finish("已经预定过了哦，请不要重复预定！")
            for i in now:
                if i["desc"] == group:
                    time_ = int(round(time.time() * 1000))
                    new = {"type":type_, "id": id, "info": info, "time": time_}
                    i["book"].append(new)
                    write(final_path, json.dumps(now, ensure_ascii = False))
                    await book.finish("预定成功！")
            await book.finish("唔……目前还没有这个团，检查一下是不是完全一致哦~")

books = on_command("books", aliases = {"预定列表"}, priority = 5)
@books.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text()
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    now = json.loads(read(final_path))
    for i in now:
        if i["desc"] == data:
            msg = ""
            for a in i["book"]:
                id = a["id"]
                type_ = a["type"]
                info = a["info"]
                msg = msg + f"{id}预定{type_}坑，备注：{info}。\n申请时间：" + convert_time(a["time"]) + "\n"
            msg = msg[:-1]
            if msg == "":
                msg = "暂没有人预定哦，请过段时间再试~"
            await books.finish(msg)
    await books.finish("没有查到这个团哦，请检查是否一致~")

gkp = on_command("gkp", aliases={"金团"}, priority = 5)
@gkp.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    now = json.loads(read(final_path))
    if len(data) != 3:
        await gkp.finish("参数不对哦！应该有三个参数，具体请查看帮助文件~")
    desc = data[0]
    for i in now:
        if i["desc"] == desc and i["leader"] != str(event.user_id):
            await gkp.finish("唔……只有团长才能操作GKP哦~")
    all = data[1]
    ones = data[2]
    for i in now:
        if i["desc"] == desc:
            if len(i["gkp"]) == 2:
                i["gkp"].clear()
            i["gkp"].append(all)
            i["gkp"].append(ones)
            write(final_path, json.dumps(now, ensure_ascii = False))
            ones = int(ones)
            if ones < 2000:
                msg = "这也太黑了！"
            elif 2000 <= ones < 4000:
                msg = "好像有点黑？"
            elif 4000 <= ones < 8000:
                msg = "一般一般。"
            elif 8000 <= ones < 13000:
                msg = "好像有点红~"
            elif 13000 <= ones:
                msg = "发财啦！"
            await gkp.finish(msg)
    await gkp.finish("唔……没有找到，请检查团队描述是否一致~")

special = on_command("special_item",aliases = {"特殊"}, priority = 5)
@special.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    now = json.loads(read(final_path))
    if len(data) < 2:
        await special.finish("参数不对哦！至少有2个参数，具体请查看帮助文件~")
    for i in now:
        if i["desc"] == desc and i["leader"] != str(event.user_id):
            await gkp.finish("唔……只有团长才能操作GKP哦~")
    desc = data[0]
    data.remove(desc)
    special_ = data
    for i in now:
        if i["desc"] == desc:
            i["special"].clear()
            for a in special_:
                i["special"].append(a)
            write(final_path, json.dumps(now, ensure_ascii = False))
            await special.finish("已保存该团的特殊掉落记录！")
    await special.finish("唔……没有找到，请检查团队描述是否一致~")

close_ = on_command("closegroup",aliases={"结算"}, priority = 5)
@close_.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text()
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    now = json.loads(read(final_path))
    for i in now:
        if i["desc"] == data and i["leader"] != str(event.user_id):
            await close_.finish("唔……只有团长才能操作GKP哦~")
    msg = ""
    archived = False
    for i in now:
        if i["desc"] == data:
            all = i["gkp"][0]
            one = i["gkp"][1]
            time_ = i["time"]
            leader = i["leader"]
            leader_data = await bot.call_api("get_group_member_info", group_id = event.group_id, user_id = int(leader))
            leader_name = leader_data["card"]
            if leader_name == "":
                leader_name = leader_data["nickname"]
            msg = f"{leader_name}的团队（{data}），记录如下：\n总金团：{all}金，人均工资：{one}金\n开团时间：" + convert_time(time_) + "\n特殊掉落："
            for a in i["special"]:
                msg = msg + a + "、"
            archive = {"leader":leader, "leadername": leader_name, "desc":data, "time": time_, "special": i["special"], "gkp": i["gkp"]}
            old = i
            archive_now = json.loads(read(DATA + "/" + str(event.group_id) + "/record.json"))
            archive_now.append(archive)
            write(DATA + "/" + str(event.group_id) + "/record.json", json.dumps(archive_now, ensure_ascii = False))
            archived = True
            msg = msg[:-1]
            break
    if archived:
        now.remove(old)
        write(final_path, json.dumps(now, ensure_ascii = False))
        await close_.finish(msg)
    else:
        await close_.finish("唔……没有找到，请检查团队描述是否一致~")

get_gkp = on_command("get_gkp", aliases = {"金团记录"}, priority = 5)
@get_gkp.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    qq = args.extract_plain_text()
    if checknumber(qq):
        final_path = DATA + "/" + str(event.group_id) + "/record.json"
        data = json.loads(read(final_path))
        times = 0
        pays = []
        desc = []
        time__ = []
        for i in data:
            if i["leader"] == qq:
                leader = i["leadername"]
                times = times + 1
                pays.append(i["gkp"][1])
                desc.append(i["desc"])
                time__.append(i["time"])
        msg = ""
        max = 0
        mean = np.mean(pays)
        for i in range(times):
            msg = f"\n{i}.{desc[i]}({convert_time(time__[i])})：工资{pays[i]}金；"
            max = max + 1
            if max == 9:
                break
        msg = f"{leader}共开团{times}次，平均{mean}金：" + msg[:-1] + "。"
        await get_gkp.finish(msg)
    else:
        await get_gkp.finish("请使用纯数字的QQ哦~")

opening = on_command("opening", aliases = {"团列表"}, priority = 5)
@opening.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    localdata = json.loads(read(final_path))
    msg = ""
    count = 0
    for i in localdata:
        desc = i["desc"]
        time = convert_time(i["time"])
        leaderqq = int(i["leader"])
        leader_data = await bot.call_api("get_group_member_info", group_id = event.group_id, user_id = leaderqq)
        leader = leader_data["card"]
        if leader == "":
            leader = leader_data["nickname"]
        people_count = len(i["book"])
        msg = msg + f"{leader}的团队：{desc}（已有{people_count}人申请）\n开团时间：{time}\n"
        if count == 9:
            msg = msg[:-1]
            break
        else:
            continue
    if msg:
        await opening.finish(msg)
    else:
        await opening.finish("唔……没有找到任何团哦~")

modify = on_command("modify", aliases = {"修改"}, priority = 5)
@modify.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    if len(data) != 2:
        await modify.finish("参数不对哦！应该有2个参数，具体请查看帮助文件~")
    old = data[0]
    new = data[1]
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    data = json.loads(read(final_path))
    for i in data:
        if i["desc"] == old:
            i["desc"] = new
            write(final_path, json.dumps(data, ensure_ascii = False))
            await modify.finish("修改团队信息成功！")
    await modify.finish("唔……没有找到，请检查团队描述是否一致~")