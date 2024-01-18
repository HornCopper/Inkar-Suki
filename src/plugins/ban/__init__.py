from nonebot import get_bot, on_command
from nonebot.exception import ActionFailed
from src.tools.dep import *
from src.tools.config import Config
from src.tools.utils import checknumber
from src.tools.file import read, write
from src.tools.permission import checker, error
import json
import sys
import nonebot

from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg


def in_it(qq: str):
    for i in json.loads(read(bot_path.TOOLS + "/ban.json")):
        if i == qq:
            return True
    return False


ban = on_command("ban", priority=5)  # 封禁，≥10的用户无视封禁。


@ban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    sb = args.extract_plain_text()
    self_protection = False
    if sb in Config.owner:
        await ban.send("不能封禁机器人主人，这么玩就不好了，所以我先把你ban了QwQ")
        sb = str(event.user_id)
        self_protection = True
    x = Permission(event.user_id).judge(10, '拉黑用户')
    if not x.success:
        if self_protection is False:
            return await ban.finish(x.description)
    if sb is False:
        return await ban.finish("您输入了什么？")
    if checknumber(sb) is False:
        return await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    info = await bot.call_api("get_stranger_info", user_id=int(sb))
    if info["user_id"] == 0:
        return await ban.finish("唔……全域封禁失败，没有这个人哦~")
    elif in_it(sb):
        return ban.finish("唔……全域封禁失败，这个人已经被封禁了。")
    else:
        now = json.loads(read(bot_path.TOOLS + "/ban.json"))
        now.append(sb)
        write(bot_path.TOOLS + "/ban.json", json.dumps(now))
        sb_name = info["nickname"]
        if self_protection:
            return
        return await ban.finish(f"好的，已经全域封禁{sb_name}({sb})。")

unban = on_command("unban", priority=5)  # 解封


@unban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    x = Permission(event.user_id).judge(10, '解除拉黑用户')
    if not x.success:
        return await ban.finish(x.description)
    sb = args.extract_plain_text()
    if checknumber(sb) is False:
        return await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    info = await bot.call_api("get_stranger_info", user_id=int(sb))
    sb_name = info["nickname"]
    if sb is False:
        return await unban.finish("您输入了什么？")
    if in_it(sb) is False:
        return await unban.finish("全域解封失败，并没有封禁此人哦~")
    now = json.loads(read(bot_path.TOOLS + "/ban.json"))
    for i in now:
        if i == sb:
            now.remove(i)
    write(bot_path.TOOLS + "/ban.json", json.dumps(now))
    return await ban.finish(f"好的，已经全域解封{sb_name}({sb})。")


@matcher_common_run.handle()
async def common_match_ban_user(matcher: Matcher, event: GroupMessageEvent):
    info = json.loads(read(bot_path.TOOLS + "/ban.json"))
    if str(event.user_id) not in info:
        return

    permit = Permission(event.user_id).judge(10, '黑名单用户免除封禁', log=False)
    if not permit.success:
        matcher.stop_propagation()
        return

    GroupActivity(event.group_id).update_general(1)

mgr_cmd_echo_delay = on_command("mgr_cmd_echo_delay", aliases={'echovv'}, priority=5)

echo_list = []


@mgr_cmd_echo_delay.handle()
async def echo_delay(bot: Bot, state: T_State, event: GroupMessageEvent):
    schedule_time = DateTime() + 10e3
    echo_list.append(event.group_id)
    try:
        scheduler.add_job(
            run_echo_delay,
            "date",
            run_date=schedule_time.tostring(),
            id=f"echo_delay_{get_uuid()}")
    except ActionFailed as e:
        logger.warning(f"定时任务添加失败，{repr(e)}")


async def run_echo_delay():
    global echo_list
    for x in get_bots():
        bot = get_bot(x)
        for group in echo_list:
            await bot.call_api(
                "send_group_msg",
                group_id=group,
                message="延迟测试~"
            )
    echo_list = []

mgr_cmd_remove_robot = on_command(
    "mgr_leave_group",
    name='移除机器人',
    aliases={'移除机器人'},
    priority=5,
    description='让机器人自己体面',
    catalog=permission.mgr.group.exit,
    example=[
        Jx3Arg(Jx3ArgsType.number, default=600, alias='延迟秒数'),
    ],
    document='''退群有冷静期，期间可以取消退群
    这种退群不会进黑名单
    可以明确退群的时间，默认为10分钟(但参数的单位为妙)'''
)


