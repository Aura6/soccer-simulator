import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from team import Team


def scrape_teams_from_web() -> list[Team]:
    teams: list[Team] = []

    home_link = "http://clubelo.com"
    home_page = requests.get(home_link)
    home_soup = BeautifulSoup(home_page.content, "html.parser")

    print("Collected teams from...")

    tag: Tag

    for tag in home_soup.find_all(class_="l"):

        if tag.has_attr("colspan"):
            link_tag = tag.find("a")
            href = link_tag.get("href")
            region = link_tag.text[1:]

            regional_link = home_link + link_tag.get("href")
            regional_page = requests.get(regional_link)
            regional_soup = BeautifulSoup(regional_page.content, "html.parser")

            searching_for_team = False
            league_rank = 0

            for row_tag in regional_soup.find(class_="liste").find_all("tr"):

                if searching_for_team:

                    if row_tag.find("b"):
                        print(region)
                        break

                    if row_tag.find("i"):
                        league_rank += 1

                    else:
                        name = row_tag.find("a").get("href")[1:]
                        elo = int(row_tag.find(class_="r").text)
                        league_rank = max(league_rank, 1)
                        teams.append(Team(name, region, elo, league_rank))

                elif row_tag.find("a", attrs={"href": href}):
                    searching_for_team = True

    return teams
