from .Golds import *
from sgtpyutils.extensions.clazz import dict2obj
import time


class GoodsPriceRecord:
    def __init__(self) -> None:
        self.updated: int = 0

    def updated_time(self):
        self.updated = time.time()


class GoodsPriceSummary(GoodsPriceRecord):
    def __init__(self, data: dict = None) -> None:
        if data is None:
            data = {}
        self.Date = data.get('Date')
        self.CreatedAt = data.get('CreatedAt')
        self.UpdatedAt = data.get('UpdatedAt')
        self.SampleSize = data.get('SampleSize')
        self.LowestPrice = data.get('LowestPrice')
        self.HighestPrice = data.get('HighestPrice')
        self.AvgPrice = data.get('AvgPrice')
        super().__init__()


class GoodsPriceDetail(GoodsPriceRecord):
    Price_Valid_TotalPrice = Gold.price_by_gold(100)  # 总价在100金以上则有效
    InvalidPrice = -1

    def __init__(self, prices: list = None) -> None:
        if prices is None:
            prices = []
        self.latest = 0  # 最新数据时时间戳
        key = ['created', 'n_count', 'unit_price']
        self.prices = [[x.get(k) for k in key] for x in prices]  # 创建时间 数量 单价
        self.valid_price = self.get_valid_price()
        super().__init__()

    def get_valid_price(self, prices: list = None):
        '''
        获取当前价格的有效价（总价在{Price_Valid_TotalPrice}以上则判定为有效）
        '''
        if not prices:
            prices = self.prices
        if not prices:
            self.price_lowest = GoodsPriceDetail.InvalidPrice
            self.price_valid = GoodsPriceDetail.InvalidPrice
            return self.price_valid
        prices.sort(key=lambda x: x[2])  # 按价格升序排列
        self.latest = int(max(prices, key=lambda x: x[0])[0]) * 1e3

        total_price = 0
        self.price_lowest = prices[0][2]
        for x in prices:
            total_price += x[1] * x[2]
            if total_price >= GoodsPriceDetail.Price_Valid_TotalPrice:
                self.price_valid = x[2]
                return self.price_valid
        self.price_valid = GoodsPriceDetail.InvalidPrice
        return self.price_valid

    def to_dict(self):
        return self.__dict__
