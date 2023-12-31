import pandas as pd
from dagster import (Any, InputContext, IOManager, OutputContext,
                     get_dagster_logger)
from pandas import DataFrame
from sqlalchemy import create_engine

logger = get_dagster_logger()


class PostgresIOManager(IOManager):
    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    def load_input(self, context: InputContext) -> pd.DataFrame:
        try:
            query = context.metadata["input_query"]  # type: ignore
        except KeyError as error:
            raise ValueError(
                "You must define a `input_query` in your asset."
            ) from error

        engine = create_engine(self.conn_string)
        df = pd.read_sql(query, engine)
        engine.dispose()
        return df

    def handle_output(self, context: OutputContext, obj: Any) -> None:
        if isinstance(obj, DataFrame):
            try:
                table = context.metadata["table"]  # type: ignore
                schema = context.metadata["schema"]  # type: ignore

            except KeyError as error:
                raise ValueError(
                    "Table name or schema not provided in metadata"
                ) from error

            engine = create_engine(self.conn_string)
            obj.to_sql(
                name=table,
                con=engine,
                schema=schema,
                index=False,
                if_exists="replace",
            )
            engine.dispose()

        else:
            raise ValueError("Object type not supported by PostgresIOManager")
