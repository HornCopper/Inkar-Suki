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
        '818': lambda x: check_server(x),  # 如果只看剑网3的话太少了 # and x["name"] != "剑网3",  # 只看剑三的新闻
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
            to_send_msg = None  # 无效订阅
            result[key] = (botname, group_id, to_send_msg, sub_from)
            continue
        to_send_msg = message["msg"]
        result[key] = (botname, group_id, to_send_msg, sub_from)
    await menu_sender.start_send_msg()
