from .Equip import *
from typing import overload


class UserPanel:
    @overload
    def __init__(self, data: dict) -> None:
        ...

    @overload
    def __init__(self, name: str, percent: bool, value: float) -> None:
        ...

    def __init__(self, name: str, percent: bool, value: float) -> None:
        if isinstance(name, dict):
            percent = name.get('percent') or False
            value = name.get('value') or 0
            name = name.get('name')
        self.name: str = name  # 属性名称
        self.percent: bool = percent  # 是否是百分比
        self.value: float = value  # 数值


class Kungfu:
    mapper = {
        'mowen': '莫问'
    }

    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def alias(self):
        return Kungfu.mapper.get(self.name) or f'u:{self.name}'


class Qixue:
    def __init__(self, data: dict) -> None:
        self.name = data.get('name')
        # {FileName:https://...,Kind:技能,SubKind:长歌}
        self.icon = data.get('icon')
        self.skill_id = data.get('skill_id')


class MatchDetail:
    # "Level": 0,
    # "atAgilityBase": 0,
    # "atAgilityBasePercentAdd": 0,
    # "atAllTypeCriticalDamagePowerBase": 0,
    # "atAllTypeCriticalStrike": 0,
    # "atAllTypeHitValue": 0,
    # "atBasePotentialAdd": 0,
    # "atCriticalDamagePowerBaseLevel": 175.45,
    # "atCriticalStrikeLevel": 31.43,
    # "atDecriticalDamagePowerBase": 0,
    # "atDecriticalDamagePowerBaseLevel": 10,
    # "atDodge": 0,
    # "atHasteBase": 0,
    # "atHasteBaseLevel": 2473,
    # "atLifeAdditional": 0,
    # "atLunarAttackPowerBase": 0,
    # "atLunarCriticalDamagePowerBase": 0,
    # "atLunarCriticalStrike": 0,
    # "atLunarHitValue": 0,
    # "atLunarOvercomeBase": 0,
    # "atMagicAttackPowerBase": 0,
    # "atMagicCriticalDamagePowerBase": 0,
    # "atMagicCriticalStrike": 0,
    # "atMagicHitValue": 0,
    # "atMagicOvercome": 0,
    # "atMagicShield": 0,
    # "atMagicShieldLevel": 8.74,
    # "atMaxLifeAdditional": 0,
    # "atNeutralAttackPowerBase": 0,
    # "atNeutralCriticalDamagePowerBase": 0,
    # "atNeutralCriticalStrike": 0,
    # "atNeutralHitValue": 0,
    # "atNeutralOvercomeBase": 0,
    # "atOvercomeBaseLevel": 20.95,
    # "atParryBase": 0,
    # "atParryValueBase": 0,
    # "atPhysicsAttackPowerBase": 0,
    # "atPhysicsCriticalDamagePowerBase": 0,
    # "atPhysicsCriticalStrike": 0,
    # "atPhysicsHitValue": 0,
    # "atPhysicsOvercomeBase": 0,
    # "atPhysicsShieldAdditional": 0,
    # "atPhysicsShieldBase": 0,
    # "atPhysicsShieldBaseLevel": 5.82,
    # "atPoisonAttackPowerBase": 0,
    # "atPoisonCriticalDamagePowerBase": 0,
    # "atPoisonCriticalStrike": 0,
    # "atPoisonHitValue": 0,
    # "atPoisonOvercomeBase": 0,
    # "atSolarAndLunarAttackPowerBase": 0,
    # "atSolarAndLunarCriticalDamagePowerBase": 0,
    # "atSolarAndLunarCriticalStrike": 0,
    # "atSolarAndLunarHitValue": 0,
    # "atSolarAndLunarOvercomeBase": 0,
    # "atSolarAttackPowerBase": 0,
    # "atSolarCriticalDamagePowerBase": 0,
    # "atSolarCriticalStrike": 0,
    # "atSolarHitValue": 0,
    # "atSolarOvercomeBase": 0,
    # "atSpiritBase": 6700,
    # "atSpiritBasePercentAdd": 0,
    # "atSpunkBase": 0,
    # "atSpunkBasePercentAdd": 0,
    # "atStrainBase": 0,
    # "atStrainBaseLevel": 31.04,
    # "atStrengthBase": 0,
    # "atStrengthBasePercentAdd": 0,
    # "atSurplusValueBase": 15132,
    # "atTherapyPowerBase": 0,
    # "atToughnessBase": 0,
    # "atToughnessBaseLevel": 0,
    # "atVitalityBase": 0,
    # "atVitalityBasePercentAdd": 0,
    # "baseAttack": 22383,
    # "name": "mowen",
    # "score": 200739,
    # "totalAttack": 34781,
    # "totalLift": 527310,
    # "type": "spirit"
    def __init__(self, data: dict) -> None:
        for x in data:
            setattr(self, x, data.get(x))


class UserProperty:
    def __init__(self, data: dict = None) -> None:
        self.equips = [Equip(x) for x in data.get('Equips')]
        self.kungfu = Kungfu(data.get('Kungfu').get('Name'))
        self.matchDetail = MatchDetail(data.get('MatchDetail'))
        self.qixue = [Qixue(x) for x in data.get('Person').get('qixueList')]
        self.panel = [UserPanel(x) for x in data.get('PeronalPanel')]
        self.score = data.get('TotalEquipsScore')
