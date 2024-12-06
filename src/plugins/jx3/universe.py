from .achievement import (
    ZoneAchiMatcher,
    JX3AdventureMatcher,
    JX3ProgressV2Matcher
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
    AttributeV4Matcher
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
from .couple import (
    BindAffectionMatcher,
    DeleteAffectionMatcher,
    AffectionsCrtMatcher
)
from .daily import (
    DailyMatcher
)
from .detail import (
    TeamZoneOverviewMatcher,
    ZoneOverviewMatcher
)
from .dungeon import (
    MonstersMatcher,
    DropslistMatcher,
    ZoneRecordMatcher,
    ItemRecordMatcher
)
from .emoji import (
    EmojiMatcher
)
from .equip import (
    RecommendEquipMatcher
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
from .pendant import (
    PendentMatcher
)
from .penzai import (
    DHMatcher,
    WGMatcher
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
    TradeMatcher,
    WFTradeMatcher,
    V2ItemPriceMatcher
)