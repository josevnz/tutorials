"""
Collection of applications to display race findings
author: Jose Vicente Nunez <kodegeek.com@protonmail.com>
"""
import textwrap
from argparse import ArgumentParser
from pathlib import Path
from typing import Type

from pandas import DataFrame
from textual import on
from textual.app import ComposeResult, App, CSSPathType
from textual.containers import HorizontalScroll, VerticalScroll
from textual.driver import Driver
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Log, Label, Button, MarkdownViewer
import matplotlib.pyplot as plt

from empirestaterunup.analyze import SUMMARY_METRICS, get_5_number, count_by_age, count_by_gender, count_by_wave, \
    dt_to_sorted_dict, get_outliers, age_bins, time_bins
from empirestaterunup.data import load_data, RACE_RESULTS, to_list_of_tuples, load_country_details, \
    lookup_country_by_code, CountryColumns, RaceFields


class FiveNumberColumn(VerticalScroll):

    def __init__(self):
        super().__init__()
        self.column = None

    def compose(self) -> ComposeResult:
        yield Label(f"{self.column}:".title())
        table = DataTable(id=f'{self.column}')
        table.cursor_type = 'row'
        table.zebra_stripes = True
        yield table


class FiveNumberApp(App):
    DF: DataFrame = None
    BINDINGS = [("q", "quit_app", "Quit")]
    FIVE_NUMBER_FIELDS = ('count', 'mean', 'std', 'min', 'max', '25%', '50%', '75%')
    CSS_PATH = "five_numbers.tcss"
    TABLE_ID = ['Summary', 'Count By Age', 'Wave Bucket', 'Gender Bucket', 'Age Bucket', 'Time Bucket']
    ENABLE_COMMAND_PALETTE = False

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with HorizontalScroll():
            for table_id in FiveNumberApp.TABLE_ID:
                column = FiveNumberColumn()
                column.column = table_id
                yield column
        with HorizontalScroll():
            yield Log(id='log')
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(Log)

        summary_table = self.get_widget_by_id('Summary', expect_type=DataTable)
        columns = [x.title() for x in FiveNumberApp.FIVE_NUMBER_FIELDS]
        columns.insert(0, 'Summary')
        summary_table.add_columns(*columns)
        for metric in SUMMARY_METRICS:
            ndf = get_5_number(criteria=metric, data=FiveNumberApp.DF)
            row = [ndf[field] for field in FiveNumberApp.FIVE_NUMBER_FIELDS]
            row[0] = int(row[0])
            row.insert(0, metric.title())
            summary_table.add_row(*row)

        age_table = self.get_widget_by_id('Count By Age', expect_type=DataTable)
        adf, age_header = count_by_age(FiveNumberApp.DF)
        for column in age_header:
            age_table.add_column(column, key=column)
        age_table.add_rows(dt_to_sorted_dict(adf).items())

        gender_table = self.get_widget_by_id('Gender Bucket', expect_type=DataTable)
        gdf, gender_header = count_by_gender(FiveNumberApp.DF)
        for column in gender_header:
            gender_table.add_column(column, key=column)
        gender_table.add_rows(dt_to_sorted_dict(gdf).items())

        wave_table = self.get_widget_by_id('Wave Bucket', expect_type=DataTable)
        wdf, wave_header = count_by_wave(FiveNumberApp.DF)
        for column in wave_header:
            wave_table.add_column(column, key=column)
        wave_table.add_rows(dt_to_sorted_dict(wdf).items())

        age_bucket_table = self.get_widget_by_id('Age Bucket', expect_type=DataTable)
        age_categories, age_cols_head = age_bins(FiveNumberApp.DF)
        for column in age_cols_head:
            age_bucket_table.add_column(column, key=column)
        age_bucket_table.add_rows(dt_to_sorted_dict(age_categories.value_counts()).items())

        time_bucket_table = self.get_widget_by_id('Time Bucket', expect_type=DataTable)
        time_categories, time_cols_head = time_bins(FiveNumberApp.DF)
        for column in time_cols_head:
            time_bucket_table.add_column(column, key=column)
        time_bucket_table.add_rows(dt_to_sorted_dict(time_categories.value_counts()).items())

        log.write_line(f'\nDone processing: {RACE_RESULTS.absolute()}')

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        if table.id != 'Summary':  # Not supported yet
            table.sort(event.column_key)


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


