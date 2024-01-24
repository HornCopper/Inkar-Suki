import json
import os
import inspect

class Config:
    '''
    这里是`Inkar Suki`的配置文件，从`V0.8.3-Hotfix-3起，我们删除了`initialization.py`。
    取消了问答式配置，改为了用户自己填写。
    需要您填写的是末尾有注释的行，其他行请勿改动，感谢使用！
    '''
    config_py_path = os.path.abspath(inspect.getfile(inspect.currentframe()))[:-10]
    global_path = config_py_path[:-6]+"/"


    web_path = "/webhook" # GitHub Webhook的地址，填写`/a`，则内网地址为`http://127.0.0.1:<NB端口>/a`，`NB端口`在`.env.dev`中的`PORT`


    bot = ["3438531564"] # Bot的QQ号，此处请只填写一个，用`str`存在`list`中。


    platform = True # 平台标识，`True`为Linux，`False`为`Windows`


    owner = ["3349104868"] # Bot主人，可以有多个，用`str`存在`list`中


    size = global_path+"/tools/size.txt"
    html_path = global_path+"/plugins/help/help.html"
    chromedriver_path = global_path+"/tools/chromedriver"
    help_image_save_to = global_path+"/plugins/help/help.png"
    font_path = "file://"+global_path+"/tools/custom.ttf"


    cqhttp = "http://127.0.0.1:2334/" # CQHTTP地址，参考`https://go-cqhttp.org`。


    welcome_file = global_path+"/tools/welcome.txt"


    proxy = "http://1.15.9.114:25565" # 代理服务器地址，以`http://`开头或`https://`开头，可以跟端口。


    auaurl = "https://server.awbugl.top/botarcapi/" # Arcaea Unlimited API地址


    auatok = "004800c79f48e448daa6272adef67df31a627400" # Arcaea Unlimited API Token
    # 以上两者都请进群：“574250621”


    jx3api_wslink = "wss://socket.nicemoe.cn" # JX3API WebSocket地址


    jx3api_wstoken = "" # JX3API WebSocket Token


    jx3api_globaltoken = "axqn3mkzh3dyz0e78z" # JX3API API Token
    # 以上三者都请访问：“https://vip.jx3api.com”

    ght = "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" # GitHub Personal Access Token


    jx3_token = "7d5bd6dbf10e4fe8829ff90cdffa2086:17823651401:kingsoft::FcebOo2A6RZkmLdTKtENBw==" # 推栏Token
    
    repo_name = "codethink-cn/Inkar-Suki"

    jx3api_link = "https://www.jx3api.com"

flag = False
try:
    permission_file = open(Config.config_py_path + "/permission.json", mode="r")
except FileNotFoundError:
    permission_file = open(Config.config_py_path + "/permission.json", mode="w")
    add = {}
    for i in Config.owner:
        if i not in list(add):
            add[i] = 10
    permission_file.write(json.dumps(add))
    permission_file.close()
    flag = True
if flag == False:
    permission_file.close()