from .api import *
from src.tools.dep import *
from src.tools.generate import *
from src.plugins.help import css
jx3_cmd_jx3_rare_gain = on_command(
    "jx3_rare_gain", aliases={"cd"}, priority=5)


@jx3_cmd_jx3_rare_gain.handle()
async def jx3_rare_gain(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取部分特殊物品的上次记录：

    Notice：数据来源@茗伊插件集 https://www.j3cx.com

    Example：-cd 幽月轮 归墟玄晶
    '''
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.default)]
    arg = get_args(args.extract_plain_text(), template)
    arg_server, arg_name = arg
    arg_server = server_mapping(arg_server, event.group_id)
    if not arg_name:
        return await jx3_cmd_jx3_rare_gain.finish('没有输入物品名称哦')
    msg = await get_cd(arg_server, arg_name)
    return await jx3_cmd_jx3_rare_gain.finish(msg)

jx3_cmd_xuanjing = on_command("jx3_xuanjing", aliases={"玄晶"}, priority=5)


@jx3_cmd_xuanjing.handle()
async def jx3_xuanjing(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    group_server = getGroupServer(str(event.group_id))
    if server == "":
        if group_server == False:
            return await jx3_cmd_xuanjing.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
    else:
        server = server
    dt = json.loads(read(ASSETS + "/jx3/xuanjing.json"))
    for i in dt:
        if i["server"] == server:
            if len(i["records"]) == 0:
                return await jx3_cmd_xuanjing.finish("唔……尚未检测到玄晶哦~")
            table = []
            table.append(["时间", "地图", "角色", "名称"])
            for x in i["records"]:
                table.append([x["time"], x["map"], x["role"], x["name"]])
            msg = str(tabulate(table, headers="firstrow", tablefmt="html"))
            table.clear()
            html = "<div style=\"font-family:Custom\">" + \
                msg.replace("$", "<br>") + "</div>" + css
            path = CACHE + "/" + get_uuid() + ".html"
            write(path, html)
            img = await generate(path, False, "table")
            if type(img) != type("sb"):
                return await jx3_cmd_xuanjing.finish("唔，图片生成失败了哦~请联系机器人管理员解决此问题，附带以下信息：\n" + img)
            return await jx3_cmd_xuanjing.finish(ms.image(Path(img).as_uri()))
