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
from typing import Iterable, Any, Dict, Tuple, Union, List

import pandas
from pandas import DataFrame, Series

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
    ELITE_MEN = ["Elite Men", [1, 25], BASE_RACE_DATETIME]
    ELITE_WOMEN = ["Elite Women", [26, 49], BASE_RACE_DATETIME + datetime.timedelta(minutes=2)]
    PURPLE = ["Specialty", [100, 199], BASE_RACE_DATETIME + datetime.timedelta(minutes=10)]
    GREEN = ["Sponsors", [200, 299], BASE_RACE_DATETIME + datetime.timedelta(minutes=20)]
    """
    The date people applied for the lottery determined the colors?. Let's assume that
    General Lottery Open: 7/17 9AM- 7/28 11:59PM
    General Lottery Draw Date: 8/1
    """
    ORANGE = ["Tenants", [300, 399], BASE_RACE_DATETIME + datetime.timedelta(minutes=30)]
    GREY = ["General 1", [400, 499], BASE_RACE_DATETIME + datetime.timedelta(minutes=40)]
    GOLD = ["General 2", [500, 599], BASE_RACE_DATETIME + datetime.timedelta(minutes=50)]
    BLACK = ["General 3", [600, 699], BASE_RACE_DATETIME + datetime.timedelta(minutes=60)]


"""
Interested only in people who completed the 86 floors. So is either full course or dnf
"""


class Level(Enum):
    FULL = "Full Course"
    DNF = "DNF"


# Fields are sorted by interest
class RaceFields(Enum):
    BIB = "bib"
    NAME = "name"
    OVERALL_POSITION = "overall position"
    TIME = "time"
    GENDER = "gender"
    GENDER_POSITION = "gender position"
    AGE = "age"
    DIVISION_POSITION = "division position"
    COUNTRY = "country"
    STATE = "state"
    CITY = "city"
    PACE = "pace"
    TWENTY_FLOOR_POSITION = "20th floor position"
    TWENTY_FLOOR_GENDER_POSITION = "20th floor gender position"
    TWENTY_FLOOR_DIVISION_POSITION = "20th floor division position"
    TWENTY_FLOOR_PACE = '20th floor pace'
    TWENTY_FLOOR_TIME = '20th floor time'
    SIXTY_FLOOR_POSITION = "65th floor position"
    SIXTY_FIVE_FLOOR_GENDER_POSITION = "65th floor gender position"
    SIXTY_FIVE_FLOOR_DIVISION_POSITION = "65th floor division position"
    SIXTY_FIVE_FLOOR_PACE = '65th floor pace'
    SIXTY_FIVE_FLOOR_TIME = '65th floor time'
    WAVE = "wave"
    LEVEL = "level"
    URL = "url"


FIELD_NAMES = [x.value for x in RaceFields if x != RaceFields.URL]
FIELD_NAMES_FOR_SCRAPPING = [x.value for x in RaceFields]
FIELD_NAMES_AND_POS: Dict[RaceFields, int] = {}
pos = 0
for field in RaceFields:
    FIELD_NAMES_AND_POS[field] = pos
    pos += 1


def get_wave_from_bib(bib: int) -> Waves:
    for wave in Waves:
        (lower, upper) = wave.value[1]
        if lower <= bib <= upper:
            return wave
    return Waves.BLACK


def get_description_for_wave(wave: Waves) -> str:
    return wave.value[0]


def get_wave_start_time(wave: Waves) -> datetime:
    return wave.value[2]


