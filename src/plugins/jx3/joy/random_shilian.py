from random import randint, choice
from pydantic import BaseModel
from jinja2 import Template

from nonebot.adapters.onebot.v11 import Bot

from src.const.path import ASSETS, TEMPLATES
from src.utils.network import Request, cache_image
from src.utils.analyze import match
from src.utils.file import read
from src.utils.generate import generate
from src.utils.database.operation import get_group_settings
from src.plugins.jx3.trade.trade import JX3Trade
from src.templates import get_saohua

from .random_item import (
    JX3ShilianItem,
    get_random,
    item_colors,
    books
)

from ._template import (
    template_shilian_box,
    template_shilian_single
)

base_items = {
    "银叶子": JX3ShilianItem(
        color = item_colors[1],
        name = "银叶子·试炼之地",
        icon = "https://icon.jx3box.com/icon/77.png"
    ),
    "九花玉露散": JX3ShilianItem(
        color = item_colors[3],
        name = "九花玉露散",
        icon = "https://icon.jx3box.com/icon/1351.png"
    )
}

final_items = {
    "五行石": JX3ShilianItem(
        color = item_colors[2],
        name = "五行石（一级）",
        icon = "https://icon.jx3box.com/icon/7523.png"
    ),
    "侠行点": JX3ShilianItem(
        color = item_colors[2],
        name = "匡义令·星",
        icon = "https://icon.jx3box.com/icon/726.png"
    ),
    # "泠泉喵": JX3ShilianItem(
    #     color = item_colors[5],
    #     name = "泠泉喵",
    #     icon = "https://inkar-suki.codethink.cn/0qm.jpg"
    # )
}

friend_materials = {
    "茶饼": JX3ShilianItem(
        color = item_colors[4],
        name = "上品茶饼·兑",
        icon = "https://icon.jx3box.com/icon/4433.png"
    ),
    "丹": JX3ShilianItem(
        color = item_colors[4],
        name = "维峰丹",
        icon = "https://icon.jx3box.com/icon/7660.png"
    )
}

daily_materials = {
    "硼砂": JX3ShilianItem(
        color = item_colors[3],
        name = "硼砂",
        icon = "https://icon.jx3box.com/icon/203.png"
    ),
    "人参": JX3ShilianItem(
        color = item_colors[3],
        name = "人参",
        icon = "https://icon.jx3box.com/icon/937.png"
    ),
    "蜂王浆": JX3ShilianItem(
        color = item_colors[4],
        name = "蜂王浆",
        icon = "https://icon.jx3box.com/icon/7615.png"
    ),
    "沉香木": JX3ShilianItem(
        color = item_colors[4],
        name = "沉香木",
        icon = "https://icon.jx3box.com/icon/7621.png"
    ),
    "猫眼石": JX3ShilianItem(
        color = item_colors[4],
        name = "猫眼石",
        icon = "https://icon.jx3box.com/icon/8841.png"
    )
}

boxes = {
    "凌雪藏锋": JX3ShilianItem(
        color = item_colors[4],
        name = "福禄宝箱·凌雪藏锋",
        icon = "https://icon.jx3box.com/icon/4242.png"
    ),
    "北天药宗": JX3ShilianItem(
        color = item_colors[4],
        name = "福禄宝箱·北天药宗",
        icon = "https://icon.jx3box.com/icon/4242.png"
    ),
    "雾海寻龙": JX3ShilianItem(
        color = item_colors[4],
        name = "福禄宝箱·雾海寻龙",
        icon = "https://icon.jx3box.com/icon/4242.png"
    )
}

level_to_quality = [
    [24500, 25500, 28000],
    [25500, 28000, 30200]
]

class Equipment(BaseModel):
    attr: str
    bind_type: int
    icon: str
    name: str
    quality: int

    def __eq__(self, other):
        if not isinstance(other, Equipment):
            return False
        return (self.attr == other.attr and
                self.name == other.name and
                self.quality == other.quality)

    def __hash__(self):
        return hash((self.attr, self.name, self.quality))

