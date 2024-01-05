from src.tools.dep import *

dev_cmd_show_help = on_command(
    "show_help",
    aliases={"帮助v2"},
    priority=5,
    description='获取当前公开的命令文档',
    catalog='permission.docs.help',
    example=[
        Jx3Arg(Jx3ArgsType.command),
        Jx3Arg(Jx3ArgsType.pageIndex),
    ],
    document='''新的帮助文档'''
)


@dev_cmd_show_help.handle()
async def dev_show_help(event: Event, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    command, pageIndex = args
    data = DocumentGenerator.get_documents()
    data['command'] = command
    data['pageIndex'] = pageIndex

    img = await get_render_image("src/views/common/documents.html", data, delay=200)
    return await dev_cmd_show_help.send(ms.image(Path(img).as_uri()))
