from src.tools.basic import *
from src.tools.generate import generate, get_uuid
from src.tools.config import Config
from src.tools.file import read, write
import json
import os

from pathlib import Path
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from tabulate import tabulate


"""
帮助文件生成函数。

包含文字 + 图片信息。

文字来源于内置，图片由每个`plugin`文件夹下的`info.json`中的内容整合，再以`selenium`进行渲染所得。
"""

help = on_command("help", aliases={"帮助", "功能", "查看", "文档", "使用说明"}, priority=5)
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
</style>"""
css = css.replace("customfont", Config.font_path)
path = PLUGINS

def count_line(string: str):
    num = 0
    for i in string:
        if i == "|":
            num = num + 1
    return num

def process(markdown: str):
    """
    适配Lagrange的Markdown
    """
    to_replace = [
        [
            "\\",
            "\\\\"
        ]
        [
            "\"",
            "\\\\\\\""
        ],
        [
            "<br>",
            "\n"
        ]
    ]
    for i in to_replace:
        markdown = markdown.replace(i[0], i[1])
    return markdown

@help.handle()
async def help_():
    await help.finish(f"Inkar Suki · 音卡使用文档：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/")

getCmd = on_command("get_cmd", aliases={"查找命令"}, priority=5)
@getCmd.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    api = "https://inkar-suki.codethink.cn/Inkar-Suki-Docs/usage.md"
    data = await get_url(api)
    data = data.split("\n")
    ans = []
    for i in data:
        if i.find(args.extract_plain_text()) and count_line(i) >= 6:
            ans.append(process(i))
    ans = ["|命令|格式|别名|描述|权限|图片|","|-----|-----|-----|-----|-----|-----|"] + ans
    ans = "\n".join(ans)
    node = [
        {
            "type": "node",
            "data": 
            {
                "name": "Inkar Suki · 音卡",
                "uin": "3438531564",
                "content": 
                [
                    {
                        "type": "markdown",
                        "data": 
                        {
                            "content": ans
                        }
                    }
                ]
            }
        }
    ]
    ans = await bot.call_api("send_forward_msg", messages=node)
    ans = [
        {
            "type": "longmsg",
            "data": {
                "id":ans
            }
        }
    ]
    await bot.call_api("send_group_msg", group_id=event.group_id, message=ans)