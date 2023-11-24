"""
Data loading logic, after web scrapping process is completed.
author: Jose Vicente Nunez <kodegeek.com@protonmail.com>
"""
import csv
import datetime
import math
import re
from enum import Enum
from pathlib import Path
from typing import Iterable, Any, Dict, Tuple, Union

import pandas
from pandas import DataFrame

"""
Runners started on waves, but for basic analysis we will assume all runners were able to run
at the same time.
"""
BASE_RACE_DATETIME = datetime.datetime(
    year=2023,
    month=9,
    day=4,
    hour=20,
    minute=0,
    second=0,
    microsecond=0
)


class Waves(Enum):
    """
    22 Elite male
    17 Elite female
    There are some holes, so either some runners did not show up or there was spare capacity.
    https://runsignup.com/Race/EmpireStateBuildingRunUp/Page-4
    https://runsignup.com/Race/EmpireStateBuildingRunUp/Page-5
    I guessed who went on which category, based on the BIB numbers I saw that day
    """
    EliteMen = ["Elite Men", [1, 25], BASE_RACE_DATETIME]
    EliteWomen = ["Elite Women", [26, 49], BASE_RACE_DATETIME + datetime.timedelta(minutes=2)]
    Purple = ["Specialty", [100, 199], BASE_RACE_DATETIME + datetime.timedelta(minutes=10)]
    Green = ["Sponsors", [200, 299], BASE_RACE_DATETIME + datetime.timedelta(minutes=20)]
    """
    The date people applied for the lottery determined the colors?. Let's assume that
    General Lottery Open: 7/17 9AM- 7/28 11:59PM
    General Lottery Draw Date: 8/1
    """
    Orange = ["Tenants", [300, 399], BASE_RACE_DATETIME + datetime.timedelta(minutes=30)]
    Grey = ["General 1", [400, 499], BASE_RACE_DATETIME + datetime.timedelta(minutes=40)]
    Gold = ["General 2", [500, 599], BASE_RACE_DATETIME + datetime.timedelta(minutes=50)]
    Black = ["General 3", [600, 699], BASE_RACE_DATETIME + datetime.timedelta(minutes=60)]


"""
Interested only in people who completed the 86 floors. So is either full course or dnf
"""


class Level(Enum):
    full = "Full Course"
    dnf = "DNF"


class RaceFields(Enum):
    level = "level"
    name = "name"
    gender = "gender"
    bib = "bib"
    state = "state"
    country = "country"
    wave = "wave"
    overall_position = "overall position"
    gender_position = "gender position"
    division_position = "division position"
    pace = "pace"
    time = "time"
    city = "city"
    age = "age"
    twenty_floor_position = "20th floor position"
    twenty_floor_gender_position = "20th floor gender position"
    twenty_floor_division_position = "20th floor division position"
    twenty_floor_pace = '20th floor Pace'
    twenty_floor_time = '20th floor time'
    sixty_five_floor_position = "65th floor position"
    sixty_five_floor_gender_position = "65th floor gender position"
    sixty_five_floor_division_position = "65th floor division position"
    sixty_five_floor_pace = '65th floor pace'
    sixty_five_floor_time = '65th floor time'
    url = "url"


FIELD_NAMES = [x.value for x in RaceFields]


def get_wave_from_bib(bib: int) -> Waves:
    for wave in Waves:
        (lower, upper) = wave.value[1]
        if lower <= bib <= upper:
            return wave
    return Waves.Black


def get_description_for_wave(wave: Waves) -> str:
    return wave.value[0]


def get_wave_start_time(wave: Waves) -> datetime:
    return wave.value[2]


