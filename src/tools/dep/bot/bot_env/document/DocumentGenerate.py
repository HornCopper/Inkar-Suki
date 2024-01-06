from src.tools.dep.args import Jx3ArgsType

import inspect
import threading
from sgtpyutils.logger import logger
from sgtpyutils import extensions
from sgtpyutils.functools import *
import functools

from ..DocumentCatalog import permission, BaseCatalog
from .DocumentItem import DocumentItem
from .converter import *


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
        '''注册到帮助文档
        此处注册的名字为命令名称，需要保证名称与函数名一致'''
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            arg = AssignableArg(args=args, kwargs=kwargs, method=method)
            if 'regex' in method.__name__:  # 重写正则
                x = DocumentGenerator.get_regex(args[0])
                arg.set_args(0, x)
            docs = DocumentGenerator.register_single(arg)
            result = method(*arg.args, **arg.kwargs)
            # logger.debug(f'docs:{docs}') # 显示很慢
            return result
        return wrapper

    @staticmethod
    def record(method: callable):
        '''记录每次指令调用'''
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            args = AssignableArg(args, kwargs, method)

            raw_input, _ = args.check_if_exist('raw_input')
            raw_input = convert_to_str(raw_input)
            args.set_args(0, raw_input)

            result = method(*args.args, **args.kwargs)
            DocumentGenerator._record_log(args, result)
            return result
        return wrapper

    @staticmethod
    def _record_log(args: AssignableArg, result: list[any]):
        method, _ = args.check_if_exist('method')
        raw_input, _ = args.check_if_exist('raw_input')
        event, _ = args.check_if_exist('event')

        if method:
            if isinstance(method, str):
                caller_name = method
            else:
                caller_name = method.__name__
        else:
            method_names = [x[3] for x in inspect.stack()]
            caller_name_pos = extensions.find(enumerate(method_names), lambda x: x[1] == 'get_args')
            caller_name = method_names[caller_name_pos[0] + 1]

        log = {
            'name': caller_name,
            'args': result,
            'raw': raw_input,
            'group': event and event.group_id,
            'user': event and event.user_id,
        }
        logger.debug(f'func_called:{log}')

    @staticmethod
    def get_regex(pattern: str):
        # 精确匹配
        if not pattern[-1] == '$':
            return f'{pattern}($| )'

        # 和常规匹配
        return pattern

    @staticmethod
    def counter(method: callable):
        # TODO 不会写
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
