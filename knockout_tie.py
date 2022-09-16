import random
from collections import defaultdict
from dataclasses import dataclass, field

from tabulate import tabulate

from match import Match, MatchConfig, build_match_display
from simulation import Simulation, SimulationResult
from team import Team, TeamState
from utils import get_win_data_from_goals


@dataclass
class TieGoal:
    goals: int
    away: bool


@dataclass
class TeamTieData:
    total_goals: int = 0
    goal_list: list[TieGoal] = field(default_factory=list)


@dataclass
class KnockoutTieResult(SimulationResult):
    winning_state: TeamState
    losing_state: TeamState
    winning_data: TeamTieData
    losing_data: TeamTieData

    def display(self, show_elo: bool = False) -> str:

        if len(self.winning_data.goal_list) == 1:
            return build_match_display(
                self.winning_state,
                self.winning_data.total_goals,
                self.losing_state,
                self.losing_data.total_goals,
                show_elo=show_elo
            )

        win_display = self.winning_state.display(show_elo=show_elo)
        lose_display = self.losing_state.display(show_elo=show_elo)

        win_strings: list[str] = [f"(W) {win_display}"]
        lose_strings: list[str] = [f"(L) {lose_display}"]

        for i, (win_goals, lose_goals) in enumerate(
                zip(self.winning_data.goal_list, self.losing_data.goal_list)
        ):
            win_str, lose_str = str(win_goals.goals), str(lose_goals.goals)

            if win_goals.away:
                win_str += "⭑"

            else:
                lose_str += "⭑"

            win_strings.append(win_str)
            lose_strings.append(lose_str)

        win_strings.append(f"[{self.winning_data.total_goals}]")
        lose_strings.append(f"[{self.losing_data.total_goals}]")

        return tabulate([win_strings, lose_strings], tablefmt="fancy_grid")


@dataclass
class KnockoutTieConfig:
    legs: int = 2
    away_rule: bool = True


@dataclass
class KnockoutTie(Simulation):
    team1: Team
    team2: Team
    match_config: MatchConfig = MatchConfig()
    tie_config: KnockoutTieConfig = KnockoutTieConfig()

    def simulate(self) -> KnockoutTieResult:
        og_elo_dict: dict[Team, float] = {
            self.team1: self.team1.elo,
            self.team2: self.team2.elo
        }

        team_data: dict[Team, TeamTieData] = defaultdict(lambda: TeamTieData())
        away_goal_dict: dict[Team, int] = defaultdict(lambda: 0)

        for leg in range(self.tie_config.legs):

            if leg % 2 == 0:
                home_team, away_team = self.team1, self.team2

            else:
                home_team, away_team = self.team2, self.team1

            result = Match(home_team, away_team, self.match_config).simulate()

            team_data[home_team].total_goals += result.home_goals
            tie_goal = TieGoal(result.home_goals, False)
            team_data[home_team].goal_list.append(tie_goal)
            away_goal_dict[away_team] += 1

            team_data[away_team].total_goals += result.away_goals
            tie_goal = TieGoal(result.away_goals, True)
            team_data[away_team].goal_list.append(tie_goal)
            away_goal_dict[home_team] += 1

        win_data = get_win_data_from_goals(
            self.team1, self.team2,
            team_data[self.team1].total_goals, team_data[self.team2].total_goals
        )

        if win_data.winner:
            winner, loser = win_data.winner, win_data.loser

        else:
            winner = random.choice([self.team1, self.team2])
            loser = self.team1 if winner == self.team2 else self.team2

            if self.tie_config.away_rule:
                away_win_data = get_win_data_from_goals(
                    self.team1, self.team2,
                    away_goal_dict[self.team1], away_goal_dict[self.team2]
                )

                if away_win_data.winner:
                    winner, loser = away_win_data.winner, away_win_data.loser

        og_win_elo = og_elo_dict[winner]
        og_lose_elo = og_elo_dict[loser]

        win_state = TeamState(winner, og_win_elo, winner.elo - og_win_elo)
        lose_state = TeamState(loser, og_lose_elo, loser.elo - og_lose_elo)

        return KnockoutTieResult(
            win_state, lose_state, team_data[winner], team_data[loser]
        )
