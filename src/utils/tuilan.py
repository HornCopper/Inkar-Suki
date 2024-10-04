from datetime import datetime
import hashlib
import hmac
import json

from src.config import Config

def format_body(data: dict) -> str:
    return json.dumps(data, separators=(",", ":"))

def gen_ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:-3]

def gen_xsk(data: str) -> str:
    data += "@#?.#@"
    secret = Config.jx3.api.xsk_secret # 我不知道哦，别问我
    return hmac.new(
        secret.encode(), 
        msg=data.encode(), 
        digestmod=hashlib.sha256
    ).hexdigest()

def dungeon_sign(data: str) -> str:
    secret: bytes = Config.jx3.api.sign_secret.encode() # 我不知道哦，别问我
    return hmac.new(
        secret,
        msg=data.encode(),
        digestmod=hashlib.sha1
    ).hexdigest()