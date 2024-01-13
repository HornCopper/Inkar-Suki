class Kungfu:
    mapper = {
        'mowen': '莫问',
        'xiangzhi': '相知',
        'taixu': '太虚剑意',
        'wenshui': '问水诀',
        'shanju': '山居剑意',
        'fenshan': '分山劲',
        'linghai': '凌海诀',
        'yinlong': '隐龙诀',
        'shanhai': '山海心诀',
    }

    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def alias(self):
        return Kungfu.mapper.get(self.name) or f'u:{self.name}'
