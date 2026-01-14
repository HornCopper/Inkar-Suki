"""
命令分发器

根据解析的意图，分发到对应的命令处理函数。
"""

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment as ms
from nonebot.log import logger

from src.const.jx3.server import Server
from src.const.prompts import PROMPT


async def dispatch_command(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """
    根据意图分发到对应命令处理
    
    Args:
        bot: Bot 实例
        event: 消息事件
        intent: 解析后的意图字典
    """
    command = intent.get("command")
    if not command:
        return
    
    handler = COMMAND_HANDLERS.get(command)
    if handler:
        try:
            await handler(bot, event, intent)
        except Exception as e:
            logger.error(f"执行命令 {command} 失败: {e}")
            await bot.send(event, f"执行命令时出错了：{e}")
    else:
        logger.warning(f"未找到命令处理器: {command}")


# ==================== 命令处理函数 ====================

async def handle_serendipity(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """奇遇查询"""
    from src.plugins.jx3.serendipity.v2 import get_serendipity_v2
    
    server = intent.get("server")
    name = intent.get("name")
    
    if not name:
        await bot.send(event, "请告诉我要查询的角色名哦~")
        return
    
    server = Server(server, event.group_id).server
    if not server:
        await bot.send(event, PROMPT.ServerNotExist)
        return
    
    data = await get_serendipity_v2(server, name, True)
    await bot.send(event, data)


async def handle_exam(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """科举答案查询"""
    from src.plugins.jx3.exam.api import get_exam_answer
    
    question = intent.get("question")
    if not question:
        await bot.send(event, "请告诉我要查询的题目哦~")
        return
    
    data = await get_exam_answer(question)
    await bot.send(event, data)


async def handle_daily(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """日常查询"""
    from src.plugins.jx3.daily.v2 import get_daily_img
    
    server = intent.get("server")
    server = Server(server, event.group_id).server
    if not server:
        await bot.send(event, PROMPT.ServerNotExist)
        return
    
    data = await get_daily_img(server)
    await bot.send(event, data)


async def handle_gold(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """金价查询"""
    from src.plugins.jx3.gold.v2 import get_gold_img
    
    server = intent.get("server")
    server = Server(server, event.group_id).server
    if not server:
        await bot.send(event, PROMPT.ServerNotExist)
        return
    
    data = await get_gold_img(server)
    await bot.send(event, data)


async def handle_server(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """开服查询"""
    from src.plugins.jx3.server.v2 import get_server_img
    
    server = intent.get("server")
    server = Server(server, event.group_id).server
    if not server:
        await bot.send(event, PROMPT.ServerNotExist)
        return
    
    data = await get_server_img(server)
    await bot.send(event, data)


async def handle_checkin(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """签到"""
    from src.accounts.manage import AccountManage
    
    status = AccountManage(event.user_id).checkin()
    if not status:
        await bot.send(event, "您已经签到过了哦，请等待次日0点后重试！")
        return
    
    msg = ms.at(event.user_id) + f" 签到成功！\n本日幸运值：{status.lucky_value}\n金币：+{status.coin}\n累计签到：{status.total_days}天"
    if status.is_lucky:
        msg += "\n触发额外奖励！获得 10000 金币！"
    await bot.send(event, msg)


async def handle_coin(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """金币余额"""
    from src.accounts.manage import AccountManage
    
    coin = AccountManage(event.user_id).coins
    await bot.send(event, ms.at(event.user_id) + f"\n您的金币余额为：\n{coin}枚")


async def handle_wiki(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """Wiki 搜索"""
    keyword = intent.get("keyword")
    if not keyword:
        await bot.send(event, "请告诉我要搜索的内容~")
        return
    
    # 简化处理，返回搜索提示
    await bot.send(event, f"请使用命令 wiki {keyword} 进行搜索哦~")


async def handle_help(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """帮助"""
    await bot.send(event, "查看完整文档，请访问：https://inkar-suki.codethink.cn/Inkar-Suki-Docs/")


async def handle_guide(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """攻略查询"""
    from src.plugins.jx3.serendipity.v1 import get_preposition
    
    name = intent.get("name")
    if not name:
        await bot.send(event, "请告诉我要查询的奇遇名或副本名~")
        return
    
    data = await get_preposition(name)
    if not data:
        await bot.send(event, "唔……没有找到相关攻略~")
    else:
        await bot.send(event, data)


async def handle_equip(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """装备查询"""
    from src.plugins.jx3.attributes.v2 import get_attr_img_v2
    
    server = intent.get("server")
    name = intent.get("name")
    
    if not name:
        await bot.send(event, "请告诉我要查询的角色名哦~")
        return
    
    server = Server(server, event.group_id).server
    if not server:
        await bot.send(event, PROMPT.ServerNotExist)
        return
    
    data = await get_attr_img_v2(server, name)
    await bot.send(event, data)


async def handle_achievement(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """成就进度"""
    from src.plugins.jx3.achievement.v2 import get_progress_v2
    
    server = intent.get("server")
    name = intent.get("name")
    achievement = intent.get("achievement", "")
    
    if not name:
        await bot.send(event, "请告诉我要查询的角色名哦~")
        return
    
    server = Server(server, event.group_id).server
    if not server:
        await bot.send(event, PROMPT.ServerNotExist)
        return
    
    data = await get_progress_v2(server, name, achievement)
    await bot.send(event, data)


async def handle_player_info(bot: Bot, event: GroupMessageEvent, intent: dict) -> None:
    """玩家信息"""
    from src.plugins.jx3.role.api import get_role_info
    
    server = intent.get("server")
    name = intent.get("name")
    
    if not name:
        await bot.send(event, "请告诉我要查询的角色名哦~")
        return
    
    server = Server(server, event.group_id).server
    if not server:
        await bot.send(event, PROMPT.ServerNotExist)
        return
    
    data = await get_role_info(server, name)
    await bot.send(event, data)


# 命令处理器映射表
COMMAND_HANDLERS = {
    "奇遇": handle_serendipity,
    "科举": handle_exam,
    "日常": handle_daily,
    "金价": handle_gold,
    "开服": handle_server,
    "签到": handle_checkin,
    "金币": handle_coin,
    "wiki": handle_wiki,
    "帮助": handle_help,
    "攻略": handle_guide,
    "装备": handle_equip,
    "成就": handle_achievement,
    "玩家信息": handle_player_info,
}
