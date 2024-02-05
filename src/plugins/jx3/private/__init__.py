from .api import *

dilu = on_command("jx3_dilu", aliases={"的卢统计"}, priority=5)


@dilu.handle()
async def _(event: GroupMessageEvent):
    img = await get_dilu_data()
    return await dilu.finish(ms.image(img))


monsters_v1 = on_command("jx3_monsters_v1", aliases={"百战"}, priority=5)

@monsters_v1.handle()
async def _(event: GroupMessageEvent):
    correct_path = bot_path.ASSETS + "/jx3/monsters.jpg"
    if os.path.exists(correct_path):
        await monsters_v1.finish(ms.image(Path(correct_path).as_uri()))
    else:
        url = await get_baizhan_img()
        data = await get_content(url)
        bz = open(correct_path, mode="wb")
        bz.write(data)
        bz.close()
        await monsters_v1.finish(ms.image(Path(correct_path).as_uri()))