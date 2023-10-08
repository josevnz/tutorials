from pandas import DataFrame
from textual.app import App
from textual.widgets import DataTable, TabbedContent, TabPane, Footer, Log

from empirestaterunup.data import load_data


class FiveNumberSummaryApp(App):
    df: DataFrame = None

    def compose(self):
        with TabbedContent():
            with TabPane("Time"):
                yield DataTable(id='time_5')
            with TabPane("Sex"):
                yield DataTable(id='sex_5')
            with TabPane("Age"):
                yield DataTable(id='age_5')
            with TabPane("Logs"):
                yield Log(id='log')
        yield Footer()

    def on_mount(self):
        self.df = load_data()
        age5_tbl = self.get_widget_by_id('age_5')

    def on_ready(self):
        log: Log = self.query_one(Log)
        log.write_line(f"Loaded: {self.df.count(axis='rows')}")


def run_5_number():
    app = FiveNumberSummaryApp()
    app.title = "5-number summary"
    app.run()
