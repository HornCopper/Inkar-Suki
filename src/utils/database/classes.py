from src.utils.database.lib import LiteModel, BaseModel

class Account(LiteModel):
    TABLE_NAME: str = "accounts"
    user_id: int = 0
    checkin_counts: int = 0
    coins: int = 0
    permission: int = 0
    last_checkin: int = 0

class Affections(LiteModel):
    TABLE_NAME: str = "affections"
    server: str = ""
    uin_1: int = 0
    uin_2: int = 0
    name_1: str = ""
    name_2: str = ""
    time: int = 0
    school_1: str = ""
    school_2: str = ""

class Applicationslist(LiteModel):
    TABLE_NAME: str = "applications"
    applications_list: list = []

class BannedUser(LiteModel):
    TABLE_NAME: str = "ban"
    user_id: int = 0
    reason: str = ""    

class BanRecord(LiteModel):
    TABLE_NAME: str = "ban_record"
    user_id: int = 0
    group_id: int = 0
    expire: int = 0

class GroupSettings(LiteModel):
    TABLE_NAME: str = "settings"
    server: str = ""
    group_id: str = ""
    subscribe: list[str] = []
    additions: list[str] = []
    welcome: str = "欢迎入群！"
    blacklist: list[dict[str, str]] = [] 
    wiki: dict = {"startwiki": "", "interwiki": []}
    webhook: list[str] = []
    opening: list = []
    expire: int = 0
    invitor: int = 0

class ItemKeywordMap(LiteModel):
    TABLE_NAME: str = "item_keyword"
    map_name: str = ""
    raw_name: str = ""

class JX3APIWSData(LiteModel):
    TABLE_NAME: str = "jx3api_wsdata"
    action: int = 0
    event: str = ""
    data: dict = {}
    timestamp: int = 0

class PersonalSetting(BaseModel):
    attribute: str = "v4"
    theme: str = "浅色"
    trade: str = "v3"
    serendipity: str = "v2"
    anonymous: str = "否"
    income: str = "无增益"
    formation: str = "无阵眼"

class PersonalSettings(LiteModel):
    TABLE_NAME: str = "personal_settings"
    user_id: int = 0
    roles: list["RoleData"] = []
    setting: PersonalSetting = PersonalSetting()

class Population(LiteModel):
    TABLE_NAME: str = "population"
    populations: dict = {}

class PlayerEquipsCache(LiteModel):
    TABLE_NAME: str = "player_equip"
    equips_data: list = []
    talents_data: list = []
    global_role_id: int = 0
    kungfu_id: int = 0
    tag: str = ""
    timestamp: int = 0

class RequestData(LiteModel):
    TABLE_NAME: str = "request_data"
    url: str = ""
    headers: dict = {}
    params: dict = {}
    response_data: str = ""
    timestamp: int = 0

class RoleData(LiteModel):
    TABLE_NAME: str = "role_data"
    bodyName: str = ""
    campName: str = ""
    forceName: str = ""
    globalRoleId: str = ""
    roleName: str = ""
    roleId: str = ""
    serverName: str = ""

    def __eq__(self, other):
        if not isinstance(other, RoleData):
            return False
        return (self.serverName == other.serverName and
                self.roleName == other.roleName and
                self.roleId == other.roleId and
                self.globalRoleId == other.globalRoleId)

    def __hash__(self):
        return hash((self.serverName, self.roleName, self.roleId, self.globalRoleId))

    def __repr__(self):
        return (f"RoleData(serverName={self.serverName}, "
                f"roleName={self.roleName}, roleId={self.roleId}, "
                f"globalRoleId={self.globalRoleId})")

class SerendipityData(LiteModel):
    TABLE_NAME: str = "serendipities"
    roleName: str = ""
    roleId: str = ""
    level: int = 0
    server: str = ""
    serendipityName: str = ""
    time: int = 0

class MemberMessage(LiteModel):
    timestamp: int = 0

class GroupMessage(LiteModel):
    TABLE_NAME: str = "group_message"
    group_id: int = 0
    user_id: int = 0
    messages: list[MemberMessage] = []

class CQCRank(LiteModel):
    TABLE_NAME: str = "cqc_rank"
    role_name: str = ""
    server_name: str = ""
    kungfu_id: int = 0
    damage_per_second: int = 0
    total_damage: int = 0
    health_per_second: int = 0
    total_health: int = 0

class RandomAffectionRecord(LiteModel):
    TABLE_NAME: str = "random_affection_record"
    user_id: int = 0
    group_id: int = 0
    target_id: int = 0
    timestamp: int = 0

class HPSRankRecord(LiteModel):
    TABLE_NAME: str = "hps_rank_record"
    name: str = ""
    server: str = ""
    value: int = 0
    weapon: int = 0
    talents: list[int] = []