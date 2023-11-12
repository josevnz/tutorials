"""
Analyze original race results and give back canned reports
author: Jose Vicente Nunez <kodegeek.com@protonmail.com>
"""
from typing import Union, Tuple

import numpy as np
import pandas
from pandas import DataFrame, Categorical, Series
from datetime import timedelta

from empirestaterunup.data import RaceFields

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
    return data.groupby(RaceFields.age.value)[RaceFields.age.value].count(), ('Age', 'Count')


def count_by_gender(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby(RaceFields.gender.value)[RaceFields.gender.value].count(), ('Gender', 'Count')


def count_by_wave(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby(RaceFields.wave.value)[RaceFields.wave.value].count(), ('Wave', 'Count')


def dt_to_sorted_dict(df: Union[DataFrame | Series]) -> dict:
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


def get_fastest(df: DataFrame, limit: int = 20) -> DataFrame:
    return df[
        [RaceFields.time.value,
         RaceFields.age.value,
         RaceFields.gender.value,
         RaceFields.country.value
         ]
    ].groupby(RaceFields.time.value).value_counts().nlargest(limit)


def age_bins(df: DataFrame) -> tuple[Categorical, tuple]:
    """
    Group ages into age buckets
    """
    ages = [r * 10 for r in range(1, 11)]
    labels = [f"[{age} - {age + 10}]" for age in ages[:-1]]
    categories: Categorical = pandas.cut(df[RaceFields.age.value], ages, labels=labels)
    return categories, ('Age', 'Count')


def time_bins(df: DataFrame) -> tuple[Categorical, tuple]:
    """
    Group finish times into time buckets
    """
    times = [timedelta(minutes=r * 10) for r in range(1, 13)]
    labels = [f"[{r * 10} - {(r + 1) * 10}]" for r in range(1, 12)]
    categories: Categorical = pandas.cut(df[RaceFields.time.value], times, labels=labels)
    return categories, ('Time', 'Count')


def get_country_counts(df: DataFrame, max_participants: int = 5) -> Tuple[Series, Series]:
    """
    Gen interesting country counts
    :param df DataFrame to query
    :param max_participants Maximum number of participants, filter out above this value
    :return country counts (unfiltered), countries, which countries with less than max_participants grouped under 'Others'
    """
    countries = df[RaceFields.country.value]
    countries_counts = countries.value_counts()
    country_filter = countries_counts[countries_counts.values > max_participants]
    return countries_counts, country_filter


def better_than_median_waves(df: DataFrame) -> Tuple[float, Series]:
    """
    :param df Dataframe to analyze
    :return Tuple of median run time, Wave value counts series for values smaller than the median
    """
    median = df[RaceFields.time.value].median()
    return median, df[df[RaceFields.time.value].values <= median][RaceFields.wave.value].value_counts()
