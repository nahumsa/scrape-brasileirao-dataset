import time
from concurrent.futures import ProcessPoolExecutor, as_completed

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
    io_manager_key="postgres_io_manager_raw_soccer",
    metadata={"table": "teams_info", "schema": "raw_data"},
)
def teams_info() -> Output:
    teams_df = teams.scrape(LEAGUE_NAME)
    return Output(
        value=teams_df,
        metadata={"num_entries": len(teams_df), "columns": list(teams_df.columns)},
    )


@asset(
    io_manager_key="postgres_io_manager_raw_soccer",
    ins={
        "teams_info": AssetIn(
            metadata={"input_query": "SELECT team_id, name FROM raw_data.teams_info"}
        )
    },
    metadata={"table": "teams_matches", "schema": "raw_data"},
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
            "columns": list(all_teams_matches_df.columns),
        },
    )


@multi_asset(
    ins={
        "teams_matches": AssetIn(
            metadata={"input_query": "SELECT match_id FROM raw_data.teams_matches"}
        )
    },
    outs={
        "matches_statistics": AssetOut(
            io_manager_key="postgres_io_manager_raw_soccer",
            metadata={"table": "matches_statistics", "schema": "raw_data"},
        ),
        "matches_info": AssetOut(
            io_manager_key="postgres_io_manager_raw_soccer",
            metadata={"table": "matches_info", "schema": "raw_data"},
        ),
    },
)
def extract_matches_statistics_and_info(
    teams_matches: pd.DataFrame,
) -> tuple[Output, Output]:
    all_matches_id = teams_matches["match_id"].unique()

    with ProcessPoolExecutor() as executor:
        # Submit the tasks to the executor
        futures = [
            executor.submit(match_statistics.scrape, match_id)
            for match_id in all_matches_id
        ]

        # Wait for all tasks to complete and get the results
        results = [future.result() for future in as_completed(futures)]

    match_statistics_df = pd.concat([results_list[0] for results_list in results])
    match_info_df = pd.concat([results_list[1] for results_list in results])

    return (
        Output(
            value=match_statistics_df,
            metadata={
                "num_records": len(match_statistics_df),
                "columns": list(match_statistics_df.columns),
            },
        ),
        Output(
            value=match_info_df,
            metadata={
                "num_records": len(match_info_df),
                "columns": list(match_info_df.columns),
            },
        ),
    )
