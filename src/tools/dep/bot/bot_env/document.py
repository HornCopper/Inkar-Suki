from sgtpyutils.logger import logger
import functools
from ...args import *
from .args_template import *


class DocumentItem:
    cmd: str  # 命令
    name: str  # 名称
    aliases: set[str]  # 别名
    description: str  # 概要描述
    priority: int  # 命令优先级
    example: list[Jx3ArgsType]  # 参数类型列表
    catalog: str  # 目录，用于权限和功能分组
    document: str  # 详细描述

    def __init__(self, cmd: str, data: dict) -> None:
        self.cmd = cmd
        self.name = data.get('name')
        self.aliases = data.get('aliases') or []
        if self.name:
            if not self.name in self.aliases:
                self.aliases.insert(0, self.name)  # 将名称设置为默认命令
                data['aliases'] = self.aliases
        elif self.aliases:
            self.name = self.aliases.__iter__().__next__  # 如果没有定义名称则将别名认为是名称
        self.description = data.get('description')
        self.priority = data.get('priority') or 0
        self.example = data.get('example')
        self.catalog = data.get('catalog')
        self.document = data.get('document')

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        alias = f',({self.aliases})' if self.aliases else ''
        return f'{self.name}[{self.catalog}]{self.cmd}{alias}: {self.description}'


class DocumentGenerator:
    commands: dict[str, DocumentItem] = {}

    def register_single(*args, **kwargs):
        cmd = args[0]
        docs = DocumentItem(cmd, kwargs)
        DocumentGenerator.commands[cmd] = docs
        return docs

    @staticmethod
    def register(method: callable):
        '''TODO 注册到帮助文档
        此处注册的名字为命令名称，需要保证名称与函数名一致'''
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            result = method(*args, **kwargs)
            docs = DocumentGenerator.register_single(*args, **kwargs)
            # logger.debug(f'docs:{docs}') # 显示很慢
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
