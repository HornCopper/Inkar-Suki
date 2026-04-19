from src.config import Config
from src.utils.analyze import check_number
from src.utils.network import Request

async def get_enchant_list(enchant_name: str) -> str:
    param_enchant_id = 0
    param_enchant_name = ""

    if check_number(enchant_name):
        param_enchant_id = int(enchant_name)
    else:
        param_enchant_name = enchant_name
    
    url = f"{Config.jx3.api.calculator_url}/enchant"
    params = {
        "enchant_id": param_enchant_id,
        "enchant_name": param_enchant_name
    }
    data = (await Request(url, params=params).get()).json()
    if data["code"] != 200:
        return "未找到相关附魔，请检查关键词或附魔 ID 后重试！"
    else:
        results = []
        num = 1
        for each_enchant in data["data"]:
            key = each_enchant["Attribute1ID"]
            value = each_enchant["Attribute1Value1"]
            if key == "atExecuteScript":
                value = "<未知值>"
            score = each_enchant["Score"]
            results.append(
                str(num) + ". （" + each_enchant["ID"] + "）" + each_enchant["Name"] + "\n" + \
                "属性简介：" + each_enchant["AttriName"] + "\n" + \
                "调试用信息：" + key + " " + value + "\n" + \
                "装备分数：" + (score or "未知")
            )
            num += 1
        return "已找到以下附魔：\n" + "\n".join(results)
