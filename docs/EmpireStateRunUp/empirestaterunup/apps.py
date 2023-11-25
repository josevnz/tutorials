"""
Collection of applications to display race findings
author: Jose Vicente Nunez <kodegeek.com@protonmail.com>
"""
import csv
import re
from pathlib import Path
from typing import Type, Union, Dict, Any

from pandas import DataFrame
from rich.text import Text
from textual import on, work
from textual.app import ComposeResult, App, CSSPathType
from textual.containers import HorizontalScroll, VerticalScroll
from textual.driver import Driver
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Log, Label, Button, MarkdownViewer, ProgressBar
from textual.worker import Worker, WorkerState

from empirestaterunup.analyze import SUMMARY_METRICS, get_5_number, count_by_age, count_by_gender, count_by_wave, \
    dt_to_sorted_dict, get_outliers, age_bins, time_bins
from empirestaterunup.data import load_data, to_list_of_tuples, load_country_details, \
    lookup_country_by_code, CountryColumns, RaceFields, RACE_RESULTS_FULL_LEVEL, FIELD_NAMES
from empirestaterunup.scrapper import RacerLinksScrapper, RacerDetailsScrapper


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

        log.write_line(f'\nDone processing: {RACE_RESULTS_FULL_LEVEL.absolute()}')

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        if table.id != 'Summary':  # Not supported yet
            table.sort(event.column_key)


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
        position_markdown = {
            'full': '',
            '20th': '',
            '65th': ''
        }
        split_markdown = {
            'full': '',
            '20th': '',
            '65th': ''
        }
        for i in range(0, len(columns)):
            column = columns[i]
            detail = details[0][i]
            if re.search('pace|time', column):
                if re.search('20th', column):
                    split_markdown['20th'] += f"\n* **{column.title()}:** {detail}"
                elif re.search('65th', column):
                    split_markdown['65th'] += f"\n* **{column.title()}:** {detail}"
                else:
                    split_markdown['full'] += f"\n* **{column.title()}:** {detail}"
            elif re.search('position', column):
                if re.search('20th', column):
                    position_markdown['20th'] += f"\n* **{column.title()}:** {detail}"
                elif re.search('65th', column):
                    position_markdown['65th'] += f"\n* **{column.title()}:** {detail}"
                else:
                    position_markdown['full'] += f"\n* **{column.title()}:** {detail}"
            elif re.search('url|bib', column):
                pass  # Skip uninteresting columns
            else:
                row_markdown += f"\n* **{column.title()}:** {detail}"
        yield MarkdownViewer(f"""# Full Course Race details     
## Runner BIO (BIB: {bibs[0]})
{row_markdown}
## Positions
### 20th floor        
{position_markdown['20th']}
### 65th floor        
{position_markdown['65th']}
### Full course        
{position_markdown['full']}                
## Race time split   
### 20th floor        
{split_markdown['20th']}
### 65th floor        
{split_markdown['65th']}
### Full course        
{split_markdown['full']}         
        """)
        btn = Button("Close", variant="primary", id="close")
        btn.tooltip = "Back to main screen"
        yield btn

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
        table.tooltip = "Get runner details"
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
        log.write_line(f'\nDone processing: {RACE_RESULTS_FULL_LEVEL.absolute()}')

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        table.sort(event.column_key)

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        runner_detail = RunnerDetailScreen(df=OutlierApp.DF, detail=event)
        self.push_screen(runner_detail)


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
        for number, row in enumerate(rows[0:], start=1):
            label = Text(str(number), style="#B0FC38 italic")
            table.add_row(*row, label=label)
        table.sort('overall position')

    @on(DataTable.HeaderSelected, '#runners')
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        table.sort(event.column_key)


class ScrapperApp(App):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [("q", "quit_app", "Quit")]
    CSS_PATH = "scrapper.tcss"

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            report_file: Union[Path | None] = None
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.racers: Union[Dict[str, Any] | None] = None
        self.report_file: Union[Path | None] = report_file

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ProgressBar(show_eta=False, id="progress")
        yield VerticalScroll(id="details")
        yield Footer()

    @work(exclusive=True)
    async def get_links(self):
        details = self.query_one("#details", VerticalScroll)
        with RacerLinksScrapper(headless=True, debug=False) as link_scrapper:
            total = len(link_scrapper.racers)
            progres = self.query_one("#progress", ProgressBar)
            progres.total = total
            details.loading = False
            await details.mount(Label(f"Got {total} racer results"))
            self.racers = link_scrapper.racers

    @work(exclusive=True)
    async def get_racer_details(self):
        progres = self.query_one("#progress", ProgressBar)
        details = self.query_one("#details", VerticalScroll)
        with open(self.report_file, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for bib in self.racers:
                url = self.racers[bib][RaceFields.url.value]
                await details.mount(Label(f"Processing BIB: {bib}, will fetch: {url}"))
                with RacerDetailsScrapper(racer=self.racers[bib], debug_level=0) as rds:
                    try:
                        position = self.racers[bib][RaceFields.overall_position.value]
                        name = self.racers[bib][RaceFields.name.value]
                        writer.writerow(rds.racer)
                        await details.mount(Label(f"Wrote: name={name}, position={position}, {rds.racer}"))
                        progres.advance(1)
                    except ValueError as ve:
                        raise ValueError(f"row={rds.racer}", ve)

    async def on_mount(self) -> None:
        details = self.query_one("#details", VerticalScroll)
        if not self.report_file.parent.exists():
            self.report_file.parent.mkdir(exist_ok=True)
        self.run_worker(details.mount(Label(f"Saving results to {self.report_file}")))
        self.get_links()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        self.log(f"Got an event: {event}")
        if event.worker.name == "get_links" and event.worker.state == WorkerState.SUCCESS:
            self.log(f"Launching: get_racer_details()")
            self.get_racer_details()
