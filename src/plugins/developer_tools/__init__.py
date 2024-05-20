try:
    from .application_v2 import * # 只用于公共实例，其他实例请勿使用该代码
except:
    from .application import *
from .classic import *
from .feedback import *