"""
Collection of applications to display race findings
author: Jose Vicente Nunez <kodegeek.com@protonmail.com>
"""
import re
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Type, Any, List

from matplotlib import colors
from pandas import DataFrame
from rich.style import Style
from rich.text import Text
from textual import on
from textual.app import ComposeResult, App, CSSPathType
from textual.command import Provider, Hit
from textual.containers import Vertical
from textual.driver import Driver
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Footer, Header, Label, Button, MarkdownViewer
import matplotlib.pyplot as plt

from empirestaterunup.analyze import SUMMARY_METRICS, get_5_number, count_by_age, count_by_gender, count_by_wave, \
    dt_to_sorted_dict, get_outliers, age_bins, time_bins, get_country_counts, better_than_median_waves, FastestFilters, \
    find_fastest
from empirestaterunup.data import load_data, df_to_list_of_tuples, load_country_details, \
    lookup_country_by_code, CountryColumns, RaceFields, series_to_list_of_tuples, beautify_race_times, \
    FIELD_NAMES_AND_POS


class FiveNumberApp(App):
    DF: DataFrame = None
    BINDINGS = [("q", "quit_app", "Quit")]
    FIVE_NUMBER_FIELDS = ('count', 'mean', 'std', 'min', 'max', '25%', '50%', '75%')
    CSS_PATH = "five_numbers.tcss"

    class NumbersTables(Enum):
        Summary = 'Summary'
        CountByAge = 'Count By Age'
        WaveBucket = 'Wave Bucket'
        GenderBucket = 'Gender Bucket'
        AgeBucket = 'Age Bucket'
        TimeBucket = 'Time Bucket'
        CountryCounts = 'Country Counts'
        BetterThanAverage = 'Better than average Wave Counts'

    ENABLE_COMMAND_PALETTE = False

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        for table_id in FiveNumberApp.NumbersTables:
            table = DataTable(id=table_id.name)
            table.cursor_type = 'row'
            table.zebra_stripes = True
            yield Vertical(
                Label(str(table_id.value)),
                table
            )
        yield Footer()

    def on_mount(self) -> None:

        wave_table = self.get_widget_by_id(id=self.NumbersTables.BetterThanAverage.name, expect_type=DataTable)
        median_run_time, wave_series = better_than_median_waves(FiveNumberApp.DF)
        wave_table.tooltip = f"Median running time: {median_run_time}"
        rows = series_to_list_of_tuples(wave_series)
        for column in ['Wave', 'Count']:
            wave_table.add_column(column, key=column)
        wave_table.add_rows(rows)

        summary_table = self.get_widget_by_id(id=self.NumbersTables.Summary.name, expect_type=DataTable)
        columns = [x.title() for x in FiveNumberApp.FIVE_NUMBER_FIELDS]
        columns.insert(0, 'Summary')
        summary_table.add_columns(*columns)
        for metric in SUMMARY_METRICS:
            ndf = get_5_number(criteria=metric, data=FiveNumberApp.DF)
            row = [ndf[field] for field in FiveNumberApp.FIVE_NUMBER_FIELDS]
            row[0] = int(row[0])
            row.insert(0, metric.title())
            summary_table.add_row(*row)

        age_table = self.get_widget_by_id(id=self.NumbersTables.CountByAge.name, expect_type=DataTable)
        adf, age_header = count_by_age(FiveNumberApp.DF)
        for column in age_header:
            age_table.add_column(column, key=column)
        age_table.add_rows(dt_to_sorted_dict(adf).items())

        gender_table = self.get_widget_by_id(id=self.NumbersTables.GenderBucket.name, expect_type=DataTable)
        gdf, gender_header = count_by_gender(FiveNumberApp.DF)
        for column in gender_header:
            gender_table.add_column(column, key=column)
        gender_table.add_rows(dt_to_sorted_dict(gdf).items())

        wave_table = self.get_widget_by_id(id=self.NumbersTables.WaveBucket.name, expect_type=DataTable)
        wdf, wave_header = count_by_wave(FiveNumberApp.DF)
        for column in wave_header:
            wave_table.add_column(column, key=column)
        wave_table.add_rows(dt_to_sorted_dict(wdf).items())

        age_bucket_table = self.get_widget_by_id(id=self.NumbersTables.AgeBucket.name, expect_type=DataTable)
        age_categories, age_cols_head = age_bins(FiveNumberApp.DF)
        for column in age_cols_head:
            age_bucket_table.add_column(column, key=column)
        age_bucket_table.add_rows(dt_to_sorted_dict(age_categories.value_counts()).items())
        age_bucket_table.tooltip = f"Median running time: {median_run_time}"

        time_bucket_table = self.get_widget_by_id(id=self.NumbersTables.TimeBucket.name, expect_type=DataTable)
        time_categories, time_cols_head = time_bins(FiveNumberApp.DF)
        for column in time_cols_head:
            time_bucket_table.add_column(column, key=column)
        time_bucket_table.add_rows(dt_to_sorted_dict(time_categories.value_counts()).items())
        time_bucket_table.tooltip = f"Median running time: {median_run_time}"

        country_counts_table = self.get_widget_by_id(id=self.NumbersTables.CountryCounts.name, expect_type=DataTable)
        countries_counts, min_country_filter, max_country_filter = get_country_counts(FiveNumberApp.DF)
        rows = series_to_list_of_tuples(countries_counts)
        for column in ['Country', 'Count']:
            country_counts_table.add_column(column, key=column)
        country_counts_table.add_rows(rows)

        self.notify(
            message=f"All metrics were calculated for {FiveNumberApp.DF.shape[0]} runners.",
            title="Race statistics status",
            severity="information"
        )

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
            row: List[Any] | None = None,
            df: DataFrame = None,
            country_df: DataFrame = None
    ):
        super().__init__(name, ident, classes)
        self.row = row
        self.df = df
        if not country_df:
            self.country_df = load_country_details()
        else:
            self.country_df = country_df

    def compose(self) -> ComposeResult:
        bib_idx = FIELD_NAMES_AND_POS[RaceFields.BIB]
        bibs = [self.row[bib_idx]]
        columns, details = df_to_list_of_tuples(self.df, bibs)
        self.log.info(f"Columns: {columns}")
        self.log.info(f"Details: {details}")
        row_markdown = ""
        position_markdown = {}
        split_markdown = {}
        for legend in ['full', '20th', '65th']:
            position_markdown[legend] = ''
            split_markdown[legend] = ''
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
        for column_name in SUMMARY_METRICS:
            table = DataTable(id=f'{column_name}_outlier')
            table.cursor_type = 'row'
            table.zebra_stripes = True
            table.tooltip = "Get runner details"
            if column_name == RaceFields.AGE.value:
                label = Label(f"{column_name} (older) outliers:".title())
            else:
                label = Label(f"{column_name} (slower) outliers:".title())
            yield Vertical(
                label,
                table
            )
        yield Footer()

    def on_mount(self) -> None:
        for column in SUMMARY_METRICS:
            table = self.get_widget_by_id(f'{column}_outlier', expect_type=DataTable)
            columns = [x.title() for x in ['bib', column]]
            table.add_columns(*columns)
            table.add_rows(*[get_outliers(df=OutlierApp.DF, column=column).to_dict().items()])

        self.notify(
            message=f"All metrics were calculated for {OutlierApp.DF.shape[0]} runners.",
            title="Outliers statistics status",
            severity="information"
        )

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        table.sort(event.column_key)

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row = table.get_row(event.row_key)
        runner_detail = RunnerDetailScreen(df=OutlierApp.DF, row=row)
        self.push_screen(runner_detail)


