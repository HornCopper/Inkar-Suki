from __future__ import annotations
from src.tools.dep.api.argparser import *
import enum
from src.tools.utils.request import *


class Jx3ApiResponse:
    def convert_403(self):
        if '侠客隐藏了游戏信息' in self.msg:
            return '这个人设置了隐藏'
        if '仅互关好友可见' in self.msg:
            return '这个人设置了仅好友可见'
        return '这个人不允许查看他的信息'

    errors = {
        400: lambda x: '输入的命令可能有错哦~',
        403: convert_403,
        404: lambda x: '没有找到这个人。',
        406: lambda x: '获取信息失败了，先别用了o(╥﹏╥)o',
    }

    def __init__(self, data: dict) -> None:
        self.code: int = data.get('code')
        self.data: dict = data
        self.url: str = data.get('url')
        self.msg: str = data.get('msg')

    @property
    def success(self):
        return self.code == 200

    @property
    def error_msg(self):
        if self.success:
            return None
        callback = Jx3ApiResponse.errors.get(self.code)
        error = callback(self) or f'未知错误(代码:{self.code})'
        return error

    @property
    def output_url(self):
        err = self.error_msg
        return [err] or self.url


class ArgRequire(enum.Enum):
    token = Jx3Arg.requireToken
    ticket = Jx3Arg.requireTicket


class Jx3ApiRequest:
    def __init__(self, url: str, argRequest: ArgRequire = None) -> None:
        self.url = url
        self.argRequest = argRequest

    async def output_url(self):
        data = await get_api(self.url)
        response = Jx3ApiResponse(data)
        return response.output_url

    @classmethod
    def request(cls, x: Jx3ApiRequest):
        '''TODO AOP generate'''
        return 
