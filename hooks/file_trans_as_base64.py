from sgtpyutils.logger import logger
import os
import typing
import pathlib
from io import BytesIO
import nonebot.adapters.onebot.v11.message
import nonebot.adapters.onebot.utils
__raw_f2s = nonebot.adapters.onebot.v11.message.f2s

protocal_file = 'file://'


def __base64d_f2s(file: typing.Union[str, bytes, BytesIO, pathlib.Path]):
    if isinstance(file, pathlib.Path):
        file = file.as_uri()
    if not isinstance(file, str):
        return __raw_f2s(file)
    if file.startswith(protocal_file):
        file = file[len(protocal_file)+1:]

    if not os.path.exists(file):
        logger.warning(f'target image file not exist:{file}')
        return __raw_f2s(file)

    with open(file, 'rb') as f:
        return __raw_f2s(f.read())


nonebot.adapters.onebot.v11.message.f2s = __base64d_f2s
nonebot.adapters.onebot.utils.f2s = __base64d_f2s