def raw_csv_read(raw_file: Path) -> Iterable[Dict[str, Any]]:
    record = {}
    with open(raw_file, 'r') as raw_csv_file:
        reader = csv.DictReader(raw_csv_file)
        row: Dict[str, Any]
        for row in reader:
            try:
                csv_field: str
                for csv_field in FIELD_NAMES_FOR_SCRAPPING:
                    column_val = row[csv_field].strip()
                    if csv_field == RaceFields.BIB.value:
                        bib = int(column_val)
                        record[csv_field] = bib
                    elif csv_field in [
                        RaceFields.GENDER_POSITION.value,
                        RaceFields.DIVISION_POSITION.value,
                        RaceFields.OVERALL_POSITION.value,
                        RaceFields.TWENTY_FLOOR_POSITION.value,
                        RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value,
                        RaceFields.TWENTY_FLOOR_GENDER_POSITION.value,
                        RaceFields.SIXTY_FLOOR_POSITION.value,
                        RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value,
                        RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value,
                        RaceFields.AGE.value
                    ]:
                        try:
                            record[csv_field] = int(column_val)
                        except ValueError:
                            record[csv_field] = math.nan
                    elif csv_field == RaceFields.WAVE.value:
                        record[csv_field] = get_description_for_wave(get_wave_from_bib(bib)).upper()
                    elif csv_field in [
                        RaceFields.GENDER.value,
                        RaceFields.COUNTRY.value
                    ]:
                        record[csv_field] = column_val.upper()
                    elif csv_field in [
                        RaceFields.CITY.value,
                        RaceFields.STATE.value,

                    ]:
                        record[csv_field] = column_val.capitalize()
                    elif csv_field in [
                        RaceFields.SIXTY_FIVE_FLOOR_PACE.value,
                        RaceFields.SIXTY_FIVE_FLOOR_TIME.value,
                        RaceFields.TWENTY_FLOOR_PACE.value,
                        RaceFields.TWENTY_FLOOR_TIME.value,
                        RaceFields.PACE.value,
                        RaceFields.TIME.value
                    ]:
                        parts = column_val.strip().split(':')
                        for idx in range(0, len(parts)):
                            if len(parts[idx]) == 1:
                                parts[idx] = f"0{parts[idx]}"
                        if len(parts) == 2:
                            parts.insert(0, "00")
                        record[csv_field] = ":".join(parts)
                    else:
                        record[csv_field] = column_val
                if record[csv_field] in ['-', '--']:
                    record[csv_field] = ""
                yield record
            except IndexError:
                raise


