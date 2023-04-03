import nonebot
import sys

from bs4 import BeautifulSoup

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"

from utils import get_url

async def get_tieba(thread: int):
    '''
    贴吧内容获取。
    '''
    final_url = f"https://tieba.baidu.com/p/{thread}"
    data = await get_url(final_url)
    if data.find("该帖已被删除") != -1:
        return "唔……该帖子不存在或已被删除。"
    bs = BeautifulSoup(data, 'html.parser')
    title = bs.title.get_text()
    for i in bs.find_all(class_="l_reply_num"):
        reply_count = i.get_text()
        break
    id =  bs.find_all(class_="d_name")[0].get_text().replace("\n","")
    msg = f"标题：{title}\n楼主：{id}\n{reply_count}\n链接：{final_url}"
    return msg