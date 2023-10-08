from pandas import DataFrame


def get_5_number(criteria: str, data: DataFrame) -> DataFrame:
    return data[criteria].describe()
