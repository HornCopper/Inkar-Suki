from sgtpyutils.logger import logger

from nonebot.adapters.onebot.v11.message import Message as v11Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters import Message, MessageSegment


def convert_to_str(msg: MessageSegment):
    if isinstance(msg, GroupMessageEvent):
        x = msg.get_message().extract_plain_text()
        msg = str.join(" ", x.split(" ")[1:])  # 将命令去除
    if isinstance(msg, MessageSegment):
        msg = msg.data
    if isinstance(msg, v11Message):
        msg = str(msg)
        pass
    if isinstance(msg, dict):
        import json
        msg = json.dumps(msg, ensure_ascii=False)

    if isinstance(msg, str):
        return msg
    logger.warning(f"message cant convert to str:{msg}")
    return msg
