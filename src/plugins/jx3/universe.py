from .achievement import (
    ZoneAchiMatcher,
    JX3AdventureMatcher,
    JX3ProgressV2Matcher
)
from .almanac import (
    AlmanacMatcher,
    AlmanacImageMatcher
)
from .announce import (
    AnnounceMatcher,
    BetaAnnounceMatcher
)
from .assistance import (
    BookTeamMatcher,
    TeamlistMatcher,
    CancelTeamMatcher,
    CreateTeamMatcher,
    LookupTeamMatcher,
    DissolveTeamMatcher,
    ShareTeamMatcher
)
from .attributes import (
    AttributeV2Matcher,
    AttributeV2RemakeMatcher
)
from .bind import (
    BindServerMatcher,
    RoleCheckMatcher
)
# from .calculator import (
#     DJCalcMatcher,
#     WFCalcMatcher,
#     YLJCalcMatcher,
#     ZXGCalcMatcher,
#     SHXJCalcMatcher
# )
# RIP: not adapted
from .calculator import (
    YLJCalcMatcher
)
from .cost import (
    CostCalculatorMatcher
)
from .couple import (
    BindAffectionMatcher,
    DeleteAffectionMatcher,
    AffectionsCrtMatcher
)
from .daily import (
    DailyMatcher
)
from .detail import (
    AchievementMatcher
)
from .dungeon import (
    MonstersMatcher,
    DropslistMatcher,
    ZoneRecordMatcher,
    AllServerItemRecordMatcher,
    AllRolesTeamcdMatcher
)
from .emoji import (
    EmojiMatcher
)
from .equip import (
    EquipRecommendMatcher
)
from .events import (
    ZhueMatcher,
    ChutianMatcher,
    YuncongMatcher
)
from .exam import (
    ExamMatcher
)
from .gold import (
    CoinPriceMatcher
)
from .horse import (
    DiluMatcher,
    HorseChatMatcher,
    HorseSpawnMatcher
)
from .item import (
    ItemSearcherMatcher
)
from .joy import (
    SaohuaMatcher,
    TiangouMatcher
)
from .lookup import (
    LookupPersonMatcher
)
from .penzai import (
    DHMatcher,
    WGMatcher
)
from .personal import (
    AllBoundRolesMatcher,
    PersonalBindMathcer,
    PersonalUnbindMathcer
)
from .pvp import (
    ArenaRecordMatcher
)
from .rank import (
    ZiliRankMatcher
)
from .recruit import (
    RecruitMatcher
)
from .role import (
    RoleInfoMatcher
)
from .sandbox import (
    SandboxMatcher
)
from .serendipity import (
    V2SerendipityMatcher,
    V3SerendipityMatcher,
    PrepositionMatcher
)
from .server import (
    ServerMatcher
)
from .show import (
    ShowMatcher
)
from .skill import (
    MatrixMatcher,
    MacroMatcher,
    SkillMatcher
)
from .snacks import (
    SchoolSnacksMatcher
)
from .subscribe import (
    EnableMatcher,
    DisableMatcher
)
from .trade import (
    V2TradeMatcher,
    V2SLTradeMatcher,
    V2ItemPriceMatcher,
    WBLRolePriceMatcher
)
from .version import (
    VersionMatcher
)