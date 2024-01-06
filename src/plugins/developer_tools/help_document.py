from src.tools.dep import *

dev_cmd_show_help = on_command(
    "show_help",
    aliases={"帮助v2"},
    priority=5,
    description='获取当前公开的命令文档',
    catalog='permission.docs.help',
    example=[
        Jx3Arg(Jx3ArgsType.pageIndex, is_optional=True, default=1),
        Jx3Arg(Jx3ArgsType.command, is_optional=True),
    ],
    document='''新的帮助文档'''
)


@dev_cmd_show_help.handle()
async def dev_show_help(event: Event, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    pageIndex, command = args
    data = DocumentGenerator.get_documents()
    data['item_name'] = command
    data['pageIndex'] = pageIndex

    template = 'document-detail' if command else 'documents'
    img = await get_render_image(f"src/views/common/{template}.html", data, delay=200)
    return await dev_cmd_show_help.send(ms.image(Path(img).as_uri()))
