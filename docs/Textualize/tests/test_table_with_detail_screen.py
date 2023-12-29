import unittest
from textual.widgets import DataTable, MarkdownViewer
from kodegeek_textualize.table_with_detail_screen import CompetitorsApp


class TableWithDetailTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_app(self):
        app = CompetitorsApp()
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:

            """
            Test the command palette
            """
            await pilot.press("ctrl+\\")
            for char in "manuela".split():
                await pilot.press(char)
            await pilot.press("enter")
            markdown_viewer = app.screen.query(MarkdownViewer).first()
            self.assertTrue(markdown_viewer.document)
            await pilot.click("#close")  # Close the new screen, pop the original one

            """
            Test the table
            """
            table = app.screen.query(DataTable).first()
            coordinate = table.cursor_coordinate
            self.assertTrue(table.is_valid_coordinate(coordinate))
            await pilot.press("enter")
            await pilot.pause()
            markdown_viewer = app.screen.query(MarkdownViewer).first()
            self.assertTrue(markdown_viewer)
            # Quit the app by pressing q
            await pilot.press("q")


if __name__ == '__main__':
    unittest.main()
