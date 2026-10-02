"""全局签到奖池；概率、库存和背包与原有金币奖励独立。"""
from decimal import Decimal, InvalidOperation
import random

from src.utils.database import db
from src.utils.database.classes import CheckinPrize, CheckinPrizeAward
from src.utils.permission import check_permission
from src.utils.time import Time


POOL_PERMISSION = "economy.checkin.pool.manage"
PROBABILITY_SCALE = 1_000_000
MAX_STOCK = 9_223_372_036_854_775_807


def parse_probability(value: str) -> int:
    try:
        percent = Decimal(value.removesuffix("%"))
    except InvalidOperation:
        raise ValueError("概率需要是大于 0、不超过 100 的百分数。") from None
    if not percent.is_finite() or not 0 < percent <= 100:
        raise ValueError("概率需要是大于 0、不超过 100 的百分数。")
    _, digits, exponent = percent.as_tuple()
    if not isinstance(exponent, int):
        raise ValueError("概率需要是有限的百分数。")
    # 在乘法前检查精度，避免 Decimal 默认精度舍入过长的输入。
    while digits and digits[-1] == 0:
        digits = digits[:-1]
        exponent += 1
    if exponent < -4:
        raise ValueError("概率最多支持四位小数。")
    return int(percent * 10_000)


def format_probability(value: int) -> str:
    percent = f"{Decimal(value) / 10_000:f}"
    if "." in percent:
        percent = percent.rstrip("0").rstrip(".")
    return percent + "%"


class PrizePoolManage:
    def __init__(self, operator_id: int):
        self.operator_id = operator_id

    def _authorize(self) -> None:
        if not check_permission(self.operator_id, POOL_PERMISSION):
            raise PermissionError(POOL_PERMISSION)

    def _prize(self, prize_id: int) -> CheckinPrize:
        prize = db.where_one(CheckinPrize(), "id = ?", prize_id)
        if prize is None:
            raise ValueError("没有这个奖品，请先查看签到奖池。")
        return prize

    def _validate_total(self, prize: CheckinPrize) -> None:
        entries = db.where_all(CheckinPrize(), "enabled = 1", default=[])
        total = sum(entry.probability for entry in entries if entry.id != prize.id)
        if prize.enabled and total + prize.probability > PROBABILITY_SCALE:
            raise ValueError("上架奖品的总概率不能超过 100%（包含已耗尽的奖品）。")

    def add(self, name: str, probability: int, remaining: int) -> CheckinPrize:
        self._authorize()
        name = name.strip()
        if not name or len(name) > 80 or "\n" in name or "\r" in name:
            raise ValueError("奖品名称需要为 1～80 个字符，且不能换行。")
        if not 0 < probability <= PROBABILITY_SCALE:
            raise ValueError("概率需要大于 0 且不超过 100%。")
        if remaining != -1 and not 0 < remaining <= MAX_STOCK:
            raise ValueError("投放数量需要是正整数，或使用「不限量」。")
        with db.transaction():
            prize = CheckinPrize(name=name, probability=probability, remaining=remaining,
                                 creator_id=self.operator_id, created_at=Time().raw_time)
            self._validate_total(prize)
            db.save(prize)
            prize.id = db.fetch_all("SELECT last_insert_rowid()")[0][0]
            return prize

    def change(self, prize_id: int, action: str, value: int = 0) -> CheckinPrize:
        self._authorize()
        with db.transaction():
            prize = self._prize(prize_id)
            if action == "概率":
                if not 0 < value <= PROBABILITY_SCALE:
                    raise ValueError("概率需要大于 0 且不超过 100%。")
                prize.probability = value
            elif action == "补货":
                if prize.remaining == -1:
                    raise ValueError("不限量奖品无需补货。")
                if not 0 < value <= MAX_STOCK - prize.remaining:
                    raise ValueError("补货数量需要是有效的正整数，且不能超出库存上限。")
                prize.remaining += value
            elif action in {"上架", "下架"}:
                prize.enabled = action == "上架"
            elif action == "删除":
                db.delete(prize, "")
                return prize
            else:
                raise ValueError("不支持的奖池操作。")
            self._validate_total(prize)
            db.save(prize)
            return prize

    def deliver(self, award_id: int) -> CheckinPrizeAward:
        self._authorize()
        with db.transaction():
            award = db.where_one(CheckinPrizeAward(), "id = ?", award_id)
            if award is None:
                raise ValueError("没有这个背包记录编号。")
            if award.delivered_at:
                raise ValueError("该奖品已经兑付，请勿重复兑付。")
            award.delivered_at = Time().raw_time
            award.delivered_by = self.operator_id
            db.save(award)
            return award


def draw_checkin_prize(user_id: int) -> CheckinPrizeAward | None:
    """由签到事务调用，库存扣减和获奖记录随签到一起提交。"""
    entries = db.where_all(CheckinPrize(), "enabled = 1 AND remaining != 0 ORDER BY id", default=[])
    if not entries:
        return None
    roll = random.randrange(PROBABILITY_SCALE)
    threshold = 0
    for prize in entries:
        threshold += prize.probability
        if roll >= threshold:
            continue
        if prize.id is None:
            raise ValueError("奖池数据缺少奖品编号。")
        if prize.remaining > 0:
            prize.remaining -= 1
            db.save(prize)
        award = CheckinPrizeAward(user_id=user_id, prize_id=prize.id,
                                  prize_name=prize.name, provider_id=prize.creator_id,
                                  awarded_at=Time().raw_time)
        db.save(award)
        award.id = db.fetch_all("SELECT last_insert_rowid()")[0][0]
        return award
    return None
