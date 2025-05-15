from random import random
from pydantic import BaseModel

item_colors = [
    "(167, 167, 167)", # 灰色
    "(255, 255, 255)", # 白色
    "(0, 210, 75)", # 绿色
    "(0, 126, 255)", # 蓝色
    "(254, 45, 254)", # 紫色
    "(255, 165, 0)" # 橙色
]

def get_random(probability: int) -> bool:
    return random() < probability / 100

class JX3RandomItem(BaseModel):
    attr: str = ""
    color: str = "(254, 45, 254)"
    icon: str
    name: str

class JX3ShilianItem(JX3RandomItem):
    bind: str = ""
    count: int = 1
    quality: int = 0

books = {
    "《寸险律·残卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/tiance_book_3.png?v=2",
    "《纵横之剑·阖》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/chunyang_shuliandu_1.png?v=2",
    "《纵横之剑·捭》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/shaolin_shuliandu_1.png?v=2",
    "《蜀山剑诀·秘卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/chunyang_book_3.png?v=2",
    "《圣灵心法·秘卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/wanhua_shuliandu_3.png?v=2",
    "《月朔实录·残卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/chunyang_shuliandu_2.png?v=2",
    "《易筋经·秘卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/shaolin_book_2.png?v=2",
    "《惊羽诀·秘卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/wanhua_book_3.png?v=2",
    "《离经易道·秘卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/wanhua_book_2.png?v=2",
    "《纯阳别册·残卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/chunyang_book_2.png?v=2",
    "《气经·残卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/tiance_book_2.png?v=2",
    "《相知剑意·残卷》": "https://dl.pvp.xoyo.com/prod/icons/skill/SkillBook/wudu_book_2.png?v=2"
}
