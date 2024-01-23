from src.tools.dep import *


global_cmd_flush_database = on_command(
    'flush_database',
    example=[
        Jx3Arg(Jx3ArgsType.bool, default=False, alias='丢弃内存')
    ]
)


@global_cmd_flush_database.handle()
async def global_flush_database(event: GroupMessageEvent, args=Depends(Jx3Arg.arg_factory)):
    arg_drop, = args
    x = Permission(event.user_id).judge(10, '查询和更新配置')
    if not x.success:
        return await global_cmd_update_grp_config.finish(x.description)
    total = filebase_database.Database.cache
    if arg_drop:
        filebase_database.Database.cache = {}
        msg = '已丢弃内存，即将重启'
        await global_cmd_flush_database.send(msg)
        with open("./src/plugins/developer_tools/example.py", mode="w") as cache:
            cache.write("status=\"OK\"")
        return

    filebase_database.Database.save_all()
    msg = f'已完成更新,此次可能更新配置项:{len(list(total))}条'
    return await global_cmd_flush_database.send(msg)

global_cmd_update_grp_config = on_command(
    'update_grp_config',
    example=[
        Jx3Arg(Jx3ArgsType.group_id),
        Jx3Arg(Jx3ArgsType.string, alias='配置路径'),
        Jx3Arg(Jx3ArgsType.string, alias='配置值', default='VIEW'),
    ]
)


@global_cmd_update_grp_config.handle()
async def global_update_grp_config(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_group, arg_path, arg_value = args
    msg = await _update_grp_config(arg_path, arg_value, event.user_id, arg_group)
    return await global_cmd_update_grp_config.send(msg)

global_cmd_update_usr_config = on_command(
    'update_usr_config',
    example=[
        Jx3Arg(Jx3ArgsType.group_id),
        Jx3Arg(Jx3ArgsType.string, alias='配置路径'),
        Jx3Arg(Jx3ArgsType.string, alias='配置值', default='VIEW'),
    ]
)


@global_cmd_update_usr_config.handle()
async def global_update_usr_config(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_group, arg_path, arg_value = args
    msg = await _update_grp_config(arg_path, arg_value, event.user_id, None, arg_group)
    return await global_cmd_update_usr_config.send(msg)


async def _update_grp_config(arg_path, arg_value, user_id, arg_group=None, arg_user=None):
    x = Permission(user_id).judge(10, '查询和更新配置')
    if not x.success:
        return x.description  # TODO 全局检测返回类型并进行动作
    new_val = Ellipsis if arg_value == 'VIEW' else arg_value

    gc = GroupConfig(arg_group) if arg_group else GroupUserConfig(arg_user)
    try:
        result = gc.mgr_property(arg_path, new_val)
    except Exception as ex:
        result = f'更新失败:{ex}'
    update_path = gc._db.database_filename
    db_instance = hex(id(gc._db.data_obj) & 0xffffffff)[2:]
    update_result = f'已管理更新{db_instance}@{arg_path}\nnew_value={new_val},result=\n{result}'
    msg = f'{update_path}\n{update_result}'
    return msg
