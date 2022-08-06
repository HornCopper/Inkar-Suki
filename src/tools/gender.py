import uuid
import time
import traceback
import sys
import nonebot
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
CACHE = TOOLS.replace("tools","cache")
from config import Config

def get_uuid():
    return str(uuid.uuid1()).replace("-","")

def gender(html: str,waiting: int,size: str, web: bool):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument(f'window-size={size}')
    if web:
        pass
    else:
        html = Path(html).as_uri()
    try:
        driver = webdriver.Chrome(options=options,executable_path=Config.chromedriver_path)
        driver.maximize_window()
        driver.get(html)
        time.sleep(waiting)
        uuid_=get_uuid()
        final_path=CACHE + "/" + uuid_ + ".png"
        driver.get_screenshot_as_file(final_path)
        driver.quit()
        return final_path
    except WebDriverException:
        traceback.print_exc()
        return WebDriverException
        
