from src.utils.network import Request

async def get_poem():
    data = (await Request("https://v1.jinrishici.com/all.json").get()).json()
    content = data["content"]
    origin = data["origin"]
    author = data["author"]
    return [content, origin, author]