class DataCache:
    wuxiu_list: list[Equipment] = []
    def __init__(self): ...

    @classmethod
    async def get_wuxiu(cls, name: str, quality: int, bind_type: int) -> Equipment:
        matched = [e for e in cls.wuxiu_list if match(e, name=name, quality=quality, bind_type=bind_type)]
        if matched:
            return choice(matched)
        params = {
            "keyword": name,
            "MinLevel": quality,
            "MaxLevel": quality,
            "BindType": bind_type,
            "per": 50,
            "page": 1,
            "client": "std"
        }
        url = "https://node.jx3box.com/api/node/item/search"
        data = (await Request(url, params=params).get()).json()
        results: list[dict] = data["data"]["data"]
        for e in results:
            attribute = e["attributes"]
            if attribute == []:
                attr = ""
            else:
                attr = " ".join(
                    [
                        (attr["label"].split("提高" if "提高" in attr["label"] else "增加")[0]).replace("等级", "").replace("值", "")
                        for attr in e["attributes"]
                        if attr.get("color") == "green"
                    ]
                )
            new_equipment = Equipment(
                attr = attr,
                bind_type = bind_type,
                icon = "https://icon.jx3box.com/icon/" + str(e["IconID"]) + ".png",
                name = name,
                quality = quality
            )
            cls.wuxiu_list.append(new_equipment)
        final_equip = choice(results)
        final_attr = " ".join(
            [
                (attr["label"].split("提高" if "提高" in attr["label"] else "增加")[0]).replace("等级", "").replace("值", "")
                for attr in final_equip["attributes"]
                if attr.get("color") == "green"
            ]
        )
        return Equipment(
            attr = final_attr,
            bind_type = bind_type,
            icon = "https://icon.jx3box.com/icon/" + str(final_equip["IconID"]) + ".png",
            name = name,
            quality = quality
        )

async def get_random_equip(level: int) -> JX3ShilianItem: # 无修
    quality = choice(
        level_to_quality[int(level > 61)]
    )
    location = choice(
        ["冠", "鞋", "链", "坠", "囊"]
    )
    bind_type = 3 if get_random(70) else 2
    end_word = "玄" if quality > 25500 else "荒"
    equip_type = "内" if get_random(50) else "外"
    final_name = f"{JX3Trade.shilian_basic}{location}·{equip_type}·{end_word}"
    final_equip = await DataCache.get_wuxiu(final_name, quality, bind_type)
    return JX3ShilianItem(
        attr = final_equip.attr,
        icon = final_equip.icon,
        name = final_equip.name,
        bind = "不可交易" if bind_type == 3 else "可交易",
        quality = final_equip.quality
    )

def get_random_book() -> JX3ShilianItem: # 秘籍
    book = choice(
        list(
            books.keys()
        )
    )
    return JX3ShilianItem(
        icon = books[book],
        name = book
    )

async def get_random_stone(simplified: bool = False) -> JX3ShilianItem: # 五彩石
    if not simplified:
        level = choice(
            [4, 4, 4, 4, 4, 4, 5, 5, 5, 6]
        )
        params = {
            "per": 20,
            "page": randint(1, 74),
            "level": level
        }
        url = "https://node.jx3box.com/enchant/stone"
        data = (await Request(url, params=params).get()).json()
        stones: list[dict] = data["list"]
        stone = choice(stones)
        return JX3ShilianItem(
            color = item_colors[3 if level == 4 else 4],
            icon = "https://icon.jx3box.com/icon/" + str(stone["icon"]) + ".png",
            name = stone["Name"]
        )
    else:
        level = choice([4, 5, 6])
        keyword = choice(["济世", "守护", "击破"])
        params = {
            "per": 20,
            "page": 1,
            "level": level,
            "search": keyword
        }
        url = "https://node.jx3box.com/enchant/stone"
        data = (await Request(url, params=params).get()).json()
        stones: list[dict] = data["list"]
        stone = choice(stones)
        return JX3ShilianItem(
            color = item_colors[3 if level == 4 else 4],
            icon = "https://icon.jx3box.com/icon/" + str(stone["icon"]) + ".png",
            name = stone["Name"]
        )

