from typing import Any

from src.utils.network import Request
from src.utils.generate import generate

from playwright.async_api import TimeoutError

async def get_item_info(item_name: str):
    data = (
        await Request(
            "https://node.jx3box.com/api/node/item/search",
            params={
                "keyword": item_name,
                "page": 1,
                "per": 10,
                "client": "std"
            }
        ).get()
    ).json()
    if data["data"]["total"] == 0:
        return "未找到该物品，请检查后重试！"
    else:
        item_data: list[dict[str, Any]] = data["data"]["data"]
        if len(item_data) == 1:
            return await get_item_image(item_data[0]["id"])
        item_id_list: list[str] = []
        msg = "已找到下面的相关物品，请回复序号！"
        for num, data in enumerate(item_data, start=1):
            name = data["Name"]
            level = data["Level"] or "未知品质"
            bind = "未知" if data["BindType"] is None else "不绑定" if data["BindType"] in [0, 1, 2] else "拾取绑定"
            item_id_list.append(data["id"])
            msg += f"\n[{num}] {name}({level}·{bind})"
        return msg.strip(), item_id_list
            

async def get_item_image(item_id: str):
    try:
        image = await generate(
            "https://www.jx3box.com/item/view/" + item_id,
            ".c-item",
            first=True,
            hide_classes=["c-breadcrumb", "c-sidebar", "c-header-inner"],
            viewport={"height": 1080, "width": 1920},
            segment=True
        )
        return image
    except TimeoutError:
        return "获取数据超时，请稍后重试！"