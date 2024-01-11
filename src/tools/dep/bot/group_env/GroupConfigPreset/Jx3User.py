from src.tools.utils import *
from ..GroupConfigInfo import *
userAuthConfig: dict[str, GroupConfigInfo] = {
    'level': GroupConfigInfo('等级', default=0),
    'role': GroupConfigInfo('', default={}, description='拥有的角色'),
}
userConfigInfos: dict[str, GroupConfigInfo] = {
    'permission': GroupConfigInfo('授权', default={}, infos=userAuthConfig),
}