def raw_csv_read(raw_file: Path) -> Iterable[Dict[str, Any]]:
    record = {}
    with open(raw_file, 'r') as raw_csv_file:
        reader = csv.DictReader(raw_csv_file)
        for row in reader:
            try:
                for field in FIELD_NAMES:
                    column_val = row[field].strip()
                    if field == RaceFields.bib.value:
                        bib = int(column_val)
                        record[field] = bib
                    elif field in [
                        RaceFields.gender_position.value,
                        RaceFields.division_position.value,
                        RaceFields.overall_position.value,
                        RaceFields.twenty_floor_position.value,
                        RaceFields.twenty_floor_division_position.value,
                        RaceFields.twenty_floor_gender_position.value,
                        RaceFields.sixty_five_floor_position.value,
                        RaceFields.sixty_five_floor_division_position.value,
                        RaceFields.sixty_five_floor_gender_position.value,
                        RaceFields.age.value
                    ]:
                        try:
                            record[field] = int(column_val)
                        except ValueError:
                            record[field] = math.nan
                    elif field == RaceFields.wave.value:
                        record[field] = get_wave_from_bib(bib).name.upper()
                    elif field in [
                        RaceFields.gender.value,
                        RaceFields.country.value
                    ]:
                        record[field] = column_val.upper()
                    elif field in [
                        RaceFields.city.value,
                        RaceFields.state.value,

                    ]:
                        record[field] = column_val.capitalize()
                    elif field in [
                        RaceFields.sixty_five_floor_pace.value,
                        RaceFields.sixty_five_floor_time.value,
                        RaceFields.twenty_floor_pace.value,
                        RaceFields.twenty_floor_time.value,
                        RaceFields.pace.value,
                        RaceFields.time.value
                    ]:
                        parts = column_val.strip().split(':')
                        for idx in range(0, len(parts)):
                            if len(parts[idx]) == 1:
                                parts[idx] = f"0{parts[idx]}"
                        if len(parts) == 2:
                            parts.insert(0, "00")
                        record[field] = ":".join(parts)
                    else:
                        record[field] = column_val
                if record[field] in ['-', '--']:
                    record[field] = ""
                yield record
            except IndexError:
                raise


