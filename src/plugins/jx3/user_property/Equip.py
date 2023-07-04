class WCommonEnchant:
    '''
    大附魔属性
    '''

    def __init__(self, id: str) -> None:
        self.id = id


class Equip:
    def __init__(self, data: dict) -> None:
        self.name = data.get('Name')
        self.icon = data.get('Icon') # 图标url
        self.set = { # 套装列表
            'total': data.get('SetList'),
            'current': data.get('SetListMap')
        }
        self.color_index = int(data.get('Color') or 0)
        self.stone = data.get('FiveStone') # 五行石 [{Level,Name}]
        self.level = data.get('Level') # 游戏等级
        self.quality = data.get('Quality') # 品质

        t = data.get('WCommonEnchant') or {}  # 大附魔 {Desc:'',Id:'11111'}
        self.wCommonEnchant = WCommonEnchant(t.get('ID')) if t.get('ID') else None # 判断是否有大附魔
        self.wPermanentEnchant = data.get(
            'WPermanentEnchant')  # 小附魔 {Attributes,Name}

        self.belongs = { # 所属心法
            'kungfu':data.get('BelongKungfu'), # 心法（按,分割）列表
            'school':data.get('BelongSchool'), # 门派/精简/通用
        }