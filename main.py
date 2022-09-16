import os

from group_tournament import GroupTournament, GroupConfig
from reader import read_teams_from_csv
from scraper import scrape_teams_from_web
from team import Team
from writer import write_teams_to_csv

TEAM_PATH = "teams.csv"
CONFIG_PATH = "config.json"


def prepare_teams(team_path: str) -> list[Team]:
    if os.path.exists(team_path):
        return read_teams_from_csv(team_path)
    teams = scrape_teams_from_web()
    write_teams_to_csv(team_path, teams)
    return teams


def main() -> None:
    teams = prepare_teams(TEAM_PATH)
    teams.sort(key=lambda team: team.elo, reverse=True)
    simulation = GroupTournament(teams, group_config=GroupConfig(group_size=16, advancing_per_group=4))
    print(simulation.simulate().display(show_elo=True, show_group_matches=True))


if __name__ == "__main__":
    main()
