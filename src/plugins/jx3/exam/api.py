from src.tools.basic import *


async def exam_(question):
    def qa(q, a):
        return f"问题：{q}\n答案：{a}"
    full_link = f"{Config.jx3api_link}/data/exam/answer?match={question}&token={token}"
    info = await get_api(full_link)
    if info["code"] == 400:
        return "没有找到任何与此相关的题目哦~"
    else:
        msg = ""
    msg = "找到下列相似的题目：\n"
    for i in info["data"]:
        msg = msg + qa(i["question"], i["answer"]) + "\n"
    return msg
