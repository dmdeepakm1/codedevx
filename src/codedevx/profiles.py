from enum import IntEnum

class Version(IntEnum):
    V1 = 1
    V2 = 2
    V3 = 3

def enabled(current: int, required: Version) -> bool:
    return int(current) >= int(required)