@mgr_cmd_remove_robot.handle()
async def leave_group(bot: Bot, state: T_State, event: Event, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    delay, = args
    state['delay'] = delay
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]

    x = Permission(event.user_id).judge(10, '移除机器人')
    if not x.success and not group_admin:
        return await mgr_cmd_remove_robot.finish("唔……只有群主或管理员才能移除哦~")

    confirm_code = get_uuid()[0:6]
    state['code'] = confirm_code
    await mgr_cmd_remove_robot.send(f'确定要让机器人离开吗，回复确认码\n{confirm_code}')

cmd_cancel_leave = '取消移除机器人'
cmd_leave_task: dict[str, int] = filebase_database.Database(
    f'{bot_path.common_data_full}leave_tasks').value  # 退群状态


async def reschedule():
    '''TODO 初始化时加载历史计划'''
    pass


@mgr_cmd_remove_robot.got('confirm')
async def leave_group(bot: Bot, state: T_State, event: GroupMessageEvent, confirm: Message = Arg()):
    global cmd_leave_task
    u_input = confirm.extract_plain_text()
    if cmd_cancel_leave == u_input:
        return await cancel_leave_group(event)
    if state['code'] != u_input:
        return await mgr_cmd_remove_robot.send('没有回复正确的验证码哦~如果需要！重新发一下退出吧！')
    logger.warning(f"用户提交了注销申请:group={event.group_id},by:{event.user_id}")
    counter = state['delay'] or 10 * 60

    if counter < 0:
        counter = 0
    if counter > 365 * 86400:
        counter = 365 * 86400
    schedule_time = DateTime(DateTime() + counter * 1e3)

    await add_schedule_of_leave(event.group_id, schedule_time)
    prefix = f'[冷静期提醒]好哦~机器人将在{schedule_time.toRelativeTime()}'
    suffix = f'离开\n取消回复：{cmd_cancel_leave}'
    await mgr_cmd_remove_robot.send(f'{prefix}({schedule_time.tostring(DateTime.Format.DEFAULT)}){suffix}')


async def add_schedule_of_leave(group_id: str, schedule_time: DateTime):
    cmd_leave_task[group_id] = schedule_time.timestamp()
    try:
        scheduler.add_job(
            run_leave_group,
            "date",
            run_date=schedule_time.tostring(),
            id=f"run_leave_group_{get_uuid()}")
    except ActionFailed as e:
        logger.warning(f"定时任务添加失败，{repr(e)}")


async def run_leave_group():
    global cmd_leave_task
    to_leaves = [x for x in cmd_leave_task]
    for group_id in to_leaves:
        schedule_time = cmd_leave_task[group_id]
        if not schedule_time:
            continue
        if DateTime() + 5e3 < DateTime(schedule_time):
            continue
        await direct_leave_group(group_id)


async def direct_leave_group(group_id: str):
    logger.warning(f"根据用户要求退出群:{group_id}")
    global cmd_leave_task
    for x in get_bots():
        bot = get_bot(x)
        try:
            await bot.call_api(
                "send_group_msg",
                group_id=group_id,
                message=f"{Config.name}冷静期已到，有缘再见啦~"
            )
            await bot.call_api('set_group_leave', group_id=group_id)
            if cmd_leave_task.get(group_id):
                del cmd_leave_task[group_id]

            for i in Config.notice_to:
                await bot.call_api("send_group_msg", group_id=int(i), message=f'{Config.name}按他们的要求，离开了{group_id}')
        except Exception as ex:
            logger.warning(f'退群时操作失败:{ex}')
    logger.warning(f"完成：根据用户要求退出群:{group_id}")


mgr_cmd_cancel_remove_robot = on_command("mgr_cancel_leave_group", aliases={
                                         cmd_cancel_leave}, priority=5)


@mgr_cmd_cancel_remove_robot.handle()
async def cancel_leave_group(event: GroupMessageEvent):
    global cmd_leave_task
    if not cmd_leave_task.get(event.group_id):
        return
    del cmd_leave_task[event.group_id]
    logger.info(f'用户取消了注销:group={event.group_id},by:{event.user_id}')
    return await mgr_cmd_remove_robot.send('好哦~')
