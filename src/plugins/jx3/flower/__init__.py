import sgtpyutils.hash
import shutil

from .api import *
from .renderer import renderer as x_renderer

jx3_cmd_flower = on_command(
    "jx3_flower",
    aliases={"花价"},
    priority=5,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.string, alias='地图', is_optional=True),
        Jx3Arg(Jx3ArgsType.string, alias='花名', is_optional=True),
    ],
    document='''获取当前花价
    花价 [区服] [地图] [品种]
    Example：花价
    Example：花价 唯满侠
    Example：花价 唯满侠 广陵邑
    Example：花价 唯满侠 广陵邑 牵牛花'''
)

CACHE_flower = filebase_database.Database(f'{bot_path.common_data_full}pvx_flower')


@jx3_cmd_flower.handle()
async def jx3_flower(state: T_State, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_map, arg_species = args
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
        persisted_path = f"{bot_path.ASSETS}{os.sep}jx3{os.sep}pvx{os.sep}flower{os.sep}{os.path.basename(img)}"
        shutil.copy2(img, persisted_path)
        CACHE_flower.value[cache_key] = [code, persisted_path]
    return await jx3_cmd_flower.send(ms.image(Path(img).as_uri()))
