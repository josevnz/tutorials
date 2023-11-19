import logging
import pprint
import unittest

from empirestaterunup.data import RaceFields
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
                RaceFields.name.value: 'Alejandra Sanchez',
                RaceFields.url.value: 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/40'
            },
            {
                RaceFields.name.value: 'Alessandro Manrique',
                RaceFields.url.value: 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/562'
            },
            {
                RaceFields.name.value: 'HARPREET Sethi',
                RaceFields.url.value: 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/434'
            }
        ]
        for racer in racer_details:
            print(f"name={racer[RaceFields.name.value]}, url={racer[RaceFields.url.value]}")
            with RacerDetailsScrapper(
                racer=racer,
                debug_level=0,
            ) as rds:
                self.assertIsNotNone(rds)
                self.assertIsNotNone(rds.racer)
                pprint.pp(rds.racer)


if __name__ == '__main__':
    unittest.main()
