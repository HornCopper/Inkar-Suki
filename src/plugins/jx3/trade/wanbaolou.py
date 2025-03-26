# 万宝楼需要登录，使用爱剑三作为替代数据源

from typing_extensions import Self
from typing import Literal, Any
from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES
from src.utils.network import Request
from src.utils.file import read
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import get_saohua

import base64
import gzip
import json
import httpx
import os

class WBLAccount:
    base_info: dict[str, Any] = {}

    @classmethod
    async def use_wbl_sequence(cls, seq: int) -> Self | Literal[False]:
        url = "https://www.aijx3.cn/api/web/getZhanghaoResultWbl3"
        params = {
            "notNeedString": ",",
            "needString": ",",
            "accoSeq": seq,
            "page": 1,
            "size": 20
        }
        data = (await Request(url, params=params).get()).json()
        if len(data["zhanghaoDataList"]) < 1:
            return False
        else:
            return cls(data["zhanghaoDataList"][0]["zhanghaoId"], seq)
        
    @staticmethod
    def get_alias(data: dict[str, Any], name: str, item_type: str) -> str:
        if item_type not in data:
            return ""
        else:
            for item in data[item_type]:
                if item.get("name") == name:
                    return item.get("aliasName", "")
            return ""
    
    def __init__(self, account_id: str, sequence: int):
        self.account_id = account_id
        self.wbl_sequence = sequence

    @staticmethod
    async def get_base_info():
        url = "https://res.web.aijx3.cn/web/system/zhanghao/baseinfogzip.json"
        base64_data: str = (await Request(url).get()).text
        result: dict = json.loads(
            gzip.decompress(
                base64.b64decode(
                    base64_data
                )
            )
        )
        return result

    async def get_data_by_account_id(self) -> dict[str, Any]:
        params = {
            "ver": "2.0",
            "method": "account.get.wblaccount.detail.notlogin",
            "zhanghaoId": self.account_id
        }
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            base64_data_json: dict = (await client.post("https://www.aijx3.cn/api/web/dispath", params=params)).json()
        base64_data: str = base64_data_json["data"]
        result: dict = json.loads(
            gzip.decompress(
                base64.b64decode(
                    base64_data
                )
            ).decode(
                "utf-8",
                errors="ignore"
            )
        )
        return result
    
    async def generate_image(self):
        if not self.base_info:
            self.base_info = await self.get_base_info()
        data = await self.get_data_by_account_id()
        details: dict[str, str] = {}

        details["玄晶陨铁"] = "、".join(json.loads(data["chengwuXuanjingName"]))
        details["发型"] = "、".join(
            [
                f"{i}（{alias}）" if alias else f"{i}"
                for i in json.loads(data["faxingName"])
                if (alias := self.get_alias(self.base_info, i, "发型")) is not None
            ]
        )
        details["成衣"] = "、".join(
            [
                f"{i}（{alias}）" if alias else f"{i}"
                for i in json.loads(data["chengyiName"])
                if (alias := self.get_alias(self.base_info, i, "成衣")) is not None
            ]
        )
        details["盒子"] = "、".join(
            [
                f"{i}（{alias}）" if alias else f"{i}"
                for i in json.loads(data["heziName"])
                if (alias := self.get_alias(self.base_info, i, "盒子")) is not None
            ]
        )
        details["披风"] = "、".join(
            [
                f"{i}（{alias}）" if alias else f"{i}"
                for i in json.loads(data["pifengName"])
                if (alias := self.get_alias(self.base_info, i, "披风")) is not None
            ]
        )
        details["坐骑"] = "、".join(
            json.loads(data["zuoqiQiquName"])
        )
        details["佩囊挂宠"] = "、".join(
            [
                f"{i}（{alias}）" if alias else f"{i}"
                for i in json.loads(data["peilangGuachongName"])
                if (alias := self.get_alias(self.base_info, i, "佩囊" if i in [p["name"] for p in self.base_info["佩囊"]] else "挂宠")) is not None
            ]
        )
        details["外观收集"] = "武器" + str(len(json.loads(data["wuqiShoujiName"]))) + "件 /  装备" + str(len(json.loads(data["waiguanShoujiName"]))) + "件"
        details["红尘侠影"] = "、".join(
            [
                str(h["heroLevel"]) + "级" + h["name"] + "（" + h["kungfu"] + "）"
                for h in json.loads(data["hcxyContent"])["heroes"]
            ]
        )
        non_pet_serendipities = [os.path.splitext(file)[0] for file in os.listdir(ASSETS + "/image/jx3/serendipity/serendipity/common/")] + \
            [os.path.splitext(file)[0] for file in os.listdir(ASSETS + "/image/jx3/serendipity/serendipity/peerless/")]
        details["奇遇信息"] = "、".join([s for s in json.loads(data["qiyuQizhenName"]) if s in non_pet_serendipities])

        html = Template(
            read(
                TEMPLATES + "/jx3/wanbaolou.html"
            )
        ).render(
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            name = data["gameName"],
            level = data["gameLevel"],
            school = data["menpaiName"],
            body = data["tixin"],
            zone = data["belongQf2"],
            server = data["belongQf3"],
            camp = data["zhenYing"],
            date = Time(data["replyTime"] / 1000 + 1209600).format(),
            sequence = self.wbl_sequence,
            price = data["priceNum"],
            price_change = "->".join([str(p["updatePrice"]) for p in data["dUserZhanghaoWblPrices"]] + [str(data["priceNum"])]),
            score = data["zhuangBei1"],
            experience = data["ziliNum"],
            details = {k: v for k, v in details.items() if v},
            saohua = get_saohua()
        )

        return await generate(html, ".container", segment=True)
    
async def get_wbl_role(sequence: int):
    instance = await WBLAccount.use_wbl_sequence(sequence)
    if not instance:
        return "未找到相关账号信息！"
    else:
        image = await instance.generate_image()
        msg = image + f"电脑端：https://jx3.seasunwbl.com/role?consignment_id={sequence}\n移动端：https://m.seasunwbl.com/jx3/detail.html?consignment_id={sequence}&goods_type=2"
        return msg