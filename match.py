import random
from dataclasses import dataclass

from simulation import Simulation, SimulationResult
from team import Team, TeamState
from utils import get_win_data_from_goals, OptionalWinData


def build_match_display(
        home_state: TeamState, home_goals: int,
        away_state: TeamState, away_goals: int,
        show_elo: bool
) -> str:
    if show_elo:
        home_name = home_state.display(show_elo=show_elo)
        away_name = away_state.display(show_elo=show_elo, elo_on_left=False)

    else:
        home_name = home_state.team.name
        away_name = away_state.team.name

    return f"{home_name} {home_goals} - {away_goals} {away_name}"


@dataclass
class MatchResult(SimulationResult):
    win_data: OptionalWinData
    home_state: TeamState
    away_state: TeamState
    home_goals: int
    away_goals: int

    def display(self, show_elo: bool = False) -> str:
        return build_match_display(
            self.home_state,
            self.home_goals,
            self.away_state,
            self.away_goals,
            show_elo=show_elo
        )


@dataclass
class MatchConfig:
    goals_per_game: float = 2.75
    elo_con_var_idx: float = 20
    elo_weight: float = 400
    home_advantage: float = 60
    match_minutes: float = 90
    dynamic_elo: bool = True


@dataclass
class Match(Simulation):
    home_team: Team
    away_team: Team
    match_config: MatchConfig = MatchConfig()

    def simulate(self) -> MatchResult:
        og_home_elo, og_away_elo = self.home_team.elo, self.away_team.elo

        elo_diff = og_away_elo - og_home_elo - self.match_config.home_advantage
        weighted_elo_diff = elo_diff / self.match_config.elo_weight
        home_win_chance = 1 / (10 ** weighted_elo_diff + 1)

        goals_per_game = self.match_config.goals_per_game
        goals_per_sec = goals_per_game / self.match_config.match_minutes / 60

        home_goals = away_goals = 0

        for second in range(int(self.match_config.match_minutes * 60)):

            if goals_per_sec > random.random():

                if home_win_chance > random.random():
                    home_goals += 1

                else:
                    away_goals += 1

        win_data = get_win_data_from_goals(
            self.home_team, self.away_team, home_goals, away_goals
        )

        if win_data.winner:
            result = 1 if win_data.winner == self.home_team else 0

        else:
            result = 0

        home_elo_gain = 0

        if self.match_config.dynamic_elo:
            elo_con_var_idx = self.match_config.elo_con_var_idx
            home_elo_gain = elo_con_var_idx * (result - home_win_chance)
            self.home_team.elo += home_elo_gain
            self.away_team.elo -= home_elo_gain

        home_state = TeamState(self.home_team, og_home_elo, home_elo_gain)
        away_state = TeamState(self.away_team, og_away_elo, -home_elo_gain)

        return MatchResult(
            win_data, home_state, away_state, home_goals, away_goals
        )
