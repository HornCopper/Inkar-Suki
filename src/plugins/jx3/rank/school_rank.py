from src.tools.dep import *
from src.plugins.jx3.dungeon.api import VIEWS

template = """
<li>
    <div class="u-item" style="width: $width; background-color: $color;"><img
            src="$img" class="u-pic"><span class="u-text"> $name
        </span><span class="u-dps">$dps</span></div>
</li>
"""

colors = {
    "通用": "#c3c5c1",
    "冰心诀": "#FF7DAD",
    "云裳心经": "#ffadcb",
    "花间游": "#BA9BE4",
    "离经易道": "#d8c4ff",
    "毒经": "#4B9BFB",
    "补天诀": "#7db8ff",
    "莫问": "#6DDFE2",
    "相知": "#78f0f3",
    "傲血战意": "#EC4B2C",
    "铁牢律": "#d43618",
    "易筋经": "#E6BC31",
    "洗髓经": "#b58f12",
    "焚影圣诀": "#f16040",
    "明尊琉璃体": "#c55036",
    "分山劲": "#6568ad",
    "铁骨衣": "#4f5186",
    "紫霞功": "#37C0E2",
    "太虚剑意": "#48d6f9",
    "天罗诡道": "#90CC50",
    "惊羽诀": "#a2e05f",
    "问水诀": "#FDDD70",
    "山居剑意": "#FDDD70",
    "笑尘诀": "#D6A16F",
    "北傲诀": "#8D90D8",
    "凌海诀": "#94C7DC",
    "隐龙诀": "#872F37",
    "太玄经": "#b9c1ff",
    "无方": "#16708a",
    "灵素": "#39bf9b",
    "孤锋诀": "#6bb7f2",
    "山海心诀": "#FFFFFF"
}

async def get_school_icon(name):
    school_data = await get_api("https://inkar-suki.codethink.cn/schoolmapping")
    if name not in list(school_data):
        raise KeyError(f"The force {name} cannot be found in the offical API of Inkar Suki.")
    else:
        icon_id = school_data[name]
        return f"https://img.jx3box.com/image/xf/{icon_id}.png"

async def get_school_rank(season_key):
    rank_data = await get_api(f"https://cms.jx3box.com/api/cms/bps/dps/group/{season_key}")
    season = rank_data["data"]["label"]
    standard = rank_data["data"]["items"][0]["dps"]
    contents = []
    for i in rank_data["data"]["items"]:
        width = str(round(int(i["dps"].split(".")[0]) / int(standard.split(".")[0]) * 100, 2)) + "%"
        icon = await get_school_icon(i["xf"])
        name = i["xf"]
        dps = str(int(i["dps"].split(".")[0]))
        color = colors[i["xf"]]
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