import random
from collections import defaultdict
from dataclasses import dataclass, field

from tabulate import tabulate

from match import Match, MatchResult, MatchConfig
from simulation import Simulation, SimulationResult
from team import Team, TeamState, create_dummy


@dataclass
class TeamLeagueData:
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_diff: int = 0
    points: float = 0


@dataclass
class TeamLeagueEntry:
    state: TeamState
    data: TeamLeagueData


@dataclass
class LeagueResult(SimulationResult):
    winner: Team
    match_results_per_day: list[list[MatchResult]] = field(default_factory=list)
    entries: list[TeamLeagueEntry] = field(default_factory=list)

    def display(
            self, show_elo: bool = False, show_matches: bool = False
    ) -> str:
        output: list[str] = []

        if show_matches:

            for i, day_match_results in enumerate(self.match_results_per_day):
                output.append(f"DAY {i + 1}\n")

                for match_result in day_match_results:
                    output.append(match_result.display(show_elo=show_elo))

                output.append("")

        table: list[list[str]] = []

        for i, entry in enumerate(self.entries):
            entry_list = [f"{i + 1}. {entry.state.display(show_elo=show_elo)}"]

            for value in entry.data.__dict__.values():
                entry_list.append(value)

            table.append(entry_list)

        headers = ["Team", "MP", "W", "D", "L", "GF", "GA", "GD", "P"]
        output.append(tabulate(table, headers=headers, tablefmt="fancy_grid"))

        return "\n".join(output)


@dataclass
class LeagueConfig:
    replays: int = 1
    win_points: float = 3
    draw_points: float = 1
    loss_points: float = 0


@dataclass
class League(Simulation):
    teams: list[Team] = field(default_factory=list)
    match_config: MatchConfig = MatchConfig()
    league_config: LeagueConfig = LeagueConfig()

    def simulate(self) -> LeagueResult:
        og_elo_dict: dict[Team, float] = {team: team.elo for team in self.teams}

        home_pool = self.teams[:len(self.teams) // 2]
        away_pool = self.teams[len(self.teams) // 2:][::-1]

        team_count = len(self.teams)

        if len(self.teams) % 2 == 1:
            home_pool.append(create_dummy())
            team_count += 1

        match_results_per_day: list[list[MatchResult]] = []

        team_data: dict[Team, TeamLeagueData] = defaultdict(
            lambda: TeamLeagueData()
        )

        days = team_count * (self.league_config.replays + 1) - \
            self.league_config.replays - 1

        for i in range(days):
            match_results: list[MatchResult] = []

            for home_team, away_team in zip(home_pool, away_pool):

                if i % 2 == 0:
                    home_team, away_team = away_team, home_team

                if not home_team.dummy and not away_team.dummy:
                    match = Match(home_team, away_team, self.match_config)
                    result = match.simulate()
                    match_results.append(result)

                    team_data[home_team].played += 1
                    team_data[away_team].played += 1

                    team_data[home_team].goals_for += result.home_goals
                    team_data[away_team].goals_for += result.away_goals

                    net_home_goals = result.home_goals - result.away_goals
                    team_data[home_team].goal_diff += net_home_goals
                    team_data[away_team].goal_diff -= net_home_goals

                    team_data[home_team].goals_against += result.away_goals
                    team_data[away_team].goals_against += result.home_goals

                    if result.win_data.winner == home_team:
                        team_data[result.win_data.loser].losses += 1
                        team_data[result.win_data.winner].wins += 1

                        team_data[result.win_data.winner].points += (
                            self.league_config.win_points
                        )
                        team_data[result.win_data.loser].points += (
                            self.league_config.loss_points
                        )

                    else:
                        team_data[home_team].draws += 1
                        team_data[away_team].draws += 1

                        team_data[home_team].points += (
                            self.league_config.draw_points
                        )
                        team_data[away_team].points += (
                            self.league_config.draw_points
                        )

            match_results_per_day.append(match_results)

            away_pool.append(home_pool.pop())
            home_pool.insert(1, away_pool[0])
            away_pool.remove(away_pool[0])

        unsorted_entries: list[TeamLeagueEntry] = []

        for team, data in team_data.items():
            og_elo = og_elo_dict[team]
            state = TeamState(team, og_elo, team.elo - og_elo)
            unsorted_entries.append(TeamLeagueEntry(state, data))

        all_entries: list[TeamLeagueEntry] = sorted(
            unsorted_entries,
            key=lambda entry: (
                -entry.data.points,
                -entry.data.goal_diff,
                -entry.data.goals_for
            )
        )

        if all_entries[0].data.points == all_entries[1].data.points:
            highest_goals_for = all_entries[0].data.goals_for
            tied_entries: list[TeamLeagueEntry] = [all_entries[0]]

            for team_entry in all_entries[1:]:

                if team_entry.data.goals_for == highest_goals_for:
                    tied_entries.append(team_entry)

                else:
                    break

            random.shuffle(tied_entries)
            all_entries[:len(tied_entries)] = tied_entries

        return LeagueResult(
            all_entries[0].state.team, match_results_per_day, all_entries
        )
