import json
import os
import unittest

from fetcher.scopus_batch.parser import ScopusCsvParser


class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_path = os.path.dirname(__file__)
        cls.data_dir = os.path.join(base_path, 'data', 'scopus-batch')

    def test_batch_parser_1(self):
        cases = ['1']

        for case in cases:
            input_name = f'golden-{case}.csv'
            golden_name = f'golden-{case}-expected.json'
            with self.subTest(csv=input_name):
                input_path = os.path.join(self.data_dir, input_name)
                golden_path = os.path.join(self.data_dir, golden_name)
                with open(input_path, 'r') as input_file:
                    parser = ScopusCsvParser(input_file.read())
                    pubs = parser.read_all_publications()
                with open(golden_path, 'r') as golden_file:
                    expected = json.load(golden_file)

                # The same order of actual, parsed publications and expected ones is expected
                for i in range(len(expected)):
                    actual_ith_pub = pubs[i].__dict__
                    expected_ith_pub = expected[i]
                    self.assertEqual(actual_ith_pub, expected_ith_pub)

    def test_invalid_header_throw(self):
        input_path = os.path.join(self.data_dir, 'invalid-header.csv')
        with open(input_path, 'r') as input_file:
            parser = ScopusCsvParser(input_file.read())
            with self.assertRaises(ValueError) as cm:
                _ = parser.read_all_publications()
            self.assertEqual(str(cm.exception),
                             'The actual CSV header row does not match the expected header row.',
                             f'Unexpected error message: {cm.exception}')


if __name__ == '__main__':
    unittest.main()
