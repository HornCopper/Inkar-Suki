import sgtpyutils.hash
import shutil

from .api import *
from .renderer import renderer as x_renderer
from .Caches import *

jx3_cmd_flower = on_command("jx3_flower", aliases={"花价"}, priority=5)

@jx3_cmd_flower.handle()
async def jx3_flower(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取当前花价
    花价 [区服] [地图] [品种]
    Example：花价
    Example：花价 唯满侠
    Example：花价 唯满侠 广陵邑
    Example：花价 唯满侠 广陵邑 牵牛花
    """
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.default)]
    arg = get_args(args, template)
    arg_server, arg_map, arg_species = arg
    arg_server = server_mapping(arg_server, group_id = str(event.group_id))
    data = await get_flower(arg_server, arg_map, arg_species)
    code = sgtpyutils.hash.get_hash(json.dumps(data))  # 检查是否有变化
    cache_key = f"{arg_server}-{arg_map}-{arg_species}"
    prev_code = CACHE_flower.get(cache_key) or [None, None]
    if isinstance(data, str):
        return await jx3_cmd_flower.finish(data)
    if len(prev_code) == 2 and prev_code[0] == code and os.path.exists(prev_code[1]):
        img = prev_code[1]
    else:
        img = await x_renderer(arg_server, arg_map, arg_species, data) 
        persisted_path = f"{ASSETS}{os.sep}jx3{os.sep}pvx{os.sep}flower{os.sep}{os.path.basename(img)}"
        shutil.copy2(img, persisted_path)
        CACHE_flower[cache_key] = [code, persisted_path]
        flush_CACHE_flower()
    return await jx3_cmd_flower.send(ms.image(Path(img).as_uri()))