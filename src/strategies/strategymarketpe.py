from base import BaseStrategy
import loader
from stocks import PEMarket


class StrategyMarketPE(BaseStrategy):

    params = (
        ('market', PEMarket.HS300)
        ('period', 500),
        ('highpercent', 0.8),
        ('lowpercent', 0.2),
        ('printlog', True)
    )

    def __init__(self):
        self.north_history = loader.load_north_single(self.params.market)
        self.order = None