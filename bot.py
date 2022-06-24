#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nonebot, json
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
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