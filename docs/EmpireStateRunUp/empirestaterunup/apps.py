
from textual.app import ComposeResult, App
from textual.widgets import DataTable, Footer, Header, Log, Rule

from empirestaterunup.analyze import SUMMARY_METRICS, get_5_number, count_by_age, count_by_gender, count_by_wave, \
    dt_to_sorted_dict
from empirestaterunup.data import load_data, RACE_RESULTS


class FiveNumberApp(App):
    DF = None
    BINDINGS = [("q", "quit_app", "Quit")]
    FIVE_NUMBER_FIELDS = ('count', 'mean', 'std', 'min', 'max', '25%', '50%', '75%')

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DataTable(id='summary')
        yield Rule()
        yield DataTable(id='age_cnt')
        yield Rule()
        yield DataTable(id='wave_cnt')
        yield Rule()
        yield DataTable(id='gender_cnt')
        yield Rule()
        yield Log(id='log')
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(Log)
        summary_table = self.get_widget_by_id('summary', expect_type=DataTable)
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

        age_table = self.get_widget_by_id('age_cnt', expect_type=DataTable)
        age_table.zebra_stripes = True
        age_table.cursor_type = 'row'
        adf, age_header = count_by_age(FiveNumberApp.DF)
        age_table.add_columns(*age_header)
        age_table.add_rows(dt_to_sorted_dict(adf).items())

        gender_table = self.get_widget_by_id('gender_cnt', expect_type=DataTable)
        gender_table.zebra_stripes = True
        gender_table.cursor_type = 'row'
        gdf, gender_header = count_by_gender(FiveNumberApp.DF)
        gender_table.add_columns(*gender_header)
        gender_table.add_rows(dt_to_sorted_dict(gdf).items())

        wave_table = self.get_widget_by_id('wave_cnt', expect_type=DataTable)
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
