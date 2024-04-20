from src.tools.basic import *

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.params import CommandArg


# 机器人管理员权限设置
op = on_command("setop", aliases={"admin", "setadmin"}, priority=5)


@op.handle()
async def handle_first_receive(bot: Bot, event: Event, args: Message = CommandArg()):
    if not checker(str(event.user_id), 10):
        await op.finish(error(10))
    info = args.extract_plain_text()
    if info:
        try:
            arguments = info.split(" ")
        except:
            pass
        try:
            if not checknumber(str(arguments[0])) or not checknumber(str(arguments[1])):
                await op.finish("唔……QQ号和权限等级都必须是数字哦~")
        except:
            await op.finish("唔，你好像少了点参数。")
        else:
            adminlist = json.loads(read(TOOLS+"/permission.json"))
            if arguments[0] in Config.owner:
                await op.finish("哈哈你改不了主人的权限的啦！")
            if arguments[1] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                await op.finish("你这设置的什么鬼权限啊？！")
            if arguments[1] == "10" and str(event.user_id) not in Config.owner:
                await op.finish("这么高的权限还是请后台修改吧。")
            if arguments[0] in adminlist:
                if arguments[1] == "0":
                    adminlist.pop(arguments[0])
                    msg = f"管理员账号({arguments[0]})已经被我撤了哦~"
                else:
                    msg = f"管理员账号({arguments[0]})已经有了，本来是{str(adminlist[arguments[0]])}，已经被我改成{str(arguments[1])}了哦~"
                    adminlist[arguments[0]] = int(arguments[1])
            else:
                adminlist[arguments[0]] = int(arguments[1])
                msg = f"已经帮你添加管理员账号({arguments[0]})及权限等级{str(arguments[1])}了哦~。"
            write(TOOLS+"/permission.json", json.dumps(adminlist))
            await op.finish(msg)

    else:
        await op.finish("您输入了什么？")