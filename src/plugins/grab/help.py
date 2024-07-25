from src.tools.basic import *

help = on_command("help", aliases={"帮助", "功能", "查看", "文档", "使用说明"}, force_whitespace=True, priority=5)

@help.handle()
async def help_(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    await help.finish(f"Inkar Suki · 音卡使用文档：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/\n点击下面的链接直达剑网3模块简化版文档：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/jx3_easy")