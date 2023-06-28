import pandas as pd
from dagster import asset

import scraping_soccer.scrapers.teams as teams


@asset
def teams_info() -> pd.DataFrame:
    return teams.scrape("bra.1")