class RunnerDetailScreen(ModalScreen):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "runner_details.tcss"

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            detail: DataTable.RowSelected = None,
            df: DataFrame = None,
            country_df: DataFrame = None
    ):
        super().__init__(name, ident, classes)
        self.detail = detail
        self.df = df
        if not country_df:
            self.country_df = load_country_details()
        else:
            self.country_df = country_df

    def compose(self) -> ComposeResult:
        table = self.detail.data_table
        row = table.get_row(self.detail.row_key)
        bibs = [row[0]]
        columns, details = to_list_of_tuples(self.df, bibs)
        self.log.info(f"Columns: {columns}")
        self.log.info(f"Details: {details}")
        row_markdown = ""
        for i in range(0, len(columns)):
            row_markdown += f"\n* **{columns[i].title()}:** {details[0][i]}"
        yield MarkdownViewer(textwrap.dedent(f"""# Runner details        
        {row_markdown}
        """))
        yield Button("Close", variant="primary", id="close")

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        self.app.pop_screen()


class OutlierColumn(VerticalScroll):

    def __init__(self):
        super().__init__()
        self.column = None

    def compose(self) -> ComposeResult:
        yield Label(f"{self.column} outliers:".title())
        table = DataTable(id=f'{self.column}_outlier')
        table.cursor_type = 'row'
        table.zebra_stripes = True
        yield table


class OutlierApp(App):
    DF: DataFrame = None
    BINDINGS = [
        ("q", "quit_app", "Quit"),
    ]
    CSS_PATH = "outliers.tcss"
    ENABLE_COMMAND_PALETTE = False

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with HorizontalScroll():
            for column_name in SUMMARY_METRICS:
                column = OutlierColumn()
                column.column = column_name
                yield column
        with HorizontalScroll():
            yield Log(id='log')
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(Log)
        for column in SUMMARY_METRICS:
            table = self.get_widget_by_id(f'{column}_outlier', expect_type=DataTable)
            columns = [x.title() for x in ['bib', column]]
            table.add_columns(*columns)
            table.add_rows(*[get_outliers(df=OutlierApp.DF, column=column).to_dict().items()])
        log.write_line(f'\nDone processing: {RACE_RESULTS.absolute()}')

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        table.sort(event.column_key)

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        runner_detail = RunnerDetailScreen(df=OutlierApp.DF, detail=event)
        self.push_screen(runner_detail)


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


class Plotter:

    def __init__(self, data_file: Path = None):
        self.df = load_data(data_file)

    def plot_age(self, gtype: str):
        if gtype == 'box':
            self.df[RaceFields.age.value].plot.box(
                title="Age details",
                grid=True,
                color={
                    "boxes": "DarkGreen",
                    "whiskers": "DarkOrange",
                    "medians": "DarkBlue",
                    "caps": "Gray",
                }
            )
        elif gtype == 'hist':
            self.df[RaceFields.age.value].plot.hist(
                title="Age details",
                grid=True,
                color='k'
            )

    def plot_country(self):
        self.df[RaceFields.country.value].value_counts().plot.barh(
            title="Participants per country",
            stacked=True
        )

    def plot_gender(self):
        self.df[RaceFields.gender.value].value_counts().plot.pie(
            title="Gender participation",
            subplots=True,
            autopct="%.2f"
        )


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


class BrowserApp(App):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [("q", "quit_app", "Quit")]
    CSS_PATH = "browser.tcss"

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            country_data: DataFrame = None,
            df: DataFrame = None
    ):
        super().__init__(driver_class, css_path, watch_css)
        if not country_data:
            self.country_data = load_country_details()
        else:
            self.country_data = country_data
        if df:
            self.df = df
        else:
            self.df = load_data()
        for three_letter_code in set(self.df[RaceFields.country.value].tolist()):
            filtered_country = lookup_country_by_code(
                df=self.country_data,
                three_letter_code=three_letter_code
            )
            country_name: str = three_letter_code
            if CountryColumns.name.value in filtered_country.columns:
                country_name = filtered_country[CountryColumns.name.value].values[0]
            filtered = self.df[RaceFields.country.value] == three_letter_code
            self.df.loc[
                filtered,
                [RaceFields.country.value]
            ] = [country_name.strip().title()]

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DataTable(id='runners')
        yield Footer()

    def on_mount(self) -> None:
        table = self.get_widget_by_id(f'runners', expect_type=DataTable)
        table.zebra_stripes = True
        table.cursor_type = 'row'
        columns_raw, rows = to_list_of_tuples(self.df)
        for column in columns_raw:
            table.add_column(column.title(), key=column)
        table.add_rows(rows)
        table.sort('overall position')

    @on(DataTable.HeaderSelected, '#runners')
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        table.sort(event.column_key)


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
