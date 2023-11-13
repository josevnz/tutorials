import logging
import unittest

from empirestaterunup.scrapper import EmpireStateScrapper

logger = logging.getLogger('selenium')
logger.setLevel(logging.DEBUG)


class ScrapperTestCase(unittest.TestCase):
    def test_scrapper(self):
        with EmpireStateScrapper(headless=True) as esc:
            self.assertIsNotNone(esc)
            print(esc.get_race_links())
            while esc.click_next_button():
                print(esc.get_race_links())


if __name__ == '__main__':
    unittest.main()
