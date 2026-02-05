from src.infra.time.clock import Clock


class ClockMock(Clock):
    def __init__(self, fixed_time: float) -> None:
        self._fixed_time = fixed_time
        self.called_times = 0

    def time(self) -> float:
        self.called_times += 1
        return self._fixed_time
