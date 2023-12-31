from sgtpyutils.logger import logger
import functools
from ...args import *


class DocumentItem:
    aliases: set[str]  # 别名
    description: str  # 概要描述
    priority: int  # 命令优先级
    example: list[Jx3ArgsType]  # 参数类型列表
    catalog: str  # 目录，用于权限和功能分组
    document: str  # 详细描述

    def __init__(self, data: dict) -> None:
        self.aliases = data.get('aliases')
        self.description = data.get('description')
        self.priority = data.get('priority') or 0
        self.example = data.get('example')
        self.catalog = data.get('catalog')
        self.document = data.get('document')


class DocumentGenerator:
    commands: dict[str, DocumentItem] = {}

    def register_single(*args, **kwargs):
        cmd = args[0]
        DocumentGenerator.commands[cmd] = DocumentItem(kwargs)

    @staticmethod
    def register(method: callable):
        '''TODO 注册到帮助文档'''
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            result = method(*args, **kwargs)
            DocumentGenerator.register_single(*args, **kwargs)
            return result
        return wrapper

    # TODO 不会写
    @staticmethod
    def counter(method: callable):
        '''TODO 用户每次使用时调用'''
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            result = method(*args, **kwargs)
            logger.debug(f'功能调用:{args},{kwargs}')
            return result
        return wrapper
