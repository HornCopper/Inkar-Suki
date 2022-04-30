import os
import time
import traceback
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import sys
import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from config import Config
def main():
    path = os.getcwd()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument(f'window-size={Config.size}')
    full_path = Path(Config.html_path).as_uri()
    try:
        driver = webdriver.Chrome(options=options,executable_path=Config.chromedriver_path)
        driver.maximize_window()
        driver.get(full_path)
        time.sleep(0.1)
        driver.get_screenshot_as_file(Config.help_image_save_to)
        driver.quit()
        return "200 OK"
    except WebDriverException:
        traceback.print_exc()
        return WebDriverException