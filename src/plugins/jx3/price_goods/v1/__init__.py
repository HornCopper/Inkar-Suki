from src.tools.dep import *
from .renderer import *

jx3_cmd_item = on_command(
    '物品',
    aliases={'道具', '描述'},
    description='查看物品属性'
)


@jx3_cmd_item.handle()
async def jx3_item(event: GroupMessageEvent, args: Message = CommandArg()):
    id = args.extract_plain_text()
    info = await getItem(id)
    if isinstance(info, list):
        return await jx3_cmd_item.finish(info[0])
    info = await render_item_img(info)
    return await jx3_cmd_item.finish(ms.image(Path(info).as_uri()))
