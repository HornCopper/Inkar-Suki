import json
import sys

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


gm = on_command("gm", aliases={"getmarry"}, priority=5)


@gm.handle()
async def _(event: Event, args: Message = CommandArg()):
    husband = str(event.user_id)
    wife = args.extract_plain_text()
    if husband == wife:
        await gm.finish("诶？不能自娱自乐啊！")
    if checknumber(wife) == True or wife == "3438531564":
        pass
    else:
        await gm.finish("你在跟谁求婚啊喂？！")
    if already_married(husband):
        await gm.finish("你已经求过婚了哦，不能再要了。")
    elif already_married(wife):
        await gm.finish("可惜别人抢先求婚/结婚了，除非对方拒绝/离婚，否则您只能下次早点了。")
    else:
        newmarry = {"wife": wife, "husband": husband, "confirm": "No"}
        nowlist = json.loads(read(TOOLS+"/marry.json"))
        nowlist.append(newmarry)
        write(TOOLS+"/marry.json", json.dumps(nowlist))
        msg = ms.at(husband) + " 已收到！请提醒对方使用+cm <你的QQ号>来同意哦，其他人都没办法抢哦~"
        await gm.finish(msg)
        
cm = on_command("confirmmarryapply",aliases={"cm","cmp"},priority=5)

@cm.handle()
async def __(event: Event, args: Message = CommandArg()):
    husband = args.extract_plain_text()
    wife = str(event.user_id)
    nowlist = json.loads(read(TOOLS+"/marry.json"))
    for i in nowlist:
        if i["wife"] == wife and i["husband"] == husband:
            if i["confirm"] == "Yes":
                await cm.finish("不能再同意了哦，你们已经结婚了。")
            else:
                i["confirm"] = "Yes"
                write(TOOLS+"/marry.json", json.dumps(nowlist))
                await cm.finish("恭喜" + ms.at(husband) + "和" + ms.at(wife) + "结婚！")
    await cm.finish("你不能和他结婚，因为他还没有求婚呢！")

dm = on_command("denymarryapply",aliases={"dm","dmp"},priority=5)

@dm.handle()
async def ___(event: Event, args: Message = CommandArg()):
    husband = args.extract_plain_text()
    wife = str(event.user_id)
    nowlist = json.loads(read(TOOLS+"/marry.json"))
    for i in nowlist:
        if i["wife"] == wife and i["husband"] == husband:
            if i["confirm"] == "No":
                nowlist.remove(i)
                write(TOOLS+"/marry.json", json.dumps(nowlist))
                await dm.finish(ms.at(husband) + " 你的求婚被拒绝了！")
            else:
                await dm.finish("已经结婚了，不能拒绝求婚，请使用+lm进行离婚，非常不推荐的哦！")
    await dm.finish("你不能拒绝他的求婚，因为他还没向你求婚呢！")
    
lm = on_command("leavemarry",aliases={"lm","delmarry"},priority=5)

@lm.handle()
async def ____(event: Event):
    self_id = str(event.user_id)
    nowlist = json.loads(read(TOOLS+"/marry.json"))
    for i in nowlist:
        if i["wife"] == self_id or i["husband"] == self_id:
            if i["confirm"] == "Yes":
                nowlist.remove(i)
                write(TOOLS+"/marry.json", json.dumps(nowlist))
                await lm.finish("你们离婚了！")
            else:
                await lm.finish("你们不能离婚，因为尚未接受对方求婚！")
    await lm.finish("你和他没有任何瓜葛，不可以离婚。")

m = on_command("marry",aliases={"老婆","我的老婆","老公","我的老公"},priority=5)

@m.handle()
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
    await m.finish(msg)
