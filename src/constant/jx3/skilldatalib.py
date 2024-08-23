from pathlib import Path
from typing import Union, Literal, Optional

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.tools.utils import get_url, get_status, get_content
from src.tools.file import read, write
from src.tools.utils.path import CONSTANT, ASSETS

import json
import os

with open(CONSTANT + "/jx3/schoolcolors.json", mode="r", encoding="utf-8") as colors:
    colorList = json.load(colors)

with open(CONSTANT + "/jx3/schoolid.json", mode="r", encoding="utf-8") as school:
    force_list = json.load(school)


def kungfu_to_school(kungfu_name: str) -> Union[str, Literal[False]]:
    with open(CONSTANT + "/jx3/school.json", "r", encoding="utf-8") as f:
        kf_dict = json.load(f)
    for school_name, school_aliases in kf_dict.items():
        if kungfu_name in school_aliases:
            return school_name
        elif kungfu_name == school_name:
            return school_name  # 如果传入参数本身就是键，直接返回该键
    return False


def school_name_aliases(SkillName: str) -> Union[str, Literal[False]]:
    with open(CONSTANT + "/jx3/kungfu.json", "r", encoding="utf-8") as f:
        aliases_dict = json.load(f)

    for kungfu, kungfu_aliases in aliases_dict.items():
        if SkillName in kungfu_aliases:
            return kungfu
    return False


async def get_talents():
    """
    获取所有门派的奇穴。

    数据来源：`JX3BOX` & `JX3API`
    """
    data_list = list(force_list)
    for i in data_list:
        status_code = await get_status(f"https://data.jx3box.com/talent/{i}.json")
        if status_code != 404:
            info = await get_url(f"https://data.jx3box.com/bps/std/{i}/talent.json")
            data = json.loads(info)
            for a in data:
                write(ASSETS + "/jx3/talents/" + a["kungfu"] + ".json", json.dumps(a, ensure_ascii=False))


async def getSkills():
    """
    获取所有门派的技能。

    数据来源：`JX3BOX` & `JX3API`。
    """
    data_list = list(force_list)
    for i in data_list:
        status_code = await get_status(f"https://data.jx3box.com/bps/std/{i}/skill.json")
        if status_code != 404:
            info = await get_url(f"https://data.jx3box.com/bps/std/{i}/skill.json")
            data = json.loads(info)
            for a in data:
                write(ASSETS + "/jx3/skills/" +
                      a["kungfuName"] + ".json", json.dumps(a, ensure_ascii=False))


async def get_icon(skillName: str, type_: str, api_icon: str = "", kungfu: Optional[str] = "") -> Union[str, ms]:
    if kungfu is None:
        raise ValueError("Key value `kungfu` was not found.")
    final_path = ASSETS + "/jx3/icons/" + kungfu + "_" + skillName + ".png"
    if os.path.exists(final_path):
        if type_ == "cq":
            return "[CQ:image,file=" + Path(final_path).as_uri() + "]"
        else:
            return ms.image(Path(final_path).as_uri())
    else:
        api_icon_url = api_icon
        icon = await get_content(api_icon_url)
        cache = open(ASSETS + "/jx3/icons/" + kungfu +
                     "_" + skillName + ".png", mode="wb")
        cache.write(icon)
        cache.close()
        if type_ == "cq":
            return "[CQ:image,file=" + Path(final_path).as_uri() + "]"
        else:
            return ms.image(Path(final_path).as_uri())