class Plotter:

    def __init__(self, data_file: Path = None):
        self.df = load_data(data_file)

    def plot_age(self, gtype: str):
        if gtype == 'box':
            series = self.df[RaceFields.AGE.value]
            fig, ax = plt.subplots(layout='constrained')
            ax.boxplot(series)
            ax.set_title("Age details")
            ax.set_ylabel('Years')
            ax.set_xlabel('Age')
            ax.grid(True)
        elif gtype == 'hist':
            series = self.df[RaceFields.AGE.value]
            fig, ax = plt.subplots(layout='constrained')
            n, bins, patches = ax.hist(series, density=False, alpha=0.75)
            # Borrowed coloring recipe for histogram from Matplotlib documentation
            fractions = n / n.max()
            norm = colors.Normalize(fractions.min(), fractions.max())
            for frac, patch in zip(fractions, patches):
                color = plt.cm.viridis(norm(frac))
                patch.set_facecolor(color)
            ax.set_xlabel('Age [years]')
            ax.set_ylabel('Count')
            ax.set_title(f'Age details for {series.shape[0]} racers\nBins={len(bins)}')
            ax.grid(True)

    def plot_country(self):
        fastest = find_fastest(self.df, FastestFilters.Country)
        series = self.df[RaceFields.COUNTRY.value].value_counts()
        series.sort_values(inplace=True)
        fig, ax = plt.subplots(layout='constrained')
        rects = ax.barh(series.keys(), series.values)
        ax.bar_label(
            rects,
            [f"{country_count} - {fastest[country]['name']}({beautify_race_times(fastest[country]['time'])})" for
             country, country_count in series.items()],
            padding=1,
            color='black'
        )
        ax.set_title = "Participants per country"
        ax.set_stacked = True
        ax.set_ylabel('Country')
        ax.set_xlabel('Count per country')

    def plot_gender(self):
        series = self.df[RaceFields.GENDER.value].value_counts()
        fig, ax = plt.subplots(layout='constrained')
        wedges, texts, auto_texts = ax.pie(
            series.values,
            labels=series.keys(),
            autopct="%%%.2f",
            shadow=True,
            startangle=90,
            explode=(0.1, 0, 0)
        )
        ax.set_title = "Gender participation"
        ax.set_xlabel('Gender distribution')
        # Legend with the fastest runners by gender
        fastest = find_fastest(self.df, FastestFilters.Gender)
        fastest_legend = [f"{fastest[gender]['name']} - {beautify_race_times(fastest[gender]['time'])}" for gender in
                          series.keys()]
        ax.legend(wedges, fastest_legend,
                  title="Fastest by gender",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))


