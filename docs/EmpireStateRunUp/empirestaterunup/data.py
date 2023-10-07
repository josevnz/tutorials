import re
from pathlib import Path
from typing import Iterable, Any, Dict

from empirestaterunup import Waves


def get_wave_from_bib(bib: int) -> Waves:
    for wave in Waves:
        (lower, upper) = wave.value
        if lower <= bib <= upper:
            return wave
    return Waves.Black


def quick_read(raw_file: Path, verbose: bool = False) -> Iterable[Dict[str, Any]]:
    """
    Read the whole file, return a normalized version
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
    :param verbose:
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
