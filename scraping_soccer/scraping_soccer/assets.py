import time

import pandas as pd
from dagster import AssetOut, Output, asset, get_dagster_logger, multi_asset

import scraping_soccer.scrapers.teams as teams
from scraping_soccer.scrapers import latest_matches, match_statistics

BASE_URL = "https://www.espn.com.br"
LEAGUE_NAME = "bra.1"
SEASON = 2023

logger = get_dagster_logger()


@asset
def teams_info() -> Output:
    teams_df = teams.scrape(LEAGUE_NAME)
    return Output(value=teams_df, metadata={"num_entries": len(teams_df)})


@asset
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
    outs={"extract_matches_statistics": AssetOut(), "extract_matches_info": AssetOut()}
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


@asset
def matches_statistics(extract_matches_statistics: pd.DataFrame) -> Output:
    return Output(
        value=extract_matches_statistics,
        metadata={
            "num_records": len(extract_matches_statistics),
        },
    )


@asset
def matches_info(extract_matches_info: pd.DataFrame) -> Output:
    return Output(
        value=extract_matches_info,
        metadata={
            "num_records": len(extract_matches_info),
        },
    )
