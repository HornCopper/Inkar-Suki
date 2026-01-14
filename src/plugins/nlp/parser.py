"""
意图解析器

使用 LLM 解析用户自然语言，识别意图并提取参数。
"""

from nonebot.log import logger

from src.utils.llm import llm_chat

import json
import re


SYSTEM_PROMPT = """你是 Inkar-Suki 机器人的自然语言理解模块。
根据用户输入，识别用户想要执行的命令并提取参数。

## 可识别的命令

### 剑网3 相关
- 奇遇查询: {"command": "奇遇", "server": "服务器名", "name": "角色名"}
- 装备查询: {"command": "装备", "server": "服务器名", "name": "角色名"}
- 科举答案: {"command": "科举", "question": "问题内容"}
- 日常查询: {"command": "日常", "server": "服务器名"}
- 金价查询: {"command": "金价", "server": "服务器名"}
- 开服查询: {"command": "开服", "server": "服务器名"}
- 战绩查询: {"command": "战绩", "server": "服务器名", "name": "角色名"}
- 成就进度: {"command": "成就", "server": "服务器名", "name": "角色名", "achievement": "成就名"}
- 招募查询: {"command": "招募", "server": "服务器名", "keyword": "关键词"}
- 攻略查询: {"command": "攻略", "name": "奇遇名或副本名"}
- 玩家信息: {"command": "玩家信息", "server": "服务器名", "name": "角色名"}

### 通用功能
- 签到: {"command": "签到"}
- 金币余额: {"command": "金币"}
- 天气查询: {"command": "天气", "city": "城市名"}
- Wiki搜索: {"command": "wiki", "keyword": "搜索内容"}
- 帮助: {"command": "帮助"}

## 服务器别名
常见服务器别名：
- 电五/电信五区 -> 唯我独尊
- 双一/双线一区 -> 乾坤一掷
- 电一 -> 幽月轮

## 返回格式
必须返回 JSON 格式，包含 command 和相关参数。
如果无法识别用户意图，返回 {"command": null, "message": "无法理解您的请求"}
如果用户只是在闲聊，同样返回 {"command": null}

仅返回 JSON，不要有其他内容。"""


async def parse_intent(text: str) -> dict:
    """
    解析用户自然语言意图
    
    Args:
        text: 用户输入的文本
    
    Returns:
        解析后的意图字典，包含 command 和相关参数
    """
    try:
        response = await llm_chat(
            messages=text,
            system=SYSTEM_PROMPT,
            temperature=0.1  # 低温度，确保输出稳定
        )
        
        # 尝试提取 JSON
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            intent = json.loads(json_match.group())
            logger.debug(f"解析意图: {text} -> {intent}")
            return intent
        else:
            logger.warning(f"LLM 返回非 JSON 格式: {response}")
            return {"command": None}
            
    except json.JSONDecodeError as e:
        logger.warning(f"解析 JSON 失败: {e}")
        return {"command": None}
    except Exception as e:
        logger.error(f"意图解析异常: {e}")
        raise
