class PROMPT:
    ArgumentInvalid = "唔……参数有误！"
    NoToken = "唔……该音卡实例没有填写JX3API的token，数据获取失败，请联系机器人主人！"
    ServerNotExist = "唔……没有找到服务器参数，群聊似乎也没有绑定服务器哦，要不绑定试试呢？"
    ArgumentCountInvalid = "唔……参数数量有误，请检查后重试~"
    NoTicket = "唔……该音卡实例没有填写推栏的Ticket，数据获取失败，请联系机器人主人！"
    ServerInvalid = "唔……服务器输入有误！"
    ArgumentCountInvalid = "唔……参数数量有误，请检查后重试！"
    NumberInvalid = "唔……输入的不是数字或超出搜索范围，请重新搜索！"
    InvalidToken = "唔……该音卡实例的JX3API的token无效，请联系机器人主人！"
    NumberNotExist = "唔……输入的数字不在范围内哦，请检查后重试！"
    PlayerNotExist = "唔……未找到该玩家，请提交角色！\n提交角色 服务器 UID"

    KungfuNotExist = "未找到该心法，请检查后重试！"

    # jx3/achievement
    AchievementNotFound = "唔……未找到任何相关成就！"
    DungeonNameInvalid = "唔……副本名称输入错误！"
    DungeonInvalid = "唔……难度或名称输入错误！"

    # utils/database/player.py
    UIDInvalid = "唔……没有找到玩家，请检查UID和服务器是否正确！"

    # ban
    BanRepeatInvalid = "唔……封禁失败！（重复封禁）"

    # jx3/couple
    AffectionFormatInvalid = "绑定失败！请参考下面的命令格式：\n绑定情缘 自己ID 对方ID 对方QQ 时间(可不填)"
    AffectionUINInvalid = "绑定失败！对方QQ需要为纯数字！"
    AffectionExist = "唔……您已经绑定情缘了，无法再绑定新的情缘！"
    AffectionRoleNotExist = "绑定失败，对方或者自己的ID无法对应到角色！\n请检查对面或自身角色是否在本群聊绑定的服务器中！"
    AffectionBindComplete = "成功绑定情缘！\n可通过“查看情缘证书”生成一张情缘证书图！"
    AffectionUnbindWithNo = "咱就是说，还没绑定情缘，在解除什么呢？"
    AffectionGenerateWithNo = "咱就是说，还没绑定情缘，在生成什么呢？"

    # jx3/calculator
    CalculatorNotMatch = "唔……门派和计算器不匹配！"
    CalculatorValueInvalid = "唔……获取到的数据无法用于计算！\n请检查装备和职业！"

    # jx3/penzai
    NoCondition = "您没有输入条件哦，请检查后重试~\n条件以空格分割哦~"