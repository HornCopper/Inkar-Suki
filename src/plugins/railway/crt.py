from pathlib import Path
from urllib.parse import quote

from src.tools.utils.request import get_api
from src.tools.file import read, write
from src.tools.generate import get_uuid, generate
from src.tools.utils.path import ASSETS, CACHE, VIEWS

template_3 = """
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;color:$color1;">
        <!-- color为线路颜色 -->
        $line1
        <!-- 第一段线路名称 -->
    </span>
    <span  style="float: left; line-height: 14px; margin: 10px 0 10px 22px">
        <img src="$icon1" style="width: 16px; height: 16px;">
        <!-- 第一段线路图标 -->
    </span>
    <span
        style="float: left;width: 135px;height: 16px;font-size: 16px;color: $color1;text-align: center;line-height: 14px;position: relative;right: 38px;">
        $start
        <!-- 起始站点名称 -->
    </span>
</div>
<div style="width: 458px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;background-color: $color1;height: 3px;width: 502px;border: 6.5px solid #ffffff;border-left: 0;border-right: 0;margin-top: 26px;position: relative;right: 22px;">
    </span>
    <span style="float: left;width: 286px;color: #999999;font-size: 14px;text-align: center;margin-top: 4px;">
        $direction1
        <!-- 第一段方向 -->
    </span>
</div>
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;width: 136px;color:$color1;">
        $line1
        <!-- 第一段线路名称 -->
    <span style="font-size: 14px; color: #333333; margin-left: 10px;">
        （换乘）
        <!-- 是否换乘 如果结束填Null -->
    </span>
</span>
<span style="float: left; line-height: 14px; margin: 10px 0 10px 22px;">
    <img src="$icon1" alt="" style="width: 16px; height:16px;">
</span>
<span style="float: left;width: 135px;height: 16px;font-size: 16px;text-align: center;line-height: 14px;position: relative;right: 38px;color:$color1">
    $swap1
    <!-- 第一段末站 -->
</span>
</div>
<div style="width: 458px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;background-color: $color2;height: 3px;width: 502px;border: 6.5px solid #ffffff;border-left: 0;border-right: 0;margin-top: 26px;position: relative;right: 22px;">
    </span>
    <span style="float: left;width: 286px;color: #999999;font-size: 14px;text-align: center;margin-top: 4px;">
        $direction2
        <!-- 第二段线路方向 -->
    </span>
</div>
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;width: 106px;color:$color2;">
        $line2
        <!-- 第二段线路名称 -->
    </span>
    <span style="float: left; line-height: 14px; margin: 10px 0 10px 22px;">
        <img src="$icon2" alt="" style="width: 16px; height: 16px;">
    </span>
    <span style="float: left;width: 135px;height: 16px;font-size: 16px;text-align: center;line-height: 14px;position: relative;right: 38px;color:#333333;">
        $end
        <!-- 第二段末站 -->
    </span>
</div>
"""  # 适用于3站线路

template_2 = """
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;color:$color1">
        $line1
    </span>
    <span style="float: left; line-height: 14px; margin: 10px 0 10px 22px">
        <img src="$icon1" style="width: 16px; height: 16px">
    </span>
    <span style="float: left;width: 135px;height: 16px;font-size: 16px;color: $color1;text-align: center;line-height: 14px;position: relative;right: 38px;">
        $start
    </span>
</div>
<div style="width: 982px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float:left;background-color: $color1;height: 3px;width: 1025px;border: 6.5px solid #ffffff;border-left: 0;border-right: 0;margin-top: 26px;position: relative;right:22px;">
    </span>
    <span style="float: left;width: 980px;color: #999999;font-size: 14px;text-align: center;margin-top: 4px;">
        $direction1
    </span>
</div>
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;width: 106px;color:$color1">
        $line1
    </span>
    <span style="float: left; line-height: 14px; margin: 10px 0 10px 22px">
        <img src="$icon1" alt="" style="width: 16px; height: 16px">
    </span>
    <span style="float: left;width: 135px;height: 16px;font-size: 16px;text-align: center;line-height: 14px;position: relative;right: 38px;color:$color1">
        $end
    </span>
</div>"""  # 适用于2站线路

