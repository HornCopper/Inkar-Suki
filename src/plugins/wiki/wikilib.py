from urllib import parse
from bs4 import BeautifulSoup

from src.utils.network import Request

import json
import re

"""
状态码：
200 - 正常，含 status(int) 、 link(str) 、 decription(str) 三个参数
201 - 特殊正常，含 status(int) 、 link(str) 两个参数
202 - 搜索正常，含 status(int) 、 api(str) 、 data(list) 两个参数
301 - 重定向正常，含 status(int) 、 redirect(list) 、 link(str) 、 description(str) 四个参数
404 - 未找到，含 status(int) 一个参数
500 - 网站问题，含 status(int) 一个参数
502 - 网站问题，含 status(int) 、 reason(str) 两个参数
"""

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://bj.ke.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def convert(source_string: str):
    return parse.quote(source_string)


class wiki:
    """
    `wiki`插件的核心部分。
    包含了获取API、简单搜索、跨维搜索等。
    """

    @staticmethod
    async def get_site_info(api: str):
        final_link = api + "?action=query&meta=siteinfo&siprop=general&format=json"
        info = (await Request(final_link, headers=headers).get()).json()
        sitename = info["query"]["general"]["sitename"]
        return sitename

    @staticmethod
    async def get_iw_url(api: str, iwprefix: str) -> dict:
        """
        工具型函数：不参与对话
        """
        final_link = api + "?action=query&meta=siteinfo&siprop=interwikimap&sifilteriw=local&format=json"
        data = (await Request(final_link, headers=headers).get()).json()
        for i in data["query"]["interwikimap"]:
            if i["prefix"] == iwprefix:
                return {"status": 200, "data": i["url"]}
        return {"status": 404}

    @staticmethod
    async def extension_checker(api: str, extension: str) -> dict:
        """
        工具型函数：不参与对话
        """
        final_link = api + "?action=query&meta=siteinfo&siprop=extensions&format=json"
        data = (await Request(final_link, headers=headers).get()).json()
        for i in data["query"]["extensions"]:
            if i["name"] == extension:
                return {"status": 200}
        return {"status": 404}

    @staticmethod
    async def get_api(init_link: str) -> dict:
        page_info = (await Request(init_link, headers=headers).get()).text
        api_links = re.findall(
            r"(?im)<\s*link\s*rel=\"EditURI\"\s*type=\"application/rsd\+xml\"\s*href=\"([^>]+?)\?action=rsd\"\s*/?\s*>", page_info)
        api_link = api_links[0]
        try:
            await Request(api_link).get()
        except Exception as _:
            api_link = "http:" + api_link
        if len(api_links) != 1:
            return {"status": 500}
        else:
            return {"status": 200, "data": api_link}

    @staticmethod
    async def simple(api: str, title: str) -> dict | None:
        final_link = api + f"?action=query&titles={title}&prop=extracts&format=json&redirects=True&explaintext=True"
        info = (await Request(final_link, headers=headers).get()).json()
        try:
            page = json.loads(info)
        except Exception as _:
            return {"status": 502, "reason": "该百科的API阻止了我们的连接请求，请过一会儿再试哦~"}

        try:
            iw_flag = page["query"]["interwiki"]
            iw = iw_flag[0]["iw"]
            await wiki.interwiki_search(api, iw, title[len(iw)+1:])
        except Exception as _:
            curid_dict = page["query"]["pages"]
        for i in curid_dict:
            try:
                if page["query"]["pages"][i]["special"] == "":
                    special = True
            except Exception as _:
                special = False
            try:
                if page["query"]["pages"][i]["missing"] == "":
                    missing = True
            except Exception as _:
                missing = False

            if missing and special:
                return {"status": 404}
            elif missing and special is False:
                await wiki.search(api, title)
            elif missing is False and special:
                actually_title = page["query"]["pages"][i]["title"]
                link = api.replace("/api.php", "/index.php") + "?title=" + convert(actually_title)
                desc = ""
                if actually_title != title:
                    return {"status": 301, "redirect": [title, actually_title], "link": link, "desc": desc}
                else:
                    return {"status": 200, "link": link, "desc": desc}
            else:
                actually_title = page["query"]["pages"][i]["title"]
                link = api.replace("/api.php", "/index.php") + "?curid=" + i
                try:
                    desc = page["query"]["pages"][i]["extract"].split("\n")
                    desc = "\n" + desc[0]
                except Exception as _:
                    desc = await wiki.get_wiki_content(api, actually_title)
                    if desc != "":
                        desc = "\n" + desc
                if actually_title != title:
                    return {"status": 301, "redirect": [title, actually_title], "link": link, "desc": desc}
                else:
                    return {"status": 200, "link": link, "desc": desc}

    @staticmethod
    async def interwiki_search(source_wiki: str, interwiki: str, title: str):
        if not await wiki.extension_checker(source_wiki, "Interwiki"):
            return {"status": 201, "link": source_wiki + interwiki + f":{title}"}
        iwdata = await wiki.get_iw_url(source_wiki, interwiki)
        iwlink = iwdata["data"]
        data = await wiki.get_api(iwlink)
        new_api = data["data"]
        await wiki.simple(new_api, title)

    @staticmethod
    async def search(api, title):
        final_link = api + f"?action=query&list=search&format=json&srsearch={title}"
        info = (await Request(final_link, headers=headers).get()).json()
        results = []
        curids = []
        for i in info["query"]["search"]:
            results.append(i["title"])
            curids.append(i["pageid"])
        if len(results) >= 1:
            return {"status": 202, "api": api, "data": [results, curids]}
        else:
            return {"status": 404}

    @staticmethod
    async def get_wiki_content(api, title):
        final_url = api.replace("api.php", "index.php") + "?title=" + title
        data = (await Request(final_url).get()).text
        bs_obj_data = BeautifulSoup(data, "html.parser")
        main_content = bs_obj_data.body.find(id="mw-content-text").find(class_="mw-parser-output") # type: ignore
        div_s = main_content.find_all("div") # type: ignore
        for i in div_s:
            i.decompose()
        text = main_content.get_text() # type: ignore
        ans = re.sub("\n\n+", "\n\n", text).split("\n\n")
        try:
            for i in range(128):
                if len(ans[i]) >= 3:
                    fans = ans[i]
                    if fans[0] == "\n":
                        fans = fans[1:]
                    if fans[-1] == "\n":
                        fans = fans[:-1]
                    return fans
            return ""
        except Exception as _:
            return ""
