from src.tools.basic import *

banword = on_command("banword", force_whitespace=True, priority=5)


@banword.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):  # 违禁词封锁
    if args.extract_plain_text() == "":
        return
    bw = args.extract_plain_text()
    if not checker(str(event.user_id), 5):
        await banword.finish(error(5))
    if bw:
        now = json.loads(read(TOOLS + "/banword.json"))
        if bw in now:
            await banword.finish("唔……封禁失败，已经封禁过了。")
        now.append(bw)
        write(TOOLS + "/banword.json", json.dumps(now, ensure_ascii=False))
        await banword.finish("已成功封禁词语！")
    else:
        await banword.finish("您封禁了什么？")

unbanword = on_command("unbanword", force_whitespace=True, priority=5)  # 违禁词解封


@unbanword.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 5):
        await unbanword.finish(error(5))
    cmd = args.extract_plain_text()
    if cmd:
        now = json.loads(read(TOOLS + "/banword.json"))
        try:
            now.remove(cmd)
            write(TOOLS + "/banword.json",
                  json.dumps(now, ensure_ascii=False))
            await unbanword.finish("成功解封词语！")
        except ValueError:
            await unbanword.finish("您解封了什么？")
    else:
        await unbanword.finish("您解封了什么？")