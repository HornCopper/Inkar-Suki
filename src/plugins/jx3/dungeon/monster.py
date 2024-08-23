from pathlib import Path

from src.tools.generate import generate, get_uuid
from src.tools.utils.request import get_api
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.time import convert_time, get_current_time
from src.tools.utils.file import read, write

import re

level_desc = ["", "+300", "秒杀首领;+80", "稀有提高;+80", "随机前进;+80",
              "后六翻倍;+50", "前六减半;+50", "+100", "后跃三步;+100", "+300", "逆向前进"]
level_icon = [18505, 4533, 13548, 13547, 3313, 4577, 4543, 4558, 4576, 4573]

template = """
<div class="el-tooltip u-column$Flag">
    <div class="u-img"><img src="$Icon" class="u-effect"></div>
    <div class="u-index"><span class="u-index-number">$Count</span></div>
    <div class="u-name">$bossName</div>
    <div class="u-gift"><span class="u-tag">$Desc</span><span class="u-coin">$Coin</span></div>
    <div class="u-elite"></div>
</div>
"""

# $Flag 特殊层标识 ; $Icon 图标 ; $Count 层数 ; $bossName 首领名称 ; $Desc 描述 ; $Coin 修罗之印


async def get_monsters_map():
    map_data = await get_api("https://cms.jx3box.com/api/cms/app/monster/map")
    boss = await get_api("https://node.jx3box.com/monster/boss")
    content = ["<div class=\"u-row\">"]
    for i in range(len(map_data["data"]["data"])):
        bid = map_data["data"]["data"][i]["dwBossID"]
        for x in boss["data"]:
            if x["dwNpcID"] == bid:
                name = x["szName"]
        level = map_data["data"]["data"][i]["nEffectID"]
        info = level_desc[level]
        icon = f"https://icon.jx3box.com/icon/{level_icon[level]}.png"
        flag = " is-effect" if level != 0 else ""  # 勿除空格
        details = info.split(";")
        if len(details) == 2:
            desc = details[0]
            coin = details[1]
        elif len(details) == 1:
            if details[0] == "":
                desc = ""
                coin = ""
            else:
                if details[0][0] == "+":
                    desc = ""
                    coin = details[0]
                else:
                    desc = details[0]
                    coin = ""
        else:
            desc = ""
            coin = ""
        count = i + 1
        if count % 10 == 0:
            flag = flag + " is-elite"  # 勿除空格
        new = template.replace("$Flag", flag).replace("$Icon", icon).replace("$Count", str(
            count)).replace("$bossName", name).replace("$Desc", desc).replace("$Coin", coin)
        if count % 10 == 0:
            content.append(new)
            if count / 10 in [1, 2, 3, 4, 5, 6]:
                content.append("</div>\n<div class=\"u-row\">")
            elif count / 10 == 7:
                content.append("</div>")
        else:
            content.append(new)
    start = re.sub(r"\..+\Z", "", map_data["data"]["start"].replace("T", " ")).split(" ")[0]
    html = read(VIEWS + "/jx3/monster/monster.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo_time = convert_time(get_current_time(), "%H:%M:%S")
    appinfo = f"自{start}起7天 · 当前时间：{appinfo_time}<br>{saohua}"
    html = html.replace("$content", "\n".join(content)).replace(
        "$customfont", font).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".m-bmap.is-map-phone", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
