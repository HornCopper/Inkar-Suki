"""
NLP 意图解析插件

当用户 @机器人 发送自然语言消息时，使用 LLM 解析用户意图并分发到对应命令。
需要群聊订阅 Preview 才能触发。
"""

from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.log import logger

from src.config import Config
from src.utils.database.operation import get_group_settings

from .parser import parse_intent
from .dispatcher import dispatch_command

# 仅在 @机器人 时触发，优先级较低避免干扰正常命令
nlp_matcher = on_message(rule=to_me(), priority=99, block=False)


@nlp_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """处理自然语言消息"""
    # 检查 LLM 功能是否启用
    if not Config.llm.enable:
        return
    
    # 检查 Preview 订阅
    additions = get_group_settings(str(event.group_id), "additions")
    if "Preview" not in additions:
        return
    
    # 提取纯文本
    text = event.get_plaintext().strip()
    if not text:
        return
    
    # 如果以常见命令前缀开头，跳过（让正常命令处理）
    if text.startswith(("-", "/", "!", "！", "。", ".")):
        return
    
    try:
        # 解析意图
        intent = await parse_intent(text)
        
        if intent.get("command"):
            # 分发到对应命令
            await dispatch_command(bot, event, intent)
    except Exception as e:
        logger.warning(f"NLP 意图解析失败: {e}")
        # 静默失败，不打扰用户
