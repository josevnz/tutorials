import logging
import pprint
import unittest

from empirestaterunup.scrapper import RacerLinksScrapper

logger = logging.getLogger('selenium')
logger.setLevel(logging.DEBUG)


class RacerLinksScrapperTestCase(unittest.TestCase):
    def test_navigate(self):
        with RacerLinksScrapper(headless=True) as esc:
            self.assertIsNotNone(esc)
            links = esc.get_all_links()
            pprint.pprint(links)
            self.assertEqual(377, len(links))


if __name__ == '__main__':
    unittest.main()
