from pathlib import Path

from src.const.path import ASSETS, build_path
from src.utils.network import Request
from src.utils.generate import generate

prefix_html_code = """
<html>
<div style="width:770px;padding-left:40px;padding-right:40px;padding-top:80px">
<style>
    @font-face {
        font-family: Harmony;
        src: url("font_url");
    }

    body {
        font-family: Harmony, sans-serif !important;
    }
</style>
""".replace("font_url", Path(build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"])).as_uri())

async def get_image(ver: str = "latest"):
    raw_html = (await Request(f"https://jx3.xoyo.com/launcher/update/{ver}.html").get()).text
    html = prefix_html_code + raw_html + "</div></html>"
    return await generate(html.replace("font-family:微软雅黑;", ""), "div", True, segment=True, output_path=build_path(ASSETS, ["image", "jx3", "update.png"]) if ver != "latest_exp" else "")