template_4 = """
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;color:$color1">
        $line1
    </span>
    <span style="float: left; line-height: 14px; margin: 10px 0 10px 22px">
        <img src="$icon1" style="width: 16px; height: 16px;">
    </span>
    <span style="float: left;width: 135px;height: 16px;font-size: 16px;text-align: center;line-height: 14px;position: relative;right: 38px;color: $color1">
        $start
    </span>
</div>
<div style="width: 286px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;background-color: $color1;height: 3px;width: 330px;border: 6.5px solid #ffffff;border-left: 0;border-right: 0;margin-top: 26px;position: relative;right: 22px;">
    </span>
    <span style="float: left;width: 286px;color: #999999;font-size: 14px;text-align: center;margin-top: 4px;">
        $direction1
    </span>
</div>
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;width: 136px;color:$color1;">
        $line1
        <span style="font-size: 14px; color: #333333; margin-left: 10px;">
            （换乘）
        </span>
    </span>
    <span style="float: left; line-height: 14px; margin: 10px 0 10px 22px;">
        <img src="$icon2" alt="" style="width: 16px; height:16px;">
    </span>
    <span style="float: left;width: 135px;height: 16px;font-size: 16px;text-align: center;line-height: 14px;position: relative;right: 38px;color:$color2">
        $swap1
    </span>
</div>
<div style="width: 286px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;background-color: $color2;height: 3px;width: 330px;border: 6.5px solid #ffffff;border-left: 0;border-right: 0;margin-top: 26px;position: relative;right: 22px;">
    </span>
    <span style="float: left;width: 286px;color: #999999;font-size: 14px;text-align: center;margin-top: 4px;">
        $direction2
    </span>
</div>
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;width: 136px;color:$color2;">
        $line2
        <span style="font-size: 14px; color: #333333; margin-left: 10px;">
            （换乘）
        </span>
    </span>
    <span style="float: left; line-height: 14px; margin: 10px 0 10px 22px;">
        <img src="$icon2" alt="" style="width: 16px; height:16px;">
    </span>
    <span style="float: left;width: 135px;height: 16px;font-size: 16px;text-align: center;line-height: 14px;position: relative;right: 38px;color:$color2">
        $swap2
    </span>
</div>
<div style="width: 286px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;background-color: $color3;height: 3px;width: 330px;border: 6.5px solid #ffffff;border-left: 0;border-right: 0;margin-top: 26px;position: relative;right: 22px;">
    </span>
    <span style="float: left;width: 286px;color: #999999;font-size: 14px;text-align: center;margin-top: 4px;">
        $direction3
    </span>
</div>
<div style="width: 60px;height: 68px;margin-top: 22px;margin-bottom: 40px;float: left;">
    <span style="float: left;font-size: 16px;line-height: 15px;margin-left: 10px;width: 106px;color:$color3;">
        $line3
    </span>
    <span style="float: left; line-height: 14px; margin: 10px 0 10px 22px;">
        <img src="$icon3" alt="" style="width: 16px; height: 16px;">
    </span>
    <span style="float: left;width: 135px;height: 16px;font-size: 16px;text-align: center;line-height: 14px;position: relative;right: 38px;color:$color3;">
        $end
    </span>
</div>"""


def get_line_icon(line):
    if line == "江跳线(市郊铁路)":
        return "https://www.cqmetro.cn/imgs/route-5.png"
    if line == "空港线":
        return "https://www.cqmetro.cn/imgs/route-3.png"
    if line == "国博线":
        return "https://www.cqmetro.cn/imgs/route-6.png"
    if line == "环线":
        return "https://www.cqmetro.cn/imgs/dothuan.png"
    else:
        num = line[0]
        return f"https://www.cqmetro.cn/imgs/route-{num}.png"


def get_color(raw):
    if raw == "pt3005c":
        return "#0077c8"
    else:
        return "#" + raw


def seconds_to_minutes(seconds):
    minutes = seconds / 60
    rounded_minutes = round(minutes)
    return rounded_minutes


async def cq_crt(start: str, end: str):
    if start == end:
        return ["请您原地站着不动即可。"]
    start_ = quote(quote(start))
    end_ = quote(quote(end))
    api = f"https://www.cqmetro.cn/Front/html/TakeLine!queryYsTakeLine.action?entity.startStaName={start_}&entity.endStaName={end_}"
    data = await get_api(api)
    if not data.get("result", []):
        return ["未查询到线路，请检查起始站名或到达站名是否有误？"]
    data = data["result"][0]
    count = len(data["transferStaNames"].split(","))
    if data["transferStaNames"] == "":
        template = template_2
    elif count == 1:
        template = template_3
    elif count == 2:
        template = template_4
    price = data["price"]
    minute = seconds_to_minutes(data["needTimeScope"])
    lines = data["transferLines"].split(",")
    colors = data["transferLinesColor"].split(",")
    directions = data["transferStaDerict"].split(",")
    swaps = data["transferStaNames"].split(",")
    for i in range(1, 4):
        try:
            lines[i - 1]
        except:
            break
        line = lines[i - 1]
        color = get_color(colors[i - 1])
        icon = get_line_icon(line)
        template = template.replace("$line" + str(i), line).replace("$color" + str(i), color).replace("$icon" + str(i), icon)
        try:
            directions[i - 1]
        except:
            continue
        direction = directions[i - 1]
        template = template.replace("$direction" + str(i), direction)
        try:
            swaps[i - 1]
        except:
            continue
        swap = swaps[i - 1]
        template = template.replace("$swap" + str(i), swap)
    basic = read(VIEWS + "/railway/crt/crt.html")
    basic = basic.replace("$ticket", str(price)).replace("$minute", str(minute))
    final_html = basic.replace("$content", template)
    font = ASSETS + "/font/custom.ttf"
    final_html = final_html.replace("$customfont", font).replace("$start", start).replace("$end", end)
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, final_html)
    generated = await generate(final_path, False, ".search-result", False)
    if not isinstance(generated, str):
        return
    return Path(generated).as_uri()
