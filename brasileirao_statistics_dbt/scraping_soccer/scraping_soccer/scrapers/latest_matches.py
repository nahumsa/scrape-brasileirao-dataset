import pandas as pd
import requests
from bs4 import BeautifulSoup
from dagster import get_dagster_logger

BASE_URL = "https://www.espn.com.br"
logger = get_dagster_logger()


def extract_match_ids(relative_url: str) -> int:
    try:
        match_id = relative_url.split("/")[-1]
    except IndexError as error:
        raise ValueError("Unable to get match_id") from error

    return int(match_id)


def scrape(team_id: int, league_name: str, season: int) -> pd.DataFrame:
    results_url = (
        f"/futebol/time/resultados/_/id/{team_id}/liga/{league_name}/temporada/{season}"
    )

    logger.info(
        f"getting matches for team_id={team_id} league_name={league_name} season={season}"
    )

    response = requests.get(
        BASE_URL + results_url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"  # noqa
        },
    )
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    links = soup.find_all(
        "a", href=lambda href: href and href.startswith("/futebol/partida/_/jogoId")
    )

    # Extract the href attribute from each link and print them
    team_match_list = []

    for link in links:
        match_url = link.get("href")
        team_match_list.append(
            {
                "url": BASE_URL + match_url,
                "match_id": extract_match_ids(match_url),
                "team_id": team_id,
            }
        )
    matches_df = pd.DataFrame(team_match_list)
    matches_df = matches_df.drop_duplicates().reset_index(drop=True)
    return matches_df


if __name__ == "__main__":
    team_id = 6154
    LEAGUE_NAME = "bra.1"
    SEASON = 2023
    matches_df = scrape(team_id=team_id, league_name=LEAGUE_NAME, season=SEASON)
    print(matches_df)
