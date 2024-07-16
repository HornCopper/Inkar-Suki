from src.plugins.sign.manage import Sign

from .process import *

throw_out = on_command("投掷漂流瓶", force_whitespace=True, priority=5)

@throw_out.handle()
async def _(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not os.path.exists(bottle_path):
        write(bottle_path, "[]")
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await throw_out.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        msg = arg[0]
        anonymous = False
    elif len(arg) == 2:
        msg = arg[0]
        anonymous = mapping(arg[1])
    coin = Sign.get_coin(str(event.user_id))
    if int(coin) < 100:
        await throw_out.finish("投掷失败，需要至少100枚金币！\n金币可通过音卡每日签到或活动等途径获取~")
    else:
        Sign.reduce(str(event.user_id), 100)
    processd = await createBottle(msg, str(event.user_id), anonymous)
    if type(processd) == type(""):
        await throw_out.finish(processd)
    else:
        await throw_out.finish(f"已经将您的漂流瓶丢进池塘啦，会被有缘人捡起来的哦~\n如果您开启了匿名，他们不会看到您的QQ号，您的漂流瓶ID为：「{processd}」")

throw_in = on_command("收回漂流瓶", force_whitespace=True, priority=5)

@throw_in.handle()
async def _(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    args = args.extract_plain_text()
    if not checknumber(args):
        await throw_in.finish("唔……收回漂流瓶命令后面需要带一个漂流瓶ID，请提供给我纯数字的ID！")
    else:
        admin = False
        if checker(str(event.user_id), 10):
            admin = True
        processd = await deleteBottle(str(event.user_id), args, admin)
        if type(processd) == type(""):
            await throw_in.finish(processd)
        else:
            await throw_in.finish("已经将这个瓶子从水池里移除啦！")

report = on_command("举报漂流瓶", force_whitespace=True, priority=5)

@report.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    args = args.extract_plain_text()
    if not checknumber(args):
        await report.finish("唔……收回漂流瓶命令后面需要带一个漂流瓶ID，请提供给我纯数字的ID！")
    else:
        processd = await reportBottle(str(event.user_id), args)
        if type(processd) == type(""):
            await throw_in.finish(processd)
        else:
            id = processd[0]
            for i in Config.bot_basic.bot_notice[str(event.self_id)]:
                await bot.call_api("send_group_msg", group_id = int(i), message = f"用户「{str(event.user_id)}」举报了漂流瓶ID：「{str(id)}」")
            await report.finish("您的举报已投递至用户群，举报成功后会获得金币奖励！")

lookup = on_command("查看漂流瓶", force_whitespace=True, priority=5)

@lookup.handle()
async def _(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await lookup.finish(error(10))
    args = args.extract_plain_text()
    if not checknumber(args):
        await lookup.finish("唔……收回漂流瓶命令后面需要带一个漂流瓶ID，请提供给我纯数字的ID！")
    else:
        processd = await lookupBottle(args)
        await lookup.finish(processd)

getO = on_command("随机漂流瓶", force_whitespace=True, priority=5)

@getO.handle()
async def _(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    msg = await randomBottle()
    await getO.finish(msg)