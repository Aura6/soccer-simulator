from dataclasses import dataclass


@dataclass
class Team:
    name: str
    region: str
    elo: float
    regional_league_rank: int
    dummy: bool = False

    def __hash__(self) -> int:
        return hash(self.name)


def create_dummy(dummy_id: int = 0) -> Team:
    return Team(f"Dummy {dummy_id}", "", 0, 0, True)


@dataclass
class TeamState:
    team: Team
    elo_before: float
    elo_change: float

    def display(self, show_elo: bool = False, elo_on_left: bool = True) -> str:
        if not self.elo_change or not show_elo:
            return self.team.name

        sign = "+" if self.elo_change > 0 else ""
        elo_part = f"({round(self.elo_before)}, {sign}{round(self.elo_change)})"

        if elo_on_left:
            return f"{elo_part} {self.team.name}"

        return f"{self.team.name} {elo_part}"
