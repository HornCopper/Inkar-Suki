from src.utils.network import Request
from src.utils.generate import generate

async def get_item_info(item_name: str):
    data = (
        await Request(
            "https://node.jx3box.com/api/node/item/search",
            params={
                "keyword": item_name,
                "page": 1,
                "per": 1,
                "client": "std"
            }
        ).get()
    ).json()
    if data["data"]["total"] == 0:
        return "未找到该物品，请检查后重试！"
    else:
        item_id = data["data"]["data"][0]["id"]
        image = await generate(
            "https://www.jx3box.com/item/view/" + item_id,
            ".c-item",
            first=True,
            hide_classes=["c-breadcrumb", "c-sidebar", "c-header-inner"],
            viewport={"height": 1080, "width": 1920},
            segment=True
        )
        return image