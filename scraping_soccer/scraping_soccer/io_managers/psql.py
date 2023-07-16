import pandas as pd
from dagster import (Any, InputContext, IOManager, OutputContext,
                     get_dagster_logger)
from pandas import DataFrame
from sqlalchemy import create_engine

logger = get_dagster_logger()


class PostgresIOManager(IOManager):
    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    def load_input(self, context: InputContext):
        try:
            query = context.metadata["input_query"]
        except KeyError as error:
            raise ValueError("You must define a `input_query` in your asset.")
        engine = create_engine(self.conn_string)
        df = pd.read_sql(query, engine)
        return df

    def handle_output(self, context: OutputContext, obj: Any):
        if isinstance(obj, DataFrame):
            try:
                table = context.metadata["table"]

            except KeyError as error:
                raise ValueError("Table name not provided in metadata") from error
            engine = create_engine(self.conn_string)
            obj.to_sql(table, engine, if_exists="replace")

        else:
            raise ValueError("Object type not supported by PostgresIOManager")
