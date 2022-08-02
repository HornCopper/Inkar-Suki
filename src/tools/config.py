from local_version import nbv, ikv
import nonebot
import sys
import json
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from file import read
configs = json.loads(read("./src/tools/config.json"))
class Config:
    config_py_path = configs["abpath"]
    global_path = config_py_path[:-6]+"/"
    web_path = configs["web_path"]
    bot = configs["bot"]
    platform = configs["platform"]
    owner = configs["owner"]
    size = global_path+"/tools/size.txt"
    html_path = global_path+"/plugins/help/help.html"
    chromedriver_path = global_path+"/tools/chromedriver"
    help_image_save_to = global_path+"/plugins/help/help.png"
    font_path = "file://"+global_path+"/tools/custom.ttf"
    cqhttp = configs["cqhttp"]
    welcome_file = global_path+"/tools/welcome.txt"
    version = ikv
    nonebot = nbv
    auaurl = configs["aua_api"]
    auatok = configs["aua_token"]