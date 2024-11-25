from nonebot.adapters.onebot.v11 import Message, MessageSegment as ms

from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.network import Request

async def get_skill(kungfu: str, /, skill_keyword: str = "") -> str | Message:
    school = School(Kungfu(kungfu).school)
    if school.name is None:
        return "无法识别心法，请检查后重试！"
    data = (await Request("https://m.pvp.xoyo.com/force/gest", params={"forceId": str(school.internel_id)}).post(tuilan=True)).json()
    for each_kf_data in data["data"]:
        if each_kf_data["kungfuName"] == Kungfu(kungfu).name:
            kf_data = each_kf_data["remarks"]
            for each_series in kf_data:
                for each_skill in each_series["forceSkills"]:
                    if skill_keyword in each_skill["skillName"]:
                        msg = ms.image(each_skill["icon"]["FileName"]) \
                            + each_series["remark"] + "·" + each_skill["skillName"] \
                            + "\n" + each_skill["specialDesc"] \
                            + "\n" + each_skill["desc"] + "\n" + each_skill["simpleDesc"]
                        return msg
    return "未找到相关技能，请检查后重试？"