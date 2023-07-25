from bs4 import BeautifulSoup
from src.tools.utils import get_url

<<<<<<< HEAD
words = ["避雷","骗子","【818】","跑单"]
=======
>>>>>>> 373c826e40363761fc1455e30b8c8d0d6ef1d5d0

async def verify_cheater(content):
    url = f"https://tieba.baidu.com/f/search/res?ie=utf-8&qw={content}"
    dt = await get_url(url)
    bs_obj = BeautifulSoup(dt, "html.parser")
    list_ = bs_obj.find(class_="s_post_list")
    try:
        objects = list_.find_all(class_="s_post")
    except:
        return False
    for i in objects:
<<<<<<< HEAD
        content = i.find(class_ = "p_content").get_text()
        title = i.find(class_ = "bluelink").string
        url = "https://tieba.baidu.com" + i.find(class_ = "bluelink")["href"]
        for x in words:
            if content.find(x) != -1 or title.find(x) != -1:
                return url
    return False
=======
        content = i.find(class_="p_content").get_text()
        title = i.find(class_="bluelink").string
        url = "https://tieba.baidu.com" + i.find(class_="bluelink")["href"]
        if content.find("骗子") != -1 or title.find("骗子") != -1:
            return url
    return False
>>>>>>> 373c826e40363761fc1455e30b8c8d0d6ef1d5d0
