from pathlib import Path

from src.tools.utils.request import post_url
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.file import read, write
from src.tools.generate import get_uuid, generate

import json
import re

api = "https://www.j3sl.com/entity/wujie.php"

def extract_numbers(string):
    pattern = r"\d+"
    numbers = re.findall(pattern, string)
    return [int(num) for num in numbers]
 
def convertAttrs(raw: str):
    # 手搓关键词提取
    def fd(raw: str, to: str):
        if raw.find(to) != -1:
            return True
        return False

    raw = raw.replace("攻击", "")
    raw = raw.replace("攻", "")
    raw = raw.replace("品", "")

    more = []

    # 基础类型 内外功
    if fd(raw, "外"):
        basic = "外功"
    elif fd(raw, "内"):
        basic = "内功"
    else:
        return False

    more.append(basic + "攻击")

    # 基础类型 会心 破防 无双 破招（不存在纯破招无封）
    if fd(raw, "纯会"):
        if basic == "外功":
            more.append(basic + "会心")
        else:
            more.append("全会心")
    if fd(raw, "纯无"):
        more.append("无双")
    if fd(raw, "纯破"):
        more.append(basic + "破防")

    # 双会类
    if fd(raw, "双会") or fd(raw, "会心会效") or fd(raw, "会会"):
        if basic == "外功":
            more.append(basic + "会心")
            more.append(basic + "会心效果")
        else:
            more.append("全会心")
            more.append("全会心效果")

    # 双会可能出现的组合
    if fd(raw, "破") and not fd(raw, "纯破") and not fd(raw, "破招"):
        more.append(basic + "破防")
    
    if fd(raw, "招") or fd(raw, "破破"):
        more.append("破招")
    
    if fd(raw, "无") and not fd(raw, "纯无"):
        more.append("无双")
    
    # 会心
    if fd(raw, "会") and not fd(raw, "双会") and not fd(raw, "纯会") and not fd(raw, "会效") and not fd(raw, "会心会效") and not fd(raw, "会会"):
        if basic == "外功":
            more.append(basic + "会心")
        else:
            more.append("全会心")

    num_list = extract_numbers(raw)
    if len(num_list) != 1:
        return False
    
    # 部位
    place = ""

    quality = num_list[0]
    
    if fd(raw, "头") or fd(raw, "帽") or fd(raw, "脑壳"):
        place = "头饰"
    elif fd(raw, "手") or fd(raw, "臂"):
        place = "护臂"
    elif fd(raw, "裤") or fd(raw, "下装"):
        place = "裤"
    elif fd(raw, "鞋") or fd(raw, "jio") or fd(raw, "脚"):
        place = "鞋"
    elif fd(raw, "链") or fd(raw, "项"):
        place = "项链"
    elif fd(raw, "坠") or fd(raw, "腰"):
        if not fd(raw, "腰带"):
            place = "腰坠"
    elif fd(raw, "暗器") or fd(raw, "囊") or fd(raw, "弓弦"):
        place = "囊"
    else:
        return False

    return [more, place, quality]

async def getCurrentOnSale():
    ...

raw_data = {
    "头饰": 0,
    "护臂": 3,
    "裤": 4,
    "鞋": 5,
    "项链": 6,
    "腰坠": 7,
    "囊": "a"
}

def processAttributes(raw_attributes: list):
    new = []
    for i in raw_attributes:
        i: str
        if i.find("攻击") == -1:
            new.append(
                i
                .replace("全", "")
                .replace("外功", "")
                .replace("内功", "")
                .replace("会心效果", "会效")
            )
    return new

def checkType(raw_attributes: list):
    for i in raw_attributes:
        if i.find("内功") != -1:
            return "内功"
        if i.find("外功") != -1:
            return "外功"
    return False

def convertPositionToNum(raw_position: str):
    return raw_data[raw_position]

def convertPositionName(raw_name: str):
    dictionary = {
        "头饰": "帽子",
        "护臂": "护腕",
        "裤": "裤子",
        "鞋": "鞋子",
        "项链": "项链",
        "腰坠": "腰坠",
        "囊": "暗器"
    }
    return dictionary[raw_name]

async def checkAttributesAtQuality(type: str, quality: int, attributes: list, position: str):
    standardName = convertPositionName(position)
    params = {
        "action": "get_search",
        "data[xinfa]": type,
        "data[pos]": standardName,
        "data[quality]": quality
    }
    data = await post_url(api, data=params)
    data = json.loads(data)
    for i in data["data"]:
        if set(i.split(" ")) == set(attributes):
            return i
    return False

template_sl = """
<tr>
    <td class="short-column"><img src="https://www.j3sl.com/image/$Po.png"></td>
    <td class="short-column name">$N</td>
    <td class="short-column">$Q</td>
    <td class="short-column attributes">$A</td>
    <td class="short-column">$Ty</td>
    <td class="short-column">$S</td>
    <td class="short-column">$Pi</td>
    <td class="short-column">$Ti</td>
</tr>
"""

async def getSingleEquipment(raw_message: str):
    judgeResult = convertAttrs(raw_message)
    if not judgeResult:
        return [f"您输入的装备词条有误，请确保包含以下四个要素：\n品级、属性、部位、内外功\n示例：13550内功双会头"]
    equipmentType = checkType(judgeResult[0])
    equipmentAttributes = processAttributes(judgeResult[0])
    equipmentQuality = int(judgeResult[2])
    equipmentPositionNum = convertPositionToNum(judgeResult[1])
    correctAttributes = await checkAttributesAtQuality(equipmentType, equipmentQuality, equipmentAttributes, judgeResult[1])
    if correctAttributes == False:
        equipmentAttributes_str = " ".join(equipmentAttributes)
        return [f"唔……在{equipmentQuality}品级阶段不存在属性为[{equipmentAttributes_str}]的无封装备！"]
    params = {
        "action": "get_chart_data",
        "data[xinfa]": equipmentType,
        "data[pos]": equipmentPositionNum,
        "data[quality]": equipmentQuality,
        "data[property]": correctAttributes,
        "data[offset]": 0,
        "data[limit]": 8,
        "data[order]": "id desc"
    }
    data = await post_url(api, data=params)
    data = json.loads(data)
    if data["data"] == []:
        return ["唔……已找到该属性无封装备，但没有数据。"]
    contents = []
    for i in data["data"]:
        image = i["image"]
        quality = i["quality"]
        type = i["xinfa"]
        attributes = i["property"]
        server = i["service"]
        price = str(i["price"]) + str(i["price_type"])
        time = i["created_time"]
        name = "无封" + judgeResult[1]
        contents.append(
            template_sl
                .replace("$Po", image)
                .replace("$N", name)
                .replace("$Q", quality)
                .replace("$A", attributes)
                .replace("$Ty", type)
                .replace("$S", server)
                .replace("$Pi", price)
                .replace("$Ti", time)
        )
    final_table = "\n".join(contents)
    html = read(VIEWS + "/jx3/trade/sl.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "数据来源：www.j3sl.com"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f" · 无封查询")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()