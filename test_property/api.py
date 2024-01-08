from src.tools.dep import *


@Jx3Arg.requireToken
async def get_user_uid(server: str, userid: str):
    url = f"{Config.jx3api_link}/data/role/detailed?token={token}&server={server}&name={userid}"
    data = await Jx3ApiRequest(url).output_data()
    pass


async def get_property_by_uid():
    uid = await get_user_uid(server, userid)
    param = {
        "zone": Zone_mapping(server),
        "server": server,
        "game_role_id": uid[0],
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "Accept": "application/json",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "cache-control": "no-cache",
        "fromsys": "APP",
        "clientkey": "1",
        "apiversion": "3",
        "gamename": "jx3",
        "platform": "ios",
        "sign": "true",
        "token": token,
        "deviceid": device_id,
        "User-Agent": "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/mine/equip/get-role-equip", data=param, headers=headers)
