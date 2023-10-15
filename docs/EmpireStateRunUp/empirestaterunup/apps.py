from argparse import ArgumentParser
from textual.app import ComposeResult, App
from textual.widgets import DataTable, Footer, Header, Log, Rule, Label
import matplotlib.pyplot as plt
from empirestaterunup.analyze import SUMMARY_METRICS, get_5_number, count_by_age, count_by_gender, count_by_wave, \
    dt_to_sorted_dict, get_outliers
from empirestaterunup.data import load_data, RACE_RESULTS


class FiveNumberApp(App):
    DF = None
    BINDINGS = [("q", "quit_app", "Quit")]
    FIVE_NUMBER_FIELDS = ('count', 'mean', 'std', 'min', 'max', '25%', '50%', '75%')
    TABLE_ID = ['Summary', 'Age Count', 'Wave Count', 'Gender Count']

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        for table_id in FiveNumberApp.TABLE_ID:
            yield Label(table_id.title())
            yield DataTable(id=table_id)
            yield Rule()
        yield Log(id='log')
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(Log)
        summary_table = self.get_widget_by_id('Summary', expect_type=DataTable)
        summary_table.zebra_stripes = True
        summary_table.cursor_type = 'row'
        columns = [x.title() for x in FiveNumberApp.FIVE_NUMBER_FIELDS]
        columns.insert(0, 'Summary')
        summary_table.add_columns(*columns)
        for metric in SUMMARY_METRICS:
            ndf = get_5_number(criteria=metric, data=FiveNumberApp.DF)
            row = [ndf[field] for field in FiveNumberApp.FIVE_NUMBER_FIELDS]
            row[0] = int(row[0])
            row.insert(0, metric.title())
            summary_table.add_row(*row)

        age_table = self.get_widget_by_id('Age Count', expect_type=DataTable)
        age_table.zebra_stripes = True
        age_table.cursor_type = 'row'
        adf, age_header = count_by_age(FiveNumberApp.DF)
        age_table.add_columns(*age_header)
        age_table.add_rows(dt_to_sorted_dict(adf).items())

        gender_table = self.get_widget_by_id('Gender Count', expect_type=DataTable)
        gender_table.zebra_stripes = True
        gender_table.cursor_type = 'row'
        gdf, gender_header = count_by_gender(FiveNumberApp.DF)
        gender_table.add_columns(*gender_header)
        gender_table.add_rows(dt_to_sorted_dict(gdf).items())

        wave_table = self.get_widget_by_id('Wave Count', expect_type=DataTable)
        wave_table.zebra_stripes = True
        wave_table.cursor_type = 'row'
        wdf, wave_header = count_by_wave(FiveNumberApp.DF)
        wave_table.add_columns(*wave_header)
        wave_table.add_rows(dt_to_sorted_dict(wdf).items())

        log.write_line(f'\nDone processing: {RACE_RESULTS.absolute()}')


def run_5_number():
    app = FiveNumberApp()
    FiveNumberApp.DF = load_data()
    app.title = f"Five Number Summary".title()
    app.sub_title = f"Runners: {FiveNumberApp.DF.shape[0]}"
    app.run()


class OutlierApp(App):
    DF = None
    BINDINGS = [("q", "quit_app", "Quit")]

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        for column in SUMMARY_METRICS:
            yield Label(f"{column} outliers".title())
            yield DataTable(id=f'{column}_outlier')
            yield Rule()
        yield Log(id='log')
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(Log)
        for column in SUMMARY_METRICS:
            table = self.get_widget_by_id(f'{column}_outlier', expect_type=DataTable)
            columns = [x.title() for x in ['bib', column]]
            table.add_columns(*columns)
            table.cursor_type = 'row'
            table.zebra_stripes = True
            table.add_rows(*[get_outliers(df=OutlierApp.DF, column=column).to_dict().items()])

        log.write_line(f'\nDone processing: {RACE_RESULTS.absolute()}')


def run_outlier():
    app = OutlierApp()
    OutlierApp.DF = load_data()
    app.title = f"Outliers Summary".title()
    app.sub_title = f"Runners: {OutlierApp.DF.shape[0]}"
    app.run()


class Plotter:

    def __init__(self):
        self.df = load_data()

    def plot_age(self, gtype: str):
        self.df.age.plot(kind=gtype, title="Age details", grid=True)


def plot_age():
    parser = ArgumentParser(description="Different plots for ESRU")
    parser.add_argument(
        "--type",
        action="store",
        default="box",
        choices=["box", "hist"],
        help="Plot type"
    )
    options = parser.parse_args()
    pzs = Plotter()
    pzs.plot_age(options.type)
    plt.show()
