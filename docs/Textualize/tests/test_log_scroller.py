import unittest
from textual.widgets import Log, Button
from kodegeek_textualize.log_scroller import OsApp


class LogScrollerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_log_scroller(self):
        app = OsApp()
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            # Execute the default commands
            await pilot.click(Button)
            await pilot.pause()
            event_log = app.screen.query(Log).first()  # We pushed the screen, query nodes from there
            self.assertTrue(event_log.lines)
            await pilot.click("#close")  # Close the new screen, pop the original one
            await pilot.press("q")  # Quit the app by pressing q


if __name__ == '__main__':
    unittest.main()
