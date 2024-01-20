from src.tools.dep import *
from nonebot.message import event_preprocessor

dev_global_command_record: dict[str, str] = filebase_database.Database(
    f'{bot_path.common_data_full}global_command_record'
).value


@event_preprocessor
async def dev_command_mapper(event: GroupMessageEvent):
    raw_command = event.message.extract_plain_text()
    new_command = raw_command

    # TODO 暂不实现 # 映射个人命令
    # grp_config = GroupUserConfig(event.group_id, log=False)
    # if tmp := run_mapper(grp_config.mgr_property('command_map'), new_command):
    #     new_command = tmp

    if new_command == raw_command:
        # 映射本群命令
        grp_config = GroupConfig(event.group_id, log=False)
        if tmp := CommandMapper(grp_config.mgr_property('command_map')).convert(new_command):
            new_command = tmp

    if new_command == raw_command:
        # 映射全局命令
        if tmp := CommandMapper(dev_global_command_record).convert(new_command):
            new_command = tmp

    if new_command == raw_command:
        return

    logger.debug(f'map [{raw_command}] to new msg:{new_command}')
    event.message = obMessage(new_command)

# TODO 实现占位符
# #     命令占位符用`@`来表示
# #     例如 设置映射 配装-pve 配装-@-pve
#     这样，再发[配装 pve 刀宗]等价于发了[配装 刀宗 pve]
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
    额外附加的参数使用`-`来分割
    例如 设置映射 小药 接引人-小药
    这样，再发[小药]就等价发了[接引人 小药]


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

    if arg_grp is None:
        arg_grp = event.group_id

    # 此处导致无法应用单元测试
    personal_data = await bot.call_api("get_group_member_info", group_id=arg_grp, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]

    if not permission.success and not group_admin:
        return await dev_cmd_mgr_command_map.finish(PROMPT_NoPermissionAdmin)

    grp_config = GroupConfig(arg_grp).mgr_property('command_map')
    return await complete(grp_config, f'群{arg_grp}')
