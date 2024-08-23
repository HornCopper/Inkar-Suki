from typing import Union, Any

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment as ms
from nonebot.params import CommandArg
from nonebot.adapters import Message

from src.tools.config import Config
from src.tools.utils.time import convert_time, get_current_time
from src.tools.utils.request import post_url
from src.tools.permission import checker, error
from src.tools.database import group_db, Population

from .stastic import generate_bar_chart

github_token = Config.github.github_personal_token

async def createIssue(uin: str, comment: str):
    title = "【反馈】Inkar Suki · 使用反馈"
    date = convert_time(get_current_time())
    msg = f"日期：{date}\n用户：{uin}\n留言：{comment}"
    url = f"https://api.github.com/repos/{Config.bot_basic.bot_repo}/issues"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": msg
    }
    response = await post_url(url, headers=headers, json=data)
    return response

feedback_ = on_command("feedback", aliases={"反馈"}, force_whitespace=True, priority=5)

@feedback_.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    user = str(event.user_id)
    if len(msg) <= 8:
        await feedback_.finish("唔……反馈至少需要8字以上，包括标点符号。")
    else:
        await createIssue(user, msg)
        await feedback_.finish("已经将您的反馈内容提交至Inkar Suki GitHub，处理完毕后我们会通过电子邮件等方式通知您，音卡感谢您的反馈！")

stastic = on_command("stastic", aliases={"统计数据", "命令统计"}, priority=5, force_whitespace=True)

@stastic.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if not checker(str(event.user_id), 10):
        await stastic.finish(error(10))
    current_data: Union[Population, Any] = group_db.where_one(Population(), default=Population())
    current_population: dict = current_data.populations
    img: bytes
    if args.extract_plain_text() == "":
        img = await generate_bar_chart(current_population)
    else:
        for name in current_population:
            if name == args.extract_plain_text():
                await stastic.finish("该命令截至目前的总调用量为：" + str(current_population[name]))
        await stastic.finish("没有找到该命令的统计数据，可能是调用量为0或者不存在。")
    await stastic.finish(ms.image(img))