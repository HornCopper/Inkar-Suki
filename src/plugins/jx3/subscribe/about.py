from src.tools.basic import *

from . import subscribe_options

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
    current = await getGroupData(group_id, "subscribe")
    if len(current) <= 0:
        return ["本群聊没有开启任何内容哦~"]
    else:
        contents = []
        for i in list(subscribe_options):
            desc = subscribe_options[i][0]
            icon = subscribe_options[i][1]
            if i in current:
                status = "enabled"
                flag = "✔"
            else:
                status = "disabled"
                flag = "✖"
            contents.append(template_subscribe.replace("$image", icon).replace("$subject", i).replace("$description", desc).replace("$status", status).replace("$flag", flag))
        final_contents = "\n".join(contents)
        html = read(VIEWS + "/jx3/subscribe/subscribe.html")
        font = ASSETS + "/font/custom.ttf"
        group_info = await bot.call_api("get_group_info", group_id=int(group_id), no_cache=True)
        group_name = group_info["group_name"]
        html = html.replace("$customfont", font).replace("$contents", final_contents).replace("$group_id", group_id).replace("$group_name", group_name)
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, ".total", False)
        return Path(final_path).as_uri()