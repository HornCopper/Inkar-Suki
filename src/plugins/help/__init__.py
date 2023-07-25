from src.tools.generate import generate, get_uuid
from src.tools.config import Config
from src.tools.file import read, write
import json
import os
import sys
import nonebot

from pathlib import Path
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from tabulate import tabulate

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
CACHE = TOOLS[:-5] + "cache"
PLUGINS = TOOLS[:-5] + "plugins"

"""
帮助文件生成函数。

包含文字 + 图片信息。

文字来源于内置，图片由每个`plugin`文件夹下的`info.json`中的内容整合，再以`selenium`进行渲染所得。
"""

help = on_command("help", aliases={"帮助", "功能"}, priority=5)
css = """
<style>
            ::-webkit-scrollbar 
            {
                display: none;   
            }
            table 
            { 
                border-collapse: collapse; 
            } 
            table, th, td
            { 
                border: 1px solid rgba(0,0,0,0.05); 
                font-size: 0.8125rem; 
                font-weight: 500; 
            } 
            th, td 
            { 
                padding: 15px; 
                text-align: left; 
            }
            @font-face
            {
                font-family: Custom;
                src: url("customfont");
            }
</style>"""
css = css.replace("customfont", Config.font_path)
path = PLUGINS


@help.handle()
async def help_(args: Message = CommandArg()):
    module = args.extract_plain_text()
    if module:
        name = {}
        version = {}
        author = {}
        json_ = {}
        desc = {}
        admin = {}
        aliases = {}
        table = []
        modules = os.listdir(PLUGINS)
        if module not in modules:
            await help.finish("唔……没有找到此模块哦，请使用+help查看所有模块及其帮助。")
        else:
            plugin_info = json.loads(read(PLUGINS + "/" + module + "/info.json"))
            name = plugin_info["name"]
            version = plugin_info["version"]
            author = plugin_info["author"]
            desc = plugin_info["desc"]
            admin = plugin_info["admin"]
            aliases = plugin_info["aliases"]
            table.append(["插件名称", "插件版本", "插件介绍", "插件作者", "权限等级", "别名"])
            table.append([name, version, desc, author, admin, aliases])
            msg = str(tabulate(table, headers="firstrow", tablefmt="html"))
            table.clear()
            html = "<div style=\"font-family:Custom\">" + msg.replace("$", "<br>") + "</div>" + css
            final_path = CACHE + "/" + get_uuid() + ".html"
            write(final_path, html)
            image = await generate(final_path, False, "table", False)
            if type(image) != type("sb"):
                await help.finish("唔，帮助文件生成失败了哦~请联系机器人管理员解决此问题，附带以下信息：\n"+image)
            else:
                picture_message = ms.image(Path(image).as_uri())
                await help.finish("查询到插件"
                                  + module
                                  + "的帮助文件啦~\n"
                                  + picture_message
                                  + "还有文档可以找哦~\nhttps://inkar-suki.codethink.cn\n如果你觉得有帮助的话，欢迎来给作者赞助哦~\n链接：https://inkar-suki.codethink.cn/donate.html")
    else:
        final_plugin_information_file_path = {}
        name = {}
        version = {}
        author = {}
        json_ = {}
        desc = {}
        admin = {}
        aliases = {}
        table = []
        all_module = os.listdir(path)
        for plugin in all_module:
            final_plugin_information_file_path[plugin] = path + "/" + plugin + "/info.json"
            cache = read(final_plugin_information_file_path[plugin])
            json_[plugin] = cache
            json_[plugin] = json.loads(json_[plugin])
            cache = json_[plugin]
            name[plugin] = cache["name"]
            version[plugin] = cache["version"]
            author[plugin] = cache["author"]
            desc[plugin] = cache["desc"]
            admin[plugin] = cache["admin"]
            aliases[plugin] = cache["aliases"]
        table.append(["插件名称", "插件版本", "插件介绍", "插件作者", "权限等级", "别名"])
        for i in all_module:
            table.append([name[i], version[i], desc[i], author[i], admin[i], aliases[i]])
        msg = str(tabulate(table, headers="firstrow", tablefmt="html"))
        table.clear()
        html = "<div style=\"font-family:Custom\">" + msg.replace("$", "<br>") + "</div>"+css
        final_path = CACHE + "/" + get_uuid() + ".html"
        write(final_path, html)
        image = await generate(final_path, False, "table", False)
        if type(image) != type("sb"):
            await help.finish("唔，帮助文件生成失败了哦~请联系机器人管理员解决此问题，附带以下信息：\n"+image)
        else:
            picture_message = ms.image(Path(image).as_uri())
            await help.finish("帮助信息来啦！输入+help <module>可快速定位你要查找的模块哦~\n"
                              + picture_message
                              + "还有文档可以找哦~\nhttps://inkar-suki.codethink.cn/\n如果你觉得有帮助的话，欢迎来给作者赞助哦~\n链接：https://inkar-suki.codethink.cn/donate.html")
