from src.utils.database.lib import Database
from src.utils.database.classes import (
    Account,
    Applicationslist,
    Affections,
    BannedUser,
    GroupSettings,
    ItemKeywordMap,
    PersonalSettings,
    Population,
    RoleData,
    JX3APIWSData,
    RequestData,
    SerendipityData,
    GroupMessage
)

from src.const.path import DATA, build_path

db = Database(build_path(DATA, ["Snowykami.db"]))

db.auto_migrate(
    Account(),
    Applicationslist(),
    Affections(),
    BannedUser(),
    GroupSettings(),
    ItemKeywordMap(),
    PersonalSettings(),
    Population(),
    RoleData()
)

cache_db = Database(build_path(DATA, ["cache.db"]))

cache_db.auto_migrate(
    JX3APIWSData(),
    RequestData(),
    GroupMessage()
)

serendipity_db = Database(build_path(DATA, ["serendipity.db"]))

serendipity_db.auto_migrate(
    SerendipityData()
)