"""
Analyze original race results and give back canned reports
author: Jose Vicente Nunez <kodegeek.com@protonmail.com>
"""
import re
from enum import Enum
from typing import Union, Tuple, Dict, Any

import numpy as np
import pandas
from pandas import DataFrame, Categorical, Series, Timedelta
from datetime import timedelta

from empirestaterunup.data import RaceFields

SUMMARY_METRICS = (RaceFields.AGE.value, RaceFields.TIME.value, RaceFields.PACE.value)


class FastestFilters(Enum):
    Gender = 0
    Age = 1
    Country = 2


def get_5_number(criteria: str, data: DataFrame) -> DataFrame:
    return data[criteria].describe()


def count_by_age(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby(RaceFields.AGE.value)[RaceFields.AGE.value].count(), ('Age', 'Count')


def count_by_gender(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby(RaceFields.GENDER.value)[RaceFields.GENDER.value].count(), ('Gender', 'Count')


def count_by_wave(data: DataFrame) -> tuple[DataFrame, tuple]:
    return data.groupby(RaceFields.WAVE.value)[RaceFields.WAVE.value].count(), ('Wave', 'Count')


def dt_to_sorted_dict(df: Union[DataFrame | Series]) -> dict:
    return {k: v for k, v in sorted(df.to_dict().items(), key=lambda item: item[1], reverse=True)}


def get_zscore(df: DataFrame, column: str):
    filtered = df[column]
    return filtered.sub(filtered.mean()).div(filtered.std(ddof=0))


def get_outliers(df: DataFrame, column: str, std_threshold: int = 3) -> Series:
    """
    Use the z-score, anything further away than 3 standard deviations is considered an outlier.
    """
    filtered_df = df[column]
    z_scores = get_zscore(df=df, column=column)
    is_over = np.abs(z_scores) > std_threshold
    return filtered_df[is_over]


def age_bins(df: DataFrame) -> tuple[Categorical, tuple]:
    """
    Group ages into age buckets
    """
    ages = [r * 10 for r in range(1, 11)]
    labels = [f"[{age} - {age + 10}]" for age in ages[:-1]]
    categories: Categorical = pandas.cut(df[RaceFields.AGE.value], ages, labels=labels)
    return categories, ('Age', 'Count')


def time_bins(df: DataFrame) -> tuple[Categorical, tuple]:
    """
    Group finish times into time buckets
    """
    times = [timedelta(minutes=r * 10) for r in range(1, 13)]
    labels = [f"[{r * 10} - {(r + 1) * 10}]" for r in range(1, 12)]
    categories: Categorical = pandas.cut(df[RaceFields.TIME.value], times, labels=labels)
    return categories, ('Time', 'Count')


def get_country_counts(df: DataFrame, min_participants: int = 5, max_participants: int = 5) -> Tuple[Series, Series, Series]:
    """
    Gen interesting country counts
    :param df DataFrame to query
    :param min_participants Minimum number of participants, filter out above this value
    :param max_participants Maximum number of participants, filter out below this value
    :return country counts (unfiltered), countries, which countries with less than max_participants grouped under 'Others'
    """
    countries = df[RaceFields.COUNTRY.value]
    countries_counts = countries.value_counts()
    min_country_filter = countries_counts[countries_counts.values > min_participants]
    max_country_filter = countries_counts[countries_counts.values < max_participants]
    return countries_counts, min_country_filter, max_country_filter


def better_than_median_waves(df: DataFrame) -> Tuple[Timedelta, Series]:
    """
    Get runners whose race time is better than the median
    :param df Dataframe to analyze
    :return Tuple of median run time, Wave value counts series for values smaller than the median
    """
    median = df[RaceFields.TIME.value].median()
    return median, df[df[RaceFields.TIME.value].values <= median][RaceFields.WAVE.value].value_counts()


def find_fastest(df: DataFrame, criteria: FastestFilters) -> Dict[str, Dict[str, Any]]:
    """
    Find the fastest runners, per category
    :param df Dataframe to analyze
    :param criteria Filtering rules
    :return Dictionary with the fastest runners, includes criteria and value
    """
    results = {}
    if criteria == FastestFilters.Age:
        age_bucket, _ = age_bins(df)
        buckets = age_bucket.unique()
        for bucket in buckets:
            matcher = re.search('(\\d+) - (\\d+)', bucket)
            if matcher:
                low = int(matcher.group(1))
                high = int(matcher.group(2))
                runners_by_bucket = df[(df[RaceFields.AGE.value] >= low) & (df[RaceFields.AGE.value] <= high)]
                fastest_time = runners_by_bucket[RaceFields.TIME.value].min()
                fastest_runner = runners_by_bucket[(runners_by_bucket[RaceFields.TIME.value]) == fastest_time]
                name = fastest_runner.name.values[0]
                age = fastest_runner.age.values[0]
                results[bucket] = {
                    "name": name,
                    "age": age,
                    "time": fastest_time
                }
    elif criteria == FastestFilters.Gender:
        genders = df[RaceFields.GENDER.value].unique()
        for gender in genders:
            runners_by_gender = df[(df[RaceFields.GENDER.value] == gender)]
            fastest_time = runners_by_gender[RaceFields.TIME.value].min()
            fastest_runner = runners_by_gender[(runners_by_gender[RaceFields.TIME.value]) == fastest_time]
            name = fastest_runner.name.values[0]
            gender = fastest_runner.gender.values[0]
            results[gender] = {
                "name": name,
                "time": fastest_time
            }
    elif FastestFilters.Country:
        countries = df[RaceFields.COUNTRY.value].unique()
        for country in countries:
            runners_by_country = df[(df[RaceFields.COUNTRY.value] == country)]
            fastest_time = runners_by_country[RaceFields.TIME.value].min()
            fastest_runner = runners_by_country[(runners_by_country[RaceFields.TIME.value]) == fastest_time]
            name = fastest_runner.name.values[0]
            country = fastest_runner.country.values[0]
            results[country] = {
                "name": name,
                "time": fastest_time
            }
    return results
