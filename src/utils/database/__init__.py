from src.utils.database.lib import Database
from src.utils.database.classes import (
    Account,
    ApplicationsList,
    Affections,
    BannedUser,
    GroupSettings,
    Population,
    RoleData,
    JX3APIWSData,
    RequestData,
    SerendipityData
)

from src.const.path import DATA, build_path

db = Database(build_path(DATA, ["Snowykami.db"]))

db.auto_migrate(
    Account(),
    ApplicationsList(),
    Affections(),
    BannedUser(),
    GroupSettings(),
    Population(),
    RoleData()
)

cache_db = Database(build_path(DATA, ["cache.db"]))

cache_db.auto_migrate(
    JX3APIWSData(),
    RequestData()
)

serendipity_db = Database(build_path(DATA, ["serendipity.db"]))

serendipity_db.auto_migrate(
    SerendipityData()
)