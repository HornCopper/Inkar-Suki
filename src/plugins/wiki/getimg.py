import sys
from pathlib import Path

from bs4 import BeautifulSoup

TOOLS = Path(__file__).resolve().parent.parent.parent / "tools"
sys.path.append(str(TOOLS))
from http_ import http


class main:
    async def mcw(title):
        url = f"https://minecraft.fandom.com/zh/wiki/{title}"
        html = await http.get_url(url)
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        for x in soup.find_all(class_="infobox-imagearea"):
            soup_ = BeautifulSoup(str(x), 'html.parser')
            for y in soup_.find_all(class_="image"):
                tag = str(y['href'])
                images.append(tag[:tag.find("/revision")])
        return images

    async def wzh(title):
        url = f"https://zh.wikipedia.org/wiki/{title}"
        html = await http.get_url(url)
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        for x in soup.find_all(class_="infobox biota"):
            soup2 = BeautifulSoup(str(x), 'html.parser')
            for y in soup2.find_all(style="text-align: center"):
                soup3 = BeautifulSoup(str(y), 'html.parser')
                for z in soup3.find_all(decoding="async"):
                    filename = str(z["alt"]).replace(" ","_")
                    src = z["src"]
                    src = src[:src.find(filename)+len(filename)]
                    src = "https"+src
                    images.append(src)
        return images