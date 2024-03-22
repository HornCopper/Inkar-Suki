from src.tools.basic import *

banword = on_command("banword", priority=5)


@banword.handle()
async def __(event: GroupMessageEvent, args: Message = CommandArg()):  # 违禁词封锁
    bw = args.extract_plain_text()
    if checker(str(event.user_id), 5) == False:
        await banword.finish(error(5))
    if bw:
        now = json.loads(read(DATA + "/" + str(event.group_id) + "/banword.json"))
        if bw in now:
            await banword.finish("唔……封禁失败，已经封禁过了。")
        now.append(bw)
        write(DATA + "/" + str(event.group_id) + "/banword.json", json.dumps(now, ensure_ascii=False))
        await banword.finish("已成功封禁词语！")
    else:
        await banword.finish("您封禁了什么？")

unbanword = on_command("unbanword", priority=5)  # 违禁词解封


@unbanword.handle()
async def ___(event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id), 5) == False:
        await unbanword.finish(error(5))
    cmd = args.extract_plain_text()
    if cmd:
        now = json.loads(read(DATA + "/" + str(event.group_id) + "/banword.json"))
        try:
            now.remove(cmd)
            write(DATA + "/" + str(event.group_id) + "/banword.json",
                  json.dumps(now, ensure_ascii=False))
            await unbanword.finish("成功解封词语！")
        except ValueError:
            await unbanword.finish("您解封了什么？")
    else:
        await unbanword.finish("您解封了什么？")