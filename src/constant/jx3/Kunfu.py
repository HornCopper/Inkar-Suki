class Kunfu:
    '''心法'''

    belong: str
    '''归属的门派'''
    alias: list[str]
    '''别称'''
    name: str
    '''名称'''
    gameid: int
    '''游戏id'''
    color: str
    '''主色调'''

    @property
    def icon(self):
        return f"https://img.jx3box.com/image/xf/{self.gameid}.png"
