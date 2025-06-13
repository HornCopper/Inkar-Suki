from .achievement import (
    zone_achievement_matcher,
    achievement_v2_matcher
)
from .almanac import (
    almanac_matcher,
    almanac_image_matcher
)
from .announce import (
    announce_matcher,
    beta_announce_matcher,
    skill_change_matcher
)
from .assistance import (
    book_team_matcher,
    teamlist_matcher,
    cancel_team_matcher,
    create_team_matcher,
    lookup_team_matcher,
    dissolve_team_matcher,
    share_team_matcher
)
from .attributes import (
    attribute_v2_matcher,
    attribute_v2remake_matcher
)
from .bind import (
    server_bind_matcher,
    role_check_matcher
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
    yinlongjue_calc_matcher
)
from .cost import (
    cost_calc_matcher
)
from .couple import (
    bind_affection_matcher,
    delete_affection_matcher,
    affection_crt_matcher
)
from .daily import (
    daily_matcher
)
from .detail import (
    achievement_overview_matcher
)
from .dungeon import (
    monsters_matcher,
    drops_list_matcher,
    zone_record_matcher,
    allserver_item_record_matcher,
    all_roles_teamcd_matcher,
    role_monsters_matcher
)
from .emoji import (
    emoji_matcher
)
from .equip import (
    referenced_equip_matcher
)
from .events import (
    chutian_matcher,
    yuncong_matcher,
    zhue_matcher
)
from .exam import (
    exam_matcher
)
from .firework import (
    firework_matcher
)
from .gold import (
    coin_price_matcher
)
from .horse import (
    horse_chat_matcher,
    horse_spawn_matcher
)
from .item import (
    item_detail_matcher
)
from .joy import (
    saohua_matcher,
    tiangou_matcher,
    random_loot_matcher,
    random_shilian_matcher
)
from .lookup import (
    lookup_matcher
)
from .penzai import (
    dunhao_matcher,
    waiguan_matcher
)
from .personal import (
    all_personal_roles_matcher,
    personal_bind_matcher,
    personal_unbind_matcher
)
from .pvp import (
    arena_record_matcher
)
from .rank import (
    exp_rank_matcher,
    rhps_rank_matcher,
    rdps_rank_matcher,
    slrank_matcher
)
from .recruit import (
    recruit_matcher
)
from .role import (
    role_info_matcher
)
from .sandbox import (
    sandbox_matcher
)
from .serendipity import (
    serendipity_v2_matcher,
    serendipity_v3_matcher,
    preposition_matcher
)
from .server import (
    server_matcher
)
from .show import (
    show_matcher
)
from .skill import (
    matrix_matcher,
    macro_matcher,
    skill_matcher
)
from .snacks import (
    school_snacks_matcher
)
from .subscribe import (
    enable_matcher,
    disable_matcher
)
from .trade import (
    trade_v2_matcher,
    trade_v2_sl_matcher,
    item_price_v2_matcher,
    wanbaolou_role_matcher
)
from .version import (
    version_matcher
)