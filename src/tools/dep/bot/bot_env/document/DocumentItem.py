
from src.tools.dep.args import Jx3ArgsType
from sgtpyutils.logger import logger
from sgtpyutils.functools import *
from .. import DocumentCatalog


class DocumentItem:
    cmd: str  # 命令
    name: str  # 名称
    aliases: set[str]  # 别名
    description: str  # 概要描述
    priority: int  # 命令优先级
    example: list[Jx3ArgsType]  # 参数类型列表
    catalog: DocumentCatalog.BaseCatalog  # 目录，用于权限和功能分组
    document: str  # 详细描述

    def __init__(self, cmd: str, arg: AssignableArg) -> None:
        self.cmd = cmd
        data = arg.kwargs

        self.name = data.get('name')
        self.aliases: set = data.get('aliases') or set()
        if self.name:
            if self.name not in self.aliases:
                self.aliases.add(self.name)  # 将名称设置为默认命令
                data['aliases'] = self.aliases
        elif self.aliases:
            self.name = self.aliases.__iter__().__next__()  # 如果没有定义名称则将别名认为是名称
        elif self.cmd:  # 否则以命令来命名
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
