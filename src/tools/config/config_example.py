import json
import os
import inspect

class Config:
    """
    这里是`Inkar Suki`的配置文件，从`V0.8.3-Hotfix-3起，我们删除了`initialization.py`。
    取消了问答式配置，改为了用户自己填写。
    需要您填写的是末尾有注释的行，其他行请勿改动，感谢使用！
    """
    config_py_path = os.path.abspath(inspect.getfile(inspect.currentframe()))[:-10]
    global_path = config_py_path[:-6]+"/"
    name = "音卡" 

    web_path = "/webhook" # GitHub Webhook的地址，填写`/a`，则内网地址为`http://127.0.0.1:<NB端口>/a`，`NB端口`在`.env.dev`中的`PORT`


    platform = True # 平台标识，`True`为Linux，`False`为`Windows`


    owner = [""] # Bot主人，可以有多个，用`str`存在`list`中


    size = global_path + "/tools/size.txt"
    html_path = global_path + "/plugins/help/help.html"
    chromedriver_path = global_path + "/tools/chromedriver"
    help_image_save_to = global_path + "/plugins/help/help.png"
    font_path = "file://"+ global_path + "/assets/font/custom.ttf"


    cqhttp = "" # CQHTTP地址，参考`https://go-cqhttp.org`。


    proxy = "" # 代理服务器地址，以`http://`开头或`https://`开头，可以跟端口。


    auaurl = "" # Arcaea Unlimited API地址


    auatok = "" # Arcaea Unlimited API Token
    # 以上两者都请进群：“574250621”


    jx3api_wslink = "" # JX3API WebSocket地址


    jx3api_wstoken = "" # JX3API WebSocket Token


    jx3api_globaltoken = "" # JX3API API Token
    # 以上三者都请访问：“https://vip.jx3api.com”

    ght = "" # GitHub Personal Access Token


    jx3_token = "" # 推栏Token
    
    repo_name = "codethink-cn/Inkar-Suki"
    
    jx3api_link = "https://api.jx3api.com"
    
    notice_to = {
        "your_bot_uin": "admin_group_uin"
    }
    
    bot = list(notice_to)
    
    inkarsuki_offical_apitoken = "" # 非官方就留空