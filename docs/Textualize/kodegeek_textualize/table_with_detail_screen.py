#!/usr/bin/env python
"""
Author: Jose Vicente Nunez
"""
from functools import partial
from typing import Any, List

from rich.style import Style
from textual import on
from textual.app import ComposeResult, App
from textual.command import Provider, Hit
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Footer, Header, Button, MarkdownViewer

MY_DATA = [
    ("level", "name", "gender", "country", "age"),
    ("Green", "Wai", "M", "MYS", 22),
    ("Red", "Ryoji", "M", "JPN", 30),
    ("Purple", "Fabio", "M", "ITA", 99),
    ("Blue", "Manuela", "F", "VEN", 25)
]


class DetailScreen(ModalScreen):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "details_screen.tcss"

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            row: List[Any] | None = None,
    ):
        super().__init__(name, ident, classes)
        self.row: List[Any] = row

    def compose(self) -> ComposeResult:
        self.log.info(f"Details: {self.row}")
        columns = MY_DATA[0]
        row_markdown = "\n"
        for i in range(0, len(columns)):
            row_markdown += f"* **{columns[i].title()}:** {self.row[i]}\n"
        yield MarkdownViewer(f"""## User details:
        {row_markdown}
        """)
        button = Button("Close", variant="primary", id="close")
        button.tooltip = "Go back to main screen"
        yield button

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        self.app.pop_screen()


class CustomCommand(Provider):

    def __init__(self, screen: Screen[Any], match_style: Style | None = None):
        super().__init__(screen, match_style)
        self.table = None

    async def startup(self) -> None:
        my_app = self.app
        my_app.log.info(f"Loaded provider: CustomCommand")
        self.table = my_app.query(DataTable).first()

    async def search(self, query: str) -> Hit:
        matcher = self.matcher(query)

        my_app = self.screen.app
        assert isinstance(my_app, CompetitorsApp)

        my_app.log.info(f"Got query: {query}")
        for row_key in self.table.rows:
            row = self.table.get_row(row_key)
            my_app.log.info(f"Searching {row}")
            searchable = row[1]
            score = matcher.match(searchable)
            if score > 0:
                runner_detail = DetailScreen(row=row)
                yield Hit(
                    score,
                    matcher.highlight(f"{searchable}"),
                    partial(my_app.show_detail, runner_detail),
                    help=f"Show details about {searchable}"
                )


class CompetitorsApp(App):
    BINDINGS = [
        ("q", "quit_app", "Quit"),
    ]
    CSS_PATH = "competitors_app.tcss"
    # Enable the command palette, to add our custom filter commands
    ENABLE_COMMAND_PALETTE = True
    # Add the default commands and the TablePopulateProvider to get a row directly by name
    COMMANDS = App.COMMANDS | {CustomCommand}

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        table = DataTable(id=f'competitors_table')
        table.cursor_type = 'row'
        table.zebra_stripes = True
        table.loading = True
        yield table
        yield Footer()

    def on_mount(self) -> None:
        table = self.get_widget_by_id(f'competitors_table', expect_type=DataTable)
        columns = [x.title() for x in MY_DATA[0]]
        table.add_columns(*columns)
        table.add_rows(MY_DATA[1:])
        table.loading = False
        table.tooltip = "Select a row to get more details"

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        table = event.data_table
        table.sort(event.column_key)

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row = table.get_row(event.row_key)
        runner_detail = DetailScreen(row=row)
        self.show_detail(runner_detail)

    def show_detail(self, detailScreen: DetailScreen):
        self.push_screen(detailScreen)


def main():
    app = CompetitorsApp()
    app.title = f"Summary".title()
    app.sub_title = f"{len(MY_DATA)} users"
    app.run()


if __name__ == "__main__":
    main()
