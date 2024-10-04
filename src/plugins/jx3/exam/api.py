from src.config import Config
from src.utils.network import Request

async def get_exam_answer(question):
    def qa(q, a):
        return f"问题：{q}\n答案：{a}"
    full_link = f"{Config.jx3.api.url}/data/exam/answer?subject={question}"
    info = (await Request(full_link).get()).json()
    if info["code"] == 400:
        return "没有找到任何与此相关的题目哦~"
    else:
        msg = ""
    msg = "找到下列相似的题目：\n"
    for i in info["data"]:
        msg = msg + qa(i["question"], i["answer"]) + "\n"
    return msg
