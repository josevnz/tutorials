#!/usr/bin/env python
"""
I wrote this script to normalize the data results from the 'Empire State Building Run-Up', October 4, 2023.
The race results website doesn't offer an export option and quite honestly writing a web scrapper seemed to be overkill.
So just coping and pasting the 8 pages of results took less time, the data normalizer is quite simple and was used
to generate a nicer CSV file.

https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Results

Author Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import csv
from pathlib import Path
from argparse import ArgumentParser
import logging

from empirestaterunup.data import raw_read, FIELD_NAMES

logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)


def main():
    PARSER = ArgumentParser(description=__doc__)
    PARSER.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Enable verbose mode'
    )
    PARSER.add_argument(
        '--rawfile',
        type=Path,
        required=True,
        help='Raw file'
    )
    PARSER.add_argument(
        'reportfile',
        type=Path,
        help='New report file'
    )
    OPTIONS = PARSER.parse_args()
    try:
        with open(OPTIONS.reportfile, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            writer.writeheader()
            for row in raw_read(OPTIONS.rawfile):
                try:
                    writer.writerow(row)
                    if OPTIONS.verbose:
                        logging.warning(row)
                except ValueError as ve:
                    raise ValueError(f"row={row}", ve)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
