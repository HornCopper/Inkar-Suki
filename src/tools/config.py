from local_version import local_version, nonebot_version
import nonebot, sys
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from file import read
configs = json.loads(read("./config.json"))
class Config:
    global_path = "./src"
    web_path = config["web_path"]
    bot = configs["bot"]
    platform = config["platform"]
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
