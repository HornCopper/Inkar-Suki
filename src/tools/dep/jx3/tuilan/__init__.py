from src.tools.config import *
from src.tools.generate import generate, get_uuid
import datetime
import hashlib
import hmac
import json
jx3_token = Config.jx3_token


def format_body(data: dict) -> str:
    return json.dumps(data, separators=(',', ':'))


def gen_ts() -> str:
    return f"{datetime.datetime.now():%Y%m%d%H%M%S%f}"[:-3]


def gen_xsk(data: str) -> str:
    data += "@#?.#@"
    secret = "MaYoaMQ3zpWJFWtN9mqJqKpHrkdFwLd9DDlFWk2NnVR1mChVRI6THVe6KsCnhpoR"
    return hmac.new(secret.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()


def with_header(params: dict, raw: dict = None) -> dict:
    if not raw:
        raw = {}
        device_id = jx3_token.split("::")[1]
    param_data = format_body(params)
    xsk = gen_xsk(param_data)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "accept": "application/json",
        "deviceid": device_id,
        "platform": "android",
        "gamename": "jx3",
        "fromsys": "APP",
        "clientkey": "1",
        "cache-control": "no-cache",
        "apiversion": "3",
        "sign": "true",
        "token": jx3_token,
        "content-type": "application/json",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/3.12.2",
        "x-sk": xsk
    }
    headers.update(raw)
    return headers
