import json
import sys

import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))

global redirect_flag
global redirect_from
global redirect_to
global img_flag
from http_ import http


class apilinks:
    def mcw(msg):
        return f"https://minecraft.fandom.com/zh/api.php?action=query&titles={msg}&prop=extracts&format=json&redirects=True&explaintext=True"

    def wzh(msg):
        return f"https://zh.wikipedia.org/w/api.php?action=query&titles={msg}&prop=extracts&format=json&redirects=True&explaintext=True&variant=zh-cn"
class wikilinks:
    mcw = "https://minecraft.fandom.com/zh/wiki/"
    wzh = "https://zh.wikipedia.org/wiki/"
class curidlinks:
    mcw = "https://minecraft.fandom.com/zh/index.php?curid="
    wzh = "https://zh.wikipedia.org/w/index.php?curid="
async def wiki(title,wiki):
    redirect_flag = False
    redirect_from = None
    redirect_to = None
    url = getattr(apilinks, wiki)(title)
    info = await http.get_url(url)
    info = json.loads(info)
    try:
        info["query"]["interwiki"]
        for i in info["query"]["interwiki"]:
            title = i["title"]
        interwiki_link = getattr(wikilinks, wiki) + title
        iwlink = interwiki_link.replace(" ","_")
        return f"ヾ(≧へ≦)〃 唔..你的搜索跨站了嗷，暂时没办法完成，但是可以给你链接嘞：{iwlink}"
    except:
        curid_json = info["query"]["pages"]
        for i in curid_json:
            if str(i) == "-1":
                return f"ヾ(≧へ≦)〃 你要找的页面不存在哦。"
            else:
                try:
                    info["query"]["redirects"]
                    redirect_flag = True
                    for a in info["query"]["redirects"]:
                        redirect_from = str(a["from"])
                        redirect_to = str(a["to"])
                except:
                    redirect_flag = False
                curid = str(i)
        link = getattr(curidlinks, wiki) + curid
        try:
            all_desc = str(curid_json[curid]["extract"])
            desc = all_desc[:int(all_desc.find("。")+1)]
            if redirect_flag:
                return f"ヾ(≧▽≦*)o  你的输入不准确哦，已经帮你将{redirect_from}重定向到{redirect_to}啦：\n{link}\n{desc}"
            else:
                return f"ヾ(≧▽≦*)o  找到啦：\n{link}\n{desc}"
        except:
            return f"ヾ(≧へ≦)〃 发生了一些错误，是因为这个页面没有分段落造成的，但已经确认页面存在，链接如下：{link}"
    