async def getSingleSkill(kungfu_name: str, skillName: str):
    final_kungfu_name = school_name_aliases(kungfu_name)
    if final_kungfu_name == "隐龙诀":
        final_kungfu_name = "隐龙决"
    if not final_kungfu_name:
        return False
    try:
        data = json.loads(read(ASSETS + "/jx3/skills/" + final_kungfu_name + ".json"))
    except Exception:
        await getSkills()
        await getSingleSkill(final_kungfu_name, skillName)
    moreInfo = data["remarks"]
    msg = ""
    for i in moreInfo:
        for x in i["forceSkills"]:
            if x["skillName"] == skillName:
                image = await get_icon(x["skillName"], "ms", x["icon"]["FileName"], final_kungfu_name)
                releaseType = x["releaseType"]  # 释放类型
                if releaseType != "瞬间释放":
                    releaseType = releaseType + "释放"
                if releaseType == "":
                    releaseType = "释放时间未知"
                cd = x["cd"]  # 调息时间
                skillName = x["skillName"]  # 技能名
                specialDesc = x["specialDesc"]  # 简单描述
                weapon = x["weapon"]  # 武器
                desc = x["desc"]  # 描述
                simpleDesc = x["simpleDesc"]  # 简单描述，包含伤害/治疗/威胁值等基础信息
                distance = x["distance"]  # 距离
                consumption = x["consumption"]  # 内力消耗
                cheasts = x["cheasts"]  # 秘籍
                skillType = i["remark"]  # 武学派别
                if len(cheasts) == 0:
                    cheastsInfo = "无"
                else:
                    cheastsInfo = ""
                    for y in cheasts:
                        cheastsInfo = cheastsInfo + "\n" + \
                            y["name"] + "：" + y["desc"]
                msg = image + \
                    f"\n技能名：{skillName}\n{releaseType} {cd}\n距离：{distance}\n武器：{weapon}\n内力消耗：{consumption}\n{specialDesc}\n{desc}\n{simpleDesc}\n技能归属：{skillType}\n秘籍：{cheastsInfo}"
                return msg
            continue
    return "没有找到技能哦，请检查后重试~\n也许这是该门派另一个心法的技能哦~"


async def getSingleTalent(Kungfu: str, TalentName: str):
    kungfuname = school_name_aliases(Kungfu)
    if not kungfuname:
        return "此心法不存在哦，请检查后重试~"
    try:
        data = json.loads(
            read(ASSETS + "/jx3/talents/" + kungfuname + ".json"))
    except Exception:
        await get_talents()
        await getSingleTalent(kungfuname, TalentName)
    detail = data["kungfuLevel"]
    correct = {str(i["level"]): i for i in detail}
    for i in range(1, 13):
        Skills = correct[str(i)]["forceSkills"]
        Talents = correct[str(i)]["kungfuSkills"]
        for a in Skills:
            if a["skillName"] == TalentName:
                image = await get_icon(TalentName, "ms", a["icon"]["FileName"], kungfuname)
                releaseType = a["releaseType"]  # 释放类型
                if releaseType != "瞬间释放":
                    releaseType = releaseType + "释放"
                if releaseType == "":
                    releaseType = "释放时间未知"
                cd = a["cd"]  # 调息时间
                skillName = a["skillName"]  # 技能名
                specialDesc = a["specialDesc"]  # 简单描述
                weapon = a["weapon"]  # 武器
                desc = a["desc"]  # 描述
                simpleDesc = a["simpleDesc"]  # 简单描述，包含伤害/治疗/威胁值等基础信息
                distance = a["distance"]  # 距离
                consumption = a["consumption"]  # 内力消耗
                cheasts = a["cheasts"]  # 秘籍
                if len(cheasts) == 0:
                    cheastsInfo = "无"
                else:
                    cheastsInfo = ""
                    for y in cheasts:
                        cheastsInfo = cheastsInfo + "\n" + \
                            y["name"] + "：" + y["desc"]
                msg = f"第{i}重\n" + image + f"\n技能名：{skillName}\n{releaseType} {cd}\n距离：{distance}\n武器：{weapon}\n内力消耗：{consumption}\n{specialDesc}\n{desc}\n{simpleDesc}\n秘籍：{cheastsInfo}"
                return msg
        for a in Talents:
            if a["name"] == TalentName:
                image = await get_icon(TalentName, "ms", a["icon"]["FileName"], kungfuname)
                desc = a["desc"]
                msg = f"第{i}重·{TalentName}\n" + image + f"\n{desc}"
                return msg
    return "没有找到奇穴哦，请检查后重试~"