from nonebot.log import logger

class log:
    def __init__():
        pass
    
    @staticmethod
    def info(msg: str, color: str = "green"):
        return logger.opt(colors=color).info(level=25, msg=msg)

logger.info("加载配置文件")