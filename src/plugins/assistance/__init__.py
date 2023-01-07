import nonebot
import json
import sys
import time

from nonebot.typing import T_State
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Event
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
import numpy as np
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"
from config import Config
from file import read, write
from utils import convert_time, checknumber, get_api
from permission import checker, error

proxy = Config.proxy
if proxy != None:
    proxies = {
        "http://": proxy,
        "https://": proxy
     }
else:
    proxies = None

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
        if i["desc"] == data[0]:
            if i["leader"] != str(event.user_id):
                await special.finish("唔……只有团长才能操作GKP哦~")
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

get_gkp = on_command("get_gkp", aliases = {"团长"}, priority = 5)
@get_gkp.handle()
async def _(state: T_State, bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    qq = args.extract_plain_text()
    if checknumber(qq):
        final_path = DATA + "/" + str(event.group_id) + "/record.json"
        data = json.loads(read(final_path))
        data.reverse()
        times = 0
        max = 0
        gkp = []
        pays = []
        special_ = []
        desc = []
        time__ = []
        for i in data:
            if i["leader"] == qq:
                leader = i["leadername"]
                times = times + 1
                if max <= 10:
                    special_.append("、".join(i["special"]))
                    gkp.append(int(i["gkp"][0]))
                    pays.append(int(i["gkp"][1]))
                    desc.append(i["desc"])
                    time__.append(i["time"])
                max = max + 1
        msg = ""
        max = 0
        mean = np.mean(pays)
        mean = round(mean, 2)
        for i in range(times):
            msg = msg + f"\n{i}.{desc[i]}({convert_time(time__[i])})：工资{pays[i]}金；"
            max = max + 1
            if max == 10:
                break
        try:
            state["leader"] = leader
            state["time"] = time__
            state["desc"] = desc
            state["pays"] = pays
            state["gkp"] = gkp
            state["special"] = special_
            msg = f"{leader}共开团{times}次，平均{mean}金：" + msg[:-1] + "。"
        except UnboundLocalError:
            msg = "没有查到这位团长的开团记录哦~"
        await get_gkp.send(msg)
        return
    else:
        await get_gkp.finish("请使用纯数字的QQ哦~")
        
@get_gkp.got("num", prompt = "发送序号可以获取该次的详细信息，其他内容则无视。")
async def _(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num) == False:
        return
    num = int(num)
    if num not in [0,1,2,3,4,5,6,7,8,9]:
        await get_gkp.finish("只能查找最近10次的记录哦~")
    else:
        leader = state["leader"]
        time__ = state["time"]
        desc = state["desc"]
        pays = state["pays"]
        gkp = state["gkp"]
        special_ = state["special"]
        msg = f"团长：{leader}\n团队描述：{desc[num]}\n开团时间：{convert_time(time__[num])}\n总金团：{gkp[num]}金，人均工资：{pays[num]}金\n特殊掉落：{special_[num]}"
        await get_gkp.finish(msg)

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

cancel = on_command("jx3_cancel", aliases={"取消开团"}, priority=5)
@cancel.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    name = args.extract_plain_text()
    final_path = DATA + "/" + str(event.group_id) + "/opening.json"
    data = json.loads(read(final_path))
    for i in data:
        if i["desc"] == name:
            data.remove(i)
            write(final_path, json.dumps(data,ensure_ascii=True))
            await cancel.finish("删除成功！")
    await cancel.finish("唔……没有找到该团队描述对应的团哦~")

set_group = on_command("jx3_auto", aliases={"认证"}, priority=5)
@set_group.handle()
async def _(state: T_State, bot: Bot, event: GroupMessageEvent):
    leader = str(event.user_id)
    leader_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id)
    leader_role = leader_data["role"]
    if leader_role != "owner":
        await set_group.finish("唔，抱歉，只有群主可以认证团长哦，若欲申请副团长，请联系团长发送“+副团长 +[副团长QQ]”。\n（QQ号前面的“+”或“-”不可以省略哦~）")
    else:
        role = "群主"
    group_data = await bot.call_api("get_group_info", group_id=event.group_id)
    group_name = group_data["group_name"]
    correct = json.loads(read(DATA + "/" + str(event.group_id) + "/jx3group.json"))
    if correct["status"] == True:
        await set_group.finish("本群已经认证过啦，请不要重复认证哦~")
    if group_name[0] != "【":
        await set_group.finish("群名称不正确哦，请修改为“【团牌】任意文字”的格式！")
    else:
        rest_string = group_name[1:]
        other_side = rest_string.find("】")
        if other_side == -1:
            await set_group.finish("群名称不正确哦，请修改为“【团牌】任意文字”的格式！")
        final_name = rest_string[0:other_side]
    await set_group.send(f"整理出以下信息：\n团牌：{final_name}\n团长QQ号：{leader}\n申请人权限：{role}\n申请类别：群认证 + 主团长认证")
    cache = [final_name, leader, role, str(event.group_id)] # 团牌 团长QQ 申请人权限
    state["data"] = cache
    return

