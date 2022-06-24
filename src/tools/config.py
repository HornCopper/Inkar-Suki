from local_version import local_version, nonebot_version
import nonebot, sys, json
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from file import read
configs = json.loads(read("./src/tools/config.json"))
class Config:
    config_py_path = __file__
    global_path = config_py_path[:config_py_path.find("/tools")]+"/"
    web_path = configs["web_path"]
    bot = configs["bot"]
    platform = configs["platform"]
    owner = configs["owner"]
    size = global_path+"/tools/size.txt"
    html_path = global_path+"/plugins/help/help.html"
    chromedriver_path = global_path+"/plugins/help/chromedriver"
    help_image_save_to = global_path+"/plugins/help/help.png"
    font_path = "file://"+global_path+"/plugins/help/oppo_sans.ttf"
    cqhttp = configs["cqhttp"]
    welcome_file = global_path+"/tools/welcome.txt"
    version = local_version
    nonebot = nonebot_version
