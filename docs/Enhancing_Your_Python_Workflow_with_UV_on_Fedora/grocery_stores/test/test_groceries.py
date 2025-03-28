"""
Unit tests for Groceries application
https://textual.textualize.io/guide/testing/
"""
import pytest

from grocery_stores_ct.groceries import GroceryStoreApp


@pytest.mark.asyncio
async def test_groceries_app():
    groceries_app = GroceryStoreApp()
    async with groceries_app.run_test() as pilot:
        await pilot.press("ctrl+q")  # Quit
