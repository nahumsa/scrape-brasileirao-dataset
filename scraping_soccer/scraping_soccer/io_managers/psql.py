from dagster import Any, InputContext, IOManager
from pandas import DataFrame
from sqlalchemy import create_engine


class PostgresIOManager(IOManager):
    def __init__(self, conn_string: str, table_name: str):
        self.conn_string = conn_string
        self.table_name = table_name

    def load_input(self, context):
        raise NotImplementedError("Loading not supported by PostgresIOManager")

    def handle_output(self, context: InputContext, obj: Any):
        if isinstance(obj, DataFrame):
            if not self.table_name:
                raise ValueError("Table name not provided in metadata")

            engine = create_engine(self.conn_string)
            obj.to_sql(self.table_name, engine)
        else:
            raise ValueError("Object type not supported by PostgresIOManager")
