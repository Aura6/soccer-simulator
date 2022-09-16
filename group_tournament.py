import random
from dataclasses import dataclass, field

from bracket import BracketResult, Bracket, BracketConfig
from knockout_tie import KnockoutTieConfig
from league import League, LeagueResult, LeagueConfig
from match import MatchConfig
from simulation import SimulationResult, Simulation
from team import Team


@dataclass
class GroupData:
    league_result: LeagueResult
    advancing_teams: list[Team] = field(default_factory=list)


@dataclass
class GroupTournamentResult(SimulationResult):
    winner: Team
    bracket_result: BracketResult
    all_group_data: list[GroupData] = field(default_factory=list)
    teams_with_group_bye: list[Team] = field(default_factory=list)

    def display(
            self, show_elo: bool = False, show_group_matches: bool = False
    ) -> str:
        display: list[str] = []

        if self.teams_with_group_bye:
            names: list[str] = [t.name for t in self.teams_with_group_bye]
            display.append(f"{len(names)} Byes: {', '.join(names)}")
            display.append("")

        if show_group_matches:

            for i, group_data in enumerate(self.all_group_data):
                side = "-" * 7
                display.append(f"{side} GROUP {i + 1} {side}")

                display.append("")

                for results in group_data.league_result.match_results_per_day:

                    for match_result in results:
                        display.append(match_result.display(show_elo=show_elo))

                    display.append("")

            display.append("")

        for i, group_data in enumerate(self.all_group_data):
            display.append(f"GROUP {i + 1}")

            names: list[str] = [t.name for t in group_data.advancing_teams]
            display.append(f"Advanced: {', '.join(names)}")

            display.append(group_data.league_result.display(show_elo=show_elo))
            display.append("")

        display.append(self.bracket_result.display(show_elo=show_elo))

        return "\n".join(display)


@dataclass
class GroupConfig:
    group_size: int = 4
    advancing_per_group: int = 2
    shuffle_groups: bool = True


@dataclass
class GroupTournament(Simulation):
    teams: list[Team] = field(default_factory=list)
    match_config: MatchConfig = MatchConfig()
    league_config: LeagueConfig = LeagueConfig()
    tie_config: KnockoutTieConfig = KnockoutTieConfig()
    bracket_config: BracketConfig = BracketConfig()
    group_config: GroupConfig = GroupConfig()

    def simulate(self) -> GroupTournamentResult:

        if self.group_config.shuffle_groups:
            random.shuffle(self.teams)

        all_group_data: list[GroupData] = []
        advancing_teams: list[Team] = []
        stop = len(self.teams) - self.group_config.group_size + 1

        for i in range(0, stop, self.group_config.group_size):
            group: list[Team] = self.teams[i:i + self.group_config.group_size]
            league = League(group, self.match_config, self.league_config)
            result = league.simulate()

            current_advancing_teams: list[Team] = []

            for entry in result.entries[:self.group_config.advancing_per_group]:
                current_advancing_teams.append(entry.state.team)
                advancing_teams.append(entry.state.team)

            all_group_data.append(GroupData(result, current_advancing_teams))

        bye_count = len(self.teams) % self.group_config.group_size
        teams_with_bye: list[Team] = self.teams[len(self.teams) - bye_count:]

        bracket = Bracket(
            advancing_teams,
            self.match_config,
            self.tie_config,
            self.bracket_config
        )

        return GroupTournamentResult(
            self.teams[0],
            bracket.simulate(),
            all_group_data,
            teams_with_bye
        )
