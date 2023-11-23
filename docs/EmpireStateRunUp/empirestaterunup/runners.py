#!/usr/bin/env python
"""
I wrote this script to normalize the data results from the 'Empire State Building Run-Up', October 4, 2023.
The race results website doesn't offer an export option and quite honestly writing a web scrapper seemed to be overkill.
So just coping and pasting the 8 pages of results took less time, the data normalizer is quite simple and was used
to generate a nicer CSV file.

Author Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import csv
from pathlib import Path
from argparse import ArgumentParser
import logging

from matplotlib import pyplot as plt

from empirestaterunup.apps import FiveNumberApp, OutlierApp, Plotter, BrowserApp
from empirestaterunup.data import raw_copy_paste_read, FIELD_NAMES, load_data, load_country_details, RaceFields, \
    raw_csv_read
from empirestaterunup.scrapper import RacerLinksScrapper, RacerDetailsScrapper

logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO)


def run_raw_cleaner():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Enable verbose mode'
    )
    parser.add_argument(
        '--raw_file',
        type=Path,
        required=True,
        help='Raw file'
    )
    parser.add_argument(
        'report_file',
        type=Path,
        help='New report file'
    )
    OPTIONS = parser.parse_args()
    try:
        with open(OPTIONS.report_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            writer.writeheader()
            for row in raw_copy_paste_read(OPTIONS.raw_file):
                try:
                    writer.writerow(row)
                    if OPTIONS.verbose:
                        logging.warning(row)
                except ValueError as ve:
                    raise ValueError(f"row={row}", ve)
    except KeyboardInterrupt:
        pass


def run_5_number():
    parser = ArgumentParser(description="5 key indicators report")
    parser.add_argument(
        "results",
        action="store",
        type=Path,
        nargs="*",
        help="Race results."
    )
    options = parser.parse_args()
    app = FiveNumberApp()
    if options.results:
        FiveNumberApp.DF = load_data(options.results[0])
    else:
        FiveNumberApp.DF = load_data()
    app.title = f"Five Number Summary".title()
    app.sub_title = f"Runners: {FiveNumberApp.DF.shape[0]}"
    app.run()


def run_outlier():
    parser = ArgumentParser(description="Show race outliers")
    parser.add_argument(
        "results",
        action="store",
        type=Path,
        nargs="*",
        help="Race results."
    )
    options = parser.parse_args()
    if options.results:
        OutlierApp.DF = load_data(options.results[0])
    else:
        OutlierApp.DF = load_data()
    app = OutlierApp()
    app.title = f"Outliers Summary".title()
    app.sub_title = f"Runners: {OutlierApp.DF.shape[0]}"
    app.run()


def simple_plot():
    parser = ArgumentParser(description="Different Age plots for Empire State RunUp")
    parser.add_argument(
        "--type",
        action="store",
        default="box",
        choices=["box", "hist"],
        help="Plot type. Not all reports honor this choice (like country)"
    )
    parser.add_argument(
        "--report",
        action="store",
        default="age",
        choices=["age", "country", "gender"],
        help="Report type"
    )
    parser.add_argument(
        "results",
        action="store",
        type=Path,
        nargs="*",
        help="Race results."
    )
    options = parser.parse_args()
    if options.results:
        pzs = Plotter(options.results[0])
    else:
        pzs = Plotter()
    if options.report == 'age':
        pzs.plot_age(options.type)
    elif options.report == 'country':
        pzs.plot_country()
    elif options.report == 'gender':
        pzs.plot_gender()
    plt.show()


def run_browser():
    parser = ArgumentParser(description="Browse user results")
    parser.add_argument(
        "--country",
        action="store",
        type=Path,
        required=False,
        help="Country details"
    )
    parser.add_argument(
        "results",
        action="store",
        type=Path,
        nargs="*",
        help="Race results."
    )
    options = parser.parse_args()
    df = None
    country_df = None
    if options.results:
        df = load_data(options.results[0])
    if options.country:
        country_df = load_country_details(options.country)
    app = BrowserApp(
        df=df,
        country_data=country_df
    )
    app.title = f"Race runners".title()
    app.sub_title = f"Browse details: {app.df.shape[0]}"
    app.run()


def run_scrapper():
    parser = ArgumentParser(description="Scrapper Website")
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Enable verbose mode'
    )
    parser.add_argument(
        "report_file",
        action="store",
        type=Path,
        help="Location of the final scrapping results"
    )
    options = parser.parse_args()
    report_file = Path(options.report_file)
    logging.info("Saving results to %s", report_file)
    with RacerLinksScrapper(headless=True, debug=False) as link_scrapper:
        logging.info("Got %s racer results", len(link_scrapper.racers))
        if not report_file.parent.exists():
            report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for bib in link_scrapper.racers:
                url = link_scrapper.racers[bib][RaceFields.url.value]
                logging.info("Processing BIB: %s, will fetch: %s", bib, url)
                with RacerDetailsScrapper(racer=link_scrapper.racers[bib], debug_level=0) as rds:
                    try:
                        position = link_scrapper.racers[bib][RaceFields.overall_position.value]
                        name = link_scrapper.racers[bib][RaceFields.name.value]
                        writer.writerow(rds.racer)
                        logging.info("Wrote: name=%s, position=%s", name, position)
                        if options.verbose:
                            logging.warning(rds.racer)
                    except ValueError as ve:
                        raise ValueError(f"row={rds.racer}", ve)


def run_csv_cleaner():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Enable verbose mode'
    )
    parser.add_argument(
        '--raw_file',
        type=Path,
        required=True,
        help='Raw file'
    )
    parser.add_argument(
        'report_file',
        type=Path,
        help='New report file'
    )
    OPTIONS = parser.parse_args()
    try:
        with open(OPTIONS.report_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            writer.writeheader()
            for row in raw_csv_read(OPTIONS.raw_file):
                try:
                    writer.writerow(row)
                    if OPTIONS.verbose:
                        logging.warning(row)
                except ValueError as ve:
                    raise ValueError(f"row={row}", ve)
    except KeyboardInterrupt:
        pass
