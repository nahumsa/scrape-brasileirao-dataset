import re
from enum import Enum

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dagster import get_dagster_logger

from .errors import GetScoreError

BASE_URL = "https://www.espn.com.br"

logger = get_dagster_logger()


def get_numbers_from_string(text: str) -> int:
    try:
        return int(re.findall(r"\d+", text)[0])

    except IndexError as error:
        raise IndexError(f"It was not possible to get numbers from {text}") from error

    except ValueError as error:
        raise ValueError(f"There is no number in {text}") from error


def get_team_names_from_match(soup: BeautifulSoup) -> tuple[int, int]:
    teams = soup.find_all(
        "h2", class_="ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db"
    )

    home_team, away_team = [element.text for element in teams]
    return home_team, away_team


def get_score_from_match(soup: BeautifulSoup) -> tuple[int, int]:
    scores = soup.find_all(
        "div",
        class_="Gamestrip__ScoreContainer flex flex-column items-center justify-center relative",  # noqa
    )
    try:
        home_score, away_score = [element.text for element in scores]
    except AttributeError as error:
        logger.error("Unable to get score")
        raise GetScoreError() from error

    home_score = get_numbers_from_string(home_score)
    away_score = get_numbers_from_string(away_score)
    return home_score, away_score


def get_stats_table(
    soup: BeautifulSoup, columns_name: list[str] = ["stat_name", "home", "away"]
) -> pd.DataFrame:
    div_table = soup.find("div", class_="eZKk aoVn Shbr")
    data = []

    if div_table:
        for div in div_table.find_all("div", recursive=False):  # type: ignore
            data.append([span.text for span in div.find_all("span")])
        # TODO: find a better way to do this
        data = data[1:]
        data[0] = list(filter(lambda x: x != "%", data[0]))

    return pd.DataFrame(data, columns=columns_name)


class TeamFieldCommandEnum(str, Enum):
    HOME: str = "home"
    AWAY: str = "away"


def scrape(match_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info(f"getting data from match_id {match_id}")
    match_url = f"/futebol/partida/_/jogoId/{match_id}"
    response = requests.get(
        BASE_URL + match_url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"  # noqa
        },
    )

    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    base_stats = get_stats_table(soup)
    home_team_name, away_team_name = get_team_names_from_match(soup)
    home_score, away_score = get_score_from_match(soup)
    match_info_df = pd.DataFrame(
        [
            {"team": home_team_name, "field_command": "home", "score": home_score},
            {"team": away_team_name, "field_command": "away", "score": away_score},
        ]
    )

    away_stats_df = base_stats[["stat_name", "away"]]
    away_stats_df = away_stats_df.rename(columns={"away": "stat_value"})
    away_stats_df["team"] = away_team_name

    home_stats_df = base_stats[["stat_name", "home"]]
    home_stats_df = home_stats_df.rename(columns={"home": "stat_value"})
    home_stats_df["team"] = home_team_name
    all_stats_df = pd.concat([home_stats_df, away_stats_df])
    all_stats_df["match_id"] = match_id
    match_info_df["match_id"] = match_id

    return all_stats_df, match_info_df


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor, as_completed

    all_matches_id = [665914] * 3
    with ProcessPoolExecutor() as executor:
        # Submit the tasks to the executor
        futures = [executor.submit(scrape, match_id) for match_id in all_matches_id]

        # Wait for all tasks to complete and get the results
        results = [future.result() for future in as_completed(futures)]

        print(results)
