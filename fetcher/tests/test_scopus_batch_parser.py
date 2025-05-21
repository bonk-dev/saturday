import json
import os
import unittest

from fetcher.scopus_batch.parser import ScopusCsvParser


class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_path = os.path.dirname(__file__)
        cls.data_dir = os.path.join(base_path, 'data')

    def test_batch_parser_1(self):
        cases = ['1']

        for case in cases:
            input_name = f'scopus-batch-{case}.csv'
            golden_name = f'scopus-batch-{case}-expected.json'
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


if __name__ == '__main__':
    unittest.main()
