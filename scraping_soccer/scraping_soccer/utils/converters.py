import pandas as pd
from pydantic import BaseModel


def convert_basemodel_to_df(model_list: list[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([model.dict() for model in model_list])
