from pathlib import Path
from jinja2 import Template
from typing import Any

from src.const.path import build_path, TEMPLATES, ASSETS
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.file import read
from src.templates import get_saohua

from ._template import (
    global_view_head,
    template_global_view,
    dungeon_first,
    template_dungeon_view,
    dungeon_view_head
)

def match_css_key(value: float) -> str:
    if 0 <= value <= 0.25:
        return "0"
    elif 0.25 < value <= 0.5:
        return "25"
    elif 0.5 < value <= 0.75:
        return "50"
    elif 0.75 < value < 1:
        return "75"
    elif value == 1:
        return "100"
    else:
        return "0"

async def get_exp_info(
    server: str,
    name: str,
    guid: str,
    object: str
):
    total_data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params={"gameRoleId": guid, "cursor": 0, "size": 20000}).post(tuilan=True)).json()
    data: list[dict[str, Any]] = total_data["data"]["data"]
    if "全局总览" in object or object == "五甲总览":
        not_leading = ("含五甲" not in object) and object != "五甲总览"
        if not_leading:
            data = [a for a in data if ("五甲" not in a["name"] and "十甲" not in a["name"])]
        if object != "五甲总览":
            data = [a for a in data if ("排名" not in a["sub_class"] and a["sub_class"] not in ["大师赛", "八荒衡鉴", "江湖百态"])]
        else:
            data = [a for a in data if ("五甲" in a["name"] or "十甲" in a["name"])]
        total_point = sum([a["reward_point"] for a in data])
        finish_point = sum([a["reward_point"] for a in data if a["isFinished"]])
        total_detail: dict[str, int] = {}
        finish_detail: dict[str, int] = {}
        for achievement in data:
            total_detail[achievement["sub_class"]] = total_detail.get(achievement["sub_class"], 0) + achievement["reward_point"]
            finish_detail[achievement["sub_class"]] = finish_detail.get(achievement["sub_class"], 0) + (achievement["reward_point"] if achievement["isFinished"] else 0)
        final_result: dict[str, str] = {}
        for k, v in total_detail.items():
            if k in finish_detail:
                final_result[k] = str(finish_detail[k]) + "/" + str(v)
            else:
                final_result[k] = f"0/{v}"
        tables = []
        for k, v in final_result.items():
            done, total = v.split("/")
            tables.append(
                Template(template_global_view).render(
                    subject = k,
                    progress = match_css_key(int(done) / int(total)),
                    width = str(int(round(int(done) / int(total), 2) * 100)),
                    value = v
                )
            )
        html = Template(
            read(
                build_path(
                    TEMPLATES,
                    ["jx3", "exp_overview.html"]
                )
            )
        ).render(
            css = Path(
                build_path(
                    TEMPLATES,
                    ["jx3", "exp.css"]
                )
            ).as_uri(),
            font = build_path(
                ASSETS,
                ["font", "PingFangSC-Semibold.otf"]
            ),
            name = name,
            server = server,
            width = str(int(round(finish_point / total_point, 2) * 100)),
            progress = match_css_key(finish_point / total_point),
            finish = str(finish_point),
            total = str(total_point),
            head = global_view_head,
            table = "\n".join(tables),
            saohua = get_saohua(),
            subject = object
        )
        return await generate(html, ".total", segment=True)
    if object == "地图总览":
        data = [a for a in data if (a["maps"])]
        total_point = sum([a["reward_point"] for a in data])
        finish_point = sum([a["reward_point"] for a in data if a["isFinished"]])
        total_detail: dict[str, int] = {}
        finish_detail: dict[str, int] = {}
        for achievement in data:
            total_detail[achievement["maps"][0]["name"]] = total_detail.get(achievement["maps"][0]["name"], 0) + achievement["reward_point"]
            finish_detail[achievement["maps"][0]["name"]] = finish_detail.get(achievement["maps"][0]["name"], 0) + (achievement["reward_point"] if achievement["isFinished"] else 0)
        final_result: dict[str, str] = {}
        for k, v in total_detail.items():
            if k in finish_detail:
                final_result[k] = str(finish_detail[k]) + "/" + str(v)
            else:
                final_result[k] = f"0/{v}"
        tables = []
        for k, v in final_result.items():
            done, total = v.split("/")
            tables.append(
                Template(template_global_view).render(
                    subject = k,
                    progress = match_css_key(int(done) / int(total)),
                    width = str(int(round(int(done) / int(total), 2) * 100)),
                    value = v
                )
            )
        html = Template(
            read(
                build_path(
                    TEMPLATES,
                    ["jx3", "exp_overview.html"]
                )
            )
        ).render(
            css = Path(
                build_path(
                    TEMPLATES,
                    ["jx3", "exp.css"]
                )
            ).as_uri(),
            font = build_path(
                ASSETS,
                ["font", "PingFangSC-Semibold.otf"]
            ),
            name = name,
            server = server,
            finish = str(finish_point),
            progress = match_css_key(finish_point / total_point),
            width = str(int(round(finish_point / total_point, 2) * 100)),
            total = str(total_point),
            head = global_view_head,
            table = "\n".join(tables),
            saohua = get_saohua(),
            subject = object
        )
        return await generate(html, ".total", segment=True)
    if "秘境总览" in object:
        dungeon_data: list[dict] = (await Request("https://m.pvp.xoyo.com/achievement/list/dungeon-maps", params={"detail": True}).post(tuilan=True)).json()["data"]
        dungeons: dict[str, list[str]] = {
            d["name"]: [
                m["name"]
                for m in d["maps"]
            ]
            for d in dungeon_data
        }
        dungeons["仙踪林"].remove("历程5人普通")
        tables = []
        total_count = 0
        finish_count = 0
        data = [a for a in data if len(a["dungeons"]) >= 1]
        tz5 = ["鹿桥驿", "漳水南路", "周天屿", "稻香秘事"]
        tz25 = ["永王行宫·花月别院", "永王行宫·仙侣庭园", "太原之战·夜守孤城", "太原之战·逐虎驱狼"]
        only_yx = ["荻花洞窟", "南诏皇宫"]
        yx10 = ["龙渊泽", "荻花圣殿"]
        if object == "秘境总览":
            appended_dungeons = []
            for dungeon, mode in dungeons.items():
                if dungeon in ["古剑台", "神剑冢", "原野奇踪", "百战异闻录", "一之窟", "不染窟", "风砂旧垒", "冰川宫宝库", "天龙寺"]:
                    continue
                for each_mode in mode:
                    _mode = each_mode
                    if _mode in ["5人普通", "10人普通"]:
                        _mode = ""
                    else:
                        if "英雄" in _mode:
                            with_prefix = bool(sum(s.count("英雄") for s in mode) - 1)
                            if with_prefix and dungeon not in tz5 and dungeon not in yx10 or dungeon in only_yx:
                                _mode = _mode[2:] if mode[0].startswith("5人") else _mode[3:]
                        elif "挑战" in _mode:
                            with_prefix = bool(sum(s.count("挑战") for s in mode) - 1)
                            if with_prefix and dungeon not in tz25:
                                _mode = _mode[2:] if mode[0].startswith("5人") else _mode[3:]
                    if (mode[0].startswith("5人") and "5人普通" not in mode and _mode == "5人英雄") and dungeon not in tz5:
                        _mode = ""
                    if _mode.startswith("5人"):
                        _mode = _mode[2:]
                    if dungeon in ["光明顶秘道", "唐门密室"]:
                        _mode = ""
                    dungeon_name = _mode + dungeon
                    data_ = [a for a in data if (dungeon_name in [d["name"] for d in a["dungeons"]])]
                    if data_ == []:
                        dungeon_name = dungeon_name[3:] if dungeon_name.startswith("25人") or dungeon_name.startswith("10人") else ""
                        data_ = [a for a in data if (dungeon_name in [d["name"] for d in a["dungeons"]])]
                        if data_ == []:
                            continue
                    done = sum([a["reward_point"] for a in data_ if a["isFinished"]])
                    total = sum(a["reward_point"] for a in data_)
                    total_count += total
                    finish_count += done
                    first_flag = dungeon not in appended_dungeons
                    template = template_dungeon_view.replace("$first", dungeon_first if first_flag else "")
                    tables.append(
                        Template(template).render(
                            mode_count = str(len(mode)),
                            name = dungeon,
                            mode = each_mode,
                            progress = match_css_key(done / total),
                            width = str(int(round(done / total, 2) * 100)),
                            value = f"{done}/{total}"
                        )
                    )
                    appended_dungeons.append(dungeon)
        html = Template(
            read(
                build_path(
                    TEMPLATES,
                    ["jx3", "exp_overview.html"]
                )
            )
        ).render(
            css = Path(
                build_path(
                    TEMPLATES,
                    ["jx3", "exp.css"]
                )
            ).as_uri(),
            font = build_path(
                ASSETS,
                ["font", "PingFangSC-Semibold.otf"]
            ),
            name = name,
            server = server,
            finish = str(finish_count),
            progress = match_css_key(finish_count / total_count),
            total = str(total_count),
            width = str(int(round(finish_count / total_count, 2) * 100)),
            head = dungeon_view_head,
            table = "\n".join(tables),
            saohua = get_saohua(),
            subject = object
        )
        return await generate(html, ".total", segment=True)