from __future__ import annotations
from .Base import *


class Kunfu(Aliasable):
    '''心法'''
    database = './config.kunfu'

    belong: str
    '''归属的门派'''
    gameid: int
    '''游戏id'''
    color: str
    '''主色调'''

    def register_alias(self):
        d = self._get_dict()
        d[self.gameid] = self  # 将id也注册到缓存
        return super().register_alias()

    @property
    def icon(self):
        return f"https://img.jx3box.com/image/xf/{self.gameid}.png"