class BrowserAppCommand(Provider):

    def __init__(self, screen: Screen[Any], match_style: Style | None = None):
        super().__init__(screen, match_style)
        self.table = None

    async def startup(self) -> None:
        browser_app = self.app
        self.table = browser_app.query(DataTable).first()

    async def search(self, query: str) -> Hit:
        matcher = self.matcher(query)
        browser_app = self.screen.app
        assert isinstance(browser_app, BrowserApp)
        df = browser_app.df
        for row_key in self.table.rows:
            row = self.table.get_row(row_key)
            for name in [RaceFields.BIB, RaceFields.NAME, RaceFields.OVERALL_POSITION]:
                idx = FIELD_NAMES_AND_POS[name]
                searchable = str(row[idx])
                score = matcher.match(searchable)
                if score > 0:
                    details = f"{searchable} - {name.value}"
                    runner_detail = RunnerDetailScreen(df=df, row=row)
                    yield Hit(
                        score,
                        matcher.highlight(f"{searchable}"),
                        partial(browser_app.push_screen, runner_detail),
                        help=f"{details}"
                    )


class BrowserApp(App):
    BINDINGS = [("q", "quit_app", "Quit")]
    CSS_PATH = "browser.tcss"
    ENABLE_COMMAND_PALETTE = True
    COMMANDS = App.COMMANDS | {BrowserAppCommand}

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
        for three_letter_code in set(self.df[RaceFields.COUNTRY.value].tolist()):
            filtered_country = lookup_country_by_code(
                df=self.country_data,
                three_letter_code=three_letter_code
            )
            country_name: str = three_letter_code
            if CountryColumns.NAME.value in filtered_country.columns:
                country_name = filtered_country[CountryColumns.NAME.value].values[0]
            filtered = self.df[RaceFields.COUNTRY.value] == three_letter_code
            self.df.loc[
                filtered,
                [RaceFields.COUNTRY.value]
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
        columns_raw, rows = df_to_list_of_tuples(self.df)
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

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row = table.get_row(event.row_key)
        runner_detail = RunnerDetailScreen(df=self.df, row=row)
        self.push_screen(runner_detail)
