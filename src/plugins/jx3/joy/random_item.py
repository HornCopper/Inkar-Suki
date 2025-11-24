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
    "《寸险律·残卷》": "https://icon.jx3box.com/icon/2265.png",
    "《纵横之剑·阖》": "https://icon.jx3box.com/icon/2244.png",
    "《纵横之剑·捭》": "https://icon.jx3box.com/icon/2260.png",
    "《蜀山剑诀·秘卷》": "https://icon.jx3box.com/icon/2241.png",
    "《圣灵心法·秘卷》": "https://icon.jx3box.com/icon/2238.png",
    "《月朔实录·残卷》": "https://icon.jx3box.com/icon/2245.png",
    "《易筋经·秘卷》": "https://icon.jx3box.com/icon/2256.png",
    "《惊羽诀·秘卷》": "https://icon.jx3box.com/icon/2273.png",
    "《离经易道·秘卷》": "https://icon.jx3box.com/icon/2272.png",
    "《纯阳别册·残卷》": "https://icon.jx3box.com/icon/2240.png",
    "《气经·残卷》": "https://icon.jx3box.com/icon/2264.png",
    "《相知剑意·残卷》": "https://icon.jx3box.com/icon/2739.png",
    "《冰心诀·残卷》": "https://icon.jx3box.com/icon/2250.png"
}
