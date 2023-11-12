from src.tools.dep import *
from src.plugins.jx3.dungeon.api import VIEWS

template = """
<li>
    <div class="u-item" style="width: $width; background-color: $color;"><img
            src="$img" class="u-pic"><span class="u-text"> $name
        </span><span class="u-dps">$dps</span></div>
</li>
"""

async def get_school_rank(season_key):
    rank_data = await get_api(f"https://cms.jx3box.com/api/cms/bps/dps/group/{season_key}")
    season = rank_data["data"]["label"]
    standard = rank_data["data"]["items"][0]["dps"]
    contents = []
    for i in rank_data["data"]["items"]:
        width = str(round(int(i["dps"].split(".")[0]) / int(standard.split(".")[0]) * 100, 2)) + "%"
        kunfu = std_kunfu(i["xf"])
        icon = kunfu.icon
        name = kunfu.name
        dps = str(int(i["dps"].split(".")[0]))
        color = kunfu.color
        contents.append(template.replace("$width", width).replace("$color", color).replace("$name", name).replace("$dps", dps).replace("$img", icon))
    contents = "\n".join(contents)
    html = read(VIEWS + "/jx3/schoolrank/schoolrank.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
    saohua = saohua["data"]["text"]
    appinfo_time = time.strftime("%H:%M:%S",time.localtime(time.time()))
    appinfo = f"{season} · 当前时间：{appinfo_time}<br>{saohua}"
    html = html.replace("$content", contents).replace("$customfont", font).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".m-ladder-rank", False)
    return Path(final_path).as_uri()