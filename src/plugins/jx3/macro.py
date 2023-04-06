import nonebot
import sys
import json

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api

icon_to_xf = {
    "10175":"毒经",
    "10447":"莫问",
    "10021":"花间游",
    "10081":"冰心诀",
    "10026":"傲血战意",
    "10003":"易筋经",
    "10242":"焚影圣诀",
    "10390":"分山劲",
    "10014":"紫霞功",
    "10015":"太虚剑意",
    "10225":"天罗诡道",
    "10224":"惊羽诀",
    "10585":"隐龙诀",
    "10533":"凌海诀",
    "10268":"笑尘诀",
    "10464":"北傲诀",
    "10615":"太玄经",
    "10144":"问水诀",
    "10627":"无方",
    "10062":"铁牢律",
    "10002":"洗髓经",
    "10243":"明尊琉璃体",
    "10389":"铁骨衣",
    "10698":"孤锋诀"
}

async def get_url(xf):
    data = await get_api("https://helper.jx3box.com/api/menu_group/macro-rec")
    macro_list = data["data"]["menu_group"]["menus"]
    for i in macro_list:
        xf_ = icon_to_xf[i["icon"]]
        if xf_ == xf:
            if xf_ == "花间游":
                return "https://cms.jx3box.com/api/cms/post/53569" # 谁叫你花间还在招标找不到宏啊寄
            return "https://cms.jx3box.com/api/cms" + i["link"].replace("macro","post")
        
async def get_macro(xf):
    url = await get_url(xf)
    data = await get_api(url)
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
    msg = f"推荐的宏命令如下：\n{macro}\n\n奇穴：{talent_info}\n来源：@{title}\n推荐加速：{speed}"
    return msg

async def get_talent(talent):
    ver = talent["version"]
    data = await get_api(url = f"https://oss.jx3box.com/data/qixue/{ver}.json")
    xf_data = data[talent["xf"]]
    talents = []
    num = 1
    for i in talent["sq"].split(","):
        talents.append(xf_data[str(num)][i]["name"])
        num = num + 1
    talents_msg = ",".join(talents)
    return talents_msg
