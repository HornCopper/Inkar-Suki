from src.tools.dep import *
from src.plugins.jx3.price_goods.lib.coin import brickl, goldl
import re

ikst = Config.inkarsuki_offical_apitoken


def get_headers(application_type: str) -> dict:
    headers = {
        "token": ikst,
        "type": application_type
    }
    return headers


async def get_url_with_token(app: str) -> dict:
    if ikst == "":
        raise KeyError("Unmatched the token to Inkar-Suki offical API.")
    api = "https://inkar-suki.codethink.cn/api"
    data = await post_url(url=api, headers=get_headers(app))
    return json.loads(data)["url"]

template = """
<tr>
    <td class="short-column">$server</td>
    <td class="short-column">刷新：$flush<br>捕获：$captured<br>竞拍：$sell</td>
    <td class="short-column">$map</td>
    <td class="short-column">$capturer<br>$ci<span style="color: grey;font-size:small">$cc</span></td>
    <td class="short-column">$auctioner<br>$bi<span style="color: grey;font-size:small">$bc</span></td>
    <td class="short-column">$price</td>
</tr>
"""

bad = "<img src=\"https://jx3wbl.xoyocdn.com/img/icon-camp-bad.07567e9f.png\">"
good = "<img src=\"https://jx3wbl.xoyocdn.com/img/icon-camp-good.0db444fe.png\">"


async def get_dilu_data():
    url = await get_url_with_token("dilu")
    data = await get_api(url)
    table = []
    for i in data["data"]:
        if i["data"] == []:
            table.append(re.sub(r"\$.+<", "暂无信息<",
                         template.replace("$server", i["server"]).replace("$img", "")))
        else:
            data_ = i["data"]
            server = i["server"]
            flush = convert_time(data_["refresh_time"])
            capture = convert_time(data_["capture_time"])
            auction = convert_time(data_["auction_time"])
            map = data_["map_name"]
            capturer = data_["capture_role_name"]
            capturer_camp = data_["capture_camp_name"]
            bidder = data_["auction_role_name"]
            bidder_camp = data_["auction_camp_name"]
            ci = good if capturer_camp == "浩气盟" else bad
            bi = good if bidder_camp == "浩气盟" else bad
            price = data_["auction_amount"].replace("万金", "万0金").replace(
                "万", f"<img src=\"{brickl}\">").replace("金", f"<img src=\"{goldl}\">")
            replace_string = [["$server", server], ["$flush", flush], ["$captured", capture], ["$sell", auction], ["$map", map], [
                "$capturer", capturer], ["$bi", bi], ["$ci", ci], ["$price", price], ["$auctioner", bidder], ["$bc", bidder_camp], ["$cc", capturer_camp]]
            t = template
            for x in replace_string:
                t = t.replace(x[0], x[1])
            table.append(t)
    content = "\n".join(table)
    html = read(VIEWS + "/jx3/dilu/dilu.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
    saohua = saohua["data"]["text"]
    appinfo_time = time.strftime("%H:%M:%S", time.localtime(time.time()))
    html = html.replace("$customfont", font).replace("$tablecontent", content).replace(
        "$randomsaohua", saohua).replace("$appinfo", f"的卢统计 · {appinfo_time}")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
