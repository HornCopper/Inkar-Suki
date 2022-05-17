import json, sys
import nonebot
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.params import CommandArg
from .marry import already_married
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from file import read, write

def checknumber(number):
    return number.isdecimal()

get_married = on_command("marry", priority=5)

@get_married.handle()
async def _(event: Event, args: Message = CommandArg()):
    husband = str(event.user_id)
    wife = args.extract_plain_text()
    if husband == wife:
        await get_married.finish("诶？不能自娱自乐啊！")
    if checknumber(wife) == True or wife == "3438531564":
        pass
    else:
        await get_married.finish("你在跟谁求婚啊喂？！")
    if already_married(husband):
        await get_married.finish("你已经求过婚了哦，不能再要了。")
    elif already_married(wife):
        await get_married.finish("可惜别人抢先求婚/结婚了，除非对方拒绝/离婚，否则您只能下次早点了。")
    else:
        newmarry = {"wife": wife, "husband": husband, "confirm": "No"}
        nowlist = json.loads(read(TOOLS+"/marry.json"))
        nowlist.append(newmarry)
        write(TOOLS+"/marry.json", json.dumps(nowlist))
        msg = ms.at(husband) + " 已收到！请提醒对方使用+comfirm_marry <你的QQ号>来同意哦，其他人都没办法抢哦~"
        await get_married.finish(msg)
        
comfirm_marry = on_command("confirm_marry",priority=5)

@comfirm_marry.handle()
async def __(event: Event, args: Message = CommandArg()):
    husband = args.extract_plain_text()
    wife = str(event.user_id)
    nowlist = json.loads(read(TOOLS+"/marry.json"))
    for i in nowlist:
        if i["wife"] == wife and i["husband"] == husband:
            if i["confirm"] == "Yes":
                await comfirm_marry.finish("不能再同意了哦，你们已经结婚了。")
            else:
                i["confirm"] = "Yes"
                write(TOOLS+"/marry.json", json.dumps(nowlist))
                await comfirm_marry.finish("恭喜" + ms.at(husband) + "和" + ms.at(wife) + "结婚！")
    await comfirm_marry.finish("你不能和他结婚，因为他还没有求婚呢！")

deny_marry = on_command("deny_marry",priority=5)

@deny_marry.handle()
async def ___(event: Event, args: Message = CommandArg()):
    husband = args.extract_plain_text()
    wife = str(event.user_id)
    nowlist = json.loads(read(TOOLS+"/marry.json"))
    for i in nowlist:
        if i["wife"] == wife and i["husband"] == husband:
            if i["confirm"] == "No":
                nowlist.remove(i)
                write(TOOLS+"/marry.json", json.dumps(nowlist))
                await deny_marry.finish(ms.at(husband) + " 你的求婚被拒绝了！")
            else:
                await deny_marry.finish("已经结婚了，不能拒绝求婚，请使用+leave_marry进行离婚，非常不推荐的哦！")
    await deny_marry.finish("你不能拒绝他的求婚，因为他还没向你求婚呢！")
    
leave_marry = on_command("leave_marry",priority=5)

@leave_marry.handle()
async def ____(event: Event):
    self_id = str(event.user_id)
    nowlist = json.loads(read(TOOLS+"/marry.json"))
    for i in nowlist:
        if i["wife"] == self_id or i["husband"] == self_id:
            if i["confirm"] == "Yes":
                nowlist.remove(i)
                write(TOOLS+"/marry.json", json.dumps(nowlist))
                await leave_marry.finish("你们离婚了！")
            else:
                await leave_marry.finish("你们不能离婚，因为尚未接受对方求婚！")
    await leave_marry.finish("你和他没有任何瓜葛，不可以离婚。")

marry = on_command("my_marry",priority=5)

@marry.handle()
async def _____(event: Event):
    self_id = str(event.user_id)
    nowlist = json.loads(read(TOOLS+"/marry.json"))
    role = ""
    another = ""
    for i in nowlist:
        if i["wife"] == self_id and i["confirm"] == "Yes":
            role = "老公"
            another = i["husband"]
        elif i["husband"] == self_id and i["confirm"] == "Yes":
            role = "老婆"
            another = i["wife"]
    if role:
        another_qq = int(another)
        info = await bot.call_api("get_stranger_info",user_id=another_qq)
        full_another = info["nickname"] + f"({another_qq})"
        msg = ms.at(self_id) + f" 你的{role}是{full_another}！"
    else:
        msg = ms.at(self_id) + " 没有查到呢，你应该还没结婚吧！"
    await marry.finish(msg)
