from src.tools.basic import *

# 施工中……
# def delete_binded(raw: list):
#     ans = []
#     for i in raw:
#         if i["BindType"] not in [0, 1, 2, None]:
#             continue
#         else:
#             ans.append(i)
#     return ans

# async def getTrend(server: str, name: str, group: str):
#     server = server_mapping(server, group)
#     if not server:
#         return [PROMPT_ServerNotExist]
#     for i in filters:
#         if name.find(i) != -1:
#             return ["唔……请勿查找无封装备！\n如果您需要查找无封装备，可以使用“交易行无封”（注意没有空格），使用方法参考：交易行无封 服务器 词条\n词条示例：13550内功双会头"]
#     for i in banned:
#         if name == i:
#             return ["唔……请勿查找无封装备！"]
#     data = await get_api(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&per=35")
#     if data["data"]["total"] == 0:
#         return ["唔……没有任何匹配的搜索结果，请尝试使用标准名称搜索？"]
#     data = delete_binded(data["data"])
#     if len(data) != 1:
#         return ["唔……没有任何匹配的搜索结果，或候选项过多，请尝试使用标准名称搜索？"]
#     id = data[0]["id"]
#     data2 = await get_api(f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}")
#     if data2["data"]["logs"] == None:
#         return ["唔……交易行没有该物品数据！"]
#     date = []
#     for i in data2:
#         date.append("")