def raw_copy_paste_read(raw_file: Path) -> Iterable[Dict[str, Any]]:
    """
    Read the whole RAW file, product of a manual copy and paste, return a clean version.
    Deprecation warning: You should use the raw_csv_read() method on the file produced by the scrapper.
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
                    record[RaceFields.NAME.value] = line.strip()
                elif tk_cnt == 2:
                    """
                    M 29Bib 19Kuala Lumpur, -, MYS
                    M 50Bib 3Colorado Springs, CO, USA
                    """
                    matcher = info_pattern.search(line.strip())
                    if matcher:
                        record[RaceFields.GENDER.value] = matcher.group(1).upper()
                        record[RaceFields.AGE.value] = int(matcher.group(2))
                        record[RaceFields.BIB.value] = int(matcher.group(3))
                        if record[RaceFields.BIB.value] in DNF_BIB:
                            record[
                                RaceFields.LEVEL.value] = Level.DNF.value
                        else:
                            record[RaceFields.LEVEL.value] = Level.FULL.value
                        location = matcher.group(4).split(',')
                        if len(location) == 3:
                            record[RaceFields.CITY.value] = location[0].strip().capitalize()
                            record[RaceFields.STATE.value] = location[1].strip().capitalize()
                            record[RaceFields.COUNTRY.value] = location[2].strip().upper()
                        elif len(location) == 2:
                            record[RaceFields.CITY.value] = ""
                            record[RaceFields.STATE.value] = location[0].strip().capitalize()
                            record[RaceFields.COUNTRY.value] = location[1].strip().upper()
                        elif len(location) == 1:
                            record[RaceFields.CITY.value] = ""
                            record[RaceFields.STATE.value] = ""
                            record[RaceFields.COUNTRY.value] = location[0].strip().upper()
                        else:  # This should not happen
                            record[RaceFields.CITY.value] = ""
                            record[RaceFields.STATE.value] = ""
                            record[RaceFields.COUNTRY.value] = ""
                        record[RaceFields.WAVE.value] = get_description_for_wave(get_wave_from_bib(record[RaceFields.BIB.value])).upper()
                    else:
                        matcher = info_pattern2.search(line.strip())
                        if matcher:
                            record[RaceFields.GENDER.value] = matcher.group(1).upper()
                            record[RaceFields.AGE.value] = math.nan
                            record[RaceFields.BIB.value] = int(matcher.group(2))
                            record[RaceFields.CITY.value] = ""
                            record[RaceFields.STATE.value] = ""
                            record[RaceFields.COUNTRY.value] = matcher.group(3).upper()
                        else:
                            raise ValueError(f"Regexp failed for {line.strip()}")
                elif tk_cnt == 3:
                    record[RaceFields.OVERALL_POSITION.value] = int(line.strip())
                elif tk_cnt == 4:
                    try:
                        record[RaceFields.GENDER_POSITION.value] = int(line.strip())
                    except ValueError:
                        # If GENDER is not specified the position is missing.
                        record[
                            RaceFields.GENDER_POSITION.value] = math.nan
                elif tk_cnt == 5:
                    record[RaceFields.DIVISION_POSITION.value] = int(line.strip())
                elif tk_cnt == 6:
                    parts = line.strip().split(':')
                    if len(parts) == 3:
                        record[RaceFields.PACE.value] = F"0{line.strip()}"
                    else:
                        record[RaceFields.PACE.value] = f"00:{line.strip()}"
                elif tk_cnt == 7:
                    pass  # Always MIN/MI
                elif tk_cnt == 8:
                    tk_cnt = 0
                    parts = line.strip().split(':')
                    if len(parts) == 3:
                        record[RaceFields.TIME.value] = line.strip()
                    else:
                        record[RaceFields.TIME.value] = f"00:{line.strip()}"

                    # None of the fields below are available on the first level copy and paste
                    record[RaceFields.TWENTY_FLOOR_POSITION.value] = ""
                    record[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value] = ""
                    record[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value] = ""
                    record[RaceFields.TWENTY_FLOOR_PACE.value] = ""
                    record[RaceFields.TWENTY_FLOOR_TIME.value] = ""
                    record[RaceFields.SIXTY_FLOOR_POSITION.value] = ""
                    record[RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value] = ""
                    record[RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value] = ""
                    record[RaceFields.SIXTY_FIVE_FLOOR_PACE.value] = ""
                    record[RaceFields.SIXTY_FIVE_FLOOR_TIME.value] = ""

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
    * The code remove by default the DNF runners to avoid distortion on the results.
    * Replace unknown/ nan values with the median, to make analysis easier and avoid distortions
    """
    if data_file:
        def_file = data_file
    else:
        def_file = RACE_RESULTS_FULL_LEVEL
    df = pandas.read_csv(
        def_file
    )
    for time_field in [
        RaceFields.PACE.value,
        RaceFields.TIME.value,
        RaceFields.TWENTY_FLOOR_PACE.value,
        RaceFields.TWENTY_FLOOR_TIME.value,
        RaceFields.SIXTY_FIVE_FLOOR_PACE.value,
        RaceFields.SIXTY_FIVE_FLOOR_TIME.value
    ]:
        try:
            df[time_field] = pandas.to_timedelta(df[time_field])
        except ValueError as ve:
            raise ValueError(f'{time_field}={df[time_field]}', ve)
    df['finishtimestamp'] = BASE_RACE_DATETIME + df[RaceFields.TIME.value]
    if remove_dnf:
        df.drop(df[df.level == 'DNF'].index, inplace=True)

    # Normalize Age
    median_age = df[RaceFields.AGE.value].median()
    df[RaceFields.AGE.value] = df[RaceFields.AGE.value].fillna(median_age)
    df[RaceFields.AGE.value] = df[RaceFields.AGE.value].astype(int)

    # Normalize state and city
    df.replace({RaceFields.STATE.value: {'-': ''}}, inplace=True)
    df[RaceFields.STATE.value] = df[RaceFields.STATE.value].fillna('')
    df[RaceFields.CITY.value] = df[RaceFields.CITY.value].fillna('')

    # Normalize overall position, 3 levels
    median_pos = df[RaceFields.OVERALL_POSITION.value].median()
    df[RaceFields.OVERALL_POSITION.value] = df[RaceFields.OVERALL_POSITION.value].fillna(median_pos)
    df[RaceFields.OVERALL_POSITION.value] = df[RaceFields.OVERALL_POSITION.value].astype(int)
    median_pos = df[RaceFields.TWENTY_FLOOR_POSITION.value].median()
    df[RaceFields.TWENTY_FLOOR_POSITION.value] = df[RaceFields.TWENTY_FLOOR_POSITION.value].fillna(median_pos)
    df[RaceFields.TWENTY_FLOOR_POSITION.value] = df[RaceFields.TWENTY_FLOOR_POSITION.value].astype(int)
    median_pos = df[RaceFields.SIXTY_FLOOR_POSITION.value].median()
    df[RaceFields.SIXTY_FLOOR_POSITION.value] = df[RaceFields.SIXTY_FLOOR_POSITION.value].fillna(median_pos)
    df[RaceFields.SIXTY_FLOOR_POSITION.value] = df[RaceFields.SIXTY_FLOOR_POSITION.value].astype(int)

    # Normalize gender position, 3 levels
    median_gender_pos = df[RaceFields.GENDER_POSITION.value].median()
    df[RaceFields.GENDER_POSITION.value] = df[RaceFields.GENDER_POSITION.value].fillna(median_gender_pos)
    df[RaceFields.GENDER_POSITION.value] = df[RaceFields.GENDER_POSITION.value].astype(int)

    median_gender_pos = df[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value].median()
    df[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value] = df[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value].fillna(median_gender_pos)
    df[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value] = df[RaceFields.TWENTY_FLOOR_GENDER_POSITION.value].astype(int)
    median_gender_pos = df[RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value].median()
    df[RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value] = df[RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value].fillna(median_gender_pos)
    df[RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value] = df[
        RaceFields.SIXTY_FIVE_FLOOR_GENDER_POSITION.value].astype(int)

    # Normalize age/ division position, 3 levels
    median_div_pos = df[RaceFields.DIVISION_POSITION.value].median()
    df[RaceFields.DIVISION_POSITION.value] = df[RaceFields.DIVISION_POSITION.value].fillna(median_div_pos)
    df[RaceFields.DIVISION_POSITION.value] = df[RaceFields.DIVISION_POSITION.value].astype(int)
    median_div_pos = df[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value].median()
    df[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value] = df[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value].fillna(median_div_pos)
    df[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value] = df[RaceFields.TWENTY_FLOOR_DIVISION_POSITION.value].astype(int)
    median_div_pos = df[RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value].median()
    df[RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value] = df[RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value].fillna(median_div_pos)
    df[RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value] = df[
        RaceFields.SIXTY_FIVE_FLOOR_DIVISION_POSITION.value].astype(int)

    # Normalize 65th floor pace and time
    sixty_five_floor_pace_median = df[RaceFields.SIXTY_FIVE_FLOOR_PACE.value].median()
    sixty_five_floor_time_median = df[RaceFields.SIXTY_FIVE_FLOOR_TIME.value].median()
    df[RaceFields.SIXTY_FIVE_FLOOR_PACE.value] = df[RaceFields.SIXTY_FIVE_FLOOR_PACE.value].fillna(sixty_five_floor_pace_median)
    df[RaceFields.SIXTY_FIVE_FLOOR_TIME.value] = df[RaceFields.SIXTY_FIVE_FLOOR_TIME.value].fillna(sixty_five_floor_time_median)

    # Normalize BIB and make it the index
    df[RaceFields.BIB.value] = df[RaceFields.BIB.value].astype(int)
    df.set_index(RaceFields.BIB.value, inplace=True)

    # URL was useful during scrapping, not needed for analysis
    df.drop([RaceFields.URL.value], axis=1, inplace=True)

    return df


