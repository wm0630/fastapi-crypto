from enum import Enum


class MarginMode(str, Enum):
    CROSS = "cross"
    ISOLATED = "isolated"
    NONE = ""