StrengthIncome = [
    0, 0.005, 0.013, 0.024, 0.038, 0.055, 0.075, 0.098, 0.124
]

EquipLocations = [
    "武器", "重剑", "暗器", "上衣", "帽子", "项链", "戒指", "戒指", "腰带", "腰坠", "下装", "鞋子", "护腕"
    #  0     1      2       3      4       5       6      7       8      9       10      11     12
]

MaxStrengthLevel = 32000
MinStrengthLevel = 27800

# MaxStrengthLevel = 37400

Colors = [
    "(167, 167, 167)",
    "(255, 255, 255)",
    "(0, 210, 75)",
    "(0, 126, 255)",
    "(254, 45, 254)",
    "(255, 165, 0)",
]

A = 8.8
B = 32.0
C = 50.0

AttributesShort = {
    "atSpiritBase": "根骨",
    "atStrengthBase": "力道",
    "atAgilityBase": "身法",
    "atSpunkBase": "元气",
    "atVitalityBase": "体质",
    "atPhysicsAttackPowerBase": "攻击",
    "atPhysicsCriticalStrike": "会心",
    "atPhysicsOvercomeBase": "破防",
    "atPhysicsCriticalDamagePowerBase": "会效",
    "atPhysicsShieldBase": "外防",

    "atSolarAndLunarAttackPowerBase": "攻击",
    "atSolarAndLunarCriticalStrike": "会心",
    "atSolarAndLunarOvercomeBase": "破防",
    "atSolarAndLunarCriticalDamagePowerBase": "会效",

    "atNeutralAttackPowerBase": "攻击",
    "atNeutralCriticalStrike": "会心",
    "atNeutralOvercomeBase": "破防",
    "atNeutralCriticalDamagePowerBase": "会效",

    "atSolarAttackPowerBase": "攻击",
    "atSolarCriticalStrike": "会心",
    "atSolarOvercomeBase": "破防",
    "atSolarCriticalDamagePowerBase": "会效",

    "atLunarAttackPowerBase": "攻击",
    "atLunarCriticalStrike": "会心",
    "atLunarOvercomeBase": "破防",
    "atLunarCriticalDamagePowerBase": "会效",

    "atPoisonAttackPowerBase": "攻击",
    "atPoisonCriticalStrike": "会心",
    "atPoisonOvercomeBase": "破防",
    "atPoisonCriticalDamagePowerBase": "会效",

    "atMagicAttackPowerBase": "攻击",
    "atMagicOvercome": "破防",
    "atMagicCriticalStrike": "会心",
    "atMagicCriticalDamagePowerBase": "会效",
    "atMagicShield": "内防",

    "atStrainBase": "无双",
    "atSurplusValueBase": "破招",
    "atHasteBase": "加速",

    "atAllTypeOvercomeBase": "破防",
    "atAllTypeCriticalStrike": "会心",
    "atAllTypeCriticalDamagePowerBase": "会效",

    "atTherapyPowerBase": "治疗",
    "atActiveThreatCoefficient": "仇恨",

    "atToughnessBase": "御劲",
    "atDecriticalDamagePowerBase": "化劲",
    
    "atMaxLifeBase": "气血"
}

Spunk_to_Attack_Cof = 185 / 1024 # 元气转基础攻击
Strength_to_Attack_Cof = 167 / 1024 # 力道转基础攻击
Spunk_to_BaseOvercome_Cof = 307 / 1024 # 元气转基础破防
Strength_to_BaseOvercome_Cof = 307 / 1024 # 力道转基础破防

Agility_to_Critical_Cof = 922 / 1024 # 身法转会心
Spirit_to_Critical_Cof = 922 / 1024 # 根骨转会心

CRITICAL_DIVISOR = 197703.0
CRITICAL_DAMAGE_DIVISOR = 72844.2
OVERCOME_DIVISOR = 225957.6
STRAIN_DIVISOR = 133333.2
HASTE_DIVISOR = 210078.0
SHIELD_134 = 83679
SHIELD_134_CONST = 155408.88
SHIELD_130_CONST = 126007.2
DECRITICAL_DAMAGE_DIVISOR = 33046.2