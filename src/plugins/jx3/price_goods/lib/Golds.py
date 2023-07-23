import math

from .coin import copperl, silverl, goldl, brickl

class Gold:
    base_OOM = [2, 2, 4]  # base order of magnitude
    base_des = ["铜", "银", "金", "砖"]
    base_img_des = [f"<img src=\"{x}\" />" for x in [copperl, silverl, goldl, brickl]]

    def __init__(self, value: int) -> None:
        self.value = value

    @staticmethod
    def price_by_brick(count: float) -> int:
        """
        将砖转换为价格
        """
        v = count * math.pow(10, Gold.base_OOM[2])
        return Gold.price_by_gold(v)

    @staticmethod
    def price_by_gold(count: float) -> int:
        """
        将金转换为价格
        """
        v = count * math.pow(10, Gold.base_OOM[1])
        return Gold.price_by_silver(v)

    @staticmethod
    def price_by_silver(count: float) -> int:
        """
        将银转换为价格
        """
        v = count * math.pow(10, Gold.base_OOM[0])
        return int(v)

    def _convert_str(self, des_arr: list) -> str:
        value = self._convert(self.value)
        v = [f"{x} {des_arr[index]}" if x >
             0 else None for index, x in enumerate(value)]
        v = [x for x in v if x]
        v.reverse()  # 转为降序列
        return " ".join(v)

    @property
    def value_str(self) -> str:
        return self._convert_str(Gold.base_des)

    @property
    def value_img(self) -> str:
        return self._convert_str(Gold.base_img_des)

    def __str__(self) -> str:
        return self.value_img

    def __repr__(self) -> str:
        return self.value_str

    def _convert(self, price: int):
        max_base = len(Gold.base_OOM)
        cur_base = 0
        result = []
        while cur_base < max_base and price > 0:
            base = int(math.pow(10, Gold.base_OOM[cur_base]))
            result.append(price % base)
            price = int(price / base)
            cur_base += 1
        result.append(price)
        # 检查是否已满位
        max_posi = max_base + 1
        if len(result) < max_posi:
            result += [0] * (max_posi - len(result))
        return result
