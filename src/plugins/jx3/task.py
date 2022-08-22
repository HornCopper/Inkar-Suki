import sys
import nonebot

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
from utils import get_api, get_content

async def getTask(Task: str):
    info = await get_api(f"https://node.jx3box.com/quests?keyword={Task}&chain=false&client=std&page=1&per=20")
    if info["total"] == 0:
        return {"status":404}
    data = info["list"]["byKeyword"]
    map = []
    id = []
    task = []
    target = []
    level = []
    for i in data:
        id.append(i["id"])
        task.append(i["name"])
        map.append(i["map"])
        level.append(i["level"])
        target.append(i["target"])
    return {"status":200, "id":id, "task":task, "map":map, "level":level, "target":target}

async def getTaskChain(TaskID: int):
    info = await get_api(f"https://node.jx3box.com/quest/?id={TaskID}&client=std")
    data = info["chain"]["current"]
    chain = []
    if len(data) <= 1:
        return "无"
    for i in data:
        try:
            chain.append(i["name"])
        except:
            branch = []
            for x in i["quests"]:
                branch.append(x["name"])
            chain.append(" & ".join(branch))
    msg = " -> ".join(chain)
    return msg