import time

import pandas as pd
from dagster import (AssetIn, AssetOut, Output, asset, get_dagster_logger,
                     multi_asset)

import scraping_soccer.scrapers.teams as teams
from scraping_soccer.scrapers import latest_matches, match_statistics

BASE_URL = "https://www.espn.com.br"
LEAGUE_NAME = "bra.1"
SEASON = 2023

logger = get_dagster_logger()


@asset(
    io_manager_key="postgres_io_manager_raw_soccer", metadata={"table": "teams_info"}
)
def teams_info() -> Output:
    teams_df = teams.scrape(LEAGUE_NAME)
    return Output(value=teams_df, metadata={"num_entries": len(teams_df)})


@asset(
    io_manager_key="postgres_io_manager_raw_soccer",
    ins={
        "teams_info": AssetIn(
            metadata={"input_query": "SELECT team_id, name FROM teams_info"}
        )
    },
    metadata={
        "table": "teams_matches",
    },
)
def teams_matches(teams_info: pd.DataFrame) -> Output:
    all_teams_matches_df = pd.DataFrame()

    for _, (team_id, _) in teams_info.iterrows():
        logger.info(f"Getting latest matches for {team_id}")
        team_match_df = latest_matches.scrape(
            team_id=team_id, league_name=LEAGUE_NAME, season=SEASON
        )
        all_teams_matches_df = pd.concat([all_teams_matches_df, team_match_df])
        time.sleep(1)

    return Output(
        value=all_teams_matches_df,
        metadata={
            "num_records": len(all_teams_matches_df),
            "unique_matches": all_teams_matches_df["match_id"].nunique(),
        },
    )


@multi_asset(
    ins={
        "teams_matches": AssetIn(
            metadata={"input_query": "SELECT match_id FROM teams_matches"}
        )
    },
    outs={
        "matches_statistics": AssetOut(
            io_manager_key="postgres_io_manager_raw_soccer",
            metadata={"table": "matches_statistics"},
        ),
        "matches_info": AssetOut(
            io_manager_key="postgres_io_manager_raw_soccer",
            metadata={"table": "matches_info"},
        ),
    },
)
def extract_matches_statistics_and_info(
    teams_matches: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_matches_statistics_df = pd.DataFrame()
    all_match_info_df = pd.DataFrame()

    for match_id in teams_matches["match_id"].unique():
        logger.info(f"Getting latest matches statistics for {match_id}")
        match_statistics_df, match_info_df = match_statistics.scrape(match_id=match_id)
        all_matches_statistics_df = pd.concat(
            [all_matches_statistics_df, match_statistics_df]
        )
        all_match_info_df = pd.concat([all_match_info_df, match_info_df])
        time.sleep(1)

    return all_matches_statistics_df, all_match_info_df
