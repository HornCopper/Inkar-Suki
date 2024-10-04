from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .version import get_be_version, get_je_version
from .server import get_bedrock_server, get_java_server

mcbv = on_command("mcbv", force_whitespace=True, priority=5)  # 获取MC基岩版最新版本

@mcbv.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    msg = await get_be_version()
    await mcbv.finish(msg)

mcjv = on_command("mcjv", force_whitespace=True, priority=5)  # 获取MC Java版最新版本


@mcjv.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    msg = await get_je_version()
    await mcjv.finish(msg)

mcjes = on_command("jes", force_whitespace=True, priority=5)  # 获取MC Java版服务器信息


@mcjes.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    ip = args.extract_plain_text()
    msg = await get_java_server(ip)
    await mcjes.finish(msg)

mcbes = on_command("bes", force_whitespace=True, priority=5)  # 获取MC 基岩版服务器信息


@mcbes.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    ip = args.extract_plain_text()
    msg = await get_bedrock_server(ip)
    await mcbes.finish(msg)
