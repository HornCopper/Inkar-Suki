from .Kunfu import *
from .School import *
import pathlib2
from sgtpyutils.extensions.clazz import *
from src.tools.dep.bot import *

current = pathlib2.Path(__file__).parent
db_school = filebase_database.Database(str(current.joinpath('./config.school'))).value  # 门派数据
dict_school: dict[str, Kunfu] = dict([[x.get('name'), dict2obj(School(), x)]
                                     for x in db_school])  # 门派字典
for x in dict_school:
    dict_school[x].register_alias()


db_kunfu = filebase_database.Database(str(current.joinpath('./config.kunfu'))).value  # 心法数据
dict_kunfu: dict[str, Kunfu] = dict([[x.get('name'), dict2obj(Kunfu(), x)]
                                     for x in db_kunfu])  # 心法字典

for x in dict_kunfu:
    dict_kunfu[x].register_alias()