async def get_third_item(level: int, group_id: int, bot: Bot) -> JX3ShilianItem:
    """
    试炼之地第三项奖励生成。

    Params:
        level(int): 层数
    """
    if get_random(15): # 无修
        return await get_random_equip(level)
    
    if get_random(15): # 福禄宝箱
        return choice(
            list(boxes.values())
        )
    
    if get_random(20): # 红尘侠影
        num = randint(1, 100)
        if num <= 40: # 茶饼
            return friend_materials["茶饼"]
        elif 40 < num <= 90: # 丹
            return friend_materials["丹"]
        else: # 秘籍
            return get_random_book()
    
    if get_random(30): # 五彩石
        num = randint(1, 100)
        return await get_random_stone(num <= 5)    
    
    if get_random(35): # 生活材料
        return choice(
            list(
                daily_materials.values()
            )
        )
    
    # if get_random(1): # 泠泉喵
    #     return final_items["泠泉喵"]
    
    if get_random(100): # 群友
        if "群友试炼" in get_group_settings(group_id, "additions"):
            members = await bot.get_group_member_list(group_id = group_id)
            members = [m for m in members if m["role"] in ["admin", "owner"]]
            member = choice(members)
            return JX3ShilianItem(
                color = item_colors[5],
                icon = "https://q.qlogo.cn/headimg_dl?dst_uin=" + str(member["user_id"]) + "&spec=100&img_type=jpg",
                name = (member["card"] or member["nickname"])[:15]
            )
    
    final_item = choice(
        list(
            final_items.values()
        )
    )
    return final_item

async def get_single_full_reward(level: int, group_id: int, bot: Bot) -> list[JX3ShilianItem]:
    silver_leaves = base_items["银叶子"]
    silver_leaves.count = randint(40, 60)
    cultivation_drug = base_items["九花玉露散"]
    cultivation_drug.count = randint(15, 25)
    final_reward = await get_third_item(level, group_id, bot)
    if final_reward.name == "匡义符·星":
        final_reward.count = randint(15, 25)
    if final_reward.name == "五行石（一级）":
        final_reward.count = choice([200, 300])
    return [silver_leaves, cultivation_drug, final_reward]

async def generate_shilian_box(level: int, user_choice: int, group_id: int, bot: Bot):
    if level > 70:
        return " 当前仅可翻牌70层及以下！"
    if user_choice not in list(range(1, 6)):
        return " 翻牌序号仅可在1-5之间！"
    result = []
    for num in range(5):
        single_result = []
        rewards = await get_single_full_reward(level, group_id, bot)
        for reward in rewards:
            color = reward.color
            if color == "(255, 255, 255)":
                color = "(0, 0, 0)"
            icon = await cache_image(reward.icon)
            if reward.name in ["银叶子·试炼之地", "九花玉露散", "匡义令·星", "五行石（一级）"]:
                name = f"{reward.name} x{reward.count}"
            elif reward.name.startswith(JX3Trade.shilian_basic):
                name = f"[{reward.bind}]{reward.name}<br>{reward.quality} {reward.attr}"
            else:
                name = reward.name
            single_result.append(
                Template(template_shilian_single).render(
                    color = color,
                    icon = icon,
                    name = name
                )
            )
        result.append(
            Template(template_shilian_box).render(
                highlight = "highlight" if user_choice - 1 == num else "",
                items = "\n".join(single_result)
            )
        )
    html = Template(
        read(
            TEMPLATES + "/jx3/shilian_box.html"
        )
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        boxes = "\n".join(result),
        saohua = get_saohua()
    )
    return await generate(html, "body", segment=True)