def raw_copy_paste_read(raw_file: Path) -> Iterable[Dict[str, Any]]:
    """
    Read the whole RAW file, product of a manual copy and paste, return a clean version.
    You should use the raw_csv_read() method on the file produced by the scrapper.
    Each record looks like this (copy and paste from the website):

    NAME
    GENDER BIB CITY,STATE,COUNTRY
    OVERALL_POSITION
    GENDER_POSITION
    DIVISION_POSITION
    PACE_MIN_PER_MILE_HH:MM:SS
    MIN/MI
    TIME_HH:MM:SS

    ```
    Wai Ching Soh
    M 29Bib 19Kuala Lumpur, -, MYS
    1
    1
    1
    53:00
    MIN/MI
    10:36
    ```
    :param raw_file: Yes, copied and pasted all the 8 pages when started the project, before writing a scrapper :D
    :return:
    """
    with open(raw_file, 'r') as file_data:
        tk_cnt = 0
        ln_cnt = 0
        record = {}
        info_pattern = re.compile("([A-Z]) (\\d+)Bib (\\d*)(.*)")
        info_pattern2 = re.compile("([A-Z]+)Bib (\\d+)-, (.*)")
        DNF_BIB = [434]
        for line in file_data:
            try:
                tk_cnt += 1
                ln_cnt += 1
                if tk_cnt == 1:
                    record[RaceFields.name.value] = line.strip()
                elif tk_cnt == 2:
                    """
                    M 29Bib 19Kuala Lumpur, -, MYS
                    M 50Bib 3Colorado Springs, CO, USA
                    """
                    matcher = info_pattern.search(line.strip())
                    if matcher:
                        record[RaceFields.gender.value] = matcher.group(1).upper()
                        record[RaceFields.age.value] = int(matcher.group(2))
                        record[RaceFields.bib.value] = int(matcher.group(3))
                        if record[RaceFields.bib.value] in DNF_BIB:
                            record[
                                RaceFields.level.value] = Level.dnf.value
                        else:
                            record[RaceFields.level.value] = Level.full.value
                        location = matcher.group(4).split(',')
                        if len(location) == 3:
                            record[RaceFields.city.value] = location[0].strip().capitalize()
                            record[RaceFields.state.value] = location[1].strip().capitalize()
                            record[RaceFields.country.value] = location[2].strip().upper()
                        elif len(location) == 2:
                            record[RaceFields.city.value] = ""
                            record[RaceFields.state.value] = location[0].strip().capitalize()
                            record[RaceFields.country.value] = location[1].strip().upper()
                        elif len(location) == 1:
                            record[RaceFields.city.value] = ""
                            record[RaceFields.state.value] = ""
                            record[RaceFields.country.value] = location[0].strip().upper()
                        else:  # This should not happen
                            record[RaceFields.city.value] = ""
                            record[RaceFields.state.value] = ""
                            record[RaceFields.country.value] = ""
                        record[RaceFields.wave.value] = get_wave_from_bib(record[RaceFields.bib.value]).name.upper()
                    else:
                        matcher = info_pattern2.search(line.strip())
                        if matcher:
                            record[RaceFields.gender.value] = matcher.group(1).upper()
                            record[RaceFields.age.value] = math.nan
                            record[RaceFields.bib.value] = int(matcher.group(2))
                            record[RaceFields.city.value] = ""
                            record[RaceFields.state.value] = ""
                            record[RaceFields.country.value] = matcher.group(3).upper()
                        else:
                            raise ValueError(f"Regexp failed for {line.strip()}")
                elif tk_cnt == 3:
                    record[RaceFields.overall_position.value] = int(line.strip())
                elif tk_cnt == 4:
                    try:
                        record[RaceFields.gender_position.value] = int(line.strip())
                    except ValueError:
                        # If GENDER is not specified the position is missing.
                        record[
                            RaceFields.gender_position.value] = math.nan
                elif tk_cnt == 5:
                    record[RaceFields.division_position.value] = int(line.strip())
                elif tk_cnt == 6:
                    parts = line.strip().split(':')
                    if len(parts) == 3:
                        record[RaceFields.pace.value] = F"0{line.strip()}"
                    else:
                        record[RaceFields.pace.value] = f"00:{line.strip()}"
                elif tk_cnt == 7:
                    pass  # Always MIN/MI
                elif tk_cnt == 8:
                    tk_cnt = 0
                    parts = line.strip().split(':')
                    if len(parts) == 3:
                        record[RaceFields.time.value] = line.strip()
                    else:
                        record[RaceFields.time.value] = f"00:{line.strip()}"

                    # None of the fields below are available on the first level copy and paste
                    record[RaceFields.twenty_floor_position.value] = ""
                    record[RaceFields.twenty_floor_gender_position.value] = ""
                    record[RaceFields.twenty_floor_division_position.value] = ""
                    record[RaceFields.twenty_floor_pace.value] = ""
                    record[RaceFields.twenty_floor_time.value] = ""
                    record[RaceFields.sixty_five_floor_position.value] = ""
                    record[RaceFields.sixty_five_floor_gender_position.value] = ""
                    record[RaceFields.sixty_five_floor_division_position.value] = ""
                    record[RaceFields.sixty_five_floor_pace.value] = ""
                    record[RaceFields.sixty_five_floor_time.value] = ""

                    yield record
            except ValueError as ve:
                raise ValueError(f"ln_cnt={ln_cnt}, tk_cnt={tk_cnt},{record}", ve)


class CourseRecords(Enum):
    Male = ('Paul Crake', 'Australia', 2003, '9:33')
    Female = ('Andrea Mayr', 'Austria', 2006, '11:23')


RACE_RESULTS_FIRST_LEVEL = Path(__file__).parent.joinpath("results-first-level-2023.csv")
RACE_RESULTS_FULL_LEVEL = Path(__file__).parent.joinpath("results-full-level-2023.csv")
COUNTRY_DETAILS = Path(__file__).parent.joinpath("country_codes.csv")


