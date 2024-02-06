from .dh import *

async def get_wg(name):
    timestamp = int(datetime.datetime.now().timestamp())
    data = await get_api(f"https://www.j3dh.com/v1/wg/data/exterior?exterior={name}&ignorePriceFlag=true&page=0&refresh=v1&time={timestamp}")
    if data["Code"] != 0:
        return "唔……API请求失败！"
    else:
        if data["Result"] == 0:
            return "没有请求到数据，请检查您的请求名称后重试？"
        else:
            links = []
            floors = []
            table = []
            for i in range(len(data["Result"]["Exteriors"])):
                x = data["Result"]["Exteriors"][i]
                time_ = x["Time"]
                thread = x["BigPostId"]
                post = x["PostId"]
                title = x["Details"]
                timestamp = datetime.datetime.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
                final_time = convert_time(int(timestamp.timestamp()), "%m月%d日 %H:%M:%S")
                link = f"http://c.tieba.baidu.com/p/{thread}?pid={post}0&cid=0#{post}"
                floor = x["Floor"]
                links.append(link)
                floors.append(floor)
                table.append(template_dh.replace("$num", str(i + 1)).replace("$context", title).replace("$time", final_time))
                num = num + 1
                if num == 10:
                    break
            if len(table) < 1:
                return "唔……没有获取到任何信息！"
            final_table = "\n".join(table)
            html = read(bot_path.VIEWS + "/jx3/trade/dunhao.html")
            font = bot_path.ASSETS + "/font/custom.ttf"
            saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
            saohua = saohua["data"]["text"]
            type_ = type_.replace(",", "+")
            html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"贴吧物价 · {type_}")
            final_html = bot_path.CACHE + "/" + get_uuid() + ".html"
            write(final_html, html)
            final_path = await generate(final_html, False, "table", False)
            return [Path(final_path).as_uri(), links, floors]
