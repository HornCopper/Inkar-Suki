import re

from bs4 import BeautifulSoup as bs

from src.tools.dep import *

async def get_typhoon_list():
    api = "http://typhoon.nmc.cn/weatherservice/typhoon/jsons/list_default"
    typhoon_list = []
    data = await get_url(api)
    for i in json.loads(data[28:-2])["typhoonList"]:
        if "start" in i:
            typhoon_list.append(i[2])
    return typhoon_list if len(typhoon_list) != 0 else False

async def get_typhoon_path(name):
    api = "http://nmc.cn/publish/typhoon/probability.html"
    data = await get_url(api)
    bs_obj = bs(data, "html.parser")
    typhoon_list = bs_obj.find_all(class_="p-wrap")[0].div.ul.find_all("li")
    flag = False
    for i in typhoon_list:
        if i.get_text() == name:
            try:
                if i.a["class"] == "actived":
                    return ["该台风近期已被中央气象台停止编号，搜索失败。"]
            except KeyError:
                pass
            url = "http://nmc.cn" + i.a["href"]
            flag = True
    if not flag:
        return ["未找到您要搜索的台风，请检查名称后重试，或是是否处在近期。"]
    obj_data = await get_url(url)
    new_bs_obj = bs(obj_data, "html.parser")
    imgblock = new_bs_obj.find_all(class_="imgblock")[0]
    imgblock_bs = bs(imgblock, "html.parser")
    img = imgblock_bs.div.img["src"]
    return img

async def get_typhoon_news():
    api = "http://www.nmc.cn/dataservice/typhoon/news.json"
    data = await get_api(api)
    msg = ""
    for i in data["data"]["list"]:
        if i["label"] not in ["","风圈半径"]:
            info = i["label"] + "：" + i["text"] + "\n"
            msg += info
        if i["label"] == "风圈半径":
            round = "风圈半径：\n" + re.sub(r" +", "\n", re.sub(r"：+", "：", re.sub(r"半径 +", "半径：", i["text"]).replace("\u3000","："))).replace("；","；\n") + "\n"
            msg += round
    return msg

async def fy4a_true_color():
    api = "http://nmc.cn/publish/satellite/FY4A-true-color.htm"
    fy4a_data = await get_url(api)
    fy4a_bs = bs(fy4a_data, "htm.parser")
    imgblock = bs(str(fy4a_bs.find_all(class_="imgblock")[0]), "html.parser")
    img = imgblock.div.img["src"]
    return img