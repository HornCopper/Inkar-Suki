from nonebot import get_driver

try:
    from .special_application import *  # 公共实例独有功能，闭源
except Exception as _:
    pass
from .jx3 import *

driver = get_driver()


@driver.on_startup
async def nonebot_on_startup():
    logger.info('nonebot_on_startup...')

    logger.debug("Connecting to JX3API...Please wait.")
    if await ws_client.init():
        logger.info("Connected to JX3API successfully.")


@driver.on_shutdown
async def nonebot_on_shutdown():
    logger.info('nonebot_on_shutdown...')
    filebase_database.Database.save_all()


@scheduler.scheduled_job("interval", id='database_save_all', seconds=3600*(1-0.05*random.random()))
async def nonebot_on_interval_task():
    logger.info('nonebot_on_interval_task...')
    filebase_database.Database.save_all()

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


ws_recev = on(type="WsRecv", priority=5, block=False)


@ws_recev.handle()
async def on_jx3_event_recv(bot: Bot, event: RecvEvent):
    message = event.get_message()
    if message == "False":
        return
    def check_server(x): return group_srv and x['server'] == group_srv
    '''已绑定服务器，且与事件一致'''
    type_callback = {
        '玄晶': lambda x: check_server(x),
        '诛恶': lambda x: check_server(x),
        '开服': lambda x: check_server(x),
        '818': lambda x: check_server(x), # 如果只看剑网3的话太少了 # and x["name"] != "剑网3",  # 只看剑三的新闻
        '机器人更新': lambda x: True,
    }

    menu_sender = await MenuCallback.from_general_name(message.get('type') or 'unknown')
    result = menu_sender.result
    # 回调判断消息是否应发送
    for key in result:
        (botname, group_id, to_send_msg, sub_from) = result[key]
        if not to_send_msg:
            continue
        group_config = GroupConfig(group_id, log=False)
        group_srv = group_config.mgr_property('server')
        callback = type_callback.get(message["type"])
        if callback and not callback(message):
            to_send_msg = None # 无效订阅
            result[key] = (botname, group_id, to_send_msg, sub_from)
            continue
        to_send_msg = message["msg"]
        result[key] = (botname, group_id, to_send_msg, sub_from)
    await menu_sender.start_send_msg()