def df_to_list_of_tuples(
        df: DataFrame,
        bibs: list[int] = None
) -> Union[Tuple | list[Tuple]]:
    """
    Take a DataFrame and return a more friendly structure to be used by a DataTable
    :param df DataFrame to convert
    :param bibs List of racing BIB to filter
    :return list of Tuple of rows, Tuple with columns
    """
    bib_as_column = df.reset_index(level=0, inplace=False)
    if not bibs:
        filtered = bib_as_column
    else:
        filtered = bib_as_column[bib_as_column[RaceFields.BIB.value].isin(bibs)]
    column_names = FIELD_NAMES
    rows = []
    for _, r in filtered.iterrows():
        ind_row: List[Any] = []
        for col in column_names:
            ind_row.append(r[col])
        tpl = tuple(ind_row)
        rows.append(tpl)

    return tuple(column_names), rows


def series_to_list_of_tuples(series: Series) -> list[Tuple]:
    dct = series.to_dict()
    rows = []
    for key, value in dct.items():
        rows.append(tuple([key, value]))
    return rows


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
    NAME = "name"
    ALPHA_2 = "alpha-2"
    ALPHA_3 = "alpha-3"
    COUNTRY_CODE = "country-code"
    ISO_3166_2 = "iso_3166-2"
    REGION = "region"
    SUB_REGION = "sub-region"
    INTERMEDIATE_REGION = "intermediate-region"
    REGION_CODE = "region-code"
    SUB_REGION_CODE = "sub-region-code"
    INTERMEDIATE_REGION_CODE = "intermediate-region-code"


COUNTRY_COLUMNS = [country.value for country in CountryColumns]


def lookup_country_by_code(df: DataFrame, three_letter_code: str) -> DataFrame:
    if not isinstance(three_letter_code, str):
        raise ValueError(f"Invalid type for three letter country code: '{three_letter_code}'")
    if len(three_letter_code) != 3:
        raise ValueError(f"Invalid three letter country code: '{three_letter_code}'")
    return df.loc[df[CountryColumns.ALPHA_3.value] == three_letter_code]


def get_times(df: DataFrame) -> DataFrame:
    return df.select_dtypes(include=['timedelta64', 'datetime64'])


def get_positions(df: DataFrame) -> DataFrame:
    return df.select_dtypes(include=['int64'])


def get_categories(df: DataFrame) -> DataFrame:
    return df.select_dtypes(include=['object'])


def beautify_race_times(time: datetime.timedelta) -> str:
    mm, ss = divmod(time.total_seconds(), 60)
    hh, mm = divmod(mm, 60)  # Ignore days part as the race doesn't last more than 24 hours
    return f"{int(hh)}:{int(mm)}:{int(ss)}"
