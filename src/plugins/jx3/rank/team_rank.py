from jinja2 import Template

from src.const.path import ASSETS
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.network import Request
from src.utils.time import Time
from src.utils.analyze import check_number
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua

from ._template import teamrank_anyone_template, teamrank_team_template

# 名人堂 by 花姐

async def fetch_team_rank_data(dungeon_name: str, dungeon_mode: str, boss_name: str) -> dict:
    url = "http://116.211.150.188:8009/getHoFRank"
    dungeon_full_name = dungeon_mode + dungeon_name
    if dungeon_name == "缚罪之渊":
        dungeon_full_name = dungeon_name
    params = {
        # "map": "25人英雄会战弓月城",
        "map": dungeon_full_name,
        # "boss": "尹雪尘",
        "boss": boss_name,
        "orderby": "firstkill"
    }
    data = (await Request(url, params=params).get()).json()
    return data

async def parse_team_rank_data(dungeon_name: str, dungeon_mode: str, boss_name: str):
    data = await fetch_team_rank_data(dungeon_name, dungeon_mode, boss_name)
    if not data["result"]["table"]:
        return "未找到相关数据，请检查首领名称！"
    table_teams = []
    for each_team in data["result"]["table"]:
        table_players = []
        end_time = Time(int(each_team["endtime"])).format("%Y-%m-%d %H:%M:%S")
        time_cost = int(each_team["length"] / 1000)
        time_cost_str = f"{time_cost // 60}分{time_cost % 60}秒"
        team_name = each_team["team"]
        team_server = each_team["server"]
        players = each_team["player"]
        for each_player in players:
            kungfu_id = each_player[1]
            player_name = each_player[0]
            # if player_name == "花一一一一一":
            #     player_name = "绕影"
            if check_number(kungfu_id):
                # 单心法职业
                kungfu = Kungfu(
                    School.with_internel_id(int(kungfu_id)).name
                )
            else:
                t = ""
                keyword = kungfu_id[-1]
                force_id = kungfu_id[:-1]
                if keyword == "h":
                    t = "HPS"
                if keyword == "t":
                    t = "T"
                if keyword == "d":
                    t = "DPS"
                if keyword == "m":
                    if force_id == "4":
                        t = "QC"
                    else:
                        t = "TL"
                if keyword == "p":
                    if force_id == "4":
                        t = "JC"
                    else:
                        t = "JY"
                kungfu = Kungfu(
                    str(School.with_internel_id(int(force_id)).name) + t
                )
            table_players.append(
                Template(teamrank_anyone_template).render(
                    kungfu_icon = kungfu.icon,
                    name = player_name
                )
            )
        table_teams.append(
            Template(teamrank_team_template).render(
                team_icon = f"https://inkar-suki.codethink.cn/team/{team_name}.png",
                team_name = team_name,
                server = f"@{team_server}",
                finish_time = end_time,
                time_cost = time_cost_str,
                players = "\n".join(table_players)
            )
        )
    html = str(
        SimpleHTML(
            "jx3",
            "team_rank",
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            teams = "\n".join(table_teams),
            dungeon_full_name = f"{dungeon_mode}{dungeon_name}",
            boss_name = boss_name,
            saohua = get_saohua()
        )
    )
    image = await generate(html, ".container", segment=True)
    return image