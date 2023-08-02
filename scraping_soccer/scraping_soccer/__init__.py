from dagster import (Definitions, load_assets_from_modules, define_asset_job, AssetSelection, ScheduleDefinition)

from . import assets
from .io_managers.psql import PostgresIOManager
all_assets = load_assets_from_modules([assets])
scraping_soccer_job = define_asset_job("scraping_soccer",
                                        selection=AssetSelection.groups("scraping"))
scraping_soccer_schedule = ScheduleDefinition(
    job=scraping_soccer_job,
    cron_schedule="0 0 * * *"
)

defs = Definitions(
    assets=all_assets,
    schedules=[scraping_soccer_schedule],
    resources={
        "postgres_io_manager_raw_soccer": PostgresIOManager(
            "postgresql://myuser:mypassword@localhost:5432/raw_soccer",
        ),
    },
)
