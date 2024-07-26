from src.tools.utils.request import get_api

async def getRandomPoem():
    data = await get_api("https://v1.jinrishici.com/all.json")
    content = data["content"]
    origin = data["origin"]
    author = data["author"]
    return [content, origin, author]