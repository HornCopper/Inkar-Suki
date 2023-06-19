from .Golds import *
from sgtpyutils.extensions.clazz import dict2obj


class GoodsPriceSummary:
    def __init__(self, data: dict = None) -> None:
        if data is None:
            data = {}
        self.id = data.get('id')
        self.price = data.get('price')
        self.SampleSize = data.get('SampleSize')
        self.UpdatedAt = data.get('UpdatedAt')
        self.Server = data.get('Server')
        self.LowestPrice = data.get('LowestPrice')
        self.HighestPrice = data.get('HighestPrice')
        self.AvgPrice = data.get('AvgPrice')
        self.ItemId = data.get('ItemId')
    

class GoodsPriceDetail:
    Price_Valid_TotalPrice = Gold.price_by_gold(100)  # 总价在100金以上则有效
    InvalidPrice = -1

    def __init__(self, data: dict = None) -> None:
        if data is None:
            data = {}
        prices = [x for x in data.get('prices', [])]
        self.prices = [
            [x['created'], x['n_count'], x['unit_price']
             ]  # 创建时间 数量 单价
            for x in prices]
        self.valid_price = self.get_valid_price()

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
        prices.sort(key=lambda x: x[2]) # 按价格升序排列

        total_price = 0
        self.price_lowest = prices[0][2]
        for x in prices:
            total_price += x[1] * x[2]
            if total_price >= GoodsPriceDetail.Price_Valid_TotalPrice:
                self.price_valid = x[2]
                return self.price_valid
        self.price_valid = GoodsPriceDetail.InvalidPrice
        return self.price_valid 
