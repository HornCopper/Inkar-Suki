from src.utils.jx3api import jx3api_get

async def get_exam_answer(question_keyword: str):

    def qa(q, a):
        return f"问题：{q}\n答案：{a}"

    url = "/exam/search"
    params = {
        "subject": question_keyword,
    }
    info = await jx3api_get(url, params = params)
    if info["code"] in (400, 404):
        return "没有找到任何与此相关的题目哦~"
    if info["code"] != 200:
        return info["msg"] or "科举查询失败，请稍后重试！"
    if not info["data"]:
        return "没有找到任何与此相关的题目哦~"
    msg = "找到下列相似的题目：\n"
    for i in info["data"]:
        msg = msg + qa(i["question"], i["answer"]) + "\n"
    return msg
