from typing import Literal, Any

from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.utils.database import attribute_db as db
from src.utils.database.player import search_player
from src.utils.database.classes import PlayerEquipsCache
from src.utils.network import Request

import re

def parse_conditions(input_str: str) -> list[str] | Literal[False]:
    input_str = input_str.strip().upper()
    regex = r"(TL|DPS|HPS|PVE|PVP|PVX|QC|JC|JY|T)"
    matches = re.findall(regex, input_str)
    if not matches:
        return False
    t_dps_hps_count = sum(1 for kw in matches if kw in ["T", "DPS", "HPS", "QC", "JC", "TL", "JY"])
    pvp_pve_pvx_count = sum(1 for kw in matches if kw in ["PVP", "PVE", "PVX"])
    if t_dps_hps_count > 1 or pvp_pve_pvx_count > 1:
        return False
    if "T" in matches and ("PVP" in matches or "PVX" in matches):
        return False
    return matches

class AttributeParser:
    @classmethod
    def pre_check(cls, data: dict) -> "AttributeParser | Literal[False]":
        if data["data"] is None:
            return False
        return cls(data)

    def __init__(self, data: dict):
        self.data = data

    @property
    def score(self) -> str:
        return str(self.data["data"]["TotalEquipsScore"])
    
    @property
    def is_wujie(self) -> bool:
        return str(Kungfu.with_internel_id(self.data["data"]["Kungfu"]["KungfuID"]).name).endswith("·悟")
    
    @property
    def kungfu_name(self) -> str:
        name = Kungfu.with_internel_id(self.data["data"]["Kungfu"]["KungfuID"]).name
        if name is None:
            raise ValueError("Cannot recognize the kungfu from id `" + self.data["data"]["Kungfu"]["KungfuID"] + "`!")
        if name == "山居问水剑·悟":
            return "问水诀"
        if name.endswith("·悟"):
            return name[:-2]
        return name
    
    @property
    def equip_type(self) -> str:
        count = {
            "秘境挑战": 0,
            "竞技对抗": 0,
            "休闲": 0
        }
        for equip in self.data["data"]["Equips"]:
            et = equip["EquipType"]["Desc"]
            if et not in count.keys():
                et = "秘境挑战"
            count[et] += 1
        most_type = max(count, key=lambda k: (count[k], -list(count).index(k)))
        final_type = {
            "秘境挑战": "PVE",
            "竞技对抗": "PVP",
            "休闲": "PVX"
        }[most_type]
        if final_type not in ["PVE", "PVP", "PVX"]:
            raise ValueError
        return final_type

class AttributesRequest:
    @classmethod
    async def with_name(cls, server: str, name: str) -> "AttributesRequest | Literal[False]":
        role_info = await search_player(
            role_name = name,
            server_name = server
        )
        role_id = role_info.roleId
        if role_id == "":
            return False
        params = {
            "zone": Server(server).zone,
            "server": server,
            "game_role_id": role_id
        }
        data = (await Request("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
        parser = AttributeParser.pre_check(data)
        # if not parser:
        #     return False
        return cls(
            server,
            name,
            role_id,
            role_info.forceName,
            role_info.globalRoleId,
            parser
        )

    def __init__(
            self,
            server: str,
            name: str,
            uid: str,
            school: str,
            guid: str,
            current_data: "AttributeParser | Literal[False]"
        ):
        self.data = current_data
        self.guid = guid
        all_equip_cache: list[PlayerEquipsCache] | Any = db.where_all(
            PlayerEquipsCache(),
            "globalRoleId = ?",
            guid,
            default=[]
        )
        same_flag = False
        
        if current_data:
            for equip_cache in all_equip_cache:
                if equip_cache.tag == current_data.equip_type and equip_cache.kungfu == current_data.kungfu_name:
                    same_flag = True
                    if equip_cache.equips_data["data"]["Person"]["qixueList"] != [] and current_data.data["data"]["Person"]["qixueList"] == []:
                        current_data.data["data"]["Person"]["qixueList"] = equip_cache.equips_data["data"]["Person"]["qixueList"]
                    db.delete(
                        PlayerEquipsCache(),
                        "globalRoleId = ? AND tag = ? AND score = ? AND kungfu = ?",
                        guid,
                        equip_cache.tag,
                        equip_cache.score,
                        equip_cache.kungfu
                    )
                    db.save(
                        PlayerEquipsCache(
                            equips_data=current_data.data,
                            globalRoleId=guid,
                            kungfu=current_data.kungfu_name,
                            roleId=uid,
                            roleName=name,
                            score=current_data.score,
                            serverName=server,
                            tag=current_data.equip_type
                        )
                    )
        if not same_flag and current_data:
            db.save(
                PlayerEquipsCache(
                    equips_data=current_data.data,
                    globalRoleId=guid,
                    kungfu=current_data.kungfu_name,
                    roleId=uid,
                    roleName=name,
                    score=current_data.score,
                    serverName=server,
                    tag=current_data.equip_type
                )
            )
        self.school = school
        self.all_data = all_equip_cache
        if not self.all_data and current_data:
            db.save(
                PlayerEquipsCache(
                    equips_data=current_data.data,
                    globalRoleId=guid,
                    kungfu=current_data.kungfu_name,
                    roleId=uid,
                    roleName=name,
                    score=current_data.score,
                    serverName=server,
                    tag=current_data.equip_type
                )
            )
            self.all_data = [PlayerEquipsCache(
                equips_data=current_data.data,
                globalRoleId=guid,
                kungfu=current_data.kungfu_name,
                roleId=uid,
                roleName=name,
                score=current_data.score,
                serverName=server,
                tag=current_data.equip_type
            )]

    def get_equip(self, tag: str = "") -> dict | bool:
        tags = parse_conditions(tag)
        final_tag = ""
        kungfu = ""
        if tags:
            equip_type_word = [t for t in tags if t not in ["DPS", "HPS", "T", "JY", "TL", "JC", "QC"]]
            if len(equip_type_word) == 0:
                final_tag = ""
            else:
                final_tag = equip_type_word[0]
            kungfu_type_word = [t for t in tags if t != final_tag]
            if len(kungfu_type_word) != 0:
                kungfu = Kungfu(self.school + kungfu_type_word[0]).name
                if kungfu is None:
                    kungfu = ""
        if (not kungfu) and (not final_tag) and isinstance(self.data, AttributeParser):
            return self.data.data
        if not kungfu:
            for equip in self.all_data:
                if equip.tag == final_tag:
                    return equip.equips_data
        if not final_tag:
            for equip in self.all_data:
                if equip.kungfu == kungfu:
                    return equip.equips_data
        for equip in self.all_data:
            if equip.kungfu == kungfu and equip.tag == final_tag:
                return equip.equips_data
        if self.data:
            return True
        else:
            return False
    
    def get_last_equip(self) -> list[AttributeParser]:
        return [AttributeParser(e.equips_data) for e in self.all_data]