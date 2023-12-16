from .api import *

wbl = on_command("jx3_wbl", aliases={"万宝楼"}, priority=5)


@wbl.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        return await wbl.finish("唔……参数有误，请检查后重试~")
    product = arg[0]
    product_num = arg[1]
    if checknumber(product_num) == False:
        return await wbl.finish("唔……检测到商品编号出现了非数字的内容！\n请检查后重试~")
    if product not in ["外观", "角色"]:
        return await wbl.finish("唔……第二个参数请填写「外观」或「角色」。")
    if product == "外观":
        product_flag = True
    else:
        product_flag = False
    msg = await get_wanbaolou(product_num, product_flag)
    return await wbl.finish(msg)
