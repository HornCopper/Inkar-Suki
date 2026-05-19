from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.network import Request

async def get_matrix(kungfu: Kungfu):
    name = kungfu.name
    if name is None or kungfu.school is None:
        return "此心法不存在哦~请检查后重试。"
    school = School(kungfu.school)
    params = {
        "forceId": str(school.internel_id),
    }
    tl_data = (await Request("https://m.pvp.xoyo.com/force/gest", params=params).post(tuilan=True)).json()
    data = tl_data.get("data") or []
    for i in data:
        if i.get("kungfuName") != name:
            continue
        zhen_fa = i.get("zhenFa") or {}
        skill_name = zhen_fa.get("skillName") or "阵眼"
        descs = zhen_fa.get("descs") or []
        if not descs:
            return f"查到了{name}的{skill_name}，但暂时没有阵眼效果数据。"
        description = ""
        for x in descs:
            description += x["name"] + "：" + x["desc"] + "\n"
        return f"查到了{name}的{skill_name}：\n" + description
    return f"暂时未找到{name}的阵眼数据，请稍后重试。"

