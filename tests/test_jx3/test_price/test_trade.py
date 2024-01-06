from ... import *

import src.plugins.jx3
from src.plugins.jx3.price_goods.lib import coin, Golds


def test_trade_gold():
    Gold = Golds.Gold
    assert Gold(1).__repr__() == '1 铜'
    assert Gold(200).__repr__() == '2 银'
    assert Gold(80000).__repr__() == '8 金'
    assert Gold(88800).__repr__() == '8 金 88 银'
    assert Gold(100888800).__repr__() == '1 砖 88 金 88 银'
    assert Gold(100008800).__repr__() == '1 砖 88 银'
    assert Gold(100000000).__repr__() == '1 砖'
    assert len(str(Gold(100888800))) > 1e3, 'image of b64 should be very long'

    t = f'98 <img src="{coin.brickl}" /> 12 <img src="{coin.goldl}" /> 34 <img src="{coin.silverl}" /> 56 <img src="{coin.copperl}" />'
    assert str(Gold(9800123456)) == t, 'convert image maybe wrong'

