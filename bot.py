#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nonebot
import sys
import json
import os
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
plugins = os.listdir("./src/plugins")
error = False
for i in plugins:
    if os.path.exists("./src/plugins/" + i + "/info.json") == False:
        error = True
        raise FileNotFoundError(f"Plugin `{i}` required a `info.json` but not found. Please check and try again.")
if error:
    sys.exit(1)
cache = open("./src/tools/config.json",mode="r")
nonebot.init(tools_path=json.loads(cache.read())["abpath"])
cache.close()
nonebot.init()
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_from_toml("pyproject.toml")
if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")