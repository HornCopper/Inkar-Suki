from pathlib import Path
from nonebot.adapters.onebot.v11 import Bot

from src.tools.utils.path import ASSETS, CACHE, PLUGINS, VIEWS
from src.tools.basic.group_opeator import getGroupSettings
from src.tools.generate import get_uuid, generate
from src.tools.file import read, write

import json

template_subscribe = """
<div class="el-col">
    <div class="el-box">
        <div class="el-image" style="margin-left: 10px;">
            <img src="$image" style="object-fit:contain">
        </div>
        <!-- 两个文字 -->
        <div class="el-text">
            <div class="element-text-up">$subject</div>
            <div class="element-text-down">$description</div>
        </div>
    </div>
    <div class="el-status $status">$flag</div>
</div>"""

async def generateGroupInfo(bot: Bot, group_id: str):
    subscribe_options = json.loads(read(PLUGINS + "/jx3/subscribe/options.json"))
    addtions_options = json.loads(read(PLUGINS + "/jx3/subscribe/addtions.json"))
    current_subscribe = getGroupSettings(group_id, "subscribe")
    current_addtions = getGroupSettings(group_id, "addtions")
    subscribe_contents = []
    addtions_contents = []
    for i in list(subscribe_options):
        desc = subscribe_options[i][0]
        icon = subscribe_options[i][1]
        if i in current_subscribe:
            status = "enabled"
            flag = "✔"
        else:
            status = "disabled"
            flag = "✖"
        subscribe_contents.append(template_subscribe.replace("$image", icon).replace("$subject", i).replace("$description", desc).replace("$status", status).replace("$flag", flag))
    for i in list(addtions_options):
        desc = addtions_options[i][0]
        icon = addtions_options[i][1]
        if i in current_addtions:
            status = "enabled"
            flag = "✔"
        else:
            status = "disabled"
            flag = "✖"
        addtions_contents.append(template_subscribe.replace("$image", icon).replace("$subject", i).replace("$description", desc).replace("$status", status).replace("$flag", flag))
    final_subscribe_contents = "\n".join(subscribe_contents)
    final_options_contents = "\n".join(addtions_contents)
    html = read(VIEWS + "/jx3/subscribe/subscribe.html")
    font = ASSETS + "/font/custom.ttf"
    group_info = await bot.call_api("get_group_info", group_id=int(group_id), no_cache=True)
    group_name = group_info["group_name"]
    html = html.replace("$customfont", font).replace("$subscribe_contents", final_subscribe_contents).replace("$addtion_contents", final_options_contents).replace("$group_id", group_id).replace("$group_name", group_name)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()