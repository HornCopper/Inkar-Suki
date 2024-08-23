from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageEvent, Bot
from nonebot.params import CommandArg

from src.tools.permission import checker, error, get_all_admin
from src.tools.config import Config
from src.tools.utils.common import checknumber
from src.tools.data import group_db

# 机器人管理员权限设置
op = on_command("setop", aliases={"admin", "setadmin"}, force_whitespace=True, priority=5)


@op.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10) and str(event.user_id) not in Config.bot_basic.bot_owner:
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
            admin_data = get_all_admin()
            admin_list = admin_data.permissions_list
            if arguments[0] in Config.bot_basic.bot_owner and str(event.user_id) not in Config.bot_basic.bot_owner:
                await op.finish("哈哈你改不了主人的权限的啦！")
            if arguments[1] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                await op.finish("你这设置的什么鬼权限啊？！")
            if arguments[1] == "10" and str(event.user_id) not in Config.bot_basic.bot_owner:
                await op.finish("这么高的权限还是请后台修改吧。")
            if arguments[0] in admin_list:
                if arguments[1] == "0":
                    admin_list.pop(arguments[0])
                    msg = f"管理员账号({arguments[0]})已经被我撤了哦~"
                else:
                    msg = f"管理员账号({arguments[0]})已经有了，本来是{str(admin_list[arguments[0]])}，已经被我改成{str(arguments[1])}了哦~"
                    admin_list[arguments[0]] = int(arguments[1])
            else:
                admin_list[arguments[0]] = int(arguments[1])
                msg = f"已经帮你添加管理员账号({arguments[0]})及权限等级{str(arguments[1])}了哦~。"
            admin_data.permissions_list = admin_list
            group_db.save(admin_data)
            await op.finish(msg)

    else:
        await op.finish("您输入了什么？")