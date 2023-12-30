class DocumentItem:
    method_name: str  # 函数名称
    aliases: list[str]  # 别名
    description: str  # 概要描述

    


class DocumentGenerator:
    def __init__(self) -> None:
        pass

    @staticmethod
    def register(method):
        '''TODO 注册到帮助文档'''
        pass
    @staticmethod
    def counter(method):
        '''TODO 用户每次使用时调用'''
        pass
