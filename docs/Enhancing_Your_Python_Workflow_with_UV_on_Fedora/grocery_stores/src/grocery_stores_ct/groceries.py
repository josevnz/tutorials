"""
Displays the latest Grocery Store data from
the Connecticut Data portal.
Author: Jose Vicente Nunez <kodegeek.com@protonmail.com>
Press ctrl+q to exit the application.
"""

import httpx
from httpx import HTTPStatusError
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer
from textual import work, on
# pylint: disable=no-name-in-module
from orjson import loads

GROCERY_API_URL = "https://data.ct.gov/resource/fv3p-tf5m.json"


class GroceryStoreApp(App):
    """
    TUI application that shows grocery stores in CT
    """
    current_sorts: set = set()

    def compose(self) -> ComposeResult:
        header = Header(show_clock=True)
        yield header
        table = DataTable(id="grocery_store_table")
        yield table
        yield Footer()

    @work(exclusive=True)
    async def update_grocery_data(self) -> None:
        """
        Update the Grocery data table and provide some feedback to the user
        :return:
        """
        table = self.query_one("#grocery_store_table", DataTable)

        async with httpx.AsyncClient() as client:
            response = await client.get(GROCERY_API_URL)
            try:
                response.raise_for_status()
                groceries_data = loads(response.text)
                table.add_columns(*[key.title() for key in groceries_data[0].keys()])
                cnt = 0
                for row in groceries_data[1:]:
                    table.add_row(*(row.values()))
                    cnt += 1
                table.loading = False
                self.notify(
                    message=f"Loaded {cnt} Grocery Stores",
                    title="Data loading complete",
                    severity="information"
                )
            except HTTPStatusError:
                self.notify(
                    message=f"HTTP code={response.status_code}, message={response.text}",
                    title="Could not download grocery data",
                    severity="error"
                )

    def on_mount(self) -> None:
        """
        Render the initial component status
        :return:
        """
        table = self.query_one("#grocery_store_table", DataTable)
        table.zebra_stripes = True
        table.cursor_type = "row"
        table.loading = True
        self.notify(
            message="Retrieving information from CT Data portal",
            title="Loading data",
            severity="information",
            timeout=5
        )
        self.update_grocery_data()

    def sort_reverse(self, sort_type: str):
        """
        Determine if `sort_type` is ascending or descending.
        """
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected):
        """
        Sort rows by column header
        """
        table = event.data_table
        table.sort(
            event.column_key,
            reverse=self.sort_reverse(event.column_key.value)
        )


if __name__ == "__main__":
    app = GroceryStoreApp()
    app.title = "Grocery Stores"
    app.sub_title = "in Connecticut"
    app.run()
