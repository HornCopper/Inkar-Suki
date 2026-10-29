from src.const.jx3.kungfu import Kungfu
from src.utils.network import Request
from src.utils.jx3_data import talent_data

import json

async def get_url(kungfu: str) -> str | None:
    data = (await Request("https://cms.jx3box.com/api/cms/menu-group/macro-rec").get()).json()
    macro_list = data["data"]["menus"]
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
    data = talent_data(ver)
    if not data or talent["xf"] not in data:
        return f"本地尚未收录 {ver} 的奇穴快照（原始序列：{talent['sq']}）"
    xf_data = data[talent["xf"]]
    talents = []
    num = 1
    for i in talent["sq"].split(","):
        entry = xf_data.get(str(num), {}).get(i)
        talents.append(entry["name"] if isinstance(entry, dict) else f"第{num}重第{i}项")
        num = num + 1
    talents_msg = ",".join(talents)
    return talents_msg
