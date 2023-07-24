from .api import *

kungfu = on_command("jx3_kungfu", aliases={"心法"}, priority=5)


@kungfu.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询心法下所有技能：

    Example：-心法 莫问
    '''
    kungfu_ = args.extract_plain_text()
    node = await getAllSkillsInfo(kungfu_)
    if node == False:
        await kungfu.finish("此心法不存在哦，请检查后重试~")
    await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=node)

skill = on_command("jx3_skill", aliases={"技能"}, priority=5)


@skill.handle()
async def _(args: Message = CommandArg()):
    '''
    查询心法下某技能：

    Example：-技能 莫问 徵
    '''
    info = args.extract_plain_text().split(" ")
    if len(info) != 2:
        await skill.finish("信息不正确哦，只能有2个参数，请检查后重试~")
    else:
        kungfu = info[0]
        skill_ = info[1]
    msg = await getSingleSkill(kungfu, skill_)
    if msg == False:
        await skill.finish("此心法不存在哦，请检查后重试~")
    await skill.finish(msg)

talent = on_command("_jx3_talent", aliases={"_奇穴"}, priority=5)


@talent.handle()
async def _(args: Message = CommandArg()):
    '''
    查询心法下某奇穴：

    Example：-_奇穴 莫问 流照

    Notice：此功能会显示秘籍，而另外一个不会（参考事件响应器为`_talent`的函数）
    '''
    data = args.extract_plain_text()
    data = data.split(" ")
    if len(data) != 2:
        await talent.finish("信息不正确哦，只能有2个参数，请检查后重试~")
    else:
        kungfu = data[0]
        talent_ = data[1]
        msg = await getSingleTalent(kungfu, talent_)
        await talent.finish(msg)


_talent = on_command("jx3_talent", aliases={"奇穴"}, priority=5)


@_talent.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    versions = await get_api("https://data.jx3box.com/talent/index.json")
    if len(arg) not in [2, 3]:
        await _talent.finish("唔……参数不正确哦~")
    if len(arg) == 2:
        kf = arg[0]
        tl = arg[1]
        ver = versions[0]["version"]
    else:
        kf = arg[0]
        tl = arg[1]
        ver = arg[2]
        for i in versions:
            if ver == i["name"]:
                ver = i["version"]
    name = aliases(kf)
    if name == False:
        await _talent.finish("未找到该心法，请检查后重试~")
    if os.path.exists(ASSETS + "/jx3/" + f"{ver}.json") == False:
        final_url = f"https://data.jx3box.com/talent/{ver}.json"
        data = await get_api(final_url)
        write(ASSETS + "/jx3/" + f"v{ver}.json", json.dumps(data, ensure_ascii=False))
    else:
        data = json.loads(read(ASSETS + "/jx3/" + f"{ver}.json"))
    try:
        real_data = data[name]
    except:
        await _talent.finish("唔……该赛季没有此心法~")
    for i in range(1, 13):
        for x in range(1, 6):
            try:
                each = real_data[str(i)][str(x)]
            except:
                continue
            if each["name"] == tl:
                if each["is_skill"] == 1:
                    special_desc = each["meta"]
                    desc = each["desc"]
                    extend = each["extend"]
                    icon = "https://icon.jx3box.com/icon/" + str(each["icon"]) + ".png"
                    msg = f"第{i}重·第{x}层：{tl}\n" + \
                        ms.image(icon) + f"\n{special_desc}\n{desc}\n{extend}"
                else:
                    desc = each["desc"]
                    icon = "https://icon.jx3box.com/icon/" + str(each["icon"]) + ".png"
                    msg = f"第{i}重·第{x}层：{tl}\n" + ms.image(icon) + f"\n{desc}"
                await _talent.finish(msg)
    await _talent.finish("唔……未找到该奇穴哦~")


macro_ = on_command("jx3_macro", aliases={"宏"}, priority=5)


@macro_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    xf = args.extract_plain_text()
    xf = aliases(xf)
    if xf == False:
        await macro_.finish("唔……心法输入有误，请检查后重试~")
    data = await get_macro(xf)
    await macro_.finish(data)
