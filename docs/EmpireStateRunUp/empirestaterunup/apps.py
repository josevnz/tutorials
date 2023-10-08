from textual.app import ComposeResult, App
from textual.widgets import DataTable, Footer, Header, Log

from empirestaterunup.analyze import SUMMARY_METRICS, get_5_number
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

        log.write_line(f'\nDone processing: {RACE_RESULTS.absolute()}')


def run_5_number():
    app = FiveNumberApp()
    FiveNumberApp.DF = load_data()
    app.title = f"Five Number Summary".title()
    app.sub_title = f"Runners: {FiveNumberApp.DF.shape[0]}"
    app.run()


if __name__ == "__main__":
    run_5_number()
