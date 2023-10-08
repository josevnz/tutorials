from pandas import DataFrame

SUMMARY_METRICS = ('age', 'time', 'pace')


def get_5_number(criteria: str, data: DataFrame) -> DataFrame:
    return data[criteria].describe()
