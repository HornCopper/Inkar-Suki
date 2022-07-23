import nonebot, json, sys, re
from urllib import parse
# TOOLS = nonebot.get_driver().config.tools_path
TOOLS = "C:/Users/HornCopper/Inkar-Suki/src/tools"
sys.path.append(TOOLS)
from http_ import http
DATA = TOOLS.replace("tools","data")
'''
状态码：
200 - 正常，含 status(int) 、 link(str) 、 decription(str) 三个参数
201 - 特殊正常，含 status(int) 、 link(str) 两个参数
202 - 搜索正常，含 status(int) 、 data(list) 两个参数
301 - 重定向正常，含 status(int) 、 redirect(list) 、 link(str) 、 description(str) 四个参数
404 - 未找到，含 status(int) 一个参数
500 - 网站问题，含 status(int) 一个参数
'''
class wiki:
    '''
    `wiki`插件的核心部分。
    包含了获取API、简单搜索、跨维搜索等。
    '''
    async def get_iw_url(api: str, iwprefix: str):
        '''
        工具型函数：不参与对话
        '''
        final_link = api + "?action=query&meta=siteinfo&siprop=interwikimap&sifilteriw=local&format=json"
        data = json.loads(await http.get_url(final_link))
        for i in data["query"]["interwikimap"]:
            if i["prefix"] == iwprefix:
                return {"status":200,"data":i["url"]}
        return {"status":404}
        
    async def extension_checker(api: str, extension: str) -> bool:
        '''
        工具型函数：不参与对话
        '''
        final_link = api + "?action=query&meta=siteinfo&siprop=extensions&format=json"
        data = await http.get_url(final_link)
        data = json.loads(data)
        for i in data["query"]["extensions"]:
            if i["name"] == extension:
                return {"status":200}
        return {"status":404}

    async def get_api(init_link: str) -> str:
        page_info = await http.get_url(init_link)
        api_links = re.findall(r"(?im)<\s*link\s*rel=\"EditURI\"\s*type=\"application/rsd\+xml\"\s*href=\"([^>]+?)\?action=rsd\"\s*/\s*>",page_info)
        if len(api_links) != 1:
            return {"status":500}
        else:
            return {"status":200, "data":api_links[0]}
    
    async def simple(api: str, title: str):
        final_link = api + f"?action=query&titles={title}&prop=extracts&format=json&redirects=True&explaintext=True"
        page = json.loads(await http.get_url(final_link))
        try:
            iw_flag = page["query"]["interwiki"]
            iw = iw_flag[0]["iw"]
            return await wiki.interwiki_search(api, iw ,title[len(iw)+1:])
        except:
            curid_dict = page["query"]["pages"]
        for i in curid_dict:
            try:
                if curid_dict[i]["missing"] == "" and title[0:6] != "Special":
                    return await wiki.search(api, title)
                elif curid_dict[i]["missing"] == "" and title[0:6] == "Special":
                    return {"status":404}
            except:
                if title[0:6] == "Special":
                    return {"status":201, "link":api.replace("api","index") + "?title=" + parse.quote(title)}
                link = api.replace("api","index") + "?curid=" + i
                desc = curid_dict[i]["extract"]
                desc = desc.split("\n\n\n")
                desc = desc[0]
                actually_title = curid_dict[i]["title"]
                if actually_title != title:
                    return {"status":301,"redirect":[{title},{actually_title}],"link":link,"description":desc}
                else:
                    return {"status":200,"link":link,"description":desc}

    async def interwiki_search(source_wiki: str, interwiki: str, title: str):
        if wiki.extension_checker(source_wiki, "Interwiki") == False:
            return {"status":201,"link":source_wiki + interwiki + f":{title}"}
        new_api = await wiki.get_api(await wiki.get_iw_url(source_wiki, interwiki))
        return await wiki.simple(new_api, title)

    async def search(api, title):
        final_link = api + f"?action=query&list=search&srsearch={title}"
        info = json.loads(await http.get_url(final_link))
        results = [""]
        curids = [""]
        for i in info["query"]["search"]:
            results.append(i["title"])
            curids.append(i["pageid"])
        return {"status":202,"data":[results,curids]}

async def run():
    print(await wiki.search("https://minecraft.fandom.com/zh/api.php","草"))
import asyncio
asyncio.run(run())