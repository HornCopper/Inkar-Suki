from pathlib import Path

from src.config import Config
from src.const.prompts import PROMPT
from src.const.path import TEMPLATES, build_path
from src.utils.file import read
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.decorators import token_required

@token_required
async def get_sandbox_image(server: str, token: str = ""):
    if server is not None:
        final_url = f"{Config.jx3.api.url}/data/server/sand?token={token}&server={server}"
    data = (await Request(final_url).get()).json()
    if data["code"] != 200:
        return [PROMPT.ServerInvalid]
    html = read(build_path(TEMPLATES, ["jx3", "sandbox.html"]))
    update_time = str(Time(data["data"]["update"]).format())
    html = html.replace("$time", update_time)
    html = html.replace("$server", server)
    html = html.replace("$css", build_path(TEMPLATES, ["jx3", "sandbox.css"]))
    for i in data["data"]["data"]:
        camp = "haoqi" if i["campName"] == "浩气盟" else "eren"
        html = html.replace("$" + i["castleName"], camp)
    final_path = await generate(html, ".m-sandbox-map", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()