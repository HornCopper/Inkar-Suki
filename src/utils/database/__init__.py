from src.utils.database.lib import Database
from src.utils.database.classes import (
    Account,
    Applicationslist,
    Affections,
    BannedUser,
    BanRecord,
    CQCRank,
    THRRank,
    GroupSettings,
    RaidTeamHealth,
    ItemKeywordMap,
    PersonalSettings,
    Population,
    PlayerEquipsCache,
    EquipmentRatingCache,
    RoleData,
    JX3APIWSData,
    RequestData,
    SerendipityData,
    GroupMessage,
    RandomAffectionRecord,
    EquipReplacementLog
)

from src.const.path import DATA, build_path

db = Database(build_path(DATA, ["Snowykami.db"]))

db.auto_migrate(
    Account(),
    Applicationslist(),
    Affections(),
    BannedUser(),
    GroupSettings(),
    RaidTeamHealth(),
    ItemKeywordMap(),
    PersonalSettings(),
    Population(),
    RoleData(),
    RandomAffectionRecord()
)

cache_db = Database(build_path(DATA, ["cache.db"]))

cache_db.auto_migrate(
    BanRecord(),
    JX3APIWSData(),
    RequestData(),
    GroupMessage()
)

serendipity_db = Database(build_path(DATA, ["serendipity.db"]))

serendipity_db.auto_migrate(
    SerendipityData()
)

attribute_db = Database(build_path(DATA, ["attributes.db"]))

attribute_db.auto_migrate(
    PlayerEquipsCache(),
    EquipmentRatingCache()
)

rank_db = Database(build_path(DATA, ["rank.db"]))

rank_db.auto_migrate(
    CQCRank(),
    THRRank()
)

logs_db = Database(build_path(DATA, ["logs.db"]))

logs_db.auto_migrate(
    EquipReplacementLog()
)
