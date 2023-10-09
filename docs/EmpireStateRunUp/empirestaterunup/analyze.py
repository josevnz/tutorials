import numpy as np
from pandas import DataFrame

SUMMARY_METRICS = ('age', 'time', 'pace')
Z_FILTER = [
    'name',
    'level',
    'gender',
    'city',
    'state',
    'country',
    'wave',
    'overall position',
    'gender position',
    'division position'
]


def get_5_number(criteria: str, data: DataFrame) -> DataFrame:
    return data[criteria].describe()


def count_by_age(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby('age')['age'].count(), ('Age', 'Count')


def count_by_gender(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby('gender')['gender'].count(), ('Gender', 'Count')


def count_by_wave(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby('wave')['wave'].count(), ('Wave', 'Count')


def dt_to_sorted_dict(df: DataFrame) -> dict:
    return {k: v for k, v in sorted(df.to_dict().items(), key=lambda item: item[1], reverse=True)}


def get_zscore(df: DataFrame, z_filter=None):
    if z_filter is None:
        z_filter = Z_FILTER
    filtered = df.drop(z_filter, axis=1)
    return filtered.sub(filtered.mean()).div(filtered.std(ddof=0))


def get_outliers(df: DataFrame, column: str, std_threshold: int = 3) -> DataFrame:
    """
    Use the z-score, anything further away than 3 standard deviations is considered an outlier.
    """
    filtered_df = df[column]
    z_scores = get_zscore(df)[column]
    is_over = np.abs(z_scores) > std_threshold
    return filtered_df[is_over]
