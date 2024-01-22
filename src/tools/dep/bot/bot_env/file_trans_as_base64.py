import os
import typing
import pathlib
from io import BytesIO
from nonebot.adapters.onebot import utils
__raw_f2s = utils.f2s


def __base64d_f2s(file: typing.Union[str, bytes, BytesIO, pathlib.Path]):
    if not isinstance(file, pathlib.Path):
        return __raw_f2s(file)
        
    if not os.path.isfile(file):
        return __raw_f2s(file)

    with open(file, 'rb') as f:
        return __raw_f2s(f.read())


utils.f2s = __base64d_f2s
