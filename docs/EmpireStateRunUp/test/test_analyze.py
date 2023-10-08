import unittest

from pandas import DataFrame

from empirestaterunup.analyze import get_5_number, SUMMARY_METRICS, count_by_age, count_by_gender, count_by_wave, \
    dt_to_sorted_dict
from empirestaterunup.data import load_data, FIELD_NAMES


class AnalyzeTestCase(unittest.TestCase):
    df: DataFrame

    @classmethod
    def setUpClass(cls) -> None:
        cls.df = load_data()

    def test_get_5_number(self):
        for key in SUMMARY_METRICS:
            ndf = get_5_number(criteria=key, data=AnalyzeTestCase.df)
            self.assertIsNotNone(ndf)

    def test_count_by_age(self):
        ndf, header = count_by_age(AnalyzeTestCase.df)
        self.assertIsNotNone(ndf)

    def test_count_by_gender(self):
        ndf, header = count_by_gender(AnalyzeTestCase.df)
        self.assertIsNotNone(ndf)

    def test_count_by_wave(self):
        ndf, header = count_by_wave(AnalyzeTestCase.df)
        self.assertIsNotNone(ndf)

    def test_dt_to_sorted_dict(self):
        ndf, _ = count_by_wave(AnalyzeTestCase.df)
        ndf_dict = dt_to_sorted_dict(ndf)
        self.assertIsNotNone(ndf_dict)
        self.assertLess(0, len(ndf_dict))


if __name__ == '__main__':
    unittest.main()
