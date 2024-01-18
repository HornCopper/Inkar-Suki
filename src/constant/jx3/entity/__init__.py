from .Server import *
from .Kunfu import *
from .School import *
from .PrimaryAttr import *


__target_types = [Kunfu, School, PrimaryAttr, Server]


for t in __target_types:
    t._register_type()
