from __future__ import annotations
from .Base import *


class Kunfu(Aliasable):
    '''心法'''

    belong: str
    '''归属的门派'''
    gameid: int
    '''游戏id'''
    color: str
    '''主色调'''

    @property
    def icon(self):
        return f"https://img.jx3box.com/image/xf/{self.gameid}.png"
