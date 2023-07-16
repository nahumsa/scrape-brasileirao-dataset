from dagster import (Definitions, load_assets_from_modules,
                     load_assets_from_package_module)

from . import assets
from .io_managers.psql import PostgresIOManager

defs = Definitions(
    assets=load_assets_from_modules([assets]),
    resources={
        "postgres_io_manager_raw_soccer": PostgresIOManager(
            "postgresql://myuser:mypassword@localhost:5432/raw_soccer",
        ),
    },
)
