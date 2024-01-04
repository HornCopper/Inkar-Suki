from .api import *

jx3_cmd_sandbox = on_command(
    "jx3_sandbox",
    aliases={"沙盘", "攻防"},
    priority=5,
    catalog='jx3.pvp.gf.worldmap',
    description="获取攻防沙盘地图",
    example=[
        Jx3Arg(Jx3ArgsType.server),
    ],
    document='''沙盘''',
)


@jx3_cmd_sandbox.handle()
async def jx3_sandbox(event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    server, = template
    data = await sandbox_(server)
    if type(data) == type([]):
        return await jx3_cmd_sandbox.finish(data[0])
    return await jx3_cmd_sandbox.send(ms.image(data))
