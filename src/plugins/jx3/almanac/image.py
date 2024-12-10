from typing import Any
from jinja2 import Template
from datetime import datetime, timedelta

from src.const.path import TEMPLATES, ASSETS
from src.utils.file import read
from src.utils.time import Time

import re

b: dict[str, list[str]] = {
    "少林": ["易筋经", "洗髓经"],
    "万花": ["花间游", "离经易道"],
    "五毒": ["毒经", "补天诀"],
    "天策": ["傲血战意", "铁牢律"],
    "纯阳": ["紫霞功", "太虚剑意"],
    "藏剑": ["问水诀"],
    "七秀": ["冰心诀", "云裳心经"],
    "药宗": ["无方", "灵素"],
    "长歌": ["莫问", "相知"],
    "明教": ["明尊琉璃体", "焚影圣诀"],
    "苍云": ["分山劲", "铁骨衣"],
    "唐门": ["天罗诡道", "惊羽诀"],
    "丐帮": ["笑尘诀"],
    "霸刀": ["北傲诀"],
    "蓬莱": ["凌海诀"],
    "凌雪": ["隐龙诀"],
    "衍天": ["太玄经"],
    "刀宗": ["孤锋诀"],
    "万灵": ["山海心诀"],
    "段氏": ["周天功"]
}

c = """
<tr>
    <td>{{ p1 }}</td>
    <td>{{ p2 }}</td>
    <td>{{ p3 }}</td>
</tr>
"""

def d(e: str):
    f = e.split("：")[0].strip()
    g = e.split("：")[1].strip()
    h = g.find("其他门派")
    if h != -1:
        i = g[:h-1].strip()
        j = g[h+4:].strip()
    else:
        i = g
        j = ""
    return f, i, j

def k(l: list[str]):
    m = {}
    for n in l:
        o, _ = n.split("id吉时")
        m[o.strip()[:-1]] = o.strip()[-1]
    return m

def p(q: str) -> str:
    r = re.search(r"（(.*?)）", q)
    if r:
        return r.group(1)
    else:
        return "-"

def t(u: str) -> str:
    v = "\n".join(
        [
            "<img src=\"" + ASSETS + "/image/jx3/kungfu/" + w + ".png\" class=\"faction-icon\">"
            for w
            in b[u]
        ]
    )
    return v + u

def x(y: str) -> Any:
    z = y.split("\n")
    aa = z[0].split("，")[1]
    _, ab, ac = d(z[1])
    _, ad, ae = d(z[2])
    af = k(z[3:z.index("")])
    ag = []
    for ah in z[z.index("")+1:-2]:
        ag.append(
            Template(
                c
            ).render(
                p1 = re.sub(r"（.*?）", "", ah.split("推荐")[0]),
                p2 = re.sub(r"（.*?）", "", ah.split("推荐")[1]),
                p3 = p(ah)
            )
        )
    ai = [f"<p>{aj}</p>" for aj in z[-2:]]
    html = Template(
        read(TEMPLATES + "/jx3/almanac.html")
    ).render(
        date = (datetime.now() + timedelta(days=1)).strftime("%Y.%m.%d"),
        day_type = aa,
        s_schools = "\n".join([t(ab) for ab in ab.split("，")]),
        d_schools = "\n".join([t(ad) for ad in ad.split("，")]),
        s_color = ac[:2] + "<strong>" + ac[2:4] + "</strong>" + ac[4:],
        d_color = ae[:2] + "<strong>" + ae[2:4] + "</strong>" + ae[4:],
        lucky_time = af,
        general = "\n".join(ag),
        drop_recommend = "\n".join(ai)
    )
    return html
