import unittest

from pandas import DataFrame

from empirestaterunup.analyze import get_5_number, SUMMARY_METRICS
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
            print()
            print(ndf)


if __name__ == '__main__':
    unittest.main()
