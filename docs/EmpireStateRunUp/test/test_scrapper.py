import logging
import pprint
import unittest

from empirestaterunup.scrapper import RacerLinksScrapper, RacerDetailsScrapper

logger = logging.getLogger('selenium')
logger.setLevel(logging.DEBUG)


class RacerLinksScrapperTestCase(unittest.TestCase):
    def test_navigate(self):
        with RacerLinksScrapper(headless=True) as esc:
            self.assertIsNotNone(esc)
            pprint.pprint(esc.links)
            self.assertEqual(377, len(esc.links))

    def test_runner_detail(self):
        links = {
            'Aaron Field': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/368',
            'Al Bueno': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/609',
            'Alan Lynch': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/57',
            'Alejandra Sanchez': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/40',
            'Alessandro Manrique': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/562'
        }
        for name in links:
            with RacerDetailsScrapper(links[name], name) as rds:
                self.assertIsNotNone(rds)


if __name__ == '__main__':
    unittest.main()
