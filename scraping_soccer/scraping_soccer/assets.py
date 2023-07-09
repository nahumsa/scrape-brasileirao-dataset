import time
import pandas as pd
from dagster import asset, get_dagster_logger

import scraping_soccer.scrapers.teams as teams
from scraping_soccer.scrapers.latest_matches import get_latest_matches

BASE_URL = "https://www.espn.com.br"
LEAGUE_NAME = "bra.1"
SEASON = 2023
LEAGUE_NAME = "bra.1"
SEASON = 2023

logger = get_dagster_logger()

@asset
def teams_info() -> pd.DataFrame:
    return teams.scrape(LEAGUE_NAME)


@asset
def teams_matches(teams_info: pd.DataFrame) -> pd.DataFrame:
    all_teams_matches_df = pd.DataFrame()

    for _, (team_id, _) in teams_info.iterrows():
        logger.info(f"Getting latest matches for {team_id}")
        team_match_df= get_latest_matches(team_id=team_id, league_name=LEAGUE_NAME, season=SEASON)
        all_teams_matches_df = pd.concat([all_teams_matches_df, team_match_df])
        time.sleep(1)

    return all_teams_matches_df

