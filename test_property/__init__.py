from .Equip import *
from .UserProperty import *
from .Jx3Player import *


async def run():
    user = Jx3PlayerInfoWithInit.from_id('唯我独尊', '步龄')

    data = await Jx3PlayerDetailInfo.get_property_by_uid(user.roleId, user.serverName)
    pass
