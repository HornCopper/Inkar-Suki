from .. import *
import asyncio
from src.tools.file import write
def test_cron_signin():
    import src.plugins.sign
    clean_data = src.plugins.sign.clean_data
    asyncio.run(clean_data())
  

def test_signin():
    import src.plugins.sign
    sign = src.plugins.sign.sign

    def handle_finish(msg: str):
        assert '签到成功' in msg, f'fail run:{msg}'
        assert '1天' in msg, f'fail run:{msg}'

    def handle_send(msg: str):
        assert False, f'fail run:{msg}'
    mc = MessageCallback(handle_finish, handle_send)
    src.plugins.sign.sign_ = mc
    event = SFGroupMessageEvent(user_id=random.randrange(int(1e8), int(1e9)))
    task = sign(event)
    asyncio.run(task)
    mc.check_counter()

    def handle_finish(msg: str):
        assert '不能重复签到' in msg, f'fail run:{msg}'

    src.plugins.sign.sign_.cb_finish = handle_finish
    task = sign(event)
    asyncio.run(task)
    mc.check_counter()
