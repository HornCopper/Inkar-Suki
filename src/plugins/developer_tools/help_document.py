from src.tools.dep import *

dev_cmd_show_help = on_command(
    "show_help",
    aliases={"帮助", "功能", "文档", "说明", "怎么用", "使用说明", "菜单", "开关", "授权"},
    priority=5,
    description='获取当前公开的命令文档',
    catalog='permission.docs.help',
    example=[
        Jx3Arg(Jx3ArgsType.pageIndex, is_optional=True, default=1),
        Jx3Arg(Jx3ArgsType.command, is_optional=True),
    ],
    document='''帮助文档'''
)


@dev_cmd_show_help.handle()
async def dev_show_help(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    pageIndex, command = args
    data = DocumentGenerator.get_documents()

    global_status = CommandRecord.get_db().value
    group_status = CommandRecord.get_db(event.group_id).value
    content = {
        'item_name': command,
        'pageIndex': pageIndex,
        'global_status': global_status,
        'group_status': group_status,
    }
    data.update(content)

    template = 'document-detail' if command else 'documents'
    img = await get_render_image(f"src/views/common/{template}.html", data, delay=200)
    return await dev_cmd_show_help.send(ms.image(Path(img).as_uri()))
