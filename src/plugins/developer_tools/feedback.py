from src.tools.basic import *

github_token = Config.ght

async def createIssue(uin: str, comment: str):
    title = "【反馈】Inkar Suki · 使用反馈"
    date = convert_time(getCurrentTime())
    msg = f"日期：{date}\n用户：{uin}\n留言：{comment}"
    url = f"https://api.github.com/repos/{Config.repo_name}/issues"
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

feedback_ = on_command("feedback", aliases={"反馈"}, priority=5)

@feedback_.handle()
async def _(event: Event, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    user = str(event.user_id)
    if len(msg) <= 8:
        await feedback_.finish("唔……反馈至少需要8字以上，包括标点符号。")
    else:
        await createIssue(user, msg)
        await feedback_.finish("已经将您的反馈内容提交至Inkar Suki GitHub，处理完毕后我们会通过电子邮件等方式通知您，音卡感谢您的反馈！")