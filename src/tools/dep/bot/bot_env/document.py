import threading
from sgtpyutils.logger import logger
import functools
from ...args import *
from .args_template import *

from . import DocumentCatalog
from .DocumentCatalog import permission, BaseCatalog


class DocumentItem:
    cmd: str  # 命令
    name: str  # 名称
    aliases: set[str]  # 别名
    description: str  # 概要描述
    priority: int  # 命令优先级
    example: list[Jx3ArgsType]  # 参数类型列表
    catalog: BaseCatalog  # 目录，用于权限和功能分组
    document: str  # 详细描述

    def __init__(self, cmd: str, arg: AssignableArg) -> None:
        self.cmd = cmd
        data = arg.kwargs

        self.name = data.get('name')
        self.aliases: set = data.get('aliases') or set()
        if self.name:
            if not self.name in self.aliases:
                self.aliases.add(self.name)  # 将名称设置为默认命令
                data['aliases'] = self.aliases
        elif self.aliases:
            self.name = self.aliases.__iter__().__next__()  # 如果没有定义名称则将别名认为是名称
        elif self.cmd: # 否则以命令来命名
            self.name = self.cmd

        self.description = data.get('description')
        self.priority = data.get('priority') or 0
        self.example = data.get('example') or []

        catalog = data.get('catalog')
        if isinstance(catalog, str):
            cata = DocumentCatalog.cata_entity_dict.get(catalog)
            if cata:
                catalog = cata
            else:
                logger.warning(f'[document]invalid catalog name:{catalog}')
                catalog = None
        self.catalog = catalog
        
        self.document = data.get('document')

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        alias = f',({self.aliases})' if self.aliases else ''
        return f'{self.name}[{self.catalog}]{self.cmd}{alias}: {self.description}'

    def to_dict(self) -> dict[str, any]:
        example = [tpl.name for tpl in self.example]
        return {
            'name': self.name,
            'cmd': self.cmd,
            'aliases': list(self.aliases or {}),
            'description': self.description,
            'priority': self.priority,
            'example': example,
            'document': self.document,
            'catalog': self.catalog and self.catalog.path,
        }


class DocumentGenerator:
    commands: dict[str, DocumentItem] = {}
    _document: dict = None
    _doc_lock = threading.RLock()

    @staticmethod
    def register_single(arg: AssignableArg):
        cmd = arg.args[0]
        docs = DocumentItem(cmd, arg)
        DocumentGenerator.commands[cmd] = docs
        return docs

    @staticmethod
    def register(method: callable):
        '''TODO 注册到帮助文档
        此处注册的名字为命令名称，需要保证名称与函数名一致'''
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            arg = AssignableArg(args, kwargs)
            docs = DocumentGenerator.register_single(arg)
            result = method(*arg.args, **arg.kwargs)
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

    @staticmethod
    def _get_documents() -> dict:
        catalogs = permission.to_dict()
        commands = [DocumentGenerator.commands[x].to_dict() for x in DocumentGenerator.commands]
        args_template = dict([[x.name, x.to_dict()] for x in Jx3ArgsType])
        return {
            'catalogs': catalogs,
            'commands': commands,
            'args_template': args_template,
        }

    @staticmethod
    def get_documents() -> dict:
        '''获取文档数据'''
        with DocumentGenerator._doc_lock:
            if DocumentGenerator._document:
                return DocumentGenerator._document
            DocumentGenerator._document = DocumentGenerator._get_documents()
            return DocumentGenerator._document
