import json
import os
import unittest

from fetcher.gscholar.bibtex_parser import merge_entries, parse_bibtex_entry
from fetcher.gscholar.models import GoogleScholarBibtexEntry, GoogleScholarHtmlEntry, GoogleScholarEntry, \
    GoogleScholarBibtexScrapeEntry


class TestBibTexParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_path = os.path.dirname(__file__)
        cls.data_dir = os.path.join(base_path, 'data', 'bibtex-parser')

    def test_parse_bibtex_entry(self):
        entries_dir = os.path.join(self.data_dir, 'raw-entries')
        for e in os.scandir(entries_dir):
            if not e.name.endswith('.bib'):
                continue
            golden_file_path = e.path.removesuffix('.bib') + '.json'
            with self.subTest(bib=e.name, json=e.name.replace('.bib', '.json')):
                with open(e.path, 'r') as bibtex_file:
                    bibtex_data = bibtex_file.read()
                with open(golden_file_path, 'r') as golden_file:
                    expected_data = GoogleScholarBibtexEntry(**json.load(golden_file))
                bibtex_scrape_entry = GoogleScholarBibtexScrapeEntry(id=e.name.removesuffix('.bib'),
                                                                     bibtex_data=bibtex_data)
                actual_data = parse_bibtex_entry(bibtex_scrape_entry)
                self.assertEqual(expected_data, actual_data,
                                 msg='Parsed BibTex entry does not equal the expected entry')

    def test_merge_entries(self):
        bibtex_file_path = os.path.join(self.data_dir, 'bibtex-entries.json')
        html_file_path = os.path.join(self.data_dir, 'html-entries.json')
        golden_file_path = os.path.join(self.data_dir, 'golden-merged.json')

        with open(bibtex_file_path, 'r') as bibtex_file:
            bibtex_entries = [GoogleScholarBibtexEntry(**json_obj) for json_obj in json.load(bibtex_file)]
        with open(html_file_path, 'r') as html_file:
            html_entries = [GoogleScholarHtmlEntry(**json_obj) for json_obj in json.load(html_file)]
        with open(golden_file_path, 'r') as golden_file:
            merged_entries = [GoogleScholarEntry(**json_obj) for json_obj in json.load(golden_file)]

        actual_entries = merge_entries(html_entries, bibtex_entries)

        self.assertSequenceEqual(merged_entries, actual_entries,
                                 msg='Merged entries were not equal to expected entries')