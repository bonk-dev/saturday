import http.cookies
import unittest

import httpx

from fetcher.scopus_batch import consts
from fetcher.scopus_batch.scraper import ScopusScraper, ScopusScraperConfig


class TestScopusBatchScraperRefresh(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async def mock_handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == '/api/auth/refresh-scopus-jwt':
                new_cookie = http.cookies.SimpleCookie()
                new_cookie[consts.COOKIE_JWT] = 'fresh_jwt'
                new_cookie[consts.COOKIE_JWT]['Path'] = '/'
                new_cookie[consts.COOKIE_JWT]['Domain'] = '.scopus.com'
                return httpx.Response(200, headers={
                    'Set-Cookie': new_cookie.output(header='').strip()
                })
            cookie = request.headers.get('Cookie')
            if 'expired_jwt' in cookie:
                return httpx.Response(403)
            elif 'fresh_jwt' in cookie and request.url.path == '/api/documents/search/eids':
                payload = {
                    'response': {
                        'numFound': 1,
                        'docs': []
                    }
                }
                return httpx.Response(200,
                                      headers={'Content-Type': 'application/json'},
                                      json=payload)
            else:
                return httpx.Response(500)
        self.mock_t = httpx.MockTransport(mock_handler)
        self.config = ScopusScraperConfig(user_agent='saturday/1.0',
                                          scopus_jwt='expired_jwt',
                                          scopus_jwt_domain='.scopus.com',
                                          awselb='aaaaaaaaaa',
                                          scopus_session_uuid='bbbbbbbbb',
                                          sc_session_id='ccccccccccc')
        self.scraper = ScopusScraper(self.config, transport=self.mock_t)

    async def test_jwt_refresh(self):
        new_cookies = self.scraper.get_cookies()
        self.assertIsNone(new_cookies, msg='ScopusScraper returned not None cookies, without refreshing the JWT token')

        _ = await self.scraper.search_eids(item_count=1, offset=0, query='whatever')

        new_cookies = self.scraper.get_cookies()
        self.assertEqual('fresh_jwt', new_cookies.scopus_jwt, msg='The JWT token was not refreshed')
