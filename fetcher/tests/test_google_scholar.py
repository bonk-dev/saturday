import json
import os
import unittest
from urllib.parse import parse_qs, urlparse

import httpx

from fetcher.gscholar.models import GoogleScholarHtmlEntry
from fetcher.gscholar.scraper import GoogleScholarScraper


class TestMyServiceWithInjectedTransport(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        base_path = os.path.dirname(__file__)
        self.data_dir = os.path.join(base_path, 'data', 'google-scholar')

        async def mock_handler(request: httpx.Request) -> httpx.Response:
            data_dir = os.path.join(base_path, 'data', 'google-scholar')

            path = request.url.path
            if path == "/":
                # initial cookies
                return httpx.Response(200, headers={"Content-Type": "text/html"}, text="<html></html>")
            elif path.startswith('/scholar_settings'):
                # set preferences
                with open(os.path.join(data_dir, 'settings-page.html.raw'), 'r') as settings_page_file:
                    return httpx.Response(200,
                                          headers={"Content-Type": "text/html"},
                                          text=settings_page_file.read())
            elif path.startswith('/scholar_setprefs'):
                return httpx.Response(302, headers={"Content-Type": "text/html"}, text="<html></html>")
            elif path.startswith('/scholar.bib'):
                params = request.url.params

                # TODO: maybe add more bibs idk
                data_id = params['q'].split(':')[1]

                file_path = os.path.join(data_dir, f'generic.bib')

                with open(file_path, 'r') as bib_file:
                    return httpx.Response(200, headers={"Content-Type": "text/plain"}, text=bib_file.read())
            elif path == '/scholar':
                params = request.url.params
                page_num = params.get('start')
                if not page_num:
                    return httpx.Response(500, text='Invalid page num')
                page_num = int(page_num)

                file_path = os.path.join(data_dir, f'page-{str(page_num)}.html.raw')
                if not os.path.isfile(file_path):
                    file_path = os.path.join(data_dir, 'empty.html.raw')

                with open(file_path, 'r') as html_file:
                    return httpx.Response(200, headers={"Content-Type": "text/html"}, text=html_file.read())
            else:
                return httpx.Response(500)
        self.mock_t = httpx.MockTransport(mock_handler)
        self.scraper = GoogleScholarScraper()
        await self.scraper.init(transport=self.mock_t, dry=True)

    async def asyncTearDown(self):
        await self.scraper.aclose()

    async def test_get_initial_cookies(self):
        await self.scraper.get_initial_cookies()

    async def test_set_preferences(self):
        await self.scraper.set_preferences()

    async def test_search_scholar_one_page(self):
        pages = [0, 10, 20]

        for offset in pages:
            with self.subTest(start=offset):
                r = await self.scraper.search_scholar("this query doesn't matter lol", start=offset)
                with open(os.path.join(self.data_dir, f'page-{offset}.json'), 'r') as golden_file:
                    golden_r = json.load(golden_file)
                self.assertSequenceEqual(golden_r, [entry.__dict__ for entry in r])

    async def test_search_scholar_empty_page(self):
        r = await self.scraper.search_scholar("this query doesn't matter lol", start=900)
        self.assertEqual(0, len(r), 'Scrape results from a non-existent page weren\'t empty')

    async def test_scrape_bibtex_file(self):
        with open(os.path.join(self.data_dir, f'page-0.json'), 'r') as sample_entries_file:
            sample_entries = json.load(sample_entries_file)
        for entry in sample_entries:
            actual_entry = GoogleScholarHtmlEntry(**entry)

            # TODO: Verify actual BibTex content
            await self.scraper.scrape_bibtex_file(actual_entry)
