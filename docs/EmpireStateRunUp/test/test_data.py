import pprint
import unittest
from pathlib import Path

from empirestaterunup.analyze import better_than_median_waves
from empirestaterunup.data import load_data, Waves, get_wave_from_bib, get_description_for_wave, get_wave_start_time, \
    to_list_of_tuples, load_country_details, lookup_country_by_code, COUNTRY_COLUMNS, get_times, get_positions, \
    get_categories, raw_copy_paste_read, raw_csv_read, RaceFields, FIELD_NAMES

RAW_COPY_PASTE_RACE_RESULTS = Path(__file__).parent.joinpath("raw_data.txt")
RAW_CSV_RACE_RESULTS = Path(__file__).parent.joinpath("raw_data.csv")


class DataTestCase(unittest.TestCase):
    def test_load_data(self):
        data = load_data()
        self.assertIsNotNone(data)
        for row in data:
            self.assertIsNotNone(row)

    def test_get_wave_from_bib(self):
        self.assertEqual(Waves.EliteMen, get_wave_from_bib(1))
        self.assertEqual(Waves.EliteWomen, get_wave_from_bib(26))
        self.assertEqual(Waves.Purple, get_wave_from_bib(100))
        self.assertEqual(Waves.Green, get_wave_from_bib(200))
        self.assertEqual(Waves.Orange, get_wave_from_bib(300))
        self.assertEqual(Waves.Grey, get_wave_from_bib(400))
        self.assertEqual(Waves.Gold, get_wave_from_bib(500))
        self.assertEqual(Waves.Black, get_wave_from_bib(600))

    def test_get_description_for_wave(self):
        self.assertEqual(Waves.EliteMen.value[0], get_description_for_wave(Waves.EliteMen))

    def test_get_wave_start_time(self):
        self.assertEqual(Waves.EliteMen.value[-1], get_wave_start_time(Waves.EliteMen))

    def test_to_list_of_tuples(self):
        data = load_data()
        self.assertIsNotNone(data)

        header, rows = to_list_of_tuples(data)
        self.assertIsNotNone(header)
        self.assertIsNotNone(rows)
        self.assertEqual(376, len(rows))

        header, rows = to_list_of_tuples(data, bibs=[537, 19])
        self.assertIsNotNone(header)
        self.assertIsNotNone(rows)
        self.assertEqual(2, len(rows))

        header, rows = to_list_of_tuples(data, bibs=[999, 10004])
        self.assertIsNotNone(header)
        self.assertIsNotNone(rows)
        self.assertEqual(0, len(rows))

    def test_load_country_details(self):
        data = load_country_details()
        self.assertIsNotNone(data)
        countries = data['name']
        self.assertIsNotNone(countries)
        for idx, country in data.iterrows():
            self.assertIsNotNone(country.iloc[2])

    def test_country_lookup(self):
        run_data = load_data()
        self.assertIsNotNone(run_data)
        country_data = load_country_details()
        self.assertIsNotNone(country_data)
        header, rows = to_list_of_tuples(run_data)
        for row in rows:
            country_code = row[5]
            country_df = lookup_country_by_code(
                df=country_data,
                three_letter_code=country_code
            )
            self.assertIsNotNone(country_df)
            for column in COUNTRY_COLUMNS:
                self.assertIsNotNone(country_df[column])

    def test_get_times(self):
        run_data = load_data()
        self.assertIsNotNone(run_data)
        df = get_times(run_data)
        self.assertIsNotNone(df)
        self.assertEqual(376, df.shape[0])

    def test_get_positions(self):
        run_data = load_data()
        self.assertIsNotNone(run_data)
        df = get_positions(run_data)
        self.assertIsNotNone(df)
        self.assertEqual(376, df.shape[0])

    def test_get_categories(self):
        run_data = load_data()
        self.assertIsNotNone(run_data)
        df = get_categories(run_data)
        self.assertIsNotNone(df)
        self.assertEqual(376, df.shape[0])

    def test_better_than_median_waves(self):
        run_data = load_data()
        self.assertIsNotNone(run_data)
        median_time, wave_series = better_than_median_waves(run_data)
        self.assertIsNotNone(median_time)
        self.assertEqual(43, wave_series.iloc[0])

    def test_raw_copy_paste_read(self):
        clean_data = [record for record in raw_copy_paste_read(RAW_COPY_PASTE_RACE_RESULTS)]
        self.assertIsNotNone(clean_data)
        self.assertEqual(375, len(clean_data))

    def test_raw_csv_read(self):
        clean_data = [record for record in raw_csv_read(RAW_CSV_RACE_RESULTS)]
        self.assertIsNotNone(clean_data)
        self.assertEqual(377, len(clean_data))
        for record in clean_data:
            for field in FIELD_NAMES:
                self.assertTrue(field in record.keys())
            if record[RaceFields.name.value] == "Kamila Chomanicova":
                self.assertEqual(record[RaceFields.age.value], 30)
                self.assertEqual(record[RaceFields.gender.value], "F")
                self.assertEqual(record[RaceFields.sixty_five_floor_time.value], "00:10:40")
            pprint.pprint(record)


if __name__ == '__main__':
    unittest.main()
