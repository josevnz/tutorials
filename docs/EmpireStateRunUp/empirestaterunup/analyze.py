from pandas import DataFrame

SUMMARY_METRICS = ('age', 'time', 'pace')


def get_5_number(criteria: str, data: DataFrame) -> DataFrame:
    return data[criteria].describe()


def count_by_age(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby('age')['age'].count(), ('Age', 'Count')


def count_by_gender(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby('gender')['gender'].count(), ('Gender', 'Count')


def count_by_wave(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby('wave')['wave'].count(), ('Wave', 'Count')
