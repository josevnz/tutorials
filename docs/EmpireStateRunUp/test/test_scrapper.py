import logging
import pprint
import unittest

from empirestaterunup.scrapper import RacerLinksScrapper, RacerDetailsScrapper

logger = logging.getLogger('selenium')
logger.setLevel(logging.DEBUG)


class RacerLinksScrapperTestCase(unittest.TestCase):
    def test_link_scrapper(self):
        with RacerLinksScrapper(headless=True, debug=False) as esc:
            self.assertIsNotNone(esc)
            self.assertEqual(377, len(esc.racers))
            self.assertEqual(377, len(esc.rank_to_bib))

    def test_runner_detail(self):
        racer_details = [
            {
                'name': 'Alejandra Sanchez',
                'url': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/40'
            },
            {
                'name': 'Alessandro Manrique',
                'url': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/562'
            },
            {
                'name': 'HARPREET Sethi',
                'url': 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/434'
            }
        ]
        for racer in racer_details:
            print(f"name={racer['name']}, url={racer['url']}")
            with RacerDetailsScrapper(
                racer=racer,
                debug_level=1,
            ) as rds:
                self.assertIsNotNone(rds)
                self.assertIsNotNone(rds.racer)
                pprint.pp(rds.racer)


if __name__ == '__main__':
    unittest.main()
