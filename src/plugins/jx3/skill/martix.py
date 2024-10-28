from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.network import Request

async def get_matrix(kungfu: Kungfu):
    name = kungfu.name
    if kungfu.name is None or kungfu.school is None:
        return "此心法不存在哦~请检查后重试。"
    school = School(kungfu.school)
    params = {
        "forceId": str(school.internel_id),
    }
    tl_data = (await Request("https://m.pvp.xoyo.com/force/gest", params=params).post(tuilan=True)).json()
    data = tl_data["data"]
    description = ""
    for i in data:
        if i["kungfuName"] == name:
            for x in i["zhenFa"]["descs"]:
                description = description + x["name"] + "：" + x["desc"] + "\n"
                skillName = i["zhenFa"]["skillName"]
    return f"查到了{name}的{skillName}：\n" + description

