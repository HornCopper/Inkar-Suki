from src.tools.permission import checker, error

from .manage import *

error_already_binded = "您已经绑定过该角色了，您可以进行“验证角色”或“解绑角色”操作~"
error_argument_count = "该命令需要2个参数，分别是服务器、角色名，并且不能省略服务器名称！"
error_not_found = "未找到该角色！"
error_not_binded = "尚未绑定该角色！\n请先发送“绑定角色 服务器 角色名”后按照指示操作！"
error_already_verified = "该角色已绑定且已验证您的所有权！"
error_delete_but_not_binded = "尚未绑定此角色！"

bind_role = on_command("jx3_bindrole", aliases={"绑定角色"}, priority=5)

@bind_role.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await bind_role.finish(error_argument_count)
    srv = arg[0]
    id = arg[1]
    if checkWtrIn(srv, id, str(event.user_id)):
        await bind_role.finish(error_already_binded)
    else:
        uuid = get_uuid()
        sts = await addRole(srv, id, str(event.user_id), uuid)
        if sts == 1:
            await bind_role.finish(f"({srv})[{id}]绑定成功！\n请将该角色推栏账号的签名改为以下内容：\n{uuid}\n“验证角色”通过后即可改回来哦~")
        elif sts == 2:
            await bind_role.finish(error_already_binded)
        elif sts == 0:
            await bind_role.finish(error_not_found)

verify = on_command("jx3_verifyrole", aliases={"验证角色"}, priority=5)

@verify.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await verify.finish(error_argument_count)
    srv = arg[0]
    id = arg[1]
    if checkWtrIn(srv, id, str(event.user_id)) == False:
        await verify.finish(error_not_binded)
    if checkVerify(srv, id, str(event.user_id)):
        await verify.finish(error_already_verified)
    data = getData(srv, id, str(event.user_id))
    pid = data["personId"]
    uuid = data["verify"]
    sts = await check_sign(pid, uuid, False)
    if sts == False:
        await verify.finish("验证失败！该角色的签名与预留的字符串不符合！")
    else:
        passVerify(srv, id, str(event.user_id))
        await verify.finish(f"({srv})[{id}]绑定成功！")

delete = on_command("jx3_deleterole", aliases={"解绑角色"}, priority=5)

@delete.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await delete.finish(error_argument_count)
    srv = arg[0]
    id = arg[1]
    if checkWtrIn(srv, id, str(event.user_id)) == False:
        await delete.finish(error_delete_but_not_binded)
    else:
        delRole(srv, id, str(event.user_id))
        await delete.finish("解绑成功！重新绑定需要再次验证哦~")

listrole = on_command("jx3_listrole", aliases={"角色列表"}, priority=5)

@listrole.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    ans = getRoleList(str(event.user_id))
    if ans in [-1,0]:
        await listrole.finish("您没有绑定任何角色哦~")
    else:
        await listrole.finish("您绑定了以下角色：\n" + "\n".join(ans))

location = on_command("jx3_iplocation", aliases={"属地查询"}, priority=5)

@location.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await location.finish(error(10))
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await bind_role.finish(error_argument_count)
    srv = arg[0]
    id = arg[1]
    pd = await getPersonInfo(srv, id)
    if pd == False:
        await location.finish("没有找到玩家信息！")
    pid = pd["personId"]
    data = await check_sign(pid, "", location = True)
    await location.finish("该玩家的IP属地为：" + data)