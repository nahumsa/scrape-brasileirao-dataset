import re
from enum import Enum

import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://www.espn.com.br/futebol/partida/_/jogoId/665914"
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, "html.parser")


def get_numbers_from_string(text: str) -> int:
    try:
        return int(re.findall(r"\d+", text)[0])
    except IndexError as error:
        raise IndexError(f"It was not possible to get numbers from {text}") from error
    except ValueError as error:
        raise ValueError(f"There is no number in {text}") from error


def get_team_names_from_match() -> tuple[int, int]:
    teams = soup.find_all(
        "h2", class_="ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db"
    )

    home_team, away_team = [element.text for element in teams]
    return home_team, away_team


def get_score_from_match() -> tuple[int, int]:
    scores = soup.find_all(
        "div",
        class_="Gamestrip__ScoreContainer flex flex-column items-center justify-center relative",  # noqa
    )

    home_score, away_score = [element.text for element in scores]

    home_score = get_numbers_from_string(home_score)
    away_score = get_numbers_from_string(away_score)
    return home_score, away_score


def get_stats_table(
    columns_name: list[str] = ["home", "stat_name", "away"]
) -> pd.DataFrame:
    div_table = soup.find("div", "Table__Scroller")
    if div_table:
        table = div_table.find("table")
        data = []
        if table:
            rows = table.find_all("tr")  # noqa
            for row in rows:
                columns = row.find_all("td")
                if columns:
                    row_data = [column.text.strip() for column in columns]
                    data.append(row_data)
    return pd.DataFrame(data, columns=columns_name)


df = get_stats_table()


class TeamFieldCommandEnum(str, Enum):
    HOME: str = "home"
    AWAY: str = "away"


def get_possesion_stats(team_field_command: TeamFieldCommandEnum) -> int:
    possession_scraped_string: str = soup.find(  # noqa
        "div", class_=f"Possession__stat Possession__stat--{team_field_command.value}"
    ).text

    try:
        possesion = re.findall(r"\d+", possession_scraped_string)[0]

        return int(possesion)

    except IndexError as error:
        raise IndexError("The format for the possession changed") from error


print(get_possesion_stats(TeamFieldCommandEnum.HOME))
print(get_possesion_stats(TeamFieldCommandEnum.AWAY))


def get_shot_stats(team_field_command: TeamFieldCommandEnum) -> tuple[int, int]:
    shots_scraped_string: str = soup.find(  # noqa
        "div", class_=f"Shots__col__target Shots__col__target--{team_field_command}"
    ).text
    try:
        kicks, kicks_on_goal = re.findall(r"\d+", shots_scraped_string)

    except IndexError as error:
        raise IndexError("The format for the kick attempts changed") from error

    return int(kicks), int(kicks_on_goal)


print(get_shot_stats(TeamFieldCommandEnum.HOME))
print(get_shot_stats(TeamFieldCommandEnum.AWAY))
