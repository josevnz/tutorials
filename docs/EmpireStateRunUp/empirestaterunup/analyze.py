from pandas import DataFrame


def get_5_number(criteria: str, data: DataFrame) -> DataFrame:
    if criteria == 'bib':
        return DataFrame()
    return data[criteria].describe()
