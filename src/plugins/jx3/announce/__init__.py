from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from pathlib import Path

from src.tools.file import get_content_local
from src.tools.utils.path import ASSETS
from src.tools.utils.request import get_api
from src.tools.config import Config
from src.tools.generate import generate

import os
import re

js_content = f"""
const style = document.createElement('style');
style.textContent = `
    @font-face {{
        font-family: 'Custom';
        src: url('$font_path') format('ttf');
    }}

    body {{
        font-family: 'Custom', sans-serif !important;
    }}
`;
document.head.appendChild(style);
"""

announce = on_command("jx3_announce", aliases={"维护公告", "更新公告", "公告", "更新"}, force_whitespace=True, priority=5)

@announce.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    if args.extract_plain_text() != "":
        return
    if os.path.exists(ASSETS + "/jx3/update.png"):
        img = get_content_local(Path(ASSETS + "/jx3/update.png").as_uri())
        await announce.finish(ms.image(img))
    else:
        data = await get_api(f"{Config.jx3.api.url}/data/news/allnews")
        for news in data["data"]:
            title = news["title"]
            url = news["url"]
            if re.match(r'(\d+)月(\d+)日(.*?)版本更新公告', title):
                final_js = js_content.replace("$font_path", Path(ASSETS + "/font/syst-mid.ttf").as_uri())
                print(final_js)
                store_path = await generate(
                    url, 
                    True, 
                    ".allnews_list_container", 
                    viewport={"height": 3840, "width": 2000}, 
                    hide_classes=["detail_bot", "bdshare-slide-button"], 
                    device_scale_factor=2.0,
                    additional_js=final_js,
                    output=ASSETS + "/jx3/update.png"
                )
                if not isinstance(store_path, str):
                    return
                img = get_content_local(Path(store_path).as_uri())
                await announce.finish(ms.image(img))
                