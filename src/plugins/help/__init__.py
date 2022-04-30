import json
import os
import sys
from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from tabulate import tabulate
import nonebot

from .picture import main as pic

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from file import read

help = on_command("help", aliases={"帮助"}, priority=5)
css = """
<style>
            ::-webkit-scrollbar 
            {
            display: none;
                
            }
            table { 
            border-collapse: collapse; 
                } 
              table, th, td { 
                border: 1px solid rgba(0,0,0,0.05); 
                font-size: 0.8125rem; 
                font-weight: 500; 
              } 
              th, td { 
              padding: 15px; 
              text-align: left; 
              }
              @font-face
              {
                  font-family: Minecraft;
                  src: url("file:///root/nb/src/plugins/help/oppo_sans.ttf");
              }
            </style>"""
path = "/root/nb/src/plugins/"
final_plugin_information_file_path = {}
name = {}
version = {}
author = {}
json_ = {}
desc = {}
admin = {}
aliases = {}
table = []
html_path = "/root/nb/src/plugins/help/help.html"
imgPath = "/root/nb/src/plugins/help/help.png"

@help.handle()
async def help_(matcher: Matcher, event: Event, args: Message = CommandArg()):
    cmd = args.extract_plain_text()
    os.system(f"rm -rf {html_path}")
    all_cmd = os.listdir(path)
    for plugin in all_cmd:
        final_plugin_information_file_path[plugin] = path + plugin + "/info.json"
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
    table.append(["插件名称","插件版本","插件介绍","插件作者","权限等级","别名"])
    for i in all_cmd:
        table.append([name[i],version[i],desc[i],author[i],admin[i],aliases[i]])
    if os.path.exists(html_path) == False:
        msg = str(tabulate(table,headers="firstrow",tablefmt="html"))
        table.clear()
        html = "<div style=\"font-family:Minecraft\">" + msg.replace("$", "<br>") + "</div>"+css
        file0 = open(html_path,mode="w")
        file0.write(html)
        file0.close()
    if os.path.exists(imgPath) == False:
        pic_status = pic()
        if pic_status == "200 OK":
            help_path = Path("/root/nb/src/plugins/help/help.png").as_uri()
            pic_msg = MessageSegment.image(help_path)
            msg = "喵……以下为帮助信息：" + pic_msg
        else:
            msg = f"唔……帮助图片生成失败了哦，请联系管理员尝试清除缓存。\n错误信息如下：{pic_status}"
    else:
        help_path = Path("/root/nb/src/plugins/help/help.png").as_uri()
        pic_msg = MessageSegment.image(help_path)
        msg = "喵……以下为帮助信息：" + pic_msg
    await help.finish(msg)
    return