@set_group.got("server", prompt="请核对信息，若无误，请发送本团所处的服务器（请发送主服名称，例如发送“幽月轮”而不是“千岛湖”）。")
async def _(state: T_State, server: Message = Arg()):
    server = server.extract_plain_text()
    server_info = await get_api("https://www.jx3api.com/data/server/status?server=" + server, proxy = proxies)
    if server_info["code"] == 401:
        await set_group.finish("认证失败，错误的服务器！")
    cache = state["data"]
    group_name = cache[0]
    leader = cache[1]
    group_id = cache[3]
    now = json.loads(read(DATA + "/" + group_id + "/jx3group.json"))
    now["group"] = group_id
    now["server"] = server
    now["leader"] = leader
    now["name"] = group_name
    now["status"] = False
    write(DATA + "/" + group_id + "/jx3group.json", json.dumps(now, ensure_ascii=False))
    await set_group.finish("已提交认证，请等待机器人管理员通过！")

add_leader = on_command("jx3_helper", aliases = {"副团长"}, priority=5)
@add_leader.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    helper = args.extract_plain_text()
    if helper[0] not in ["+","-"]:
        await add_leader.finish("副团长QQ号前要加一个“+”或“-”来区分增加或移除哦~")
    if helper[0] == "+":
        action = True # 增加
        helper = helper[1:]
    else:
        action = False # 删除
        helper = helper[1:]
    if checknumber(helper) == False:
        await add_leader.finish("添加失败，QQ号非纯数字。")
    helper_data = await bot.call_api("get_group_member_info", group_id = event.group_id, user_id = int(helper))
    if helper_data["role"] != "admin":
        await add_leader.finish("唔……副团长需要是管理员哦~")
    group_data = json.loads(read(DATA + "/" + str(event.group_id) + "/jx3group.json"))
    if str(event.user_id) != group_data["leader"]:
        await add_leader.finish("唔，只有团长能增加或减少副团长哦~")
    else:
        if helper in group_data["leaders"] and action:
            await add_leader.finish("该副团长已存在哦~")
        if helper not in group_data["leaders"] and action == False:
            await add_leader.finish("该用户尚非副团长哦~")
        if action:
            group_data["leaders"].append(helper)
        else:
            group_data["leaders"].remove(helper)
        write(DATA + "/" + str(event.group_id) + "/jx3group.json", json.dumps(group_data, ensure_ascii=False))
        action_msg = "添加" if action else "移除"
        await add_leader.finish(f"副团长{action_msg}成功")

verify_group = on_command("jx3_verify", aliases={"验证团"}, priority=5)
@verify_group.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),10) == False:
        await verify_group.finish(error(10))
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await verify_group.finish("唔，参数数量不对哦~")
    else:
        name = arg[0]
        group = arg[1]
        data = json.loads(read(DATA + "/" + group + "/jx3group.json"))
        if data == False:
            await verify_group.finish("验证失败，该群尚未加入哦~")
        if data["status"] == True:
            await verify_group.finish("验证失败，该群已认证过了哦~")
        if data["leader"] == "":
            await verify_group.finish("验证失败，该群尚未提交认证~")
        if data["name"] != name:
            await verify_group.finish(f"验证失败，该群的团牌并非“{name}”。")
        await bot.call_api("send_group_msg", group_id = int(group), message = f"团牌【{name}】（{group}）验证已通过！\n操作人：{str(event.user_id)}")
        data["status"] = True
        write(DATA + "/" + group + "/jx3group.json",json.dumps(data, ensure_ascii=False))
        await verify_group.finish("验证通过！")

from fastapi import FastAPI, Request
app: FastAPI = nonebot.get_app()

@app.post("/auth") # 该项用于`assistance`，为方便写代码，放置于此
async def recAuth(req: Request):
    headers = req.headers
    if headers["user"] not in Config.owner:
        return {"status":403}
    else:
        final = []
        groups = os.listdir(DATA)
        for i in groups:
            group_data = json.loads(read(DATA + "/" + i + "/jx3group.json"))
            try:
                if headers["type"] == "all":
                    if group_data["leader"] != "":    
                        name = group_data["name"]
                        owner = group_data["leader"]
                        group = group_data["group"]
                        server = group_data["server"]
                        dict_ = {"name":name,"leader":owner,"group":group,"server":server}
                        final.append(dict_)
                else:
                    if group_data["leader"] != "":
                        if group_data["status"] != False:
                            name = group_data["name"]
                            owner = group_data["leader"]
                            group = group_data["group"]
                            server = group_data["server"]
                            dict_ = {"name":name,"leader":owner,"group":group,"server":server}
                            final.append(dict_)
            except:
                return {"status":502}
        return final
