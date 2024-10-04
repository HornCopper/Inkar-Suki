from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.network import Request

import json


async def get_url(kungfu: str) -> str | None:
    data = (await Request("https://helper.jx3box.com/api/menu_group/macro-rec").get()).json()
    macro_list = data["data"]["menu_group"]["menus"]
    for i in macro_list:
        kungfu_ = Kungfu.with_internel_id(i["icon"]).name
        if kungfu_ == kungfu:
            return "https://cms.jx3box.com/api/cms" + i["link"].replace("macro", "post")


async def get_macro(kungfu: str) -> str | None:
    url = await get_url(kungfu)
    if not isinstance(url, str):
        return
    data = (await Request(url).get()).json()
    talent_flag = True
    title = data["data"]["post_title"]
    detail = data["data"]["post_meta"]["data"][0]
    macro = detail["macro"]
    talent = detail["talent"]
    if talent == "":
        talent_flag = False
    if talent_flag:
        talent = json.loads(talent)
        talent_info = await get_talent(talent)
    else:
        talent_info = "可恶，作者没有给奇穴！"
    speed = detail["speed"]
    if speed == "":
        speed = "未知"
    final_url = "https://www.jx3box.com/macro/" + url.split("/")[-1]
    msg = f"推荐的宏命令如下：\n{macro}\n\n奇穴：{talent_info}\n来源：@{title}\n推荐加速：{speed}\n如果上述内容不够详细，可以点击下面的传送门直达宏发布页面：\n{final_url}"
    return msg


async def get_talent(talent: dict) -> str:
    ver = talent["version"]
    data = (await Request(url=f"https://data.jx3box.com/talent/{ver}.json").get()).json()
    xf_data = data[talent["xf"]]
    talents = []
    num = 1
    for i in talent["sq"].split(","):
        talents.append(xf_data[str(num)][i]["name"])
        num = num + 1
    talents_msg = ",".join(talents)
    return talents_msg

async def get_matrix(kungfu: Kungfu):
    name = kungfu.name
    if kungfu.name is None or kungfu.school is None:
        return "此心法不存在哦~请检查后重试。"
    school = School(kungfu.school)
    params = {
        "forceId": str(school.internel_id),
    }
    tl_data = (await Request("https://m.pvp.xoyo.com/force/gest", params=params).post(tuilan=True)).json()
    tl_data = json.loads(tl_data)
    data = tl_data["data"]
    description = ""
    for i in data:
        if i["kungfuName"] == name:
            for x in i["zhenFa"]["descs"]:
                description = description + x["name"] + "：" + x["desc"] + "\n"
                skillName = i["zhenFa"]["skillName"]
    return f"查到了{name}的{skillName}：\n" + description