import re
from enum import Enum

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.espn.com.br"


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

    home_score, away_score = [element.text for element in scores]

    home_score = get_numbers_from_string(home_score)
    away_score = get_numbers_from_string(away_score)
    return home_score, away_score


def get_stats_table(
    soup: BeautifulSoup, columns_name: list[str] = ["home", "stat_name", "away"]
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


class TeamFieldCommandEnum(str, Enum):
    HOME: str = "home"
    AWAY: str = "away"


def get_possesion_stats(
    soup: BeautifulSoup, team_field_command: TeamFieldCommandEnum
) -> int:
    possession_scraped_string: str = soup.find(  # noqa
        "div", class_=f"Possession__stat Possession__stat--{team_field_command.value}"
    ).text

    try:
        possesion = re.findall(r"\d+", possession_scraped_string)[0]

        return int(possesion)

    except IndexError as error:
        raise IndexError("The format for the possession changed") from error


def get_shot_stats(
    soup: BeautifulSoup, team_field_command: TeamFieldCommandEnum
) -> tuple[int, int]:
    shots_scraped_string: str = soup.find(  # noqa
        "div", class_=f"Shots__col__target Shots__col__target--{team_field_command}"
    ).text
    try:
        kicks, kicks_on_goal = re.findall(r"\d+", shots_scraped_string)

    except IndexError as error:
        raise IndexError("The format for the kick attempts changed") from error

    return int(kicks), int(kicks_on_goal)


def scrape(match_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    match_url = f"/futebol/partida/_/jogoId/{match_id}"
    response = requests.get(BASE_URL + match_url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    base_stats = get_stats_table(soup)
    possession_df = pd.DataFrame(
        [
            {
                "home": get_possesion_stats(soup, TeamFieldCommandEnum.HOME),
                "stat_name": "posse",
                "away": get_possesion_stats(soup, TeamFieldCommandEnum.AWAY),
            }
        ]
    )
    shots_df = pd.DataFrame(
        [
            {
                "home": get_shot_stats(soup, TeamFieldCommandEnum.HOME)[0],
                "stat_name": "chutes",
                "away": get_shot_stats(soup, TeamFieldCommandEnum.AWAY)[0],
            },
            {
                "home": get_shot_stats(soup, TeamFieldCommandEnum.HOME)[1],
                "stat_name": "chutes no gol",
                "away": get_shot_stats(soup, TeamFieldCommandEnum.AWAY)[1],
            },
        ]
    )
    base_stats = pd.concat([base_stats, possession_df, shots_df])
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
