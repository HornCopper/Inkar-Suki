from math import ceil


StrengthIncome = [
    0, 0.005, 0.013, 0.024, 0.038, 0.055, 0.075, 0.098, 0.124
]

EquipLocations = [
    "武器", "重剑", "暗器", "上衣", "帽子", "项链", "戒指", "戒指", "腰带", "腰坠", "下装", "鞋子", "护腕"
    #  0     1      2       3      4       5       6      7       8      9       10      11     12
]

# MaxStrengthLevel = 32000
# MaxStrengthLevel = 37400

# MinStrengthLevel = 27800

# MaxStrengthLevel = 43900
# 能不能别抄自己写

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

    "atAllTypeAttackPowerBase": "攻击",
    "atAllTypeOvercomeBase": "破防",
    "atAllTypeCriticalStrike": "会心",
    "atAllTypeCriticalDamagePowerBase": "会效",

    "atTherapyPowerBase": "治疗",
    "atActiveThreatCoefficient": "仇恨",

    "atToughnessBase": "御劲",
    "atDecriticalDamagePowerBase": "化劲",
    
    "atMaxLifeBase": "气血"
}

Spunk_to_Attack_Cof = 195 / 1000 # 元气转基础攻击
Strength_to_Attack_Cof = 195 / 1000 # 力道转基础攻击
Spunk_to_BaseOvercome_Cof = 61 / 1000 # 元气转基础破防
Strength_to_BaseOvercome_Cof = 61 / 1000 # 力道转基础破防

Agility_to_Critical_Cof = 256 / 1024 # 身法转会心
Spirit_to_Critical_Cof = 256 / 1024 # 根骨转会心
PVX_STRAIN = 1220 / 1000 # 全能转无双

CURRENT_LEVEL = 50
LEVEL_CONST = 33 * CURRENT_LEVEL - 660
CRITICAL_DIVISOR = 9.609 * LEVEL_CONST
CRITICAL_DAMAGE_DIVISOR = 3.54 * LEVEL_CONST
OVERCOME_DIVISOR = 10.483 * LEVEL_CONST
STRAIN_DIVISOR = 7.117 * LEVEL_CONST
HASTE_DIVISOR = 10.21 * LEVEL_CONST
HASTE_205_PER_1024_BREAKPOINT = ceil(205 / 1024 * HASTE_DIVISOR)
SHIELD_134 = 6592
SHIELD_134_CONST = 12243.264
SHIELD_130_CONST = 10802.88
DECRITICAL_DAMAGE_DIVISOR = 5148
