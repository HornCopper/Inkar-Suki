from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.params import CommandArg

from src.tools.basic.msg import PROMPT
from src.tools.basic.data_server import server_mapping
from src.tools.basic.group_opeator import setGroupSettings
from src.tools.permission import checker

def server_bind(group_id: str, server: str):
    if not server == "":
        # 当server为空表示要清空
        server = server_mapping(server)
        if not server:
            return [PROMPT.ServerNotExist]
    setGroupSettings(group_id, "server", server)

jx3_cmd_server_bind = on_command("jx3_bind", aliases={"绑定", "绑定区服"}, force_whitespace=True, priority=5)

@jx3_cmd_server_bind.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    personal_data = await bot.call_api("get_group_member_info", group_id = event.group_id, user_id = event.user_id, no_cache = True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    robot_admin = checker(str(event.user_id), 8)
    if not group_admin and not robot_admin:
        await jx3_cmd_server_bind.finish("唔……只有群主或管理员才可以修改哦！")
    server = args.extract_plain_text()
    group_id = str(event.group_id)
    exact_server = server_mapping(server)
    server_bind(group_id=group_id, server=exact_server if server else "")
    if server == "":
        await jx3_cmd_server_bind.finish("已清除本群的绑定信息！")
    if server == None:
        await jx3_cmd_server_bind.finish("您给出的服务器名称音卡似乎没有办法理解，尝试使用一个更通俗的名称或者官方标准名称？")
    await jx3_cmd_server_bind.finish("绑定成功！\n当前区服为：" + exact_server)