from src.config import Config
from src.const.prompts import PROMPT
from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.decorators import token_required
from src.templates import SimpleHTML

@token_required
async def get_sandbox_image(server: str, token: str = ""):
    url = f"{Config.jx3.api.url}/data/sand/records"
    params = {
        "token": token,
        "server": server
    }
    data = (await Request(url, params=params).get()).json()
    if data["code"] != 200:
        return PROMPT.ServerInvalid
    update_time = str(Time(data["data"]["update"]).format())
    camps = {
        item["castleName"]: "haoqi" if item["campName"] == "浩气盟" else "eren"
        for item in data["data"]["data"]
    }
    html = str(
        SimpleHTML(
            "jx3",
            "sandbox.html",
            outside_css=build_path(TEMPLATES, ["jx3", "sandbox.css"]),
            font=build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]),
            server=server,
            update_time=update_time,
            camps=camps,
        )
    )
    image = await generate(html, ".m-sandbox-map", segment=True)
    return image
