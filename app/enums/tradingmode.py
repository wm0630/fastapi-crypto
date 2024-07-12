from enum import Enum

class TradingMode(str, Enum):
    SPOT = "spot"
    MARGIN = "margin"
    FUTURES = "futures"