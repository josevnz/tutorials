import logging
import unittest

from empirestaterunup.scrapper import EmpireStateScrapper

logger = logging.getLogger('selenium')
logger.setLevel(logging.DEBUG)


class ScrapperTestCase(unittest.TestCase):
    def test_navigate(self):
        with EmpireStateScrapper(headless=True) as esc:
            self.assertIsNotNone(esc)
            links = esc.navigate()
            print(links)


if __name__ == '__main__':
    unittest.main()
