from dataclasses import dataclass
from typing import Optional

from team import Team


@dataclass
class OptionalWinData:
    winner: Optional[Team]
    loser: Optional[Team]


def get_win_data_from_goals(
        team1: Team, team2: Team, team1_goals: int, team2_goals: int
) -> OptionalWinData:
    if team1_goals > team2_goals:
        return OptionalWinData(team1, team2)

    elif team1_goals < team2_goals:
        return OptionalWinData(team2, team1)

    return OptionalWinData(None, None)
