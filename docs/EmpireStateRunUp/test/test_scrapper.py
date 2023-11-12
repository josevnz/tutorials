import unittest

from empirestaterunup.scrapper import EmpireStateScrapper


class ScrapperTestCase(unittest.TestCase):
    def test_scrape(self):
        with EmpireStateScrapper(headless=False) as esc:
            self.assertIsNotNone(esc)
            source = esc.scrape()
            self.assertIsNotNone(source)
            print(source)


if __name__ == '__main__':
    unittest.main()
