from typing import List, Dict

from src.utils.database.lib import LiteModel

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

class ApplicationsList(LiteModel):
    TABLE_NAME: str = "applications"
    applications_list: list = []

class BannedUser(LiteModel):
    TABLE_NAME: str = "ban"
    user_id: int = 0
    reason: str = ""    

class GroupSettings(LiteModel):
    TABLE_NAME: str = "settings"
    server: str = ""
    group_id: str = ""
    subscribe: List[str] = []
    additions: List[str] = []
    welcome: str = "欢迎入群！"
    blacklist: List[Dict[str, str]] = [] 
    wiki: dict = {"startwiki": "", "interwiki": []}
    webhook: List[str] = []
    opening: list = []

class JX3APIWSData(LiteModel):
    TABLE_NAME: str = "jx3api_wsdata"
    action: int = 0
    event: str = ""
    data: dict = {}
    timestamp: int = 0

class Population(LiteModel):
    TABLE_NAME: str = "population"
    populations: dict = {}

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