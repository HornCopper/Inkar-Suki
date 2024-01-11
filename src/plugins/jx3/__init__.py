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

    logger.debug("Connecting to SFAPI...Please wait.")
    if await sf_ws_client.init():
        logger.info("Connected to SFAPI successfully.")


@driver.on_shutdown
async def nonebot_on_shutdown():
    logger.info('nonebot_on_shutdown...')
    filebase_database.Database.save_all()


@scheduler.scheduled_job("interval", id='database_save_all', seconds=3600*(1-0.05*random.random()))
async def nonebot_on_interval_task():
    logger.info('nonebot_on_interval_task...')
    filebase_database.Database.save_all()

global_cmd_flush_database = on_command('flush_database')


@global_cmd_flush_database.handle()
async def global_flush_database(event: GroupMessageEvent):
    x = Permission(event.user_id).judge(10, '查询和更新配置')
    if not x.success:
        return await global_cmd_update_grp_config.finish(x.description)
    total = filebase_database.Database.cache
    filebase_database.Database.save_all()
    return await global_cmd_flush_database.send(f'已完成更新,此次可能更新配置项:{len(list(total))}条')

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
    result = gc.mgr_property(arg_path, new_val)
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
    groups = os.listdir(bot_path.DATA)
    def check_server(x): return group_srv and x['server'] == group_srv
    '''已绑定服务器，且与事件一致'''
    type_callback = {
        '玄晶': lambda x: check_server(x),
        '诛恶': lambda x: check_server(x),
        '开服': lambda x: check_server(x),
        '818': lambda x: check_server(x) and x["name"] != "剑网3"  # 只看剑三的新闻
    }

    for group_id in groups:
        subscribe = GroupConfig(group_id).mgr_property('subscribe')
        msg_type = message["type"]
        if msg_type not in subscribe:
            continue
        group_config = GroupConfig(group_id)
        group_srv = group_config.mgr_property('server')
        callback = type_callback.get(message["type"])
        if callback and not callback(message):
            continue

        try:
            await bot.call_api("send_group_msg", group_id=group_id, message=message["msg"])
        except Exception as ex:
            logger.error(f"向群({group_id})推送失败，可能是因为风控、禁言或者未加入该群。ex={ex}")
