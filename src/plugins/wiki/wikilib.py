from urllib import parse
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from src.utils.network import Request


class MediaWikiClient:
    headers = {
        "User-Agent": "Inkar-Suki WikiBot/1.0",
        "Accept": "application/json,text/html,application/xhtml+xml,*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    form_headers = {
        **headers,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    @classmethod
    async def _post(cls, api: str, params: dict, attempts: int = 3) -> dict | None:
        body = parse.urlencode(params)
        for _ in range(attempts):
            try:
                return (
                    await Request(api, headers=cls.form_headers, params=body).post()
                ).json()
            except Exception:
                continue
        return None

    @classmethod
    async def discover_api(cls, page_url: str) -> dict:
        response = await Request(page_url, headers=cls.headers).get()
        soup = BeautifulSoup(response.text, "html.parser")
        edit_uri = soup.find("link", rel="EditURI")
        if edit_uri is not None and edit_uri.get("href"):
            api = urljoin(page_url, str(edit_uri["href"]).split("?", 1)[0])
            return {"status": 200, "data": api}

        parsed = urlparse(str(response.url))
        base_path = parsed.path.rsplit("/", 1)[0]
        api = f"{parsed.scheme}://{parsed.netloc}{base_path}/api.php"
        if parsed.hostname == "wiki.biligame.com":
            return {"status": 200, "data": api}

        validation = await cls._post(
            api,
            {"action": "query", "titles": "Main Page", "format": "json"},
        )
        if validation is None or "query" not in validation:
            return {"status": 500}
        return {"status": 200, "data": api}

    @classmethod
    async def get_site_name(cls, api: str) -> str:
        parsed = urlparse(api)
        hostname = parsed.hostname
        if hostname == "wiki.arcaea.cn":
            return "Arcaea Wiki"
        data = await cls._post(
            api,
            {"action": "query", "meta": "siteinfo", "format": "json"},
        )
        if data is not None:
            site_name = data.get("query", {}).get("general", {}).get("sitename")
            if site_name:
                return site_name
        if hostname == "wiki.biligame.com":
            wiki_id = parsed.path.strip("/").split("/", 1)[0].lower()
            return {
                "jx3": "剑网3 Wiki",
                "mc": "Minecraft Wiki",
            }.get(wiki_id, f"{wiki_id} Wiki" if wiki_id else "Biligame Wiki")
        return hostname or "未知 Wiki"

    @classmethod
    async def get_home_page(cls, api: str) -> str:
        data = await cls._post(
            api,
            {"action": "query", "meta": "siteinfo", "format": "json"},
        )
        if data is None:
            parsed = urlparse(api)
            return f"{parsed.scheme}://{parsed.netloc}"
        return cls.article_url(api, data["query"]["general"]["mainpage"])

    @staticmethod
    def article_url(api: str, title: str) -> str:
        parsed = urlparse(api)
        encoded_title = parse.quote(title.replace(" ", "_"))
        if parsed.hostname == "wiki.biligame.com":
            return api.rsplit("/", 1)[0] + "/" + encoded_title
        if parsed.hostname == "wiki.arcaea.cn":
            return f"{parsed.scheme}://{parsed.netloc}/{encoded_title}"
        return api.replace("/api.php", "/index.php") + "?title=" + encoded_title

    @staticmethod
    def curid_url(api: str, page_id: int | str) -> str:
        return api.replace("/api.php", "/index.php") + f"?curid={page_id}"

    @classmethod
    async def lookup(cls, api: str, title: str) -> dict:
        if ":" in title:
            interwiki = await cls._post(
                api,
                {
                    "action": "query",
                    "titles": title,
                    "redirects": "1",
                    "format": "json",
                },
            )
            if (
                interwiki is not None
                and "query" in interwiki
                and "interwiki" in interwiki["query"]
            ):
                target_url = interwiki["query"]["interwiki"][0]["url"]
                target = await cls.discover_api(target_url)
                if target["status"] == 200:
                    return await cls.lookup(target["data"], title.split(":", maxsplit=1)[1])
                return {"status": 201, "link": target_url}

        data = await cls._post(
            api,
            {
                "action": "parse",
                "page": title,
                "prop": "text",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            },
        )
        if data is None:
            return await cls._lookup_html(api, title)
        if "error" in data:
            return await cls.search(api, title)
        if "parse" not in data:
            return {"status": 502, "reason": "该百科返回了无法识别的数据，请稍后再试。"}

        page = data["parse"]
        description = cls._first_paragraph(page["text"])
        actual_title = page["title"]
        link = cls.curid_url(api, page["pageid"])
        if actual_title != title:
            return {
                "status": 301,
                "redirect": [title, actual_title],
                "link": link,
                "desc": description,
            }
        return {"status": 200, "link": link, "desc": description}

    @classmethod
    async def search(cls, api: str, title: str) -> dict:
        data = await cls._post(
            api,
            {
                "action": "query",
                "list": "search",
                "format": "json",
                "srsearch": title,
            },
        )
        if data is None or "query" not in data:
            return {"status": 502, "reason": "该百科阻止了搜索请求，请稍后再试。"}
        results = [item["title"] for item in data["query"]["search"]]
        page_ids = [item["pageid"] for item in data["query"]["search"]]
        if len(results) == 1:
            return await cls.lookup(api, results[0])
        if results:
            return {"status": 202, "api": api, "data": [results, page_ids]}
        return {"status": 404}

    @classmethod
    async def has_extension(cls, api: str, extension: str) -> bool:
        data = await cls._post(
            api,
            {
                "action": "query",
                "meta": "siteinfo",
                "siprop": "extensions",
                "format": "json",
            },
        )
        if data is None:
            return False
        return any(item["name"] == extension for item in data["query"]["extensions"])

    @classmethod
    async def get_interwiki_url(cls, api: str, prefix: str) -> str | None:
        data = await cls._post(
            api,
            {
                "action": "query",
                "meta": "siteinfo",
                "siprop": "interwikimap",
                "sifilteriw": "local",
                "format": "json",
            },
        )
        if data is None:
            return None
        for item in data["query"]["interwikimap"]:
            if item["prefix"] == prefix:
                return item["url"]
        return None

    @classmethod
    async def lookup_interwiki(cls, api: str, prefix: str, title: str) -> dict:
        if not await cls.has_extension(api, "Interwiki"):
            return {"status": 201, "link": f"{api}{prefix}:{title}"}
        target_url = await cls.get_interwiki_url(api, prefix)
        if target_url is None:
            return {"status": 404}
        target = await cls.discover_api(target_url)
        if target["status"] != 200:
            return {"status": 502, "reason": "无法连接到目标百科。"}
        return await cls.lookup(target["data"], title)

    @classmethod
    async def _lookup_html(cls, api: str, title: str) -> dict:
        link = cls.article_url(api, title)
        response = await Request(link, headers=cls.headers).get()
        if response.status_code == 404:
            return {"status": 404}
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.select_one("#mw-content-text .mw-parser-output")
        if content is None:
            return {"status": 502, "reason": "该百科阻止了连接请求，请稍后再试。"}
        description = cls._first_paragraph(str(content))
        heading = soup.select_one("#firstHeading")
        actual_title = heading.get_text(strip=True) if heading else title
        result = {
            "status": 200,
            "link": str(response.url),
            "desc": description,
        }
        if actual_title != title:
            result.update(status=301, redirect=[title, actual_title])
        return result

    @staticmethod
    def _first_paragraph(html: str) -> str:
        content = BeautifulSoup(html, "html.parser")
        for element in content.select("style, script, table, .mw-empty-elt, .navbox"):
            element.decompose()
        paragraph = next(
            (
                item
                for item in content.select(".mw-parser-output > p")
                if item.get_text(strip=True)
            ),
            content.find("p"),
        )
        return f"\n{paragraph.get_text(' ', strip=True)}" if paragraph else ""


class wiki:
    """兼容既有 Wiki 命令入口的 MediaWiki 操作接口。"""

    get_api = MediaWikiClient.discover_api
    get_site_info = MediaWikiClient.get_site_name
    get_home_page = MediaWikiClient.get_home_page
    simple = MediaWikiClient.lookup
    search = MediaWikiClient.search
    interwiki_search = MediaWikiClient.lookup_interwiki

    @staticmethod
    async def extension_checker(api: str, extension: str) -> dict:
        available = await MediaWikiClient.has_extension(api, extension)
        return {"status": 200 if available else 404}

    @staticmethod
    async def get_iw_url(api: str, prefix: str) -> dict:
        url = await MediaWikiClient.get_interwiki_url(api, prefix)
        if url is None:
            return {"status": 404}
        return {"status": 200, "data": url}

    @staticmethod
    async def get_wiki_content(api: str, title: str) -> str:
        result = await MediaWikiClient._lookup_html(api, title)
        return result["desc"].removeprefix("\n") if "desc" in result else ""
