from __future__ import annotations
from src.tools.dep.api.argparser import *
from src.tools.utils.request import *
import enum



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
