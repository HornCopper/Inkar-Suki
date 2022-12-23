import datetime
import hashlib
import hmac
import nonebot
import json
import sys
import httpx

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"

from file import read

def format_body(data: dict) -> str:
    return json.dumps(data, separators=(',', ':'))


def gen_ts() -> str:
    return f"{datetime.datetime.now():%Y%m%d%H%M%S%f}"[:-3]


def gen_xsk(data: str) -> str:
    data += "@#?.#@"
    secret = "MaYoaMQ3zpWJFWtN9mqJqKpHrkdFwLd9DDlFWk2NnVR1mChVRI6THVe6KsCnhpoR"
    return hmac.new(secret.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()

async def post_url(url, proxy: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        resp = await client.post(url, timeout = timeout, headers = headers, data = data)
        result = resp.text
        return result

async def get_arena_data(token: str) -> dict:
    param = {
        "gameVersion":0,
        "forceId":-1,
        "zone": "",
        "server": "",
        "ts": gen_ts()
    }
    param = format_body(param)
    device_id = token.split("::")[1]
    headers = {
        'Host': 'm.pvp.xoyo.com',
        'accept': 'application/json',
        'deviceid': device_id,
        'platform': 'ios',
        'gamename': 'jx3',
        'clientkey': '1',
        'cache-control': 'no-cache',
        'apiversion': '1',
        'sign': 'true',
        'token': token,
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
        'User-Agent': 'SeasunGame/178 CFNetwork/1240.0.2 Darwin/20.5.0',
        "x-sk": gen_xsk(param)
    }
    data = await post_url(url="https://m.pvp.xoyo.com/user/get-jx3-topn-self-info", data=param, headers=headers)
    return json.loads(data)

qualification = on_command("jx3_qualification",aliases={"资历"})
@qualification.handle()
async def _(event: Event):
    now = json.loads(read(TOOLS + "/token.json"))
    flag = False
    token = ""
    for i in now:
        if i["qq"] == str(event.user_id):
            flag = True
            token = i["token"]
    if flag:
        result = await get_arena_data(token=token)
        value = result["data"]["Value"]
        nickname = result["data"]["roleName"]
        msg = "查询到「" + nickname + "」的资历为：" + value + "。"   
    else:
        msg = "唔……您尚未提交Token，提交方法请戳下面文档：\nhttps://inkar-suki.codethink.cn/get_jx3_token.html"
    await qualification.finish(msg)