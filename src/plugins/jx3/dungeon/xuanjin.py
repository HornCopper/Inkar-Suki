from .api import *
from src.tools.dep.bot import *
from src.tools.file import *
from src.tools.dep.path import *
from src.tools.generate import *
from src.plugins.help import css
mc_helper = on_command("jx3_cd", aliases={"cd"}, priority=5)
@mc_helper.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取部分特殊物品的上次记录：

    Notice：数据来源@茗伊插件集 https://www.j3cx.com

    Example：-cd 幽月轮 归墟玄晶
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await mc_helper.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await mc_helper.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        name = arg[0]
    elif len(arg) ==2:
        server = arg[0]
        name = arg[1]
    msg = await get_cd(server, name)
    await mc_helper.finish(msg)
    
xuanjing = on_command("jx3_xuanjing", aliases={"玄晶"}, priority=5)
@xuanjing.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    group_server = getGroupServer(str(event.group_id))
    if server == "":
        if group_server == False:
            await xuanjing.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
    else:
        server = server
    dt = json.loads(read(ASSETS + "/jx3/xuanjing.json"))
    for i in dt:
        if i["server"] == server:
            if len(i["records"]) == 0:
                await xuanjing.finish("唔……尚未检测到玄晶哦~")
            table = []
            table.append(["时间","地图","角色","名称"])
            for x in i["records"]:
                table.append([x["time"], x["map"], x["role"], x["name"]])
            msg = str(tabulate(table, headers="firstrow", tablefmt="html"))
            table.clear()
            html = "<div style=\"font-family:Custom\">" + msg.replace("$", "<br>") + "</div>" + css
            path = CACHE + "/" + get_uuid() + ".html"
            write(path, html)
            img = await generate(path, False, "table")
            if type(img) != type("sb"):
                await xuanjing.finish("唔，图片生成失败了哦~请联系机器人管理员解决此问题，附带以下信息：\n" + img)
            await xuanjing.finish(ms.image(Path(img).as_uri()))