from pathlib import Path
from typing import Union, Any, List, Optional

from src.constant.jx3 import kungfu_to_school, color_list as colors

from src.tools.database import group_db, AffectionsList
from src.tools.utils.request import get_api
from src.tools.utils.file import read, write
from src.tools.generate import get_uuid, generate
from src.tools.utils.time import convert_time, get_relate_time, get_current_time
from src.tools.config import Config
from src.tools.basic.prompts import PROMPT
from src.tools.basic.server import getGroupServer
from src.tools.utils.path import ASSETS, CACHE, VIEWS

from src.plugins.jx3.bind import get_player_local_data

import random

token = Config.jx3.api.token

def getAffections():
    affections_data: Union[AffectionsList, Any] = group_db.where_one(AffectionsList(), default=AffectionsList())
    return affections_data
    
def storgeAffections(new_data: dict):
    current_data = getAffections()
    current_list = current_data.affections_list
    current_list.append(new_data)
    current_data.affections_list = current_list
    group_db.save(current_data)
    return True
    
def checkUinStatus(uin: int):
    data = getAffections()
    data = data.affections_list
    for i in data:
        if uin in i["uin"]:
            return True
    return False
    
async def getSchool(name: str, server: str):
    data = await get_player_local_data(role_name=name, server_name=server)
    data = data.format_jx3api()
    if data["code"] != 200:
        return False
    else:
        return data["data"]["forceName"]

async def bind_affection(uin_1: int, name_1: str, uin_2: int, name_2: str, group_id: int, custom_time: int):
    if checkUinStatus(uin_1) or checkUinStatus(uin_2):
        return ["唔……您已经绑定情缘了，无法再绑定新的情缘！"]
    server = getGroupServer(str(group_id))
    if not server: 
        return [PROMPT.ServerNotExist]
    school_1 = await getSchool(name_1, server)
    school_2 = await getSchool(name_2, server)
    if not school_1 or not school_2:
        return ["绑定失败，对方或者自己的ID无法对应到角色！\n请检查对面或自身角色是否在本群聊绑定的服务器中！"]
    new_data = {
        "server": server,
        "uin": [uin_1, uin_2],
        "name": [name_1, name_2],
        "time": custom_time,
        "school": [school_1, school_2]
    }
    storgeAffections(new_data)
    return ["成功绑定情缘！\n可通过“查看情缘证书”生成一张情缘证书图！"]

async def delete_affection(uin: int) -> Optional[List[str]]:
    if not checkUinStatus(uin):
        return ["咱就是说，还没绑定情缘，在解除什么呢？"]
    data = getAffections()
    all_list = data.affections_list
    for i in all_list:
        if uin in i["uin"]:
            all_list.remove(i)
            data.affections_list = all_list
            group_db.save(data)
            return ["已解除情缘关系！"]

def getColor(school: str):
    data = colors
    for i in data:
        if kungfu_to_school(i) == school:
            return data[i]
    return "#FFFFFF"

async def generateAffectionImage(uin: int):
    current_data = getAffections().affections_list
    for i in current_data:
        if uin in i["uin"]:
            btxbfont = ASSETS + "/font/包图小白体.ttf"
            yozaifont = ASSETS + "/font/Yozai-Medium.ttf"
            bg = ASSETS + "/image/assistance/" + str(random.randint(1, 9)) + ".jpg"
            uin_1 = i["uin"][0]
            uin_2 = i["uin"][1]
            color_1 = getColor(i["school"][0])
            color_2 = getColor(i["school"][1])
            img_1 = ASSETS + "/image/school/" + i["school"][0] + ".png"
            img_2 = ASSETS + "/image/school/" + i["school"][1] + ".png"
            name_1 = i["name"][0]
            name_2 = i["name"][1]
            server = i["server"]
            recognization = convert_time(i["time"], "%Y年%m月%d日")
            if not isinstance(recognization, str):
                return
            relate = get_relate_time(get_current_time(), i["time"])[:-1]
            html = read(VIEWS + "/jx3/affections/affections.html")
            html = html.replace("$btxbfont", btxbfont).replace("$yozaifont", yozaifont).replace("$bg", bg).replace("$uin1", str(uin_1)).replace("$uin2", str(uin_2)).replace("$color1", color_1).replace("$color2", color_2).replace("$img1", img_1).replace("$img2", img_2).replace("$name1", name_1).replace("$name2", name_2).replace("$server", server).replace("$time", recognization).replace("$relate", relate)
            final_html = CACHE + "/" + get_uuid() + ".html"
            write(final_html, html)
            final_path = await generate(final_html, False, ".background-container", False)
            if not isinstance(final_path, str):
                return
            return Path(final_path).as_uri()
    return ["咱就是说，还没绑定情缘，在生成什么呢？"]