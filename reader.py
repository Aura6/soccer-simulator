from csv import DictReader

from team import Team


def read_teams_from_csv(csv_path: str) -> list[Team]:
    teams: list[Team] = []

    with open(csv_path) as csv_file:
        for team_dict in DictReader(csv_file):
            teams.append(Team(
                team_dict["Name"],
                team_dict["Region"],
                float(team_dict["Elo"]),
                int(team_dict["Regional League Rank"])
            ))

    return teams
