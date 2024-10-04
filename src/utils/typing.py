from typing import overload

def override(method):
    """
    自定义的 @override 装饰器，仅用于文档和标识作用。
    """
    return method