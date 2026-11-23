from src.utils.database.lib import Database
from src.utils.database.classes import (
    Account,
    CheckinPrize,
    CheckinPrizeAward,
    Applicationslist,
    Affections,
    BannedUser,
    BanRecord,
    CQCRank,
    EquipmentRatingDpsRank,
    THRRank,
    TCSRank,
    GroupSettings,
    RaidTeamHealth,
    ItemKeywordMap,
    PersonalSettings,
    Population,
    PlayerEquipsCache,
    EquipmentRatingCache,
    EquipmentRatingRaceEventCache,
    EquipmentRatingRaceBossCache,
    EquipmentRatingRaceRoleCache,
    RoleData,
    JX3APIWSData,
    RequestData,
    SerendipityData,
    GroupMessage,
    RandomAffectionRecord,
    EquipReplacementLog,
    CommandUsage,
    AnalyzerUsage,
    RandomImageRecord,
)

from src.const.path import DATA, build_path

db = Database(build_path(DATA, ["Snowykami.db"]))

db.auto_migrate(
    Account(),
    CheckinPrize(),
    CheckinPrizeAward(),
    Applicationslist(),
    Affections(),
    BannedUser(),
    GroupSettings(),
    RaidTeamHealth(),
    ItemKeywordMap(),
    PersonalSettings(),
    Population(),
    RoleData(),
    RandomAffectionRecord(),
)

cache_db = Database(build_path(DATA, ["cache.db"]))

cache_db.auto_migrate(
    BanRecord(),
    JX3APIWSData(),
    RequestData(),
    EquipmentRatingRaceEventCache(),
    EquipmentRatingRaceBossCache(),
    EquipmentRatingRaceRoleCache(),
    GroupMessage(),
)

# 每条群消息都会按群、成员查找统计记录；同时支持按群查询排行榜。
with cache_db.transaction():
    cache_db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_group_message_group_user ON group_message (group_id, user_id)",
    )

serendipity_db = Database(build_path(DATA, ["serendipity.db"]))

serendipity_db.auto_migrate(
    SerendipityData(),
)

attribute_db = Database(build_path(DATA, ["attributes.db"]))

attribute_db.auto_migrate(
    PlayerEquipsCache(),
    EquipmentRatingCache(),
)

rank_db = Database(build_path(DATA, ["rank.db"]))

rank_db.auto_migrate(
    CQCRank(),
    THRRank(),
    TCSRank(),
    EquipmentRatingDpsRank(),
)

logs_db = Database(build_path(DATA, ["logs.db"]))

logs_db.auto_migrate(
    EquipReplacementLog(),
    CommandUsage(),
    AnalyzerUsage(),
    RandomImageRecord(),
)
