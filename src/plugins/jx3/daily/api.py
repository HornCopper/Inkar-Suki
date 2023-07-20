from src.tools.dep import *


async def daily_(server: str = None, group_id: str = None, predict_day_num: int = 0):
    '''
    获取日常图片链接
    @param predict_day_num 向后预测天数
    '''
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    full_link = f"{Config.jx3api_link}/view/active/current?robot={bot}&server={server}&num={predict_day_num}"
<<<<<<< HEAD
    data = await get_api(full_link, proxy=proxies)
=======
    data = await get_api(full_link)
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    return data["data"]["url"]
