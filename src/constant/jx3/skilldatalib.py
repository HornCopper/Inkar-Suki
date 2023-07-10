import json
from src.tools.dep.bot import *
from urllib.error import HTTPError
from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment


from src.tools.utils import get_url, get_status, nodetemp, get_content, get_api
from src.tools.file import read, write
from src.tools.config import Config
__kf_dict = {
    '凌雪': ["隐龙决","隐龙诀","凌雪","凌雪阁"],
    '万花': ["花间游", "离经易道", "花间", "奶花"],
    '天策': ["傲血战意", "铁牢律", "马男", "傲血", "铁牢"],
    '纯阳': ["紫霞功", "太虚剑意"],
    '七秀': ["云裳心经", "冰心诀", "bx", "qx", "nx", "奶秀", "冰心"],
    '五毒': ["毒经", "补天诀", "补天", "奶毒", "毒姐", "dj"],
    '唐门': ["惊羽诀", "天罗诡道", "田螺", "鲸鱼", "惊羽"],
    '藏剑': ["问水诀", "山居剑意", "二少", "叽哥","KFC","藏剑"],
    '明教': ["焚影圣诀", "明尊琉璃体", "喵哥"],
    '苍云': ["分山劲", "铁骨衣", "岔劲"],
    '长歌': ["莫问", "相知", "咕咕"],
    '霸刀': ["北傲诀","霸刀"],
    '蓬莱': ["凌海诀", "伞爹", "伞宗","蓬莱"],
    '少林': ["洗髓经", "易筋经", "和尚", "大师"],
    '衍天': ["太玄经", "衍天宗", "灯皇","衍天"],
    '药宗': ["无方", "灵素", "狍子"],
    '刀宗': ["孤锋诀", "刀爹", "呆宗", "刀宗"],
    '丐帮': ["丐帮", "笑尘决", "笑尘诀", "笑尘"]
}
kf_dict = {}
for x in __kf_dict:
    for y in __kf_dict[x]:
        kf_dict[y] = x
    kf_dict[x] = x


def kftosh(kf: str) -> str:
    return kf_dict.get(kf) or False


def aliases(SkillName: str) -> str:
    if SkillName in ["隐龙诀", "隐龙决", "隐龙", "凌雪", "凌雪阁"]:
        return "隐龙诀"
    elif SkillName in ["花间", "花间游"]:
        return "花间游"
    elif SkillName in ["奶花", "花奶", "离经", "离经易道"]:
        return "离经易道"
    elif SkillName in ["傲雪", "傲血", "傲血战意"]:
        return "傲血战意"
    elif SkillName in ["天策T", "策T", "铁牢", "铁牢律", "策t", "天策t", "TCT", "tct"]:
        return "铁牢律"
    elif SkillName in ["气纯", "紫霞功", "紫霞", "qc", "QC"]:
        return "紫霞功"
    elif SkillName in ["剑纯", "太虚剑意", "jc", "JC"]:
        return "太虚剑意"
    elif SkillName in ["奶秀", "秀奶", "云裳心经", "云裳"]:
        return "云裳心经"
    elif SkillName in ["冰心", "冰心诀", "冰心决", "BX", "bx"]:
        return "冰心诀"
    elif SkillName in ["毒经", "dj", "DJ", "Dj"]:
        return "毒经"
    elif SkillName in ["奶毒", "毒奶", "补天诀", "补天决", "补天"]:
        return "补天诀"
    elif SkillName in ["惊羽诀", "惊羽决", "鲸鱼", "惊羽"]:
        return "惊羽诀"
    elif SkillName in ["天罗诡道", "田螺", "天罗", "tl", "TL"]:
        return "天罗诡道"
    elif SkillName in ["问水诀", "问水决", "问水", "轻剑", "山居剑意", "山居", "重剑", "叽", "KFC", "kfc", "肯德基", "疯狂星期四", "v我50", "二少", "二小姐", "黄鸡", "鸡", "鲲", "坤", "叽哥", "鸡哥"]:
        return "问水诀"
    elif SkillName in ["丐帮", "笑尘决", "笑尘诀", "笑尘"]:
        return "笑尘诀"
    elif SkillName in ["焚影圣诀", "焚影圣决", "焚影"]:
        return "焚影圣诀"
    elif SkillName in ["明教T", "喵T", "明尊", "明尊琉璃体", "明教t", "明尊t", "喵t", "mt", "MT"]:
        return "明尊琉璃体"
    elif SkillName in ["苍云T", "铁骨", "铁骨衣", "铁骨1", "苍t", "苍云t", "盾T", "盾t", "cyt", "CYT"]:
        return "铁骨衣"
    elif SkillName in ["分山劲", "分山", "岔劲"]:
        return "分山劲"
    elif SkillName in ["莫问"]:
        return "莫问"
    elif SkillName in ["奶歌", "歌奶", "相知", "奶咕"]:
        return "相知"
    elif SkillName in ["北傲决", "北傲诀", "霸刀", "北傲"]:
        return "北傲诀"
    elif SkillName in ["蓬莱", "凌海", "凌海诀"]:
        return "凌海诀"
    elif SkillName in ["洗髓经", "洗髓", "和尚T", "秃T", "和尚t", "大师t", "大师T"]:
        return "洗髓经"
    elif SkillName in ["易筋经", "易筋"]:
        return "易筋经"
    elif SkillName in ["衍天", "衍天宗", "太玄经", "太玄"]:
        return "太玄经"
    elif SkillName in ["奶药", "药奶", "灵素"]:
        return "灵素"
    elif SkillName in ["无方"]:
        return "无方"
    elif SkillName in ["刀宗", "孤锋诀", "孤锋"]:
        return "孤锋诀"
    else:
        return False


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
            return MessageSegment.image(Path(final_path).as_uri())
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
            return MessageSegment.image(Path(final_path).as_uri())


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
        kungfu == "隐龙决"  # 由于`JX3Box`的`API`的数据错误问题，目前只能这样适配，等到数据纠正后删除这块代码。
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
