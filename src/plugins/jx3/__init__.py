from nonebot import get_driver

try:
    from .special_application import *  # 公共实例独有功能，闭源
except Exception as _:
    pass
from .jx3 import *

driver = get_driver()


@driver.on_startup
async def nonebot_on_startup():
    logger.info("Connecting to JX3API...Please wait.")
    if await ws_client.init():
        logger.info("Connected to JX3API successfully.")

    logger.info("Connecting to SFAPI...Please wait.")
    if await sf_ws_client.init():
        logger.info("Connected to SFAPI successfully.")


@scheduler.scheduled_job("interval", id='database_save_all', hours=1)
@driver.on_shutdown
async def nonebot_on_shutdown():
    filebase_database.Database.save_all()

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
        subscribe = load_or_write_subscribe(group_id)
        msg_type = message["type"]
        if msg_type not in subscribe:
            continue
        group_config = f"{bot_path.DATA}{os.sep}{group_id}{os.sep}jx3group.json"
        group_info = json.loads(read(group_config))
        group_srv = group_info["server"]
        callback = type_callback.get(message["type"])
        if callback and not callback(message):
            continue

        try:
            await bot.call_api("send_group_msg", group_id=group_id, message=message["msg"])
        except Exception as ex:
            logger.info(f"向群({group_id})推送失败，可能是因为风控、禁言或者未加入该群。ex={ex}")
