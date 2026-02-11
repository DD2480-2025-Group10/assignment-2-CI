"""
Provides a simple clock interface for getting the current time
and a concrete implementation that uses the system clock.
"""
import time
from typing import Protocol


class Clock(Protocol):
    def time(self) -> float: ...


class SystemClock(Clock):
    def time(self) -> float:
        return time.time()
