import os
import time
import traceback
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
def main():
    path = os.getcwd()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    file = open("/root/nb/src/plugins/help/size",mode="r")
    size = file.read()
    file.close()
    options.add_argument(f'window-size={size}')
    full_path = Path("/root/nb/src/plugins/help/help.html").as_uri()
    try:
        driver = webdriver.Chrome(options=options,executable_path="/root/nb/src/plugins/help/chromedriver")
        driver.maximize_window()
        driver.get(full_path)
        time.sleep(0.1)
        driver.get_screenshot_as_file('/root/nb/src/plugins/help/help.png')
        driver.quit()
        return "200 OK"
    except WebDriverException:
        traceback.print_exc()
        return WebDriverException