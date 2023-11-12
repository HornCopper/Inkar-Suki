import json
from src.tools.dep.bot import *
from urllib.error import HTTPError
from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment


from src.tools.utils import get_url, get_status, nodetemp, get_content, get_api
from src.tools.file import read, write
from src.tools.config import Config
from .Kunfu import Kunfu
from .School import School
from sgtpyutils.extensions.clazz import *


current = pathlib2.Path(__file__).parent
db_school = filebase_database.Database(str(current.joinpath('./config.school'))).value  # 门派数据
dict_school: dict[str, Kunfu] = dict([[x.get('name'), dict2obj(School(), x)]
                                     for x in db_school])  # 门派字典
dict_alias_school: dict[str, str] = {}  # 门派对应别称
for x in dict_school:
    alias = dict_school[x].alias
    for a in alias:
        dict_alias_school[a] = x


db_kunfu = filebase_database.Database(str(current.joinpath('./config.kunfu'))).value  # 心法数据
dict_kunfu: dict[str, Kunfu] = dict([[x.get('name'), dict2obj(Kunfu(), x)]
                                     for x in db_kunfu])  # 心法字典
dict_alias_kunfu: dict[str, str] = {}  # 心法对应别称
for x in dict_kunfu:
    alias = dict_kunfu[x].alias
    for a in alias:
        dict_alias_kunfu[a] = x


def kftosh(kf: str) -> str:
    '''
    将门派别名转换为门派名称
    '''
    return dict_alias_school.get(kf)


def kftoschool(kf: str) -> School:
    '''
    将门派别名转换为门派
    '''
    x = kftosh(kf)
    return x and dict_school[x]


def std_kunfu(kf_alias: str) -> Kunfu:
    '''
    将心法别称转换为标准心法
    '''
    name = aliases(kf_alias)
    if not name:
        return None
    return dict_kunfu.get(name)


def aliases(SkillName: str) -> str:
    '''
    将心法别称转换为标准心法名
    '''
    return dict_alias_kunfu.get(SkillName)


async def getTalents():
    '''
    获取所有门派的奇穴。

    数据来源：`JX3BOX` & `JX3API`
    '''
    force_list = await get_api("https://inkar-suki.codethink.cn/jx3boxdata")
    data_list = []
    for i in force_list:
        data_list.append(i)
    for i in data_list:
        if await get_status(url=f"https://data.jx3box.com/talent/{i}.json") != 404:
            info = await get_url(url=f"https://data.jx3box.com/bps/std/{i}/talent.json")
            data = json.loads(info)
            for a in data:
                write(ASSETS + "/jx3/talents/" +
                      a["kungfu"] + ".json", json.dumps(a, ensure_ascii=False))


async def getSkills():
    '''
    获取所有门派的技能。

    数据来源：`JX3BOX` & `JX3API`。
    '''
    force_list = await get_api("https://inkar-suki.codethink.cn/jx3boxdata")
    data_list = []
    for i in force_list:
        data_list.append(i)
    for i in data_list:
        if await get_status(url=f"https://data.jx3box.com/bps/std/{i}/skill.json") != 404:
            info = await get_url(url=f"https://data.jx3box.com/bps/std/{i}/skill.json")
            data = json.loads(info)
            for a in data:
                write(ASSETS + "/jx3/skills/" +
                      a["kungfuName"] + ".json", json.dumps(a, ensure_ascii=False))


async def get_icon(skillName: str, type_: str, api_icon: str = None, kungfu: str = None) -> str:
    if kungfu == None:
        raise ValueError("Key value `kungfu` was not found.")
    final_path = ASSETS + "/jx3/icons/" + kungfu + "_" + skillName + ".png"
    if os.path.exists(final_path):
        if type_ == "cq":
            return "[CQ:image,file=" + Path(final_path).as_uri() + "]"
        else:
            return ms.image(Path(final_path).as_uri())
    else:
        api_icon_url = api_icon
        try:
            icon = await get_content(api_icon_url)
        except:
            raise HTTPError(msg="Can't connect to " + api_icon_url + ".")
        cache = open(ASSETS + "/jx3/icons/" + kungfu +
                     "_" + skillName + ".png", mode="wb")
        cache.write(icon)
        cache.close()
        if type_ == "cq":
            return "[CQ:image,file=" + Path(final_path).as_uri() + "]"
        else:
            return ms.image(Path(final_path).as_uri())


async def getAllSkillsInfo(Kungfu: str) -> str:
    '''
    获取心法下所有技能。
    '''
    Kungfu = aliases(Kungfu)
    if Kungfu == "隐龙诀":
        Kungfu == "隐龙决"  # 由于`JX3Box`的`API`的数据错误问题，目前只能这样适配，等到数据纠正后删除这块代码。
    skill = read(ASSETS + "/jx3/skills/" + Kungfu + ".json")
    if skill == False:
        await getSkills()
        await getAllSkillsInfo(Kungfu)
    if Kungfu == False:
        return False
    skills = json.loads(skill)
    node = []
    moreInfo = skills["remarks"]
    for i in moreInfo:
        for x in i["forceSkills"]:
            image = await get_icon(x["skillName"], "cq", x["icon"]["FileName"], Kungfu)
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
                        y["name"] + "\n" + y["desc"] + "\n"
            msg = image + \
                f"\n技能名：{skillName}\n{releaseType} {cd}\n距离：{distance}\n武器：{weapon}\n内力消耗：{consumption}\n{specialDesc}\n{desc}\n{simpleDesc}\n技能归属：{skillType}\n秘籍：{cheastsInfo}"
            node.append(nodetemp(f"{Kungfu}技能", Config.bot[0], msg))
    return node


async def getSingleSkill(kungfu: str, skillName: str):
    kungfu = aliases(kungfu)
    if kungfu == "隐龙诀":
        kungfu == "隐龙决"  # 由于`JX3Box`的`API`的数据错误问题，目前只能这样适配，等到数据纠正后删除这块代码。其实是推栏的代码错了笑死。
    if kungfu == False:
        return False
    try:
        data = json.loads(read(ASSETS + "/jx3/skills/" + kungfu + ".json"))
    except:
        await getSkills()
        await getSingleSkill(kungfu, skillName)
    moreInfo = data["remarks"]
    msg = ""
    for i in moreInfo:
        for x in i["forceSkills"]:
            if x["skillName"] == skillName:
                image = await get_icon(x["skillName"], "ms", x["icon"]["FileName"], kungfu)
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
    kungfuname = aliases(Kungfu)
    if kungfuname == False:
        return "此心法不存在哦，请检查后重试~"
    try:
        data = json.loads(
            read(ASSETS + "/jx3/talents/" + kungfuname + ".json"))
    except:
        await getTalents()
        await getSingleTalent(kungfuname, TalentName)
    correct = {}
    detail = data["kungfuLevel"]
    for i in detail:
        correct[str(i["level"])] = i
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
