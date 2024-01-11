from src.tools.dep import *


@Jx3Arg.requireToken
async def get_user_uid(server: str, userid: str):
    url = f"{Config.jx3api_link}/data/role/detailed?token={token}&server={server}&name={userid}"
    data = await Jx3ApiRequest(url).output_data()
    pass


async def get_user_property_by_name(username: str) -> dict:
    pass
