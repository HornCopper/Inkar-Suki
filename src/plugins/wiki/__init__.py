from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from .getimg import main as image
from .wiki import wiki

mcwiki = on_command("mcw",aliases={"我的世界百科","我的世界维基","mcwiki"})
@mcwiki.handle()
async def _(args: Message = CommandArg()):
    title = args.extract_plain_text()
    args = title.split(" ")
    title = args[0]
    if len(args) == 2:
        if args[1] == "-i":
            msg = ""
            images = await getattr(image, "mcw")(title)
            for i in images:
                msg = msg + ms.image(i)
            info = await wiki(title,"mcw")
            final_msg = info+msg
            await mcwiki.finish(final_msg)
        else:
            await mcwiki.finish("请不要乱跟参数哦，使用+help获取更多信息\n温馨提示：搜索的标题中的空格请用下划线(_)代替哦~")
    else:
        info = await wiki(title,"mcw")
        final_msg = info
        await mcwiki.finish(final_msg)

wikipedia = on_command("wp",aliases={"wikipedia","维基百科","wzh"})
@wikipedia.handle()
async def _(args: Message = CommandArg()):
    title = args.extract_plain_text()
    args = title.split(" ")
    title = args[0]
    if len(args) == 2:
        if args[1] == "-i":
            msg = ""
            images = await getattr(image, "wzh")(title)
            for i in images:
                msg = msg + ms.image(i)
            info = await wiki(title,"wzh")
            final_msg = info+msg
            await wikipedia.finish(final_msg)
        else:
            await wikipedia.finish("请不要乱跟参数哦，使用+help获取更多信息\n温馨提示：搜索的标题中的空格请用下划线(_)代替哦~")
    else:
        info = await wiki(title,"wzh")
        final_msg = info
        await wikipedia.finish(final_msg)