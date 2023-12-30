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
                RaceFields.NAME.value: 'David Kilgore',
                RaceFields.URL.value: 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/106'
            },
            {
                RaceFields.NAME.value: 'Alejandra Sanchez',
                RaceFields.URL.value: 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/40'
            },
            {
                RaceFields.NAME.value: 'Alessandro Manrique',
                RaceFields.URL.value: 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/562'
            },
            {
                RaceFields.NAME.value: 'HARPREET Sethi',
                RaceFields.URL.value: 'https://www.athlinks.com/event/382111/results/Event/1062909/Course/2407855/Bib/434'
            }
        ]
        for racer in racer_details:
            name = racer[RaceFields.NAME.value]
            print(f"name={name}, url={racer[RaceFields.URL.value]}")
            with RacerDetailsScrapper(
                racer=racer,
                debug_level=0,
            ) as rds:
                self.assertIsNotNone(rds)
                self.assertIsNotNone(rds.racer)
                for field in [
                    RaceFields.TIME.value,
                    RaceFields.PACE.value
                ]:
                    self.assertRegex(rds.racer[field], "\\d+:\\d+", f"{name}: {field}={rds.racer[field]}")
                pprint.pp(rds.racer)


if __name__ == '__main__':
    unittest.main()
