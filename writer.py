from csv import DictWriter

from team import Team


def write_teams_to_csv(csv_path: str, teams: list[Team]) -> None:
    with open(csv_path, "w", newline="") as csv_file:
        writer = DictWriter(csv_file, fieldnames=[
            "Name", "Region", "Elo", "Regional League Rank"
        ])
        writer.writeheader()

        for team in teams:
            writer.writerow({
                "Name": team.name,
                "Region": team.region,
                "Elo": team.elo,
                "Regional League Rank": team.regional_league_rank
            })
