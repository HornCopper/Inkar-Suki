from .app import *

bind_affection_ = on_command("jx3_affbind", aliases={"绑定情缘"}, force_whitespace=True, priority=5)

@bind_affection_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [3, 4]:
        await bind_affection_.finish("绑定失败！请参考下面的命令格式：\n绑定情缘 自己ID 对方ID 对方QQ 时间(可不填)")
    self_name = arg[0]
    self_qq = event.user_id
    other_name = arg[1]
    other_qq = int(arg[2])
    custom_time = arg[3] if len(arg) == 4 else convert_time(getCurrentTime(), "%Y-%m-%d")
    timestamp = 0
    try:
        timestamp = int(datetime.strptime(custom_time, "%Y年%m月%d日").timestamp())
    except ValueError:
        try:
            timestamp = int(datetime.strptime(custom_time, "%Y-%m-%d").timestamp())
        except ValueError:
            await bind_affection_.finish("唔……您给出的时间无法识别，只接受下面的两种格式：\nYYYY年mm月dd日\nYYYY-mm-dd")
    if not checknumber(other_qq):
        await bind_affection_.finish("绑定失败！对方QQ需要为纯数字！")
    ans = await bind_affection(self_qq, self_name, other_qq, other_name, event.group_id, timestamp)
    await bind_affection_.finish(ans[0])

delete_affection_ = on_command("jx3_affdl", aliases={"解除情缘"}, force_whitespace=True, priority=5)

@delete_affection_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    self_id = event.user_id
    ans = await delete_affection(self_id)
    await delete_affection_.finish(ans[0])

affections_crt = on_command("jx3_affcrt", aliases={"查看情缘证书"}, force_whitespace=True, priority=5)

@affections_crt.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    img = await generateAffectionImage(event.user_id)
    if type(img) == type([]):
        await affections_crt.finish(img[0])
    else:
        img = get_content_local(img)
        await affections_crt.finish(ms.image(img))