import math
import random
from dataclasses import dataclass, field

from knockout_tie import KnockoutTie, KnockoutTieResult, KnockoutTieConfig
from match import MatchConfig
from simulation import Simulation, SimulationResult
from team import Team


@dataclass
class RoundData:
    tie_results: list[KnockoutTieResult] = field(default_factory=list)
    teams_with_bye: list[Team] = field(default_factory=list)


@dataclass
class BracketResult(SimulationResult):
    winner: Team
    all_round_data: list[RoundData] = field(default_factory=list)

    def display(self, show_elo: bool = False) -> str:
        display: list[str] = []

        for i, round_data in enumerate(self.all_round_data):
            inactive_team_count = len(round_data.teams_with_bye)
            total_ties = len(round_data.tie_results) + inactive_team_count

            if total_ties == 1:
                display.append("FINAL")

            elif total_ties == 2:
                display.append("SEMI-FINALS")

            elif total_ties == 4:
                display.append("QUARTER-FINALS")

            else:
                display.append(f"ROUND OF {2 * total_ties}")

            if round_data.teams_with_bye:
                names: list[str] = [t.name for t in round_data.teams_with_bye]
                display.append(f"{len(names)} Byes: {', '.join(names)}")

            for tie_result in round_data.tie_results:
                display.append(tie_result.display(show_elo=show_elo))

            display.append("")

        return "\n".join(display)


@dataclass
class BracketConfig:
    legs: int = 2
    final_legs: int = 1
    away_rule: bool = True
    shuffle_teams: bool = True


@dataclass
class Bracket(Simulation):
    teams: list[Team] = field(default_factory=list)
    match_config: MatchConfig = MatchConfig()
    tie_config: KnockoutTieConfig = KnockoutTieConfig()
    bracket_config: BracketConfig = BracketConfig()

    def simulate(self) -> BracketResult:
        teams: list[Team] = [team for team in self.teams]
        all_round_data: list[RoundData] = []

        while len(teams) > 2:

            if self.bracket_config.shuffle_teams:
                random.shuffle(teams)

            round_tie_results: list[KnockoutTieResult] = []
            losers: list[Team] = []
            teams_with_bye: list[Team] = []
            team_count: int = len(teams)

            if not math.log(len(teams), 2).is_integer():
                bye_count = 2 ** math.ceil(math.log(len(teams), 2)) - len(teams)
                team_count = len(teams) - bye_count
                teams_with_bye = teams[team_count:]

            for i in range(1, team_count, 2):
                team1, team2 = teams[i - 1], teams[i]

                knockout_tie = KnockoutTie(
                    team1,
                    team2,
                    self.match_config,
                    self.tie_config
                )

                tie_result = knockout_tie.simulate()
                round_tie_results.append(tie_result)
                losers.append(tie_result.losing_state.team)

            for loser in losers:
                teams.remove(loser)

            all_round_data.append(RoundData(round_tie_results, teams_with_bye))

        final = KnockoutTie(
            teams[0], teams[1], self.match_config, self.tie_config
        )
        all_round_data.append(RoundData([final.simulate()], []))

        return BracketResult(teams[0], all_round_data)
