from src.tools.permission import checker, error
from src.tools.dep.bot import *
from .api import *


def server_bind(group_id: str, server: str):
    if not server == "":
        # 当server为空表示要清空
        server = server_mapping(server)
        if not server:
            return [PROMPT_ServerNotExist]
    path = f"{DATA}/{group_id}/jx3group.json"
    now = json.loads(read(path))
    now["server"] = server
    write(path, json.dumps(now, ensure_ascii=False))


jx3_cmd_server_bind = on_command("jx3_bind", aliases={"绑定"}, priority=5)


@jx3_cmd_server_bind.handle()
async def jx3_server_bind(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    robot_admin = checker(str(event.user_id), 8)
    if not group_admin and not robot_admin:
        return await jx3_cmd_server_bind.finish("唔……只有群主或管理员才可以修改哦！")
    server = args.extract_plain_text()
    group_id = str(event.group_id)
    exact_server = server_mapping(server)
    if not exact_server:
        return await jx3_cmd_server_bind.finish("唔……服务器名称输入有误，绑定失败！")
    server_bind(group_id=group_id, server=exact_server if server else "")
    if server == "":
        return await jx3_cmd_server_bind.finish("已清除本群的绑定信息！\n注意：推送将推送全服内容！")
    return await jx3_cmd_server_bind.finish("绑定成功！\n当前区服为：" + server)