def load_data(data_file: Path = None, remove_dnf: bool = True) -> DataFrame:
    """
    ```csv
    level,name,gender,bib,state,country,wave,overall position,gender position,division position,pace,time,city,age
    Full Course,Wai Ching Soh,M,19,-,MYS,ELITEMEN,1,1,1,53:00,10:36,Kuala lumpur,29
    ```
    * The code remove by default the DNF runners to avoid distortion on the results.
    * Replace unknown ages with the median, to make analysis easier and avoid distortions
    """
    if data_file:
        def_file = data_file
    else:
        def_file = RACE_RESULTS_FULL_LEVEL
    df = pandas.read_csv(
        def_file
    )
    for field in [RaceFields.pace.value, RaceFields.time.value]:
        try:
            df[field] = pandas.to_timedelta(df[field])
        except ValueError as ve:
            raise ValueError(f'{field}=df[field]', ve)
    df['finishtimestamp'] = BASE_RACE_DATETIME + df[RaceFields.time.value]
    if remove_dnf:
        df.drop(df[df.level == 'DNF'].index, inplace=True)
    # Normalize Age
    median_age = df[RaceFields.age.value].median()
    df[RaceFields.age.value].fillna(median_age, inplace=True)
    df[RaceFields.age.value] = df[RaceFields.age.value].astype(int)
    # Normalize state and city
    df.replace({RaceFields.state.value: {'-': ''}}, inplace=True)
    df[RaceFields.state.value].fillna('', inplace=True)
    df[RaceFields.city.value].fillna('', inplace=True)
    # Normalize gender position
    median_gender_pos = df[RaceFields.gender_position.value].median()
    df[RaceFields.gender_position.value].fillna(median_gender_pos, inplace=True)
    df[RaceFields.gender_position.value] = df[RaceFields.gender_position.value].astype(int)

    # Normalize BIB and make it the index
    df[RaceFields.bib.value] = df[RaceFields.bib.value].astype(int)
    df.set_index(RaceFields.bib.value, inplace=True)
    return df


def to_list_of_tuples(df: DataFrame, bibs: list[int] = None) -> Union[Tuple | list[Tuple]]:
    bib_as_column = df.reset_index(level=0, inplace=False)
    if not bibs:
        filtered = bib_as_column
    else:
        filtered = bib_as_column[bib_as_column[RaceFields.bib.value].isin(bibs)]
    column_names = [
        RaceFields.level.value,
        RaceFields.name.value,
        RaceFields.gender.value,
        RaceFields.bib.value,
        RaceFields.state.value,
        RaceFields.country.value,
        RaceFields.wave.value,
        RaceFields.overall_position.value,
        RaceFields.gender_position.value,
        RaceFields.division_position.value,
        RaceFields.pace.value,
        RaceFields.time.value,
        RaceFields.city.value,
        RaceFields.age.value
    ]
    rows = [(
        r.level,
        r[RaceFields.name.value],
        r.gender,
        r.bib,
        r.state,
        r.country,
        r.wave,
        r[RaceFields.overall_position.value],
        r[RaceFields.gender_position.value],
        r[RaceFields.division_position.value],
        r.pace,
        r.time,
        r.city,
        r.age
    ) for _, r in filtered.iterrows()]
    return tuple(column_names), rows


def load_country_details(data_file: Path = None) -> DataFrame:
    """
    ```csv
    name,alpha-2,alpha-3,country-code,iso_3166-2,region,sub-region,intermediate-region,region-code,sub-region-code,intermediate-region-code
    United States of America,US,USA,840,ISO 3166-2:US,Americas,Northern America,"",019,021,""
    """
    if data_file:
        def_file = data_file
    else:
        def_file = COUNTRY_DETAILS
    df = pandas.read_csv(
        def_file
    )
    return df


class CountryColumns(Enum):
    name = "name"
    alpha_2 = "alpha-2"
    alpha_3 = "alpha-3"
    country_code = "country-code"
    iso_3166_2 = "iso_3166-2"
    region = "region"
    sub_region = "sub-region"
    intermediate_region = "intermediate-region"
    region_code = "region-code"
    sub_region_code = "sub-region-code"
    intermediate_region_code = "intermediate-region-code"


COUNTRY_COLUMNS = [country.value for country in CountryColumns]


def lookup_country_by_code(df: DataFrame, three_letter_code: str) -> DataFrame:
    if not isinstance(three_letter_code, str):
        raise ValueError(f"Invalid type for three letter country code: '{three_letter_code}'")
    if len(three_letter_code) != 3:
        raise ValueError(f"Invalid three letter country code: '{three_letter_code}'")
    return df.loc[df[CountryColumns.alpha_3.value] == three_letter_code]


def get_times(df: DataFrame) -> DataFrame:
    return df.select_dtypes(include=['timedelta64', 'datetime64'])


def get_positions(df: DataFrame) -> DataFrame:
    return df.select_dtypes(include=['int64'])


def get_categories(df: DataFrame) -> DataFrame:
    return df.select_dtypes(include=['object'])
