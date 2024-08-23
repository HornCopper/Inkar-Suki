try:
    from .application_v2 import * # type: ignore
    # 只用于公共实例，其他实例请勿使用该代码
except:
    pass
from .application import *
from .classic import *
from .feedback import *