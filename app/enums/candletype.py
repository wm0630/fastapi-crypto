from enum import Enum

class CandleType(str, Enum):

    SPOT = "spot"
    FUTURES = "futures"
    MARK = "mark"
    INDEX = "index"
    PREMIUMINDEX = "premiumIndex"

    FUNDING_RATE = "funding_rate"
    
    def __str__(self):
        return f"{self.name.lower()}"

    @staticmethod
    def from_string(value: str) -> "CandleType":
        if not value:
            # Default to spot
            return CandleType.SPOT
        return CandleType(value)
    
    @staticmethod
    def get_default(trading_mode: str) -> "CandleType":
        if trading_mode == "futures":
            return CandleType.FUTURES
        return CandleType.SPOT