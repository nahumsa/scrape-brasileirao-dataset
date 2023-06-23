from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class Team(BaseModel):
    team_id: int
    name: str


def convert_basemodel_to_df(model_list: list[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([model.dict() for model in model_list])


def get_team_page_url_set(url: str) -> set[str]:
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    links = soup.find_all(
        "a", href=lambda href: href and href.startswith("/futebol/time/_/id/")
    )

    # Extract the href attribute from each link and print them
    all_link_teams = set()
    for link in links:
        all_link_teams.add(link.get("href"))
    return all_link_teams


def extract_data_from_url(url: str) -> Team:
    splited_string = url.split("/")
    team_id, team_name = splited_string[-2:]
    return Team(team_id=int(team_id), name=team_name)


if __name__ == "__main__":
    BASE_URL = "https://www.espn.com.br"
    LEAGUE_NAME = "bra.1"
    LEAGUE_URL_PATH = "/soccer/teams/_/league/"
    league_url = BASE_URL + LEAGUE_URL_PATH + LEAGUE_NAME
    all_link_teams = get_team_page_url_set(league_url)
    team_data_list: list[Team] = []
    for team_link in all_link_teams:
        team_data_list.append(extract_data_from_url(team_link))

    teams_df: pd.DataFrame = convert_basemodel_to_df(team_data_list)
    teams_df.to_csv(Path(__file__).parents[1] / "teams.csv", index=False)
