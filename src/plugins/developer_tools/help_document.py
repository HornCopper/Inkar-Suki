from src.tools.dep import *


dev_cmd_show_help = on_command(
    "show_help",
    aliases={
        "帮助", "功能", "文档", "说明", "怎么用", "使用说明",
        "菜单", "开关", "授权", "咋用", "方法", "教程",
    },
    priority=5,
    description='获取当前公开的命令文档',
    catalog=permission.bot.docs.help,
    example=[
        Jx3Arg(Jx3ArgsType.pageIndex, is_optional=True, default=1),
        Jx3Arg(Jx3ArgsType.command, is_optional=True),
    ],
    document='''帮助文档'''
)


async def get_group_config(bot: Bot, group_id: str):
    group_config = GroupConfig(group_id)
    auth_start = DateTime(group_config.mgr_property('auth.start'))
    year = DateTime().year
    month = '06' if DateTime().month > 6 else '01'

    story_end: DateTime = DateTime(f'{year+1}-{month}-01')

    story_left = int((story_end - DateTime()).total_seconds() / 86400)
    story_length = int((DateTime() - auth_start).total_seconds() / 86400)
    labels = [
        {'content': f'群号：{group_id}'},
        {'content': f'机器人：{bot.self_id if bot else None}'},
        {'content': f'故事开始已：{story_length}天'},
        {'content': f'绑定区服：{group_config.mgr_property("server")}'},
        {'element': 'el-divider', 'style': 'margin:0.5rem'},
        {'content': f'SVIP 剩余{story_left}天', 'style': 'color:#ed9b00'},
        {'content': '群属性：', 'element': 'span'},
        {'content': '限时免费', 'element': 'el-tag'},
    ]

    group_info = {'name': '未知的群名'}
    if bot:
        group_info = await bot.get_group_info(group_id=int(group_id))

    return {
        'name': group_info.get('name'),
        'labels': labels
    }


@dev_cmd_show_help.handle()
async def dev_show_help(bot: Bot, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    group_id = str(event.group_id)

    pageIndex, command = args
    data = DocumentGenerator.get_documents()

    global_status = CommandRecord.get_db().value
    group_status = CommandRecord.get_db(event.group_id).value

    group_config = await get_group_config(bot, group_id)
    content = {
        'item_name': command,
        'pageIndex': pageIndex,
        'global_status': global_status,
        'group_status': group_status,
        'group_config': group_config
    }
    data.update(content)

    template = 'document-detail' if command else 'documents'
    img = await get_render_image(f"src/views/common/{template}.html", data, delay=200)
    return await dev_cmd_show_help.send(ms.image(Path(img).as_uri()))
