###############################
# 请将该文件改为 config.py 后使用
###############################

from src.tools.local_version import ikv, nbv
from src.tools.file import get_resource_path
from pathlib import Path
import os


class Config:
    '''
    这里是`Inkar Suki`的配置文件，从`V0.8.3-Hotfix-3起，我们删除了`initialization.py`。
    取消了问答式配置，改为了用户自己填写。
    需要您填写的是末尾有注释的行，其他行请勿改动，感谢使用！
    此处的内容填写完毕后，请将文件名称改为`config.py`~
    '''
    config_py_path = __file__[:-10]
    global_path = config_py_path[:-6]+"/"

    web_path = ""  # GitHub Webhook的地址，填写`/a`，则内网地址为`http://127.0.0.1:<NB端口>/a`，`NB端口`在`.env.dev`中的`PORT`

    bot = [""]  # Bot的QQ号，此处请只填写一个，用`str`存在`list`中。

    platform = True  # 平台标识，`True`为Linux，`False`为`Windows`

    owner = [""]  # Bot主人，可以有多个，用`str`存在`list`中

    size = global_path+"/tools/size.txt"
    html_path = global_path+"/plugins/help/help.html"
    chromedriver_path = global_path+"/tools/chromedriver"
    help_image_save_to = global_path+"/plugins/help/help.png"
    font_path = Path(get_resource_path(f'font{os.sep}custom.ttf')).as_uri()

    cqhttp = ""  # CQHTTP地址，参考`https://go-cqhttp.org`。

    welcome_file = global_path+"/tools/welcome.txt"
    version = ikv
    nonebot = nbv

    proxy = ""  # 代理服务器地址，以`http://`开头或`https://`开头，可以跟端口。

    auaurl = ""  # Arcaea Unlimited API地址

    auatok = ""  # Arcaea Unlimited API Token
    # 以上两者都请进群：“574250621”

    jx3api_wslink = ""  # JX3API WebSocket地址

    jx3api_wstoken = ""  # JX3API WebSocket Token

    jx3api_globaltoken = ""  # JX3API API Token
    # 以上三者都请访问：“https://vip.jx3api.com”

    sfapi_wslink = "ws://124.221.188.227:45248/subscribe"  # SFAPI WebSocket地址

    sfapi_wstoken = "8eeeeb64e126677817b775730251fbc9664f2ff7206bd18416c95506b3a197be"  # SFAPI WebSocket Token

    ght = ""  # GitHub Personal Access Token

    jx3_token = "d9de1e7c81304916ab33ab54b85efc02:aserfend:kingsoft::e9xL7/yjHzQMr2oIT1jl4A=="  # 推栏Token，抓包可得

    repo_name = ""  # 该`Inkar-Suki`的副本的来源，若从主仓库克隆，则填写`codethink-cn/Inkar-Suki`，若为fork之后克隆的仓库，则填写`<你的GitHub用户名>/Inkar-Suki`

    jx3api_link = "https://v7.jx3api.com"  # JX3API API链接
