import datetime
import re
from enum import Enum
from pathlib import Path
from typing import Iterable, Any, Dict

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


FIELD_NAMES = ['level', 'name', 'gender', 'bib', 'state', 'country', 'wave', 'overall position',
               'gender position', 'division position', 'pace', 'time', 'city', 'age']


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


def raw_read(raw_file: Path) -> Iterable[Dict[str, Any]]:
    """
    Read the whole RAW file, return a normalized version
    Each record looks like this (copy and paste from the website):

    NAME
    SEX BIB CITY,STATE,COUNTRY
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
    :param raw_file:
    :return:
    """
    with open(raw_file, 'r') as file_data:
        tk_cnt = 0
        ln_cnt = 0
        record = {'level': "Full Course"}
        info_pattern = re.compile("([A-Z]) (\\d+)Bib (\\d*)(.*)")
        info_pattern2 = re.compile("([A-Z]+)Bib (\\d+)-, (.*)")
        for line in file_data:
            try:
                tk_cnt += 1
                ln_cnt += 1
                if tk_cnt == 1:
                    record['name'] = line.strip()
                elif tk_cnt == 2:
                    """
                    M 29Bib 19Kuala Lumpur, -, MYS
                    M 50Bib 3Colorado Springs, CO, USA
                    """
                    matcher = info_pattern.search(line.strip())
                    if matcher:
                        record['gender'] = matcher.group(1).upper()
                        record['age'] = int(matcher.group(2))
                        record['bib'] = int(matcher.group(3))
                        location = matcher.group(4).split(',')
                        if len(location) == 3:
                            record['city'] = location[0].strip().capitalize()
                            record['state'] = location[1].strip().capitalize()
                            record['country'] = location[2].strip().upper()
                        elif len(location) == 2:
                            record['city'] = ""
                            record['state'] = location[0].strip().capitalize()
                            record['country'] = location[1].strip().upper()
                        elif len(location) == 1:
                            record['city'] = ""
                            record['state'] = ""
                            record['country'] = location[0].strip().upper()
                        else:  # This should not happen
                            record['city'] = ""
                            record['state'] = ""
                            record['country'] = ""
                        record['wave'] = get_wave_from_bib(record['bib']).name.upper()
                    else:
                        matcher = info_pattern2.search(line.strip())
                        if matcher:
                            record['gender'] = matcher.group(1).upper()
                            record['age'] = -1
                            record['bib'] = int(matcher.group(2))
                            record['city'] = ""
                            record['state'] = ""
                            record['country'] = matcher.group(3).upper()
                        else:
                            raise ValueError(f"Regexp failed for {line.strip()}")
                elif tk_cnt == 3:
                    record['overall position'] = int(line.strip())
                elif tk_cnt == 4:
                    record['gender position'] = int(line.strip())
                elif tk_cnt == 5:
                    record['division position'] = int(line.strip())
                elif tk_cnt == 6:
                    record['pace'] = line.strip()
                elif tk_cnt == 7:
                    pass  # Always MIN/MI
                elif tk_cnt == 8:
                    tk_cnt = 0
                    record['time'] = line.strip()
                    yield record
            except ValueError as ve:
                raise ValueError(f"ln_cnt={ln_cnt}, tk_cnt={tk_cnt},{record}", ve)


class CourseRecords(Enum):
    Male = ('Paul Crake', 'Australia', 2003, '9:33')
    Female = ('Andrea Mayr', 'Austria', 2006, '11:23')


RACE_RESULTS = Path(__file__).parent.joinpath("results.csv")


def load_data(data_file: Path = RACE_RESULTS) -> DataFrame:
    return pandas.read_csv(data_file)