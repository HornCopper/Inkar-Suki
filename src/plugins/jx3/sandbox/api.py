from pathlib import Path

from src.const.prompts import PROMPT
from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.time import Time
from src.utils.jx3api import jx3api_get
from src.utils.generate import generate
from src.utils.decorators import token_required
from src.templates import SimpleHTML, get_saohua

@token_required
async def get_sandbox_image(server: str, token: str = ""):
    url = "/sand/records"
    params = {
        "token": token,
        "server": server,
    }
    data = await jx3api_get(url, params = params)
    if data["code"] != 200:
        return data["msg"] or PROMPT.ServerInvalid
    update_time = str(Time(data["data"]["update"]).format())
    camps = {item["castleName"]: "haoqi" if item["campName"] == "浩气盟" else "eren" for item in data["data"]["data"]}
    html = str(
        SimpleHTML(
            "jx3",
            "sandbox.html",
            outside_css = Path(build_path(TEMPLATES, ["jx3", "sandbox.css"])).as_uri(),
            font = Path(build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"])).as_uri(),
            server = server,
            update_time = update_time,
            camps = camps,
            saohua = get_saohua(),
        ),
    )
    image = await generate(html, ".sandbox-report", segment = True)
    return image
