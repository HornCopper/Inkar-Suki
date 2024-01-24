from src.tools.dep import *
from nonebot.message import event_preprocessor

dev_global_command_record: dict[str, str] = filebase_database.Database(
    f'{bot_path.common_data_full}global_command_record'
).value


@event_preprocessor
async def dev_command_mapper(event: GroupMessageEvent):
    raw_command = event.message.extract_plain_text()
    new_command = raw_command

    visited = {}
    max_level = 10
    while max_level > 0:
        max_level -= 1
        round_command = new_command

        # TODO 暂不实现 # 映射个人命令
        # grp_config = GroupUserConfig(event.group_id, log=False)
        # if tmp := run_mapper(grp_config.mgr_property('command_map'), new_command):
        #     new_command = tmp

        # 映射本群命令
        grp_config = GroupConfig(event.group_id, log=False)
        if tmp := CommandMapper(grp_config.mgr_property('command_map')).convert(new_command):
            new_command = tmp

        # 映射全局命令
        if tmp := CommandMapper(dev_global_command_record).convert(new_command):
            new_command = tmp

        if new_command == round_command:
            break
        if visited.get(new_command):
            break
        visited[new_command] = True
        
    if new_command == raw_command:
        return
    logger.debug(f'map [{raw_command}] to new msg:{new_command}')
    event.message = obMessage(new_command)

dev_cmd_mgr_command_map = on_command(
    "mgr_command_map",
    name="设置映射",
    aliases={'设置映射'},
    priority=5,
    description='设置命令的映射关系',
    catalog=permission.bot.command.mapper,
    example=[
        Jx3Arg(Jx3ArgsType.command),
        Jx3Arg(Jx3ArgsType.command, default=None, alias='新命令'),
        Jx3Arg(Jx3ArgsType.group_id, default=None, alias='群号'),
        Jx3Arg(Jx3ArgsType.bool, default=False, alias='是否全局'),
    ],
    document='''将某个存在或者不存在的命令，通过映射，变成一个其他命令。
    额外附加的参数使用`-`来分割。
    例如 设置映射 小药 接引人-小药。
    这样，再发[小药]就等价发了[接引人 小药]。
    也可以加上参数，用[$参数名]表示
    例如：设置映射 PVE-$kunfu 配装-$kunfu-PVE。
    这样，再发[配装 pve 刀宗]等价于发了[配装 刀宗 pve]
    '''
)


@dev_cmd_mgr_command_map.handle()
async def dev_mgr_command_map(bot: Bot, event: GroupMessageEvent, args=Depends(Jx3Arg.arg_factory)):
    arg_prev_cmd, arg_new_cmd, arg_grp, arg_glo = args

    async def complete(target_map: dict, action: str):
        if arg_new_cmd is None:
            action = f'移除{action}'
            if arg_prev_cmd in target_map:
                del target_map[arg_prev_cmd]
            else:
                action = f'{action}(本就不存在)'
        else:
            action = f'更新{action}'
            target_map[arg_prev_cmd] = arg_new_cmd

        msg = f'已{action}命令映射：{arg_prev_cmd} -> {arg_new_cmd}'
        logger.debug(msg)
        CommandMapper(target_map).flush()
        return await dev_cmd_mgr_command_map.send(msg)

    permission = Permission(event.user_id).judge(10, '命令主映射')
    if arg_glo:
        if not permission.success:
            return await dev_cmd_mgr_command_map.finish(permission.description)

        return await complete(dev_global_command_record, '全局')

    # 此处导致无法应用单元测试
    personal_data = await bot.call_api("get_group_member_info", group_id=arg_grp, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]

    if not permission.success and not group_admin:
        return await dev_cmd_mgr_command_map.finish(PROMPT_NoPermissionAdmin)

    grp_config = GroupConfig(arg_grp).mgr_property('command_map')
    return await complete(grp_config, f'群{arg_grp}')


dev_cmd_query_command_map = on_command(
    "query_command_map",
    name="查看映射",
    aliases={'查看映射'},
    priority=5,
    description='查看命令的映射关系',
    catalog=permission.bot.command.mapper,
    example=[
        Jx3Arg(Jx3ArgsType.command),
        Jx3Arg(Jx3ArgsType.group_id, default=None, alias='群号'),
        Jx3Arg(Jx3ArgsType.pageIndex, default=0),
    ],
    document='''查看一个关键词相关的映射
    '''
)


@dev_cmd_query_command_map.handle()
async def dev_query_command_map(event: GroupMessageEvent, args=Depends(Jx3Arg.arg_factory)):
    arg_cmd, arg_grp, arg_page = args

    configs = [
        [GroupConfig(arg_grp).mgr_property('command_map'), '群映射'],
        [dev_global_command_record, '全局映射'],
    ]

    result_from = []
    result_to = []
    for config in configs:
        config_data, desc = config
        for cmd in config_data:
            if arg_cmd in cmd:
                result_from.append([cmd, config_data[cmd], desc])
                continue

            value = config_data.get(cmd)
            if not value:
                continue
            if arg_cmd in value:
                result_to.append([cmd, config_data[cmd], desc])

    result = result_from + result_to
    pageSize = 20
    headers = [
        {'name': 'prev_cmd', 'label': '原命令'},
        {'name': 'cur_cmd', 'label': '新命令'},
        {'name': 'region', 'label': '作用域'},
    ]
    start = arg_page * pageSize
    paged_result = result[start:start+pageSize]
    values = [{
        'prev_cmd': x[0],
        'cur_cmd':x[1],
        'region':x[2],
    } for x in paged_result]

    data = {
        'title': f'查看映射 · {arg_cmd}',
        'items': values,
        'headers': headers,
        'docs_tips': [
            {'label': '区分群作用域和全局作用域'},
            {'label': '根据关键词是否在映射中进行搜索'},
        ],
        'docs_usages': [
            {'title': '查看映射', 'label': '查看映射 关键词 [群号] [页码]'}
        ],
        'page': {
            'pageIndex': arg_page,
            'pageSize': pageSize,
            'totalCount': len(result),
        }
    }
    img = await get_render_image(f"src/views/common/list-view.html", data, delay=200)
    return await dev_cmd_query_command_map.send(ms.image(Path(img).as_uri()))
