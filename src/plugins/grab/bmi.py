from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg

from src.tools.utils.common import checknumber

bmi = on_command("bmi", aliases={"BMI", "身体质量指数"}, force_whitespace=True, priority=5)

@bmi.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await bmi.finish("唔……参数数量不正确哦，请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
    for i in arg:
        if not checknumber(i):
            await bmi.finish("唔……请参考以下格式，注意两个参数都是纯数字哦~\nBMI 身高(米) 体重(千克)")
    height = float(arg[0])
    weight = float(arg[1])
    bmi_value = weight / (height*height)
    final_result = round(bmi_value, 1)
    if final_result <= 18.4:
        msg = f"您的BMI计算结果是：{final_result}，属于偏瘦（0~18.4）哦~"
    elif 18.5 <= final_result <= 23.9:
        msg = f"您的BMI计算结果是：{final_result}，属于正常（18.5~23.9）哦~"
    elif 24.0 <= final_result <= 27.9:
        msg = f"您的BMI计算结果是：{final_result}，属于偏胖（24.0~27.9）哦~"
    elif final_result >= 28.0:
        msg = f"您的BMI计算结果是：{final_result}，属于肥胖（28.0+）哦~\n音卡建议您少吃高热量食物，多多运动保持健康身体哦！"
    await bmi.finish(msg)
    