#!/usr/bin/env python
"""
Author: Jose Vicente Nunez
"""
from textual import on
from textual.app import ComposeResult, App
from textual.screen import ModalScreen
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
            row_selected: DataTable.RowSelected = None
    ):
        super().__init__(name, ident, classes)
        self.row_selected = row_selected

    def compose(self) -> ComposeResult:
        self.log.info(f"Details: {self.row_selected}")
        table = self.row_selected.data_table
        row_key = self.row_selected.row_key
        row = table.get_row(row_key)
        columns = MY_DATA[0]
        row_markdown = "\n"
        for i in range(0, len(columns)):
            row_markdown += f"* **{columns[i].title()}:** {row[i]}\n"
        yield MarkdownViewer(f"""## User details:
        {row_markdown}
        """)
        button = Button("Close", variant="primary", id="close")
        button.tooltip = "Go back to main screen"
        yield button

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        self.app.pop_screen()


class CompetitorsApp(App):
    BINDINGS = [
        ("q", "quit_app", "Quit"),
    ]
    CSS_PATH = "competitors_app.tcss"
    ENABLE_COMMAND_PALETTE = False

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        table = DataTable(id=f'table_myapp')
        table.cursor_type = 'row'
        table.zebra_stripes = True
        table.loading = True
        yield table
        yield Footer()

    def on_mount(self) -> None:
        table = self.get_widget_by_id(f'table_myapp', expect_type=DataTable)
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
        runner_detail = DetailScreen(row_selected=event)
        self.push_screen(runner_detail)


def main():
    app = CompetitorsApp()
    app.title = f"Summary".title()
    app.sub_title = f"{len(MY_DATA)} users"
    app.run()


if __name__ == "__main__":
    main()
