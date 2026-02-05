import time
from typing import Protocol


class Clock(Protocol):
    def time(self) -> float: ...


class SystemClock(Clock):
    def time(self) -> float:
        return time.time()
