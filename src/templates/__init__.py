from random import choice
from pathlib import Path
from jinja2 import Template

from src.const.path import (
    ASSETS, 
    TEMPLATES, 
    build_path
)
from src.utils.file import read
from src.config import Config

import re

universal_template = read(
    build_path(
        TEMPLATES,
        [
            "universe.html"
        ]
    )
)

def get_saohua() -> str:
    return choice(
        [
            "我想在你那里买一块死心塌地",
            "我对你没有非分之想，想你是本分",
            "我的手心里软软的，你牵一下试试",
            "对你的喜欢就像这日子，只增不减",
            "你们99，我八十一难",
            "温柔这东西，全给你就好了",
            "最近天冷，借你被窝躲躲",
            "可爱不是长久之计，爱我才是",
            "这里有一箱情愿，记得签收~",
            "我的酒量大概就是你的一声宝贝",
            "有什么不懂的问题都可以来吻我哦",
            "你一笑，便是春天",
            "白茶清欢无别事，我在风里也等你",
            "你站的方向吹过来的风是暖的",
            "今晚没有星星，你可以看我的眼睛",
            "春风十里不如你",
            "为你，与风一起，不远万里",
            "岁月静好，万物可爱", 
            "愿你常年闪闪发亮，偶尔躲躲乌云",
            "请不要再到处散发魅力了",
            "我优点太多就缺点你了。",
            "江河奔海，我奔向你",
            "小太阳很忙。小云朵想吃糖。",
            "你不用多好，我喜欢就好。",
            "你有地图吗，我在你眼睛里迷路了",
            "你是三我是九，除了你还是你",
            "喜欢的少年是你，倒过来也一样", 
            "看见你的人，失了我的魂",
            "看见你我就知道，今生在劫难逃",
            "千山万水总是情，谈个恋爱行不行",
            "干啥啥不行，睡觉第一名",
            "我自横刀向天笑，笑完我就去睡觉",
            "中午不睡，下午崩溃",
            "天没降大任于你，照样苦你心智",
            "力的作用是相互的，除了爱情力量",
            "爱我的请举手，不爱我的请倒立",
            "多多微笑，阴天谨防情绪感冒",
            "说片面是失眠，说真的是想你",
            "星星在天上，你在我心里",
            "你过分帅气，我过分着迷",
            "知道我属什么吗？我属于你啊",
            "不求浮游于天地，但求浮游在你心",
            "你知道我有什么缺点吗？就缺点你",
            "你不累吗？在我脑子里跑一天了",
            "百分之九十九的心动都是因为你",
            "偷我什么都不可以偷偷喜欢我",
            "别让我看见你，看见一次喜欢一次",
            "吃了姐姐家的蘑菇，中了姐姐的毒",
            "要说多少骚话才能引起你的注意？",
            "难道要学电焊才能让你眼前一亮吗",
            "你今天怪怪的，怪可爱的！",
            "最近手头有点紧，想借你手牵牵",
            "我喜欢你不是情话，是心里话",
            "他们麻将三缺一，我的心里只缺你",
            "开开心心，可可爱爱",
            "我喜欢你不是情话，是心里话",
            "你不累吗？在我脑子里跑一天了",
            "见什么世面啊，见你就好了",
            "你今天挺怪的，怪漂亮的！",
            "你怎么不看路，都撞到我心里了"
        ]
    )

class HTMLSourceCode:
    standard = universal_template

    def __init__(
            self,
            application_name: str,
            font_path: str = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            footer: str = get_saohua(),
            additional_css: str = "",
            additional_js: Path | None = None,
            **kwargs
    ):
        """
        初始化`HTML`生成器实例。

        Args:
            application_name (str): 需要生成的`HTML`的模块名。
            font_path (str): 非必需。`HTML`整体字体，不传入则使用`src/assets/font/PingFangSC-Medium.otf`。
            footer (str): 非必需。页面最底部的字符串，推荐剑网3模块使用骚话，其他模块使用说明。
            additional_css (str): 额外定义的`CSS`，如果需要使用请提前定义！
            additional_js (Path, None): 额外定义的`JS`，只支持路径！
            **kwargs (dict)：其他替换参数，按键值对直接进行替换，请确保存在。

        **务必传入`table_head`和`table_body`参数！哪怕没有提示！！**
        """
        self.name = application_name
        self.font = font_path    
        self.font_extra = "font-weight: 700;" if font_path.endswith("PingFangSC-Semibold-Bold.otf") else ""
        self.footer = footer
        self.css = additional_css
        self.kwargs = kwargs
        if additional_js is None:
            self.js = ""
        else:
            self.js = "<script src=\"" + additional_js.as_uri() + "\"></script>"

    def __str__(self) -> str:
        if self.kwargs.get("table_head", None) is not None:
            self.kwargs["table_width_length"] = str(len(re.findall(r"<th.*?>.*?</th>", self.kwargs.get("table_head", []), re.DOTALL)))
        css_path = f"<link rel=\"stylesheet\" href=\"" + self.css + "\">" if self.css.startswith("file") or self.css.startswith("http") else ""
        css_content = self.css if not self.css.startswith("file") and not self.css.startswith("http") else ""
        return Template(self.standard).render(
            css_link = css_path,
            css = css_content,
            font = self.font,
            font_extra = self.font_extra,
            bot_name = Config.bot_basic.bot_name_argument,
            app_info = self.name,
            footer_msg = self.footer,
            js = self.js,
            **self.kwargs
        )
    
class SimpleHTML:
    """
    无法使用`HTMLSourceCode`模板生成`HTML`的解决方案。
    """
    def __init__(
        self,
        html_type: str,
        html_template: str,
        outside_js: str = "",
        outside_css: str = "",
        **kwargs
    ):
        """
        初始化简易`HTML`读取器。

        Args:
            html_type (str): `HTML`源代码类型，通常与对应的功能有关，例如`jx3`、`majsoul`等。
            html_template (str): `HTML`模板文件名，可以不带`.html`后缀。
            outside_js (str): 非必需。外部`JavaScript`路径，只接受本地的`File URL`或外部的`URL`，或文件路径。
            outside_css (str): 非必需。外部`CSS`路径，只接受本地的`File URL`或外部的`URL`，或文件路径。
        """
        if not html_template.endswith(".html"):
            html_template = html_template + ".html"
        css = "" if not outside_css else f"<link rel=\"stylesheet\" href=\"" + outside_css + "\">"
        js = "" if not outside_js else f"<script src=\"" + outside_js + "\"></script>"
        self.html_source = Template(
            read(
                build_path(
                    TEMPLATES,
                    [
                        html_type,
                        html_template
                    ]
                )
            )
        ).render(
            css = css,
            js = js,
            **kwargs
        )

    def __str__(self):
        return self.html_source