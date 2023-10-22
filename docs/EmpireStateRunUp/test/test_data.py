import unittest

from empirestaterunup.data import load_data, Waves, get_wave_from_bib, get_description_for_wave, get_wave_start_time, \
    to_list_of_tuples


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
        self.assertEqual(374, len(rows))

        header, rows = to_list_of_tuples(data, bibs=[537, 19])
        self.assertIsNotNone(header)
        self.assertIsNotNone(rows)
        self.assertEqual(2, len(rows))

        header, rows = to_list_of_tuples(data, bibs=[999, 10004])
        self.assertIsNotNone(header)
        self.assertIsNotNone(rows)
        self.assertEqual(0, len(rows))


if __name__ == '__main__':
    unittest.main()
