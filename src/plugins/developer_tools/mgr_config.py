from src.tools.dep import *


global_cmd_flush_database = on_command(
    "flush_data",
    example=[
        Jx3Arg(Jx3ArgsType.bool, default=False, alias="重启")
    ]
)

@global_cmd_flush_database.handle()
async def global_flush_database(event: GroupMessageEvent, args=Depends(Jx3Arg.arg_factory)):
    arg_drop, = args
    if checker(str(event.user_id), 10) == False:
        await global_cmd_flush_database.finish(error(10))
    total = filebase_database.Database.cache
    if arg_drop:
        filebase_database.Database.cache = {}
        msg = "好的！音卡刷新自身数据！准备重启啦~"
        await global_cmd_flush_database.send(msg)
        with open("./src/plugins/developer_tools/example.py", mode="w") as cache:
            cache.write("status=\"OK\"")
        return
    filebase_database.Database.save_all()
    msg = f"音卡已经刷新自己的数据啦，本次共更新了{len(list(total))}条新配置~"
    return await global_cmd_flush_database.send(msg)

global_cmd_update_grp_config = on_command(
    "update_grp_config",
    example=[
        Jx3Arg(Jx3ArgsType.group_id),
        Jx3Arg(Jx3ArgsType.string, alias="配置路径"),
        Jx3Arg(Jx3ArgsType.string, alias="配置值", default="VIEW")
    ]
)

@global_cmd_update_grp_config.handle()
async def global_update_grp_config(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_group, arg_path, arg_value = args
    msg = await _update_grp_config(arg_path, arg_value, event.user_id, arg_group)
    return await global_cmd_update_grp_config.send(msg)

global_cmd_update_usr_config = on_command(
    "update_usr_config",
    example=[
        Jx3Arg(Jx3ArgsType.group_id),
        Jx3Arg(Jx3ArgsType.string, alias="配置路径"),
        Jx3Arg(Jx3ArgsType.string, alias="配置值", default="VIEW")
    ]
)

@global_cmd_update_usr_config.handle()
async def global_update_usr_config(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_group, arg_path, arg_value = args
    msg = await _update_grp_config(arg_path, arg_value, event.user_id, None, arg_group)
    return await global_cmd_update_usr_config.send(msg)

async def _update_grp_config(arg_path, arg_value, user_id, arg_group=None, arg_user=None):
    if checker(str(user_id), 10) == False:
        return error(10)
    new_val = Ellipsis if arg_value == "VIEW" else arg_value

    gc = GroupConfig(arg_group) if arg_group else GroupUserConfig(arg_user)
    try:
        result = gc.mgr_property(arg_path, new_val)
    except Exception as ex:
        result = f"唔……音卡更新失败了，已捕捉报错：\n{ex}"
    update_path = gc._db.database_filename
    db_instance = hex(id(gc._db.data_obj) & 0xffffffff)[2:]
    update_result = f"音卡更新了自身数据：\n{db_instance}@{arg_path}\nnew_value={new_val},result=\n{result}"
    msg = f"{update_path}\n{update_result}"
    return msg
