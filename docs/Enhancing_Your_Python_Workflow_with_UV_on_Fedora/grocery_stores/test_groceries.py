"""
Unit tests for Groceries application
https://textual.textualize.io/guide/testing/
"""

from groceries import GroceryStoreApp


async def test_groceries_app():
    groceries_app = GroceryStoreApp()
    async with groceries_app.run_test() as pilot:
        await pilot.press("ctrl+q")  # Quit
