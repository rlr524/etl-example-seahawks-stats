from dataclasses import dataclass


@dataclass
class Stats:
    player: str = ""
    carries: int = 0
    yards: int = 0
    touchdowns: int = 0
    long: int = 0
    ypc: float = 0.0

    def get_ypc(self) -> float:
        return round(self.yards / self.carries